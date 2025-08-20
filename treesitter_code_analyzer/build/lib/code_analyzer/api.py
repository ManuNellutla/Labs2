# src/code_analyzer/api.py

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from .config import load_config, setup_logging
from .parser import load_queries, parse_code
import logging

logger = logging.getLogger(__name__)

config = load_config()
setup_logging(config["logging"]["level"])

QUERIES, SUPPORTED_LANGUAGES, SUPPORTED_MODES = load_queries(config["queries"]["custom_dir"])

app = FastAPI(title="Code Analyzer API")

@app.on_event("startup")
async def startup_event():
    logger.info("API started with supported languages: %s", SUPPORTED_LANGUAGES)

@app.get("/getParser")
async def get_parser_info():
    return {
        "languages": SUPPORTED_LANGUAGES,
        "modes": SUPPORTED_MODES,
    }

@app.post("/parse")
async def parse_endpoint(
    file: UploadFile = File(...),
    language: str = Form(...),
    mode: str = Form(...),
):
    if language not in SUPPORTED_LANGUAGES:
        logger.warning(f"Unsupported language requested: {language}")
        raise HTTPException(status_code=400, detail=f"Unsupported language: {language}")
    if mode not in SUPPORTED_MODES:
        logger.warning(f"Unsupported mode requested: {mode}")
        raise HTTPException(status_code=400, detail=f"Unsupported mode: {mode}")

    try:
        code_bytes = await file.read()
        results = parse_code(code_bytes, language, mode, QUERIES)
        return {"results": results}
    except ValueError as ve:
        logger.error(f"Value error during parsing: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.exception(f"Unexpected error during parsing: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")