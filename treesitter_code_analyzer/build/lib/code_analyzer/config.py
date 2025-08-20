# src/code_analyzer/config.py

import logging
import os
from pathlib import Path
import yaml

CONFIG_PATH = Path("config/config.yaml")

def load_config():
    default_config = {
        "backend": {"port": 8000, "host": "0.0.0.0"},
        "ui": {"port": 8501},
        "logging": {"level": "INFO"},
        "queries": {"custom_dir": "src/code_analyzer/queries/custom"},
    }
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            user_config = yaml.safe_load(f)
        default_config.update(user_config)
    return default_config

def setup_logging(level: str):
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/app.log"),
            logging.StreamHandler(),
        ],
    )
    os.makedirs("logs", exist_ok=True)