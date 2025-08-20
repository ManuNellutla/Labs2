# README.md

# Code Analyzer App

A production-ready Python application for code analysis using Tree-sitter. Features:
- FastAPI backend for API endpoints.
- Streamlit UI for user interaction.
- Configurable queries per language via YAML files.
- Support for custom parsers (add new language YAML files).
- Error handling and logging.
- Uses UV for dependency management.

## Setup

1. Install UV: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. Clone or create the project structure.
3. Run `uv sync` to install dependencies.
4. Create `config/config.yaml` if customizing (default provided in code).

## Running the App

### Backend (FastAPI)
- Run: `uv run uvicorn src.code_analyzer.api:app --reload --port 8000`
- Access API docs: http://localhost:8000/docs

### UI (Streamlit)
- Run: `uv run streamlit run src/ui.py`
- Access UI: http://localhost:8501

## Configuration

- **Queries**: Edit or add YAML files in `src/code_analyzer/queries/` (e.g., `python.yaml`).
- **Custom Parsers**: Drop new `<language>.yaml` files in `src/code_analyzer/queries/custom/` to add languages/modes.
- **General Config**: `config/config.yaml` for ports, log levels, etc.

## Expanding

- Add tests in `tests/` and run `uv run pytest`.
- Deploy: Use Docker or cloud services (e.g., Render, Heroku). Example Dockerfile:


## Troubleshooting

- Logs: Check `logs/app.log` for errors.
- Unsupported Language: Add YAML query file.
- UV Issues: Ensure UV is updated (`uv self update`).