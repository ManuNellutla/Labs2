import os
import json
from typing import Dict, Any

class ReportGenerator:
    def __init__(self, output_dir: str, report_format: str):
        self.output_dir = output_dir
        self.report_format = report_format
        os.makedirs(self.output_dir, exist_ok=True)

    def _format_analysis_section(self, title: str, content: Any, indent_level: int = 0) -> str:
        indent = "  " * indent_level
        if isinstance(content, list):
            if not content:
                return f"{indent}- No {title.lower()} identified.\n"
            return f"{indent}- {title}:\n{indent}  " + "\n".join([f"- {item}" for item in content]) + "\n"
        elif isinstance(content, dict):
            if not content:
                return f"{indent}- No {title.lower()} identified.\n"
            lines = [f"{indent}- {title}:"]
            for key, value in content.items():
                lines.append(f"{indent}  - {key}: {value}")
            return "\n".join(lines) + "\n"
        elif content:
            return f"{indent}- {title}: {content}\n"
        else:
            return f"{indent}- No {title.lower()} identified.\n"

    def _format_structured_report(self, filename: str, structured_data: Dict[str, Any], is_chunked: bool = False) -> str:
        report_lines = []
        if not is_chunked:
            if self.report_format == "markdown":
                report_lines.append(f"# Analysis Report for `{filename}`\n")
            else:
                report_lines.append(f"Analysis Report for {filename}\n")

        sections_order = [
            ("Overview", structured_data.get('overview')),
            ("Main Outline", structured_data.get('main_outline')),
            ("Process Flow", structured_data.get('process_flow')),
            ("Rules and Business Logic", structured_data.get('rules_and_business_logic')),
            ("Technical Debt", structured_data.get('technical_debt')),
            ("Vulnerabilities", structured_data.get('vulnerabilities'))
        ]

        for i, (title, content) in enumerate(sections_order):
            if self.report_format == "markdown":
                report_lines.append(f"## {i+1}. {title}:")
                if isinstance(content, list):
                    report_lines.extend([f"- {item}" for item in content if item])
                elif isinstance(content, str):
                    report_lines.append(content)
                elif content: # Handles dicts or other types that might come
                    report_lines.append(str(content))
                else:
                    report_lines.append("No information identified.")
                report_lines.append("") # Empty line for spacing
            else: # text format
                report_lines.append(f"{i+1}. {title}:")
                if isinstance(content, list):
                    report_lines.extend([f"   - {item}" for item in content if item])
                elif isinstance(content, str):
                    report_lines.append(f"   {content}")
                elif content:
                    report_lines.append(f"   {str(content)}")
                else:
                    report_lines.append("   No information identified.")
                report_lines.append("")

        return "\n".join(report_lines)

    def save_report(self, original_filepath: str, analysis_data: Dict[str, Any], is_chunked_summary: bool = False):
        filename = os.path.basename(original_filepath)
        base_report_name = f"{filename}.report"
        report_filepath = os.path.join(self.output_dir, base_report_name)

        if self.report_format == "json":
            report_filepath = report_filepath.replace(".report", ".json")
            with open(report_filepath, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, indent=4)
        elif self.report_format == "text" or self.report_format == "markdown":
            formatted_content = self._format_structured_report(filename, analysis_data, is_chunked_summary)
            if self.report_format == "markdown":
                report_filepath = report_filepath.replace(".report", ".md")
            with open(report_filepath, 'w', encoding='utf-8') as f:
                f.write(formatted_content)
        else:
            raise ValueError(f"Unsupported report format: {self.report_format}")

        return report_filepath