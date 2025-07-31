import os
import logging
from typing import Dict, Any, List, Optional
import time

# Import necessary components
from core.config_loader import AppConfig
from core.llm_client import LLMClient
from core.static_analyzer import StaticAnalyzer
from core.utils import (
    calculate_file_hash, load_cache, save_cache,
    is_text_file, read_file_content
)
from core.template_renderer import TemplateRenderer

logger = logging.getLogger(__name__)

class Processor:
    def __init__(self, app_config: AppConfig):
        self.app_config: AppConfig = app_config
        self.input_dir: str = self.app_config.input_dir
        self.output_dir: str = self.app_config.output_dir
        self.cache: Dict[str, Any] = load_cache(self.app_config)
        self.renderer = TemplateRenderer(app_config)

        self.llm_client = LLMClient(
            api_key=self.app_config.llm_api_key, # Use attribute from AppConfig
            model_name=self.app_config.llm_model_name, # Use attribute from AppConfig
            temperature=self.app_config.llm_temperature, # Use attribute from AppConfig
            timeout=self.app_config.llm_timeout, # Use attribute from AppConfig
            max_retries=self.app_config.max_retries # Use attribute from AppConfig
        )
        self.static_analyzer = StaticAnalyzer() if self.app_config.static_analysis_enabled else None

    def _get_all_source_files(self) -> List[str]:
        """Collects all relevant source files from the input directory."""
        source_files = []
        print(self.input_dir )
        for root, dirs, files in os.walk(self.input_dir, topdown=True):
            # Exclude directories as specified in config
            dirs[:] = [d for d in dirs if os.path.join(root, d) not in self.app_config.exclude_dirs]

            for file in files:
                file_path = os.path.join(root, file)
                # Exclude files based on patterns and ensure it's a text file
                if not any(pattern in file for pattern in self.app_config.exclude_file_patterns) and \
                   is_text_file(file_path):
                    source_files.append(file_path)
        logger.info(f"Found {len(source_files)} source files to analyze.")
        return source_files

    def _process_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Processes a single file: checks cache, performs analysis, and returns data."""
        relative_file_path = os.path.relpath(file_path, self.app_config.project_root)
        logger.info(f"Processing file: {relative_file_path}")

        file_hash = calculate_file_hash(file_path)
        
        # Check cache
        if file_hash in self.cache and self.cache[file_hash].get('report_generated_path'):
            logger.info(f"Cache hit for {relative_file_path}. Skipping analysis.")
            return self.cache[file_hash]

        file_content = read_file_content(file_path)
        if file_content is None:
            logger.warning(f"Could not read content for {relative_file_path}. Skipping.")
            return None

        analysis_context = {
            "file_path": relative_file_path,
            "file_content": file_content,
            "static_analysis_results": None,
        }

        # Perform static analysis if enabled
        if self.static_analyzer:
            logger.info(f"Performing static analysis on {relative_file_path}...")
            start_time = time.time()
            static_results = self.static_analyzer.analyze(file_path)
            analysis_context["static_analysis_results"] = static_results
            logger.info(f"Static analysis for {relative_file_path} completed in {time.time() - start_time:.2f}s.")

        # Perform LLM analysis
        logger.info(f"Performing LLM analysis for {relative_file_path}...")
        start_time = time.time()
        try:
            llm_analysis_data = self.llm_client.analyze_code_with_llm(
                analysis_context,
                self.app_config.analysis_chunk_size,
                self.app_config.max_tokens_per_call
            )
            logger.info(f"LLM analysis for {relative_file_path} completed in {time.time() - start_time:.2f}s.")
            
            # Add file_path to the LLM's structured output for rendering
            llm_analysis_data['file_path'] = relative_file_path
            
            # Store in cache
            self.cache[file_hash] = llm_analysis_data
            return llm_analysis_data
        except Exception as e:
            logger.error(f"LLM analysis failed for {relative_file_path}: {e}")
            return None

    def _generate_reports(self, analyzed_data: Dict[str, Any]):
        """Generates various reports based on the analysis data."""
        if not analyzed_data:
            logger.warning("No analysis data provided for report generation.")
            return

        file_path = analyzed_data.get('file_path', 'unknown_file')
        
        # Generate requested output artifacts
        for artifact_type in self.app_config.output_artifacts:
            template_name = self.app_config.artifact_templates.get(artifact_type)
            if template_name:
                output_filename_base = os.path.splitext(os.path.basename(file_path))[0]
                output_file_name = f"{output_filename_base}_{artifact_type}.md" # Assuming .md for simplicity
                output_file_path = os.path.join(self.output_dir, output_file_name)
                
                try:
                    report_content = self.renderer.render_template(template_name, analyzed_data)
                    with open(output_file_path, 'w', encoding='utf-8') as f:
                        f.write(report_content)
                    logger.info(f"Generated {artifact_type} report for {file_path} at {output_file_path}")
                    # Update cache with generated report path
                    self.cache[calculate_file_hash(os.path.join(self.app_config.project_root, file_path))]['report_generated_path'] = output_file_path
                except Exception as e:
                    logger.error(f"Failed to generate {artifact_type} report for {file_path}: {e}")
            else:
                logger.warning(f"No template found for artifact type: {artifact_type}")

    def run_analysis(self):
        """Runs the complete code analysis workflow."""
        logger.info("Starting code analysis...")
        
        # Get all relevant files
        all_files = self._get_all_source_files()
        
        if not all_files:
            logger.warning("No source files found for analysis. Please check your 'input_dir' and 'exclude' settings.")
            return

        for file_path in all_files:
            analyzed_data = self._process_file(file_path)
            print(analyzed_data)
            if analyzed_data:
                self._generate_reports(analyzed_data)
            
            # Save cache after each file or in batches for resilience
            save_cache(self.app_config, self.cache)
            time.sleep(0.1) # Small delay to prevent hitting API limits too fast

        logger.info("Code analysis finished.")
        save_cache(self.app_config, self.cache) # Final save