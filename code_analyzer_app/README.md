# Code Analyzer Application

A modular Python application for automated code analysis using Large Language Models (LLMs) and static analysis tools. Supports chunking, caching, and extensible provider integration.

---

## Table of Contents
1. [Features](#features)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Project Structure](#project-structure)
5. [Configuration (`settings.json`)](#configuration-settingsjson)
    * [General Settings](#general-settings)
    * [LLM Configuration](#llm-configuration)
        * [OpenAI](#openai)
        * [Google Gemini](#google-gemini)
        * [Hugging Face Hub (for Llama, Mistral, etc.)](#hugging-face-hub-for-llama-mistral-etc)
    * [Context and Chunking](#context-and-chunking)
    * [File Extensions](#file-extensions)
    * [Report Format](#report-format)
    * [Prompt Templates](#prompt-templates)
6. [API Keys (`.env`)](#api-keys-env)
7. [Running the Application](#running-the-application)
    * [Basic Usage](#basic-usage)
    * [With Static Analysis](#with-static-analysis)
    * [Help Command](#help-command)
8. [Output Reports](#output-reports)
9. [Caching](#caching)
10. [Static Analysis Integration](#static-analysis-integration)
11. [Adding New LLM Providers](#adding-new-llm-providers)
12. [Troubleshooting / Common Issues](#troubleshooting--common-issues)
13. [License](#license)
14. [Contributing](#contributing)

---

## Features
- LLM-powered code analysis (Gemini, OpenAI, HuggingFace, etc.)
- Static analysis integration (Pylint, Bandit)
- Handles large files with chunking and context window
- Caching for efficient re-analysis
- Customizable prompt templates
- Extensible provider and report format support

---

## Prerequisites
- Python 3.9+
- API keys for your chosen LLM provider(s)
- (Optional) Pylint and Bandit for static analysis

---

## Installation
1. Clone the repository or create the structure manually.
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the root directory and add your API keys (see [API Keys](#api-keys-env)).

---

## Project Structure
```text
code_analyzer_app/
├── config/                     # Configuration files
│   ├── __init__.py             # Makes 'config' a Python package
│   └── settings.json           # Main application configuration
├── data/
│   ├── input/                  # Input code files for analysis
│   └── output/                 # Output reports
├── core/                       # Core logic as a Python package
│   ├── __init__.py
│   ├── llm_manager.py          # LLM provider management, chunking
│   ├── processor.py            # Orchestrates file processing, LLM/static analysis, caching
│   ├── report_generator.py     # Report formatting and saving
│   ├── static_analyzer.py      # Static analysis (Pylint, Bandit)
│   ├── utils.py                # Utilities (hashing, file I/O, cache)
│   └── llm_providers/          # LLM provider implementations (OpenAI, Gemini, HuggingFace)
├── prompts/
│   ├── analysis_prompt.txt     # LLM prompt template for analysis
│   └── summary_prompt.txt      # LLM prompt template for summary
├── .env                        # API keys and environment variables
├── main.py                     # Application entry point (CLI)
├── cache.json                  # File hash and analysis cache
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

---

## Configuration (`settings.json`)

### General Settings
- `input_dir`: Directory for input code files (default: `data/input`)
- `output_dir`: Directory for output reports (default: `data/output`)

### LLM Configuration
- `llm.type`: Provider type (`openai`, `gemini`, `huggingface`)
- `llm.model`: Model name (e.g., `gpt-4`, `gemini-2.0-flash`)
- `llm.api_key`: API key (can use `env:KEY_NAME` to pull from `.env`)

#### OpenAI
```json
"llm": {
  "type": "openai",
  "model": "gpt-4",
  "api_key": "env:OPENAI_API_KEY"
}
```
#### Google Gemini
```json
"llm": {
  "type": "gemini",
  "model": "gemini-2.0-flash",
  "api_key": "env:GOOGLE_API_KEY"
}
```
#### Hugging Face Hub (for Llama, Mistral, etc.)
```json
"llm": {
  "type": "huggingface",
  "model": "meta-llama/Llama-2-70b-chat-hf",
  "api_key": "env:HUGGINGFACEHUB_API_TOKEN"
}
```

### Context and Chunking
- `context_window`: Max tokens/characters for LLM context
- `chunk_size`: Size of each code chunk
- `chunk_overlap`: Overlap between chunks

### File Extensions
- `file_extensions`: List of file types to analyze (e.g., `.py`, `.js`, `.java`)

### Report Format
- `report_format`: `text`, `markdown`, or `json`

### Prompt Templates
- `prompts.analysis_template_path`: Path to analysis prompt template
- `prompts.summary_template_path`: Path to summary prompt template

---

## API Keys (`.env`)
Store your API keys securely in a `.env` file at the project root. Example:
```ini
OPENAI_API_KEY="sk-..."
GOOGLE_API_KEY="..."
HUGGINGFACEHUB_API_TOKEN="..."
```

---

## Running the Application

### Basic Usage
From the project root:
```bash
python main.py
```

### With Static Analysis
Enable static analysis (requires Pylint/Bandit):
```bash
python main.py --static-analysis
```

### Help Command
See all options:
```bash
python main.py --help
```

---

## Output Reports
- Reports are saved in `data/output/` (or as set in config)
- Format: `.report`, `.md`, or `.json` depending on `report_format`
- Each report summarizes code structure, process flow, business logic, technical debt, and vulnerabilities

---

## Caching
- `cache.json` tracks file hashes and report paths
- Prevents re-analysis of unchanged files for efficiency
- Use `--no-cache` to force re-analysis

---

## Static Analysis Integration
- Integrates Pylint and Bandit for Python files
- Static findings are merged with LLM analysis in reports
- Install with:
  ```bash
  pip install pylint bandit
  ```

---

## Adding New LLM Providers
- Add a new invoker in `core/llm_providers/`
- Register it in `core/llm_manager.py`
- Update `settings.json` with the new provider type and model

---

## Troubleshooting / Common Issues
- **Missing API keys:** Ensure `.env` is present and keys are valid
- **Dependency errors:** Run `pip install -r requirements.txt` in your venv
- **Static analysis not working:** Install Pylint/Bandit
- **Large files:** Adjust `chunk_size` and `context_window` in config
- **Provider/model errors:** Check model name and API key in config

---

## License
MIT License (add LICENSE file if needed)

---

## Contributing
Contributions welcome! Open issues or PRs for improvements.


