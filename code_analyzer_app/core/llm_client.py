import google.generativeai as genai
import logging
import json
import textwrap
import time
from typing import Dict, Any, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, api_key: str, model_name: str, temperature: float = 0.1,
                 timeout: int = 120, max_retries: int = 3):
        if not api_key:
            raise ValueError("LLM API key is not provided.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.generation_config = genai.GenerationConfig(
            temperature=temperature,
            candidate_count=1 # We usually only need one candidate
        )
        self.timeout = timeout
        self.max_retries = max_retries
        logger.info(f"LLMClient initialized with model: {model_name}, temperature: {temperature}")

    def _call_llm(self, prompt: str) -> Optional[str]:
        """
        Makes a call to the LLM with retry logic.
        """
        for attempt in range(self.max_retries):
            try:
                # Add a timeout to the request
                response = self.model.generate_content(
                    prompt,
                    generation_config=self.generation_config,
                    request_options={"timeout": self.timeout}
                )
                if response.parts:
                    return response.text
                elif response.prompt_feedback and response.prompt_feedback.block_reason:
                    logger.error(f"LLM prompt blocked: {response.prompt_feedback.block_reason}")
                    return None
                else:
                    logger.warning("LLM returned no content.")
                    return None
            except genai.types.BlockedPromptException as e:
                logger.error(f"LLM call blocked due to prompt content: {e}")
                return None # No point retrying if blocked by content
            except Exception as e:
                logger.warning(f"LLM call failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                time.sleep(2 ** attempt) # Exponential backoff
        logger.error(f"LLM call failed after {self.max_retries} attempts.")
        return None

    def _chunk_code(self, code_content: str, chunk_size: int) -> List[str]:
        """
        Chunks code content into smaller pieces if it exceeds chunk_size,
        trying to break at logical points (e.g., end of lines).
        """
        if len(code_content) <= chunk_size:
            return [code_content]

        chunks = []
        current_chunk = []
        current_len = 0

        lines = code_content.splitlines(keepends=True) # Keep newlines to maintain structure

        for line in lines:
            if current_len + len(line) <= chunk_size:
                current_chunk.append(line)
                current_len += len(line)
            else:
                chunks.append("".join(current_chunk))
                current_chunk = [line]
                current_len = len(line)

        if current_chunk:
            chunks.append("".join(current_chunk))

        # Further break down chunks if they are still too large
        final_chunks = []
        for chunk in chunks:
            if len(chunk) > chunk_size:
                # Fallback to textwrap if a single line/block is too long
                wrapped_chunks = textwrap.wrap(chunk, width=chunk_size, break_long_words=False, replace_whitespace=False)
                final_chunks.extend(wrapped_chunks)
            else:
                final_chunks.append(chunk)

        logger.debug(f"Chunked code into {len(final_chunks)} pieces.")
        return final_chunks

    def analyze_code_with_llm(self, analysis_context: Dict[str, Any],
                              chunk_size: int, max_tokens_per_call: int) -> Dict[str, Any]:
        """
        Analyzes code content using the LLM, handling chunking for large files.
        Combines individual chunk analyses into a final summary.
        """
        file_path = analysis_context.get("file_path", "unknown_file")
        file_content = analysis_context.get("file_content", "")
        static_results = analysis_context.get("static_analysis_results")

        if not file_content:
            logger.warning(f"No content to analyze for {file_path}.")
            return {}

        chunks = self._chunk_code(file_content, chunk_size)
        individual_analyses = []

        # Prompt for individual chunks
        chunk_prompt_template = """
        You are an AI assistant analyzing source code. Analyze the following code chunk.
        Focus on its purpose, functionality, potential issues, and interaction with other parts of the system.
        If static analysis results are provided, integrate them into your observations.
        
        File Path: {file_path}
        
        {static_results_section}
        
        Code Chunk:
        ```
        {code_chunk}
        ```
        
        Provide a concise JSON output structured as follows:
        
        {{
            "chunk_summary": "Overall summary of this chunk's role.",
            "key_functions": ["function_name", "another_function"],
            "dependencies_or_imports": ["module", "another_module"],
            "potential_issues": ["Issue 1", "Issue 2"],
            "observations": ["Observation 1", "Observation 2"]
        }}
        
        """
        
        static_results_text = ""
        if static_results:
            static_results_text = "Static Analysis Results:\n" + json.dumps(static_results, indent=2) + "\n"

        for i, chunk in enumerate(chunks):
            logger.debug(f"Analyzing chunk {i+1}/{len(chunks)} of {file_path}")
            chunk_prompt = chunk_prompt_template.format(
                file_path=file_path,
                static_results_section=static_results_text,
                code_chunk=chunk
            )
            raw_response = self._call_llm(chunk_prompt)
            raw_response=raw_response.strip("```").strip("json") if raw_response else None
            if raw_response:
                try:
                    chunk_analysis = json.loads(raw_response)
                    individual_analyses.append(chunk_analysis)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON for chunk {i+1} of {file_path}: {e}\nRaw response: {raw_response}...")
            else:
                logger.warning(f"No valid response for chunk {i+1} of {file_path}.")

        if not individual_analyses:
            logger.error(f"No successful individual analyses for {file_path}. Cannot synthesize summary.")
            return {}

        # Synthesize overall summary from individual analyses
        synthesis_prompt_template = """
        You have analyzed several chunks of the file '{file_path}'.
        Now, synthesize a comprehensive and structured summary of the entire file based on the individual chunk analyses provided below.
        Integrate all information to provide a holistic view.
        
        File Path: {file_path}
        
        Individual Chunk Analyses (JSON array):
        ```json
        {individual_analyses_json}
        ```
        
        Provide a final JSON output structured as follows, focusing on a clear, high-level understanding:
        
        {{
            "file_path": "{file_path}",
            "overview": "A high-level summary of the entire file's purpose and main components.",
            "main_outline": [
                "Key section 1: brief description",
                "Key section 2: brief description"
            ],
            "process_flow": "Mermaid syntax (graph TD) illustrating the main execution flow or sequence of operations. If not applicable or insufficient info, return empty string.",
            "business_logic": "Description of core business logic or algorithms implemented.",
            "technical_debt": "Identified areas of technical debt, maintainability issues, or opportunities for refactoring/improvements.",
            "vulnerabilities": "Potential security vulnerabilities or risks. If none, state 'None identified'.",
            "recommendations": "Specific recommendations for improvements, refactoring, or further analysis."
        }}
        
        Ensure the "process_flow" field contains only the Mermaid syntax string or an empty string, without any additional text or markdown fences around it.
        """
        
        # Combine individual analyses for synthesis
        combined_analyses_json = json.dumps(individual_analyses, indent=2)
        
        synthesis_prompt = synthesis_prompt_template.format(
            file_path=file_path,
            individual_analyses_json=combined_analyses_json
        )

        logger.info(f"Synthesizing overall summary for {file_path}...")
        final_raw_response = self._call_llm(synthesis_prompt)
        final_raw_response=final_raw_response.strip("```").strip("json")
        print(final_raw_response)
        if final_raw_response:
            try:
                final_summary_data = json.loads(final_raw_response)
                logger.info(f"Successfully synthesized summary for {file_path}.")
                return final_summary_data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse final JSON summary for {file_path}: {e}\nRaw response: {final_raw_response[:100]}...")
        else:
            logger.error(f"No valid final response for summary synthesis of {file_path}.")

        return {}