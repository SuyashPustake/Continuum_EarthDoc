"""
LangChain Chain Implementations
Specialized chains for different AI enrichment tasks
"""

import json
from typing import Dict, List, Any, Optional
from utils.langchain_service import LangChainService
from utils.context_builder import ContextBuilder
from utils.prompt_templates import (
    CONTENT_GENERATION_PROMPT,
    METHODOLOGY_ANALYSIS_PROMPT,
    METHODOLOGY_DETAILED_ANALYSIS_PROMPT,
    TEXT_IMPROVEMENT_PROMPT,
    QA_PROMPT,
    TABLE_FIGURE_SUGGESTION_PROMPT,
    TABLE_GENERATION_PROMPT,
    VALUE_SUGGESTION_PROMPT
)


class ContentGenerationChain:
    """Chain for generating PDD section content"""
    
    def __init__(self, langchain_service: LangChainService):
        self.service = langchain_service
        self.chain = None
        self._initialize_chain()
    
    def _initialize_chain(self):
        """Initialize the content generation chain"""
        llm = self.service.get_llm(use_fallback=True)
        if llm:
            try:
                from langchain.chains import LLMChain
            except ImportError:
                from langchain import LLMChain
            self.chain = LLMChain(
                llm=llm,
                prompt=CONTENT_GENERATION_PROMPT,
                verbose=False
            )
    
    def generate(
        self,
        methodology_data: Dict[str, Any],
        subsection_num: str,
        subsection_title: str,
        project_data: Dict[str, Any],
        task_description: Optional[str] = None
    ) -> str:
        """
        Generate content for a PDD subsection
        
        Args:
            methodology_data: Methodology dictionary
            subsection_num: Subsection number
            subsection_title: Subsection title
            project_data: Project data dictionary
            task_description: Optional task description
        
        Returns:
            Generated content string
        """
        if not self.chain:
            raise ValueError("Chain not initialized. Check LLM availability.")
        
        # Build context
        methodology_context = ContextBuilder.build_methodology_context(methodology_data)
        section_context = ContextBuilder.build_section_context(
            subsection_num,
            subsection_title
        )
        project_data_context = ContextBuilder.build_project_data_context(project_data)
        
        # Default task description
        if not task_description:
            task_description = f"Write comprehensive, audit-ready content for section {subsection_num} ({subsection_title})"
        
        # Invoke chain
        inputs = {
            "methodology_context": methodology_context,
            "section_context": section_context,
            "project_data_context": project_data_context,
            "subsection_num": subsection_num,
            "subsection_title": subsection_title,
            "task_description": task_description
        }
        
        try:
            result = self.service.invoke_with_retry(self.chain, inputs)
            return result.get('text', '') if isinstance(result, dict) else str(result)
        except Exception as e:
            raise Exception(f"Content generation failed: {str(e)}")


class MethodologyRecommendationChain:
    """Chain for recommending methodologies"""
    
    def __init__(self, langchain_service: LangChainService):
        self.service = langchain_service
        self.analysis_chain = None
        self.detailed_chain = None
        self._initialize_chains()
    
    def _initialize_chains(self):
        """Initialize recommendation chains"""
        llm = self.service.get_llm(use_fallback=True)
        if llm:
            from langchain.chains import LLMChain
            self.analysis_chain = LLMChain(
                llm=llm,
                prompt=METHODOLOGY_ANALYSIS_PROMPT,
                verbose=False
            )
            self.detailed_chain = LLMChain(
                llm=llm,
                prompt=METHODOLOGY_DETAILED_ANALYSIS_PROMPT,
                verbose=False
            )
    
    def analyze_project(
        self,
        project_description: str,
        methodology_database: Dict[str, Dict]
    ) -> Dict[str, Any]:
        """
        Analyze project and get methodology recommendations
        
        Args:
            project_description: Project description text
            methodology_database: Full methodology database
        
        Returns:
            Analysis dictionary with recommendations
        """
        if not self.analysis_chain:
            raise ValueError("Chain not initialized. Check LLM availability.")
        
        # Build methodology list context
        methodology_list = ContextBuilder.build_methodology_list_context(methodology_database)
        
        inputs = {
            "project_description": project_description,
            "methodology_list": methodology_list
        }
        
        try:
            result = self.service.invoke_with_retry(self.analysis_chain, inputs)
            response_text = result.get('text', '') if isinstance(result, dict) else str(result)
            
            # Try to parse JSON response
            try:
                # Extract JSON from response if wrapped in markdown
                if '```json' in response_text:
                    json_start = response_text.find('```json') + 7
                    json_end = response_text.find('```', json_start)
                    response_text = response_text[json_start:json_end].strip()
                elif '```' in response_text:
                    json_start = response_text.find('```') + 3
                    json_end = response_text.find('```', json_start)
                    response_text = response_text[json_start:json_end].strip()
                
                return json.loads(response_text)
            except json.JSONDecodeError:
                # Return as text if JSON parsing fails
                return {"raw_response": response_text}
        except Exception as e:
            raise Exception(f"Methodology analysis failed: {str(e)}")
    
    def get_detailed_analysis(
        self,
        methodology_id: str,
        methodology_data: Dict[str, Any],
        project_description: str
    ) -> str:
        """
        Get detailed analysis for a specific methodology
        
        Args:
            methodology_id: Methodology ID
            methodology_data: Methodology dictionary
            project_description: Project description
        
        Returns:
            Detailed analysis text
        """
        if not self.detailed_chain:
            raise ValueError("Chain not initialized. Check LLM availability.")
        
        methodology_context = ContextBuilder.build_methodology_context(methodology_data)
        
        inputs = {
            "methodology_id": methodology_id,
            "methodology_context": methodology_context,
            "project_description": project_description
        }
        
        try:
            result = self.service.invoke_with_retry(self.detailed_chain, inputs)
            return result.get('text', '') if isinstance(result, dict) else str(result)
        except Exception as e:
            raise Exception(f"Detailed analysis failed: {str(e)}")


