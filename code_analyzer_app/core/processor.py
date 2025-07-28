import os
import logging
import json
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time

from core.llm_manager import LLMManager, LLMProviderError
from core.report_generator import ReportGenerator
from core.static_analyzer import StaticCodeAnalyzer
from core.utils import calculate_file_hash, load_cache, save_cache, is_text_file, read_file_content

logger = logging.getLogger(__name__)

class CodeAnalyzerProcessor:
    def __init__(self, config: Dict[str, Any], enable_static_analysis: bool = False):
        self.config = config
        # Ensure project_root is consistently used from the processor's attribute
        self.project_root = config.get('project_root', os.getcwd()) # Safely get project_root from config, or default

        self.llm_manager = LLMManager(
            llm_config=config['llm'],
            context_window=config['context_window'],
            chunk_size=config['chunk_size'],
            chunk_overlap=config['chunk_overlap'],
            analysis_template_path=config['prompts']['analysis_template_path'],
            summary_template_path=config['prompts']['summary_template_path']
        )
        self.report_generator = ReportGenerator(
            output_dir=config['output_dir'],
            report_format=config['report_format']
        )
        # Use self.project_root here
        self.cache = load_cache(self.project_root)
        self.max_workers = os.cpu_count() * 2
        self.enable_static_analysis = enable_static_analysis
        self.static_analyzer = StaticCodeAnalyzer() if enable_static_analysis else None

    def _process_file(self, filepath: str) -> Dict[str, Any]:
        """Processes a single code file."""
        file_hash = calculate_file_hash(filepath)
        filename = os.path.basename(filepath)

        # Determine expected report path for cache check
        report_ext = ".json" if self.config['report_format'] == "json" else ".md" if self.config['report_format'] == "markdown" else ".report"
        report_filename = f"{filename}{report_ext}"
        report_path = os.path.join(self.config['output_dir'], report_filename)

        # Check cache for unchanged files
        if filepath in self.cache and self.cache[filepath].get('hash') == file_hash and \
           os.path.exists(report_path):
            logger.info(f"Skipping {filename}: File unchanged and report exists (from cache).")
            return {"filepath": filepath, "status": "skipped", "report_path": report_path}

        if not is_text_file(filepath):
            logger.warning(f"Skipping {filename}: Not a recognized text file type.")
            return {"filepath": filepath, "status": "skipped", "reason": "not_text_file"}

        try:
            code_content = read_file_content(filepath)
        except Exception as e:
            logger.error(f"Failed to read file {filename}: {e}")
            return {"filepath": filepath, "status": "failed", "reason": f"file_read_error: {e}"}

        static_analysis_findings_str = ""
        if self.enable_static_analysis and filepath.endswith(".py"):
            logger.info(f"Running static analysis for {filename}...")
            static_findings = self.static_analyzer.analyze_python_file(filepath)
            static_analysis_findings_str = self.static_analyzer.format_findings_for_llm(static_findings)
            if static_analysis_findings_str:
                logger.debug(f"Static analysis for {filename}:\n{static_analysis_findings_str[:500]}...")
            else:
                logger.debug(f"No significant static analysis findings for {filename}.")

        analysis_result: Optional[Dict[str, Any]] = None
        try:
            token_count = self.llm_manager.get_token_count(code_content)
            if token_count > self.llm_manager.context_window:
                logger.info(f"File {filename} is large ({token_count} tokens). Chunking...")
                chunks = self.llm_manager.chunk_code(code_content)
                chunk_analyses: List[Dict[str, Any]] = []

                for i, chunk in enumerate(chunks):
                    logger.info(f"Analyzing chunk {i+1}/{len(chunks)} for {filename}...")
                    retries = 3
                    for attempt in range(retries):
                        try:
                            # Pass static analysis findings only with the first chunk
                            chunk_analysis = self.llm_manager.analyze_code(
                                chunk, static_analysis_findings=static_analysis_findings_str if i == 0 else ""
                            )
                            chunk_analyses.append(chunk_analysis)
                            break
                        except LLMProviderError as e:
                            logger.warning(f"LLM error for chunk {i+1} of {filename} (attempt {attempt+1}/{retries}): {e}")
                            if attempt < retries - 1:
                                time.sleep(2 ** attempt)
                            else:
                                logger.error(f"Failed to analyze chunk {i+1} of {filename} after {retries} attempts.")
                                raise

                if chunk_analyses:
                    logger.info(f"Summarizing chunk analyses for {filename}...")
                    analysis_result = self.llm_manager.summarize_analyses(chunk_analyses)
                    analysis_result['__is_chunked_summary__'] = True
                else:
                    logger.warning(f"No analyses generated for any chunks of {filename}.")
                    analysis_result = {"overview": "No analysis could be generated for this file.", "__is_chunked_summary__": True}
            else:
                logger.info(f"Analyzing {filename}...")
                retries = 3
                for attempt in range(retries):
                    try:
                        analysis_result = self.llm_manager.analyze_code(code_content, static_analysis_findings=static_analysis_findings_str)
                        break
                    except LLMProviderError as e:
                        logger.warning(f"LLM error for {filename} (attempt {attempt+1}/{retries}): {e}")
                        if attempt < retries - 1:
                            time.sleep(2 ** attempt)
                        else:
                            logger.error(f"Failed to analyze {filename} after {retries} attempts.")
                            raise

            if analysis_result:
                is_chunked_summary = analysis_result.pop('__is_chunked_summary__', False)
                report_filepath = self.report_generator.save_report(filepath, analysis_result, is_chunked_summary)
                self.cache[filepath] = {'hash': file_hash, 'timestamp': time.time(), 'report_path': report_filepath}
                # Use self.project_root here
                save_cache(self.cache, self.project_root)
                logger.info(f"Report generated for {filename}: {report_filepath}")
                return {"filepath": filepath, "status": "success", "report_path": report_filepath}
            else:
                logger.error(f"Analysis result was None for {filename}.")
                return {"filepath": filepath, "status": "failed", "reason": "empty_llm_result"}

        except LLMProviderError as e:
            logger.error(f"LLM analysis failed for {filename}: {e}")
            return {"filepath": filepath, "status": "failed", "reason": f"llm_error: {e}"}
        except Exception as e:
            logger.exception(f"An unexpected error occurred processing {filename}: {e}")
            return {"filepath": filepath, "status": "failed", "reason": f"unexpected_error: {e}"}

    def run_analysis(self):
        """Discovers files and orchestrates parallel processing."""
        input_dir = self.config['input_dir']
        file_extensions = tuple(self.config['file_extensions'])
        all_files_to_process = []

        for root, _, files in os.walk(input_dir):
            for file in files:
                if file.endswith(file_extensions):
                    all_files_to_process.append(os.path.join(root, file))

        if not all_files_to_process:
            logger.info(f"No files with extensions {file_extensions} found in {input_dir}.")
            return

        logger.info(f"Found {len(all_files_to_process)} files to analyze.")

        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_filepath = {executor.submit(self._process_file, filepath): filepath for filepath in all_files_to_process}

            for future in tqdm(as_completed(future_to_filepath), total=len(future_to_filepath), desc="Analyzing files"):
                filepath = future_to_filepath[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.critical(f"Critical error in executor for file {filepath}: {e}", exc_info=True)
                    results.append({"filepath": filepath, "status": "failed", "reason": f"executor_critical_error: {e}"})

        successful_reports = [r['filepath'] for r in results if r.get('status') == 'success']
        failed_reports = [r['filepath'] for r in results if r.get('status') == 'failed']
        skipped_reports = [r['filepath'] for r in results if r.get('status') == 'skipped']

        logger.info("\n--- Analysis Summary ---")
        logger.info(f"Successfully analyzed: {len(successful_reports)} files")
        for f in successful_reports:
            logger.info(f"  - {f}")
        logger.info(f"Failed to analyze: {len(failed_reports)} files")
        for f in failed_reports:
            logger.info(f"  - {f} (Reason: {next((item.get('reason', 'N/A') for item in results if item.get('filepath') == f), 'N/A')})")
        logger.info(f"Skipped: {len(skipped_reports)} files")
        for f in skipped_reports:
            logger.info(f"  - {f} (Reason: {next((item.get('reason', 'N/A') for item in results if item.get('filepath') == f), 'N/A')})")

        # Use self.project_root here for the final cache save
        save_cache(self.cache, self.project_root)