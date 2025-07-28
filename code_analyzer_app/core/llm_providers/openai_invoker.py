import os
import logging
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
import tiktoken

from .base_llm_invoker import BaseLLMInvoker

logger = logging.getLogger(__name__)

class OpenAIInvoker(BaseLLMInvoker):
    """
    LLM Invoker for OpenAI models (e.g., GPT-3.5, GPT-4).
    """
    def __init__(self, llm_config: Dict[str, Any], context_window: int,
                 analysis_template: str, summary_template: str):
        super().__init__(llm_config, context_window, analysis_template, summary_template)
        self.model_name = self.llm_config.get('model', 'gpt-4o') # Default if not specified

    def _initialize_llm(self) -> BaseChatModel:
        """
        Initializes the OpenAI Chat model.
        """
        api_key = self.llm_config.get('api_key')
        if not api_key:
            raise ValueError("OpenAI API key not provided in LLM configuration.")
        logger.info(f"Initializing OpenAI LLM with model: {self.model_name}")
        # Enforce JSON output for OpenAI (binds to the LLM instance)
        return ChatOpenAI(model=self.model_name, api_key=api_key, temperature=0.0).bind(response_format={"type": "json_object"})

    def get_token_count(self, text: str) -> int:
        """
        Calculates token count for OpenAI models using tiktoken.
        """
        try:
            encoding = tiktoken.encoding_for_model(self.model_name)
            return len(encoding.encode(text))
        except Exception as e:
            logger.warning(f"Could not get precise token count for OpenAI model. Using approximation. Error: {e}")
            return len(text) // 4 # Fallback approximation