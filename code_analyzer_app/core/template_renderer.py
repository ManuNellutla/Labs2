import os
import logging
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Dict, Any

logger = logging.getLogger(__name__)

class TemplateRenderer:
    """
    Renders Jinja2 templates to generate reports.
    """
    def __init__(self, app_config: Any): # Using Any to avoid circular import with AppConfig
        self.app_config = app_config
        self.template_dir = os.path.join(self.app_config.project_root, 'config', 'artifacts')
        
        if not os.path.exists(self.template_dir):
            logger.error(f"Template directory not found: {self.template_dir}")
            raise FileNotFoundError(f"Template directory missing: {self.template_dir}")

        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=select_autoescape(['html', 'xml', 'jinja2', 'md']),
            trim_blocks=True, # Remove extra newlines from blocks
            lstrip_blocks=True # Remove leading whitespace from blocks
        )
        logger.info(f"TemplateRenderer initialized. Templates loaded from: {self.template_dir}")

    def render_template(self, template_name: str, data: Dict[str, Any]) -> str:
        """
        Renders a specified Jinja2 template with the given data.
        """
        try:
            template = self.env.get_template(template_name)
            rendered_content = template.render(data=data)
            logger.debug(f"Template '{template_name}' rendered successfully.")
            return rendered_content
        except Exception as e:
            logger.error(f"Error rendering template '{template_name}': {e}")
            raise