class TextImprovementChain:
    """Chain for improving user-provided text"""
    
    def __init__(self, langchain_service: LangChainService):
        self.service = langchain_service
        self.chain = None
        self._initialize_chain()
    
    def _initialize_chain(self):
        """Initialize text improvement chain"""
        llm = self.service.get_llm(use_fallback=True)
        if llm:
            try:
                from langchain.chains import LLMChain
            except ImportError:
                from langchain import LLMChain
            self.chain = LLMChain(
                llm=llm,
                prompt=TEXT_IMPROVEMENT_PROMPT,
                verbose=False
            )
    
    def improve(
        self,
        user_text: str,
        methodology_data: Dict[str, Any],
        subsection_num: str,
        subsection_title: str
    ) -> str:
        """
        Improve user-provided text
        
        Args:
            user_text: Original text
            methodology_data: Methodology dictionary
            subsection_num: Subsection number
            subsection_title: Subsection title
        
        Returns:
            Improved text
        """
        if not self.chain:
            raise ValueError("Chain not initialized. Check LLM availability.")
        
        methodology_context = ContextBuilder.build_methodology_context(methodology_data)
        section_context = ContextBuilder.build_section_context(
            subsection_num,
            subsection_title
        )
        
        inputs = {
            "methodology_context": methodology_context,
            "section_context": section_context,
            "user_text": user_text,
            "subsection_num": subsection_num
        }
        
        try:
            result = self.service.invoke_with_retry(self.chain, inputs)
            return result.get('text', '') if isinstance(result, dict) else str(result)
        except Exception as e:
            raise Exception(f"Text improvement failed: {str(e)}")


class QAChain:
    """Chain for answering methodology questions"""
    
    def __init__(self, langchain_service: LangChainService):
        self.service = langchain_service
        self.chain = None
        self._initialize_chain()
    
    def _initialize_chain(self):
        """Initialize Q&A chain"""
        llm = self.service.get_llm(use_fallback=True)
        if llm:
            try:
                from langchain.chains import LLMChain
            except ImportError:
                from langchain import LLMChain
            self.chain = LLMChain(
                llm=llm,
                prompt=QA_PROMPT,
                verbose=False
            )
    
    def answer(
        self,
        question: str,
        methodology_data: Dict[str, Any]
    ) -> str:
        """
        Answer a question about methodology
        
        Args:
            question: User question
            methodology_data: Methodology dictionary
        
        Returns:
            Answer text
        """
        if not self.chain:
            raise ValueError("Chain not initialized. Check LLM availability.")
        
        methodology_context = ContextBuilder.build_methodology_context(methodology_data)
        
        inputs = {
            "methodology_context": methodology_context,
            "question": question
        }
        
        try:
            result = self.service.invoke_with_retry(self.chain, inputs)
            return result.get('text', '') if isinstance(result, dict) else str(result)
        except Exception as e:
            raise Exception(f"Q&A failed: {str(e)}")


