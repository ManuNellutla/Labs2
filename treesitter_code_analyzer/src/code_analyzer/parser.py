from tree_sitter import Parser, Language, Query, QueryCursor
import yaml
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

QUERIES_DIR = Path(__file__).parent / "queries"
CUSTOM_DIR = None  # Set in load_queries

# Language bindings (add more as needed)
LANGUAGE_BINDINGS = {
    "python": "tree_sitter_python",
    "javascript": "tree_sitter_javascript",
}

def load_queries(custom_dir: str):
    global CUSTOM_DIR
    CUSTOM_DIR = Path(custom_dir)
    CUSTOM_DIR.mkdir(parents=True, exist_ok=True)

    queries = {}
    logger.info(f"Loading default queries from: {QUERIES_DIR}")
    default_files = list(QUERIES_DIR.glob("*.yaml"))
    logger.info(f"Found default query files: {default_files}")
    for yaml_file in default_files:
        lang = yaml_file.stem
        try:
            with open(yaml_file, "r") as f:
                data = yaml.safe_load(f)
            if data and "modes" in data:
                queries[lang] = data["modes"]
                logger.info(f"Loaded queries for {lang}")
            else:
                logger.warning(f"Invalid or empty query file: {yaml_file}")
        except Exception as e:
            logger.error(f"Error loading {yaml_file}: {e}")

    logger.info(f"Loading custom queries from: {CUSTOM_DIR}")
    custom_files = list(CUSTOM_DIR.glob("*.yaml"))
    logger.info(f"Found custom query files: {custom_files}")
    for yaml_file in custom_files:
        lang = yaml_file.stem
        try:
            with open(yaml_file, "r") as f:
                data = yaml.safe_load(f)
            if data and "modes" in data:
                queries[lang] = data["modes"]
                logger.info(f"Loaded custom queries for {lang}")
            else:
                logger.warning(f"Invalid or empty custom query file: {yaml_file}")
        except Exception as e:
            logger.error(f"Error loading custom {yaml_file}: {e}")

    supported_modes = set()
    for modes in queries.values():
        supported_modes.update(modes.keys())

    logger.info(f"Supported languages: {list(queries.keys())}")
    logger.info(f"Supported modes: {list(supported_modes)}")
    return queries, list(queries.keys()), list(supported_modes)

def parse_code(code_bytes: bytes, language: str, mode: str, queries: dict):
    if language not in LANGUAGE_BINDINGS:
        logger.error(f"Unsupported language: {language}")
        raise ValueError(f"Unsupported language: {language}")

    try:
        # Load language dynamically
        module = __import__(LANGUAGE_BINDINGS[language])
        lang_obj = Language(module.language())
        logger.debug(f"Successfully loaded language: {language}")
    except Exception as e:
        logger.error(f"Failed to load language {language}: {e}")
        raise ValueError(f"Unsupported language: {language}")

    parser = Parser()
    parser.language = lang_obj

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
        query = Query(lang_obj,query_str)
        print(query)
        # Use captures instead of capture_nodes
        # captures = query.captures(tree.root_node)
        captures = QueryCursor(query).captures(tree.root_node)
    except Exception as e:
        logger.error(f"Query execution failed for {language}/{mode}: {e}")
        raise ValueError(f"Query error: {str(e)}")

    call_graph = {}
    block_to_func = {}
    for func_node in captures['function.def']:
        # Find the corresponding block
        for block_node in captures['function.block']:
            # The function definition's block starts at the same line
            if block_node.start_point[0] == func_node.start_point[0] + 1:
                block_to_func[block_node] = func_node.text.decode('utf-8')
                break

    # Build the call graph
    for call_node in captures['function.call']:
        caller = None
        # Find the function block that contains the call
        for block_node, func_name in block_to_func.items():
            if block_node.start_point <= call_node.start_point and block_node.end_point >= call_node.end_point:
                caller = func_name
                break
        
        callee = call_node.text.decode('utf-8')
        if caller and caller != callee:
            if caller not in call_graph:
                call_graph[caller] = []
            if callee not in call_graph[caller]:
                call_graph[caller].append(callee)

    return call_graph