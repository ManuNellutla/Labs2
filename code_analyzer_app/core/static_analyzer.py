import subprocess
import json
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class StaticAnalysisError(Exception):
    """Custom exception for static analysis tool errors."""
    pass

class StaticAnalyzer:
    def __init__(self):
        self.pylint_available = False
        self.bandit_available = False
        self._check_tool_availability()

    def _check_tool_availability(self):
        self.pylint_available = self._is_tool_available("pylint")
        self.bandit_available = self._is_tool_available("bandit")
        if not self.pylint_available:
            logger.warning("Pylint not found. Install with 'pip install pylint' for static analysis.")
        if not self.bandit_available:
            logger.warning("Bandit not found. Install with 'pip install bandit' for static analysis.")

    def _is_tool_available(self, tool_name: str) -> bool:
        try:
            subprocess.run([tool_name, '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def analyze(self, filepath: str) -> Dict[str, List[Dict[str, any]]]:
        findings: Dict[str, List[Dict[str, any]]] = {
            "pylint": [],
            "bandit": []
        }

        if filepath.endswith(".py"):
            if self.pylint_available:
                try:
                    pylint_result = subprocess.run(
                        ['pylint', '--output-format=json', filepath],
                        capture_output=True,
                        text=True,
                        check=False,
                        encoding='utf-8',
                        errors='ignore' # Handle potential encoding issues in tool output
                    )
                    if pylint_result.stdout:
                        findings["pylint"] = json.loads(pylint_result.stdout)
                    logger.debug(f"Pylint analysis for {filepath} completed.")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse Pylint JSON output for {filepath}: {e}. Output: {pylint_result.stdout[:500]}")
                except Exception as e:
                    logger.error(f"Error running Pylint on {filepath}: {e}")
            else:
                logger.debug(f"Pylint not available, skipping Pylint analysis for {filepath}.")

            if self.bandit_available:
                try:
                    bandit_result = subprocess.run(
                        ['bandit', '-r', 'json', '-q', filepath],
                        capture_output=True,
                        text=True,
                        check=False,
                        encoding='utf-8',
                        errors='ignore'
                    )
                    if bandit_result.stdout:
                        bandit_output = json.loads(bandit_result.stdout)
                        if 'results' in bandit_output:
                            findings["bandit"] = bandit_output['results']
                    logger.debug(f"Bandit analysis for {filepath} completed.")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse Bandit JSON output for {filepath}: {e}. Output: {bandit_result.stdout[:500]}")
                except Exception as e:
                    logger.error(f"Error running Bandit on {filepath}: {e}")
            else:
                logger.debug(f"Bandit not available, skipping Bandit analysis for {filepath}.")
        else:
            logger.debug(f"Skipping static analysis for non-Python file: {filepath}")

        return findings

    def format_findings_for_llm(self, findings: Dict[str, List[Dict[str, any]]]) -> str:
        formatted_text = []

        if findings.get("pylint"):
            formatted_text.append("\n--- Pylint Findings ---")
            for item in findings["pylint"]:
                formatted_text.append(f"  [{item.get('type')}] {item.get('message_id')}: {item.get('message')} "
                                      f"(Line: {item.get('line')}, Col: {item.get('column')})")
        if findings.get("bandit"):
            formatted_text.append("\n--- Bandit Findings (Security) ---")
            for item in findings["bandit"]:
                formatted_text.append(f"  Severity: {item.get('issue_severity')}, Confidence: {item.get('issue_confidence')}")
                formatted_text.append(f"  Line: {item.get('line_number')}, Code: {item.get('code')}")
                formatted_text.append(f"  Issue: {item.get('issue_text')}")
                formatted_text.append(f"  More info: {item.get('more_info')}")

        if not formatted_text:
            return ""
        return "\n".join(formatted_text)
