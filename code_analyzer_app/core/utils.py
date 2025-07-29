import hashlib
import json
import os
import logging
from typing import Any, Dict, List, Set, Union

from core.config_loader import AppConfig # Import AppConfig correctly

# Configure logging for this module
logger = logging.getLogger(__name__)

def calculate_file_hash(file_path: str) -> str:
    """Calculates the SHA256 hash of a file's content."""
    hasher = hashlib.sha256()
    # Handle potential file access issues more robustly
    try:
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(8192)  # Read in 8KB chunks
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()
    except IOError as e:
        logger.error(f"Error calculating hash for {file_path}: {e}")
        return "ERROR_HASH" # Return a consistent error indicator

def load_cache(app_config: AppConfig) -> Dict[str, Any]:
    """Loads the analysis cache from a JSON file."""
    cache_path = os.path.join(app_config.project_root, app_config.cache_file)
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache = json.load(f)
                logger.debug(f"Cache loaded from {cache_path}")
                return cache
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding cache file {cache_path}: {e}")
            return {} # Return empty cache on decode error
        except Exception as e:
            logger.error(f"An unexpected error occurred loading cache {cache_path}: {e}")
            return {}
    logger.debug(f"No cache file found at {cache_path}. Starting with empty cache.")
    return {}

def save_cache(app_config: AppConfig, cache: Dict[str, Any]):
    """Saves the analysis cache to a JSON file."""
    cache_path = os.path.join(app_config.project_root, app_config.cache_file)
    try:
        # Ensure the directory for the cache file exists
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=4)
        logger.debug(f"Cache saved to {cache_path}")
    except Exception as e:
        logger.error(f"Error saving cache to {cache_path}: {e}")

def is_text_file(file_path: str) -> bool:
    """
    Checks if a file is likely a text file based on its extension and some basic content checks.
    This is a heuristic and not foolproof.
    """
    text_extensions: Set[str] = {'.m',
        '.py', '.js', '.ts', '.java', '.c', '.cpp', '.h', '.hpp', '.cs',
        '.go', '.php', '.rb', '.swift', '.kt', '.html', '.css', '.scss',
        '.xml', '.json', '.yaml', '.yml', '.md', '.txt', '.log', '.ini',
        '.cfg', '.toml', '.sh', '.bash', '.zsh', '.ps1', '.sql', '.vue',
        '.jsx', '.tsx', '.mjs', '.cjs', '.dockerfile', '.properties', '.env'
    }
    _, ext = os.path.splitext(file_path)
    if ext.lower() not in text_extensions:
        return False
    
    # Basic check for null bytes which usually indicate binary files
    try:
        with open(file_path, 'rb') as f:
            # Read first 1KB to check for null bytes
            initial_bytes = f.read(1024)
            if b'\0' in initial_bytes:
                return False # Likely binary
    except Exception as e:
        logger.debug(f"Could not perform binary check on {file_path}: {e}")
        # If we can't check, assume it's text if extension matches
        pass

    return True

def read_file_content(file_path: str) -> Union[str, None]:
    """Reads content of a file, attempting common encodings."""
    # Try utf-8 first, then latin-1
    encodings = ['utf-8', 'latin-1', 'cp1252'] # Added cp1252 for Windows compatibility
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue # Try next encoding
        except Exception as e:
            logger.warning(f"Error reading file {file_path} with encoding {encoding}: {e}")
            return None # Other IO errors are fatal for this read

    logger.warning(f"Could not decode {file_path} with any attempted encoding ({', '.join(encodings)}).")
    return None