class TableSuggestionChain:
    """Chain for suggesting tables and figures"""
    
    def __init__(self, langchain_service: LangChainService):
        self.service = langchain_service
        self.chain = None
        self._initialize_chain()
    
    def _initialize_chain(self):
        """Initialize table/figure suggestion chain"""
        llm = self.service.get_llm(use_fallback=True)
        if llm:
            try:
                from langchain.chains import LLMChain
            except ImportError:
                from langchain import LLMChain
            self.chain = LLMChain(
                llm=llm,
                prompt=TABLE_FIGURE_SUGGESTION_PROMPT,
                verbose=False
            )
    
    def suggest(
        self,
        methodology_data: Dict[str, Any],
        subsection_num: str,
        subsection_title: str
    ) -> Dict[str, Any]:
        """
        Suggest tables and figures for a section
        
        Args:
            methodology_data: Methodology dictionary
            subsection_num: Subsection number
            subsection_title: Subsection title
        
        Returns:
            Dictionary with tables and figures suggestions
        """
        if not self.chain:
            raise ValueError("Chain not initialized. Check LLM availability.")
        
        methodology_context = ContextBuilder.build_methodology_context(methodology_data)
        section_context = ContextBuilder.build_section_context(
            subsection_num,
            subsection_title
        )
        
        inputs = {
            "methodology_context": methodology_context,
            "section_context": section_context,
            "subsection_num": subsection_num
        }
        
        try:
            result = self.service.invoke_with_retry(self.chain, inputs)
            response_text = result.get('text', '') if isinstance(result, dict) else str(result)
            
            # Try to parse JSON
            try:
                if '```json' in response_text:
                    json_start = response_text.find('```json') + 7
                    json_end = response_text.find('```', json_start)
                    response_text = response_text[json_start:json_end].strip()
                elif '```' in response_text:
                    json_start = response_text.find('```') + 3
                    json_end = response_text.find('```', json_start)
                    response_text = response_text[json_start:json_end].strip()
                
                return json.loads(response_text)
            except json.JSONDecodeError:
                return {
                    "error": "Failed to parse JSON response",
                    "raw_response": response_text,
                    "tables": [],
                    "figures": []
                }
        except Exception as e:
            return {
                "error": str(e),
                "tables": [],
                "figures": []
            }


class TableGenerationChain:
    """Chain for generating table structures"""
    
    def __init__(self, langchain_service: LangChainService):
        self.service = langchain_service
        self.chain = None
        self._initialize_chain()
    
    def _initialize_chain(self):
        """Initialize table generation chain"""
        llm = self.service.get_llm(use_fallback=True)
        if llm:
            try:
                from langchain.chains import LLMChain
            except ImportError:
                from langchain import LLMChain
            self.chain = LLMChain(
                llm=llm,
                prompt=TABLE_GENERATION_PROMPT,
                verbose=False
            )
    
    def generate(
        self,
        methodology_data: Dict[str, Any],
        table_type: str,
        subsection_num: str,
        subsection_title: str
    ) -> str:
        """
        Generate a table structure
        
        Args:
            methodology_data: Methodology dictionary
            table_type: Type of table
            subsection_num: Subsection number
            subsection_title: Subsection title
        
        Returns:
            Markdown table string
        """
        if not self.chain:
            raise ValueError("Chain not initialized. Check LLM availability.")
        
        methodology_context = ContextBuilder.build_methodology_context(methodology_data)
        section_context = ContextBuilder.build_section_context(
            subsection_num,
            subsection_title
        )
        
        inputs = {
            "methodology_context": methodology_context,
            "table_type": table_type,
            "section_context": section_context
        }
        
        try:
            result = self.service.invoke_with_retry(self.chain, inputs)
            return result.get('text', '') if isinstance(result, dict) else str(result)
        except Exception as e:
            raise Exception(f"Table generation failed: {str(e)}")


class ValueSuggestionChain:
    """Chain for suggesting parameter values"""
    
    def __init__(self, langchain_service: LangChainService):
        self.service = langchain_service
        self.chain = None
        self._initialize_chain()
    
    def _initialize_chain(self):
        """Initialize value suggestion chain"""
        llm = self.service.get_llm(use_fallback=True)
        if llm:
            try:
                from langchain.chains import LLMChain
            except ImportError:
                from langchain import LLMChain
            self.chain = LLMChain(
                llm=llm,
                prompt=VALUE_SUGGESTION_PROMPT,
                verbose=False
            )
    
    def suggest(
        self,
        methodology_data: Dict[str, Any],
        parameter_key: str,
        parameter_name: str
    ) -> Dict[str, Any]:
        """
        Suggest values for a parameter
        
        Args:
            methodology_data: Methodology dictionary
            parameter_key: Parameter key
            parameter_name: Parameter name
        
        Returns:
            Dictionary with value suggestions
        """
        if not self.chain:
            raise ValueError("Chain not initialized. Check LLM availability.")
        
        methodology_context = ContextBuilder.build_methodology_context(methodology_data)
        
        inputs = {
            "methodology_context": methodology_context,
            "parameter_key": parameter_key,
            "parameter_name": parameter_name
        }
        
        try:
            result = self.service.invoke_with_retry(self.chain, inputs)
            response_text = result.get('text', '') if isinstance(result, dict) else str(result)
            
            # Try to parse JSON
            try:
                if '```json' in response_text:
                    json_start = response_text.find('```json') + 7
                    json_end = response_text.find('```', json_start)
                    response_text = response_text[json_start:json_end].strip()
                elif '```' in response_text:
                    json_start = response_text.find('```') + 3
                    json_end = response_text.find('```', json_start)
                    response_text = response_text[json_start:json_end].strip()
                
                return json.loads(response_text)
            except json.JSONDecodeError:
                return {
                    "suggestion": response_text,
                    "typical_range": "N/A",
                    "common_value": "N/A",
                    "factors": [],
                    "sources": []
                }
        except Exception as e:
            return {
                "error": str(e),
                "suggestion": "Unable to generate suggestion"
            }

