import os
import logging
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models.chat_models import BaseChatModel

from .base_llm_invoker import BaseLLMInvoker

logger = logging.getLogger(__name__)

class GeminiInvoker(BaseLLMInvoker):
    """
    LLM Invoker for Google Gemini models.
    """
    def __init__(self, llm_config: Dict[str, Any], context_window: int,
                 analysis_template: str, summary_template: str):
        # --- FIX: Set self.model_name *before* calling super().__init__() ---
        self.model_name = llm_config.get('model', 'gemini-1.5-pro')
        super().__init__(llm_config, context_window, analysis_template, summary_template)

    def _initialize_llm(self) -> BaseChatModel:
        """
        Initializes the Google Gemini Chat model.
        """
        api_key = self.llm_config.get('api_key')
        if not api_key:
            raise ValueError("Gemini API key (GOOGLE_API_KEY) not provided in LLM configuration.")
        logger.info(f"Initializing Google Gemini LLM with model: {self.model_name}")
        return ChatGoogleGenerativeAI(model=self.model_name, google_api_key=api_key, temperature=0.0,
                                      convert_system_message_to_human=True,
                                      response_mime_type="application/json")

    def get_token_count(self, text: str) -> int:
        """
        Estimates token count for Gemini models.
        (Google GenAI doesn't expose a direct token counter via LangChain client currently).
        """
        return len(text) // 4 # Common approximation for many models