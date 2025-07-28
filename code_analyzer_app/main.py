import argparse
import logging
import sys
import os
from dotenv import load_dotenv

# Adjust sys.path to allow imports from core and config
# This is crucial when running directly from the project root
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now we can import from our newly organized modules
from config.settings import AppConfig, ConfigError
from core.processor import CodeAnalyzerProcessor
from core.utils import save_cache, calculate_file_hash, load_cache # Import to clear cache

# Load environment variables from .env file
load_dotenv()

# Configure logging
def setup_logging(log_file='analyzer.log', debug_mode=False):
    log_level = logging.DEBUG if debug_mode else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, mode='w', encoding='utf-8'), # Overwrite log file each run
            logging.StreamHandler(sys.stdout)
        ]
    )
    # Suppress verbose logging from some libraries if not in debug mode
    if not debug_mode:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("pylint").setLevel(logging.WARNING)
        logging.getLogger("bandit").setLevel(logging.WARNING)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze code files using a configurable Large Language Model (LLM)."
    )
    parser.add_argument(
        "--config",
        type=str,
        default=os.path.join(project_root, "config", "settings.json"), # Default path updated
        help="Path to the configuration JSON file (default: config/settings.json)."
    )
    parser.add_argument(
        "--input-dir",
        type=str,
        help="Override the input directory specified in config/settings.json."
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Override the output directory specified in config/settings.json."
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging."
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable caching and force re-analysis of all files."
    )
    parser.add_argument(
        "--static-analysis",
        action="store_true",
        help="Enable static code analysis (Pylint, Bandit) for Python files to augment LLM findings."
    )

    args = parser.parse_args()

    setup_logging(debug_mode=args.debug)
    logger = logging.getLogger(__name__)

    logger.info("Starting code analysis application...")

    try:
        # Pass the project root to AppConfig to help resolve relative paths
        config_loader = AppConfig(config_path=args.config, project_root=project_root)
        app_config = config_loader.config

        # Apply CLI overrides
        if args.input_dir:
            app_config['input_dir'] = args.input_dir
            logger.info(f"Input directory overridden by CLI: {args.input_dir}")
        if args.output_dir:
            app_config['output_dir'] = args.output_dir
            logger.info(f"Output directory overridden by CLI: {args.output_dir}")

        if args.no_cache:
            cache_file_path = os.path.join(project_root, "cache.json")
            if os.path.exists(cache_file_path):
                os.remove(cache_file_path)
                logger.info("Cache file removed due to --no-cache flag.")
            # Clear lru_cache for calculate_file_hash
            calculate_file_hash.cache_clear()
            # Clear load_cache's internal memoization if it were used
            if hasattr(load_cache, 'cache_clear'):
                load_cache.cache_clear()


        processor = CodeAnalyzerProcessor(app_config, enable_static_analysis=args.static_analysis)
        processor.run_analysis()

        logger.info("Code analysis application finished.")

    except ConfigError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"An unhandled error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()