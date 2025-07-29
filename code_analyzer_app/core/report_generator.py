import os
import json
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class ReportGenerator:
    """
    Generates analysis reports in various formats using Jinja2 templates.
    """
    def __init__(self, templates_dir: str):
        self.templates_dir = templates_dir
        self.env = Environment(loader=FileSystemLoader(templates_dir))
        logger.info(f"ReportGenerator initialized with templates directory: {self.templates_dir}")

    def generate_report(self, template_name: str, data: Dict[str, Any], output_format: str) -> str:
        """
        Generates a report using the specified template and data.

        Args:
            template_name (str): The name of the Jinja2 template file (e.g., 'report_summary.jinja2').
            data (Dict[str, Any]): The data to render into the template.
                                   This typically comes from the LLM's summarized analysis.
            output_format (str): The desired output format ('json' or 'markdown'). Used for internal
                                 logic or validation within the template, but primarily determines
                                 the file extension in the calling code.

        Returns:
            str: The rendered report content.
        """
        try:
            template = self.env.get_template(template_name)
            rendered_content = template.render(data=data, output_format=output_format)
            logger.debug(f"Successfully rendered report with template: {template_name}")
            return rendered_content
        except Exception as e:
            logger.error(f"Error rendering report with template '{template_name}': {e}")
            raise

    def get_file_extension(self, output_format: str) -> str:
        """
        Returns the appropriate file extension based on the output format.
        """
        if output_format == 'json':
            return '.json'
        elif output_format == 'markdown':
            return '.md'
        else:
            logger.warning(f"Unknown output format '{output_format}'. Defaulting to '.txt'.")
            return '.txt'