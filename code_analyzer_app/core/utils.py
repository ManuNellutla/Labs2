import hashlib
import json
import os
import mimetypes
import logging
from typing import Dict, Any
from functools import lru_cache

logger = logging.getLogger(__name__)

@lru_cache(maxsize=128)
def calculate_file_hash(filepath: str) -> str:
    """Calculates the SHA-256 hash of a file's content."""
    hasher = hashlib.sha256()
    # Use a buffer for large files
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        logger.error(f"Error calculating hash for {filepath}: {e}")
        return "ERROR_HASH"

def load_cache(project_root: str) -> Dict[str, Any]:
    """Loads the cache from a JSON file. Cache file is at the project root."""
    cache_file_path = os.path.join(project_root, 'cache.json')
    if os.path.exists(cache_file_path):
        try:
            with open(cache_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.warning(f"Error decoding cache file {cache_file_path}: {e}. Starting with empty cache.")
            return {}
    return {}

def save_cache(cache: Dict[str, Any], project_root: str):
    """Saves the cache to a JSON file. Cache file is at the project root."""
    cache_file_path = os.path.join(project_root, 'cache.json')
    try:
        with open(cache_file_path, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=4)
    except IOError as e:
        logger.error(f"Error saving cache file {cache_file_path}: {e}")

def is_text_file(filepath: str) -> bool:
    """Checks if a file is likely a text file based on mime type and common extensions."""
    # Basic check for common binary file signatures
    try:
        with open(filepath, 'rb') as f:
            header = f.read(4) # Read first 4 bytes
            # Heuristic for common binary files (e.g., PDF, ZIP, PNG, JPEG)
            if header.startswith(b'\x25\x50\x44\x46') or \
               header.startswith(b'\x50\x4B\x03\x04') or \
               header.startswith(b'\x89\x50\x4E\x47') or \
               b'\x00' in header: # Presence of null bytes often indicates binary
                return False
    except Exception as e:
        logger.debug(f"Could not read file header for {filepath}: {e}")
        return False

    mime_type, _ = mimetypes.guess_type(filepath)
    if mime_type:
        # Include common text and code mime types
        if mime_type.startswith('text/') or \
           mime_type == 'application/json' or \
           mime_type == 'application/xml' or \
           mime_type == 'application/javascript' or \
           mime_type == 'application/x-sh':
            return True

    # Fallback: check for common code/text file extensions if mimetype is inconclusive
    text_extensions = {
        '.txt', '.py', '.js', '.html', '.css', '.md', '.json', '.xml', '.yaml', '.yml', '.csv',
        '.java', '.go', '.c', '.cpp', '.cs', '.php', '.rb', '.ts', '.jsx', '.tsx', '.sh', '.sql',
        '.ini', '.log', '.toml', '.cfg', '.conf', '.properties', '.gitignore', '.env', '.dockerfile',
        '.m' # Added .m for MUMPS files
    }
    return any(filepath.lower().endswith(ext) for ext in text_extensions)

def read_file_content(filepath: str) -> str:
    """Reads content from a file with robust encoding handling."""
    encodings_to_try = ['utf-8', 'latin-1', 'cp1252']
    for encoding in encodings_to_try:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            logger.debug(f"Decoding failed with {encoding} for {filepath}.")
            continue
        except Exception as e:
            logger.error(f"Error reading file {filepath} with {encoding}: {e}")
            raise
    logger.error(f"Could not decode file {filepath} with any tried encoding.")
    raise ValueError(f"Failed to read file {filepath} with known encodings.")

def load_prompt_template(filepath: str) -> str:
    """Loads a prompt template from a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise ValueError(f"Prompt template file not found: {filepath}")
    except Exception as e:
        raise ValueError(f"Error loading prompt template from {filepath}: {e}")