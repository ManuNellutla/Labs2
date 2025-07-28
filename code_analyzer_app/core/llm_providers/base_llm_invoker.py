import os
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from langchain_core.prompts import PromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import JsonOutputParser
import logging

logger = logging.getLogger(__name__)

class BaseLLMInvoker(ABC):
    """
    Abstract Base Class for all LLM Invokers.
    Defines the common interface for interacting with different LLM providers.
    """
    def __init__(self, llm_config: Dict[str, Any], context_window: int,
                 analysis_template: str, summary_template: str):
        self.llm_config = llm_config
        self.context_window = context_window
        self.output_parser = JsonOutputParser() # Output parser is common

        # Initialize the concrete LLM instance for this invoker
        self.llm = self._initialize_llm()

        # Prompt templates are passed down from LLMManager, as they define the analysis logic
        self.analysis_prompt = PromptTemplate(template=analysis_template,
                                              input_variables=["code", "static_analysis_findings"])
        self.summary_prompt = PromptTemplate(template=summary_template,
                                             input_variables=["chunk_analyses_json"])

    @abstractmethod
    def _initialize_llm(self) -> BaseChatModel:
        """
        Abstract method to be implemented by subclasses to initialize
        their specific LangChain LLM (e.g., ChatOpenAI, ChatGoogleGenerativeAI).
        """
        pass

    @abstractmethod
    def get_token_count(self, text: str) -> int:
        """
        Abstract method to be implemented by subclasses to estimate token count
        for the specific LLM.
        """
        pass

    def analyze_code(self, code: str, static_analysis_findings: str = "") -> Dict[str, Any]:
        """
        Analyzes a single code snippet using the LLM.
        Common implementation for all invokers.
        """
        try:
            chain = self.analysis_prompt | self.llm | self.output_parser
            response = chain.invoke({
                "code": code,
                "static_analysis_findings": static_analysis_findings
            })
            if isinstance(response, dict):
                return response
            else:
                logger.error(f"LLM did not return a valid JSON object. Response: {response}")
                raise ValueError("LLM response was not valid JSON.")
        except Exception as e:
            logger.error(f"Error during LLM analysis: {e}")
            raise

    def summarize_analyses(self, chunk_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Summarizes a list of individual chunk analyses using the LLM.
        Common implementation for all invokers.
        """
        chunk_analyses_json_str = json.dumps(chunk_analyses, indent=2)
        try:
            chain = self.summary_prompt | self.llm | self.output_parser
            response = chain.invoke({"chunk_analyses_json": chunk_analyses_json_str})
            if isinstance(response, dict):
                return response
            else:
                logger.error(f"LLM did not return a valid JSON object for summary. Response: {response}")
                raise ValueError("LLM summary response was not valid JSON.")
        except Exception as e:
            logger.error(f"Error during LLM summarization: {e}")
            raise