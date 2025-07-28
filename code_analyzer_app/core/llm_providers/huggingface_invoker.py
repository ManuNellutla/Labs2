import os
import logging
from typing import Dict, Any
from langchain_community.llms import HuggingFaceHub
from langchain_core.language_models.chat_models import BaseChatModel

from .base_llm_invoker import BaseLLMInvoker

logger = logging.getLogger(__name__)

class HuggingFaceInvoker(BaseLLMInvoker):
    """
    LLM Invoker for Hugging Face Hub models (e.g., Llama, Mistral via Inference API).
    """
    def __init__(self, llm_config: Dict[str, Any], context_window: int,
                 analysis_template: str, summary_template: str):
        super().__init__(llm_config, context_window, analysis_template, summary_template)
        self.repo_id = self.llm_config.get('model') # HuggingFace uses repo_id as model identifier
        if not self.repo_id:
            raise ValueError("Hugging Face Hub 'model' (repo_id) not provided in LLM configuration.")

    def _initialize_llm(self) -> BaseChatModel:
        """
        Initializes the Hugging Face Hub LLM.
        """
        api_key = self.llm_config.get('api_key')
        if not api_key:
            raise ValueError("Hugging Face API token (HUGGINGFACEHUB_API_TOKEN) not provided in LLM configuration.")
        os.environ["HUGGINGFACEHUB_API_TOKEN"] = api_key # LangChain HuggingFaceHub expects this env var
        logger.info(f"Initializing Hugging Face Hub LLM with repo_id: {self.repo_id}")
        # HuggingFaceHub generally doesn't have native JSON mode, so we rely on prompt engineering
        return HuggingFaceHub(repo_id=self.repo_id, model_kwargs={"temperature": 0.1})

    def get_token_count(self, text: str) -> int:
        """
        Estimates token count for Hugging Face Hub models.
        (Often no direct token counter via LangChain for these).
        """
        return len(text) // 4 # Rough approximation