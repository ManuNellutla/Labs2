import json
import os
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class AppConfig:
    """
    Manages application configuration, loaded from settings.json and environment variables.
    """
    def __init__(self, settings_data: Dict[str, Any], project_root: str):
        self.project_root: str = project_root
        self.input_dir: str = os.path.join(project_root, settings_data.get('input_dir', 'data/input'))
        self.output_dir: str = os.path.join(project_root, settings_data.get('output_dir', 'output'))
        self.temp_dir: str = os.path.join(project_root, settings_data.get('temp_dir', '.temp'))
        self.cache_file: str = settings_data.get('cache_file', '.analysis_cache.json')
        self.exclude_dirs: List[str] = [os.path.join(project_root, d) for d in settings_data.get('exclude_dirs', [])]
        self.exclude_file_patterns: List[str] = settings_data.get('exclude_file_patterns', [])
        print(self.exclude_file_patterns)
        # LLM specific settings
        self.llm_model_name: str = settings_data.get('llm_model_name', 'gemini-2.0-flash')
        self.llm_temperature: float = settings_data.get('llm_temperature', 0.1)
        self.llm_timeout: int = settings_data.get('llm_timeout', 120) # seconds
        self.max_retries: int = settings_data.get('max_retries', 3)
        self.analysis_chunk_size: int = settings_data.get('analysis_chunk_size', 4000) # chars
        self.max_tokens_per_call: int = settings_data.get('max_tokens_per_call', 8000)
        
        # LLM API Key (CRITICAL: Loaded from environment variable)
        self.llm_api_key: str = os.environ.get('GEMINI_API_KEY', '')
        if not self.llm_api_key:
            logger.error("GEMINI_API_KEY environment variable not set. LLM operations will fail.")
            # Depending on your preference, you could raise an error here to stop execution
            # raise ValueError("GEMINI_API_KEY environment variable is required.")

        # Analysis process settings
        self.static_analysis_enabled: bool = settings_data.get('static_analysis_enabled', False)
        self.artifact_templates: Dict[str, str] = settings_data.get('artifact_templates', {})
        self.output_artifacts: List[str] = settings_data.get('output_artifacts', [])
        
        # Logging
        self.log_level: str = settings_data.get('log_level', 'INFO').upper()

        # Ensure output and temp directories exist
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)

        logger.info(f"Configuration loaded for project: {self.project_root}")
        logger.debug(f"Input directory: {self.input_dir}")
        logger.debug(f"Output directory: {self.output_dir}")
        logger.debug(f"Cache file: {self.cache_file}")

def load_config(project_root: str) -> AppConfig:
    """Loads the application configuration from settings.json."""
    settings_path = os.path.join(project_root, 'config', 'settings.json')
    if not os.path.exists(settings_path):
        logger.critical(f"Settings file not found at: {settings_path}. Please create it.")
        raise FileNotFoundError(f"settings.json not found at {settings_path}")

    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings_data = json.load(f)
        return AppConfig(settings_data, project_root)
    except json.JSONDecodeError as e:
        logger.critical(f"Error parsing settings.json: {e}")
        raise ValueError(f"Invalid JSON in settings.json: {e}")
    except Exception as e:
        logger.critical(f"An unexpected error occurred while loading settings: {e}")
        raise