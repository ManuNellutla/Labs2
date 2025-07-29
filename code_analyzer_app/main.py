import argparse
import os
import logging

# Set up basic logging (this will be overridden by AppConfig's log_level later)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

# Import core components
from core.config_loader import load_config, AppConfig
from core.processor import Processor

def main():
    parser = argparse.ArgumentParser(description="LLM-Powered Code Analyzer.")
    parser.add_argument(
        "--static-analysis",
        action="store_true",
        help="Enable static analysis (Pylint, Bandit) before LLM analysis."
    )
    parser.add_argument(
        "--output-artifacts",
        nargs='*', # 0 or more arguments
        help="Specify output artifact types (e.g., summary_markdown detailed_json)."
             "Overrides settings.json if provided."
    )
    args = parser.parse_args()

    # Determine project root (directory where main.py is located)
    project_root = os.path.dirname(os.path.abspath(__file__))

    try:
        app_config: AppConfig = load_config(project_root)

        # Override static_analysis_enabled if --static-analysis flag is used
        if args.static_analysis:
            app_config.static_analysis_enabled = True
            logger.info("Static analysis explicitly enabled via command line.")

        # Override output_artifacts if --output-artifacts argument is used
        if args.output_artifacts:
            # Validate provided artifact names against available templates
            valid_artifacts = [
                art for art in args.output_artifacts
                if art in app_config.artifact_templates
            ]
            if len(valid_artifacts) != len(args.output_artifacts):
                invalid_artifacts = set(args.output_artifacts) - set(valid_artifacts)
                logger.warning(f"Ignoring invalid output artifact types: {', '.join(invalid_artifacts)}")
            app_config.output_artifacts = valid_artifacts
            logger.info(f"Output artifacts explicitly set via command line: {', '.join(app_config.output_artifacts)}")

        # Configure logging based on loaded config
        logging.getLogger().setLevel(getattr(logging, app_config.log_level))
        logger.info(f"Log level set to {app_config.log_level}")

        processor = Processor(app_config)
        processor.run_analysis()

        logger.info("Analysis complete!")

    except FileNotFoundError as e:
        logger.critical(f"Configuration error: {e}")
    except ValueError as e:
        logger.critical(f"Configuration parsing error: {e}")
    except Exception as e:
        logger.exception(f"An unhandled error occurred during analysis: {e}")


if __name__ == "__main__":
    main()