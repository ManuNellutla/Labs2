import os
import json
from typing import Dict, Any, List, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging

# Import the invoker classes
from core.llm_providers.base_llm_invoker import BaseLLMInvoker
from core.llm_providers.openai_invoker import OpenAIInvoker
from core.llm_providers.gemini_invoker import GeminiInvoker
from core.llm_providers.huggingface_invoker import HuggingFaceInvoker

from core.utils import load_prompt_template

logger = logging.getLogger(__name__)

class LLMProviderError(Exception):
    """Custom exception for LLM provider errors."""
    pass

class LLMManager:
    """
    Manages LLM interactions, acting as a factory for specific LLM invokers
    and handling common LLM-related tasks like chunking.
    """
    def __init__(self, llm_config: Dict[str, Any], context_window: int,
                 chunk_size: int, chunk_overlap: int,
                 analysis_template_path: str, summary_template_path: str):
        self.llm_config = llm_config
        self.context_window = context_window
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Load prompt templates once (they are global to the analysis process)
        self.analysis_template = load_prompt_template(analysis_template_path)
        self.summary_template = load_prompt_template(summary_template_path)

        # Initialize the specific LLM invoker based on settings
        self.llm_invoker = self._get_llm_invoker()

        # Text splitter remains here as it's general for chunking, not LLM-specific
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            add_start_index=True,
        )

    def _get_llm_invoker(self) -> BaseLLMInvoker:
        """
        Factory method to get the correct LLM invoker instance
        based on the 'type' specified in the configuration.
        """
        llm_type = self.llm_config['type'].lower()

        # Map LLM types to their respective invoker classes
        invoker_classes = {
            'openai': OpenAIInvoker,
            'gemini': GeminiInvoker,
            'huggingface': HuggingFaceInvoker,
            # Add new LLM providers here by mapping their 'type' string
            # from settings.json to their respective Invoker class.
        }

        invoker_class = invoker_classes.get(llm_type)
        if not invoker_class:
            raise LLMProviderError(f"Unsupported LLM type specified in settings: {llm_type}. "
                                   f"Available types: {', '.join(invoker_classes.keys())}")

        logger.info(f"Using LLM provider: {llm_type}")
        return invoker_class(
            llm_config=self.llm_config,
            context_window=self.context_window,
            analysis_template=self.analysis_template,
            summary_template=self.summary_template
        )

    def get_token_count(self, text: str) -> int:
        """
        Delegates token count estimation to the specific LLM invoker.
        """
        return self.llm_invoker.get_token_count(text)

    def analyze_code(self, code: str, static_analysis_findings: str = "") -> Dict[str, Any]:
        """
        Delegates code analysis to the specific LLM invoker.
        """
        return self.llm_invoker.analyze_code(code, static_analysis_findings)

    def chunk_code(self, code: str) -> List[str]:
        """
        Splits large code into smaller chunks using a general text splitter.
        """
        docs = self.text_splitter.create_documents([code])
        return [doc.page_content for doc in docs]

    def summarize_analyses(self, chunk_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Delegates summarization to the specific LLM invoker.
        """
        return self.llm_invoker.summarize_analyses(chunk_analyses)