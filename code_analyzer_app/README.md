# Code Analyzer Application

This application analyzes code files using a Large Language Model (LLM) to generate reports on code overview, structure, process flow, business logic, technical debt, and potential vulnerabilities. It supports chunking large files and can integrate static analysis tools (Pylint, Bandit) for Python code.

## Project Structure
```code
code_analyzer_app/
├── config/                     # Holds all configuration files
│   ├── init.py             # Makes 'config' a Python package
│   └── settings.py             # Configuration loader and validator
│   └── settings.json           # Main application configuration
├── data/                       # Default input/output directories
│   ├── input/                  # Default input directory for code files
│   └── output/                 # Default output directory for reports
├── core/                       # Core application logic as a Python package
│   ├── init.py             # Makes 'core' a Python package
│   ├── llm_manager.py          # Manages LLM interactions, prompts, and chunking
│   ├── processor.py            # Orchestrates file processing, LLM calls, static analysis, caching
│   ├── report_generator.py     # Handles report formatting and saving
│   ├── static_analyzer.py      # Runs external static analysis tools (Pylint, Bandit)
│   └── utils.py                # General utility functions (hashing, file I/O, caching)
├── prompts/                    # Directory for LLM prompt templates
│   ├── analysis_prompt.txt
│   └── summary_prompt.txt
├── .env                        # Environment variables (e.g., API keys)
├── main.py                     # The primary application entry point
├── cache.json                  # Local cache file for analysis results
└── requirements.txt            # Python dependencies
```

## Setup Instructions

1.  **Clone the repository (or create the structure manually)**:
    ```bash
    # If starting from scratch, create the main directory
    mkdir code_analyzer_app
    cd code_analyzer_app

    # Create subdirectories
    mkdir -p config core data/input data/output prompts

    # Create __init__.py files to make them Python packages
    touch config/__init__.py
    touch core/__init__.py
    ```

2.  **Place the regenerated files**: Copy the content of the regenerated files into their respective paths within the `code_analyzer_app/` directory.

3.  **Create and Activate a Python Virtual Environment (Recommended)**:
    It's best practice to use a virtual environment to manage project dependencies.

    * **Create the virtual environment**:
        ```bash
        python3 -m venv venv
        ```
        (This creates a folder named `venv` in your project directory containing an isolated Python environment.)

    * **Activate the virtual environment**:
        * **On macOS/Linux**:
            ```bash
            source venv/bin/activate
            ```
        * **On Windows (Command Prompt)**:
            ```bash
            .\venv\Scripts\activate.bat
            ```
        * **On Windows (PowerShell)**:
            ```powershell
            .\venv\Scripts\Activate.ps1
            ```
        Once activated, your terminal prompt will usually show `(venv)` at the beginning, indicating you are in the virtual environment.

4.  **Install Python Dependencies**:
    With your virtual environment activated, install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Configure Environment Variables**:
    Create a `.env` file in the `code_analyzer_app/` root directory and add your API keys:
    ```ini
    OPENAI_API_KEY="your_openai_api_key_here"
    # If using Hugging Face, add:
    # HUGGINGFACEHUB_API_TOKEN="your_huggingface_api_token_here"
    ```
    *Replace the placeholder values with your actual API keys.*

6.  **Prepare Input Code**:
    Place the code files you want to analyze into the `data/input/` directory (or specify a different input directory using the `--input-dir` flag). For testing static analysis, include some Python files.

## Usage

Navigate to the `code_analyzer_app/` directory in your terminal. Ensure your virtual environment is activated (see step 3 in "Setup Instructions").


```bash
cd code_analyzer_app
```

Run the application using main.py:

```bash
python main.py [OPTIONS]
```

I can certainly help you with that! Here are the README.md and requirements.txt files for your code_analyzer_app, designed to fit the new modular structure.

code_analyzer_app/README.md
Markdown

# Code Analyzer Application

This application analyzes code files using a Large Language Model (LLM) to generate reports on code overview, structure, process flow, business logic, technical debt, and potential vulnerabilities. It supports chunking large files and can integrate static analysis tools (Pylint, Bandit) for Python code.

## Project Structure
```code
code_analyzer_app/
├── config/                     # Holds all configuration files
│   ├── init.py             # Makes 'config' a Python package
│   └── settings.py             # Configuration loader and validator
│   └── settings.json           # Main application configuration
├── data/                       # Default input/output directories
│   ├── input/                  # Default input directory for code files
│   └── output/                 # Default output directory for reports
├── core/                       # Core application logic as a Python package
│   ├── init.py             # Makes 'core' a Python package
│   ├── llm_manager.py          # Manages LLM interactions, prompts, and chunking
│   ├── processor.py            # Orchestrates file processing, LLM calls, static analysis, caching
│   ├── report_generator.py     # Handles report formatting and saving
│   ├── static_analyzer.py      # Runs external static analysis tools (Pylint, Bandit)
│   └── utils.py                # General utility functions (hashing, file I/O, caching)
├── prompts/                    # Directory for LLM prompt templates
│   ├── analysis_prompt.txt
│   └── summary_prompt.txt
├── .env                        # Environment variables (e.g., API keys)
├── main.py                     # The primary application entry point
├── cache.json                  # Local cache file for analysis results
└── requirements.txt            # Python dependencies
```

## Setup Instructions

1.  **Clone the repository (or create the structure manually)**:
    ```bash
    # If starting from scratch, create the main directory
    mkdir code_analyzer_app
    cd code_analyzer_app

    # Create subdirectories
    mkdir -p config core data/input data/output prompts

    # Create __init__.py files to make them Python packages
    touch config/__init__.py
    touch core/__init__.py
    ```

2.  **Place the regenerated files**: Copy the content of the regenerated files into their respective paths within the `code_analyzer_app/` directory.

3.  **Install Python Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**:
    Create a `.env` file in the `code_analyzer_app/` root directory and add your API keys:
    ```ini
    OPENAI_API_KEY="your_openai_api_key_here"
    # If using Hugging Face, add:
    # HUGGINGFACEHUB_API_TOKEN="your_huggingface_api_token_here"
    ```
    *Replace the placeholder values with your actual API keys.*

5.  **Prepare Input Code**:
    Place the code files you want to analyze into the `data/input/` directory (or specify a different input directory using the `--input-dir` flag). For testing static analysis, include some Python files.

## Usage

Navigate to the `code_analyzer_app/` directory in your terminal.

```bash
cd code_analyzer_app
```

Run the application using main.py:

```bash
python main.py [OPTIONS]
```

Command-line Options:
- config <path>: Specify the path to the configuration JSON file.

Default: config/settings.json

- input-dir <path>: Override the input directory specified in settings.json.
- output-dir <path>: Override the output directory specified in settings.json.
- debug: Enable verbose debug logging.
- no-cache: Disable caching and force re-analysis of all files.
- static-analysis: Enable static code analysis (Pylint, Bandit) for Python files. Ensure Pylint and Bandit are installed 
    ```bash
    pip install pylint bandit.
    ```

### Examples:
- **Basic Analysis (using default config):**
    ```bash
    python main.py
    ```

- **Analyze with Static Analysis enabled:**
    ```bash
    python main.py --static-analysis
    ```

**Generate Markdown Reports in a custom output directory:**
(You would need to change report_format in config/settings.json to "markdown" first, or modify main.py to allow this override via CLI if desired for more flexible ad-hoc changes.)
```bash
python main.py --output-dir my_custom_reports_md
```

Run in Debug mode with no caching:

```bash
python main.py --debug --no-cache
```

## Output
Analysis reports will be saved in the data/output/ directory (or your specified output directory) in the format defined in settings.json (text, markdown, or JSON).

### Extending the Application

- **New LLM Providers:** Add new LLM provider classes in core/llm_manager.py and extend the _initialize_llm method.

- **New Static Analysis Tools:** Add new analyzer methods in core/static_analyzer.py and integrate them into core/processor.py.

- **Custom Report Formats:** Modify core/report_generator.py or introduce new generator classes for different output types. Consider using templating engines like Jinja2 for more complex custom reports.

- **More Sophisticated Chunking:** Enhance core/llm_manager.py's chunk_code method for smarter, context-aware chunking.


