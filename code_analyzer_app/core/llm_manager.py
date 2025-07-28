# Manages LLMimport os
import json
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain_community.llms import HuggingFaceHub
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import JsonOutputParser
import logging

from core.utils import load_prompt_template # Updated import

logger = logging.getLogger(__name__)

class LLMProviderError(Exception):
    """Custom exception for LLM provider errors."""
    pass

class LLMManager:
    def __init__(self, llm_config: Dict[str, Any], context_window: int,
                 chunk_size: int, chunk_overlap: int,
                 analysis_template_path: str, summary_template_path: str):
        self.llm_config = llm_config
        self.context_window = context_window
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.llm = self._initialize_llm()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            add_start_index=True,
        )
        self.output_parser = JsonOutputParser()

        self.analysis_template = load_prompt_template(analysis_template_path)
        self.summary_template = load_prompt_template(summary_template_path)

        self.analysis_prompt = PromptTemplate(template=self.analysis_template,
                                              input_variables=["code", "static_analysis_findings"])
        self.summary_prompt = PromptTemplate(template=self.summary_template,
                                             input_variables=["chunk_analyses_json"])

    def _initialize_llm(self) -> BaseChatModel:
        llm_type = self.llm_config['type'].lower()
        model_name = self.llm_config['model']
        api_key = self.llm_config['api_key']

        if llm_type == 'openai':
            if not api_key:
                raise LLMProviderError("OpenAI API key not provided.")
            return ChatOpenAI(model=model_name, api_key=api_key, temperature=0.0).bind(response_format={"type": "json_object"})
        elif llm_type == 'huggingface':
            if not api_key:
                raise LLMProviderError("Hugging Face API token not provided.")
            os.environ["HUGGINGFACEHUB_API_TOKEN"] = api_key
            return HuggingFaceHub(repo_id=model_name, model_kwargs={"temperature": 0.1})
        else:
            raise LLMProviderError(f"Unsupported LLM type: {llm_type}")

    def get_token_count(self, text: str) -> int:
        try:
            if self.llm_config['type'] == 'openai':
                import tiktoken
                encoding = tiktoken.encoding_for_model(self.llm_config['model'])
                return len(encoding.encode(text))
            else:
                return len(text) // 4
        except ImportError:
            logger.warning("tiktoken not installed. Using character count approximation for token calculation.")
            return len(text) // 4

    def analyze_code(self, code: str, static_analysis_findings: str = "") -> Dict[str, Any]:
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
                raise LLMProviderError("LLM response was not valid JSON.")
        except Exception as e:
            logger.error(f"Error during LLM analysis: {e}")
            raise LLMProviderError(f"LLM analysis failed: {e}")

    def chunk_code(self, code: str) -> List[str]:
        docs = self.text_splitter.create_documents([code])
        return [doc.page_content for doc in docs]

    def summarize_analyses(self, chunk_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        chunk_analyses_json_str = json.dumps(chunk_analyses, indent=2)

        try:
            chain = self.summary_prompt | self.llm | self.output_parser
            response = chain.invoke({"chunk_analyses_json": chunk_analyses_json_str})
            if isinstance(response, dict):
                return response
            else:
                logger.error(f"LLM did not return a valid JSON object for summary. Response: {response}")
                raise LLMProviderError("LLM summary response was not valid JSON.")
        except Exception as e:
            logger.error(f"Error during LLM summarization: {e}")
            raise LLMProviderError(f"LLM summarization failed: {e}")
