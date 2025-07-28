import json
import os
from typing import Dict, Any, List

class ConfigError(Exception):
    """Custom exception for configuration errors."""
    pass

class AppConfig:
    def __init__(self, config_path: str = 'config/settings.json', project_root: str = None):
        self.config_path = config_path
        self.project_root = project_root if project_root else os.getcwd() # Default to CWD
        self.config: Dict[str, Any] = {}
        self._load_config()
        self._validate_config()

    def _load_config(self):
        """Loads configuration from the JSON file."""
        if not os.path.exists(self.config_path):
            raise ConfigError(f"Configuration file not found: {self.config_path}")
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigError(f"Error decoding configuration JSON: {e}")

        # Resolve API key from environment variable if specified
        llm_config = self.config.get('llm', {})
        api_key_spec = llm_config.get('api_key')
        if isinstance(api_key_spec, str) and api_key_spec.startswith('env:'):
            env_var_name = api_key_spec[4:]
            llm_config['api_key'] = os.getenv(env_var_name)
            if not llm_config['api_key']:
                raise ConfigError(f"Environment variable '{env_var_name}' not set for API key.")
        self.config['llm'] = llm_config

        # Set default prompt paths if not specified and resolve to absolute paths
        if 'prompts' not in self.config:
            self.config['prompts'] = {}
        if 'analysis_template_path' not in self.config['prompts']:
            self.config['prompts']['analysis_template_path'] = "prompts/analysis_prompt.txt"
        if 'summary_template_path' not in self.config['prompts']:
            self.config['prompts']['summary_template_path'] = "prompts/summary_prompt.txt"

        # Resolve all paths relative to the project root
        self.config['input_dir'] = os.path.join(self.project_root, self.config['input_dir'])
        self.config['output_dir'] = os.path.join(self.project_root, self.config['output_dir'])
        self.config['prompts']['analysis_template_path'] = os.path.join(self.project_root, self.config['prompts']['analysis_template_path'])
        self.config['prompts']['summary_template_path'] = os.path.join(self.project_root, self.config['prompts']['summary_template_path'])


    def _validate_config(self):
        """Validates the loaded configuration."""
        required_fields = [
            'input_dir', 'output_dir', 'llm', 'context_window',
            'chunk_size', 'chunk_overlap', 'file_extensions', 'report_format'
        ]
        for field in required_fields:
            if field not in self.config:
                raise ConfigError(f"Missing required configuration field: {field}")

        # Validate LLM specific fields
        llm_config = self.config['llm']
        required_llm_fields = ['type', 'model', 'api_key']
        for field in required_llm_fields:
            if field not in llm_config:
                raise ConfigError(f"Missing required LLM configuration field: llm.{field}")

        # Validate directories after path resolution
        if not os.path.isdir(self.config['input_dir']):
            raise ConfigError(f"Input directory does not exist: {self.config['input_dir']}")

        os.makedirs(self.config['output_dir'], exist_ok=True)

        if not isinstance(self.config['file_extensions'], list) or not all(isinstance(ext, str) for ext in self.config['file_extensions']):
            raise ConfigError("file_extensions must be a list of strings.")

        if self.config['report_format'] not in ["text", "json", "markdown"]:
            raise ConfigError("report_format must be 'text', 'json', or 'markdown'.")

        # Validate prompt paths after path resolution
        for prompt_key in ['analysis_template_path', 'summary_template_path']:
            if prompt_key in self.config['prompts'] and not os.path.exists(self.config['prompts'][prompt_key]):
                raise ConfigError(f"Prompt template file not found: {self.config['prompts'][prompt_key]}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self.config.get(key, default)

    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM specific configuration."""
        return self.config.get('llm', {})

    def __str__(self):
        return json.dumps(self.config, indent=2)