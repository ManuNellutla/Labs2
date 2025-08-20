# src/code_analyzer/parser.py

from tree_sitter import Parser, Language
from tree_sitterLanguages import get_language
import yaml
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

QUERIES_DIR = Path(__file__).parent / "queries"
CUSTOM_DIR = None  # Set in load_queries

def load_queries(custom_dir: str):
    global CUSTOM_DIR
    CUSTOM_DIR = Path(custom_dir)
    CUSTOM_DIR.mkdir(parents=True, exist_ok=True)

    queries = {}
    for yaml_file in QUERIES_DIR.glob("*.yaml"):
        lang = yaml_file.stem
        with open(yaml_file, "r") as f:
            data = yaml.safe_load(f)
        queries[lang] = data.get("modes", {})

    # Load custom
    for yaml_file in CUSTOM_DIR.glob("*.yaml"):
        lang = yaml_file.stem
        if lang in queries:
            logger.warning(f"Overriding existing language: {lang}")
        with open(yaml_file, "r") as f:
            data = yaml.safe_load(f)
        queries[lang] = data.get("modes", {})

    supported_modes = set()
    for modes in queries.values():
        supported_modes.update(modes.keys())

    return queries, list(queries.keys()), list(supported_modes)

def parse_code(code_bytes: bytes, language: str, mode: str, queries: dict):
    try:
        logger.debug(f"Attempting to load language: {language}")
        lang_obj = get_language(language)
        logger.debug(f"Successfully loaded language: {language}")
    except Exception as e:
        logger.error(f"Failed to get language {language}: {e}")
        raise ValueError(f"Unsupported language: {language}")

    parser = Parser()
    parser.set_language(lang_obj)

    try:
        tree = parser.parse(code_bytes)
    except Exception as e:
        logger.error(f"Failed to parse code for {language}: {e}")
        raise ValueError(f"Parsing error: {str(e)}")

    if language not in queries or mode not in queries[language]:
        logger.warning(f"No query for mode '{mode}' in language '{language}'")
        raise ValueError(f"No query for mode '{mode}' in language '{language}'")

    try:
        query_str = queries[language][mode]
        query = lang_obj.query(query_str)
        captures = query.captures(tree.root_node)
    except Exception as e:
        logger.error(f"Query execution failed for {language}/{mode}: {e}")
        raise ValueError(f"Query error: {str(e)}")

    results = []
    for node, tag in captures:
        try:
            results.append({
                "tag": tag,
                "text": node.text.decode("utf-8"),
                "start_line": node.start_point[0] + 1,
                "start_column": node.start_point[1],
                "end_line": node.end_point[0] + 1,
                "end_column": node.end_point[1],
            })
        except Exception as e:
            logger.warning(f"Failed to process capture at {node.start_point}: {e}")
            continue

    return results