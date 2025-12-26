"""
LangChain Service - Centralized LLM orchestration
Supports Gemini 2.5 Flash (primary) and Claude (fallback)
"""

import os
from typing import Optional, Dict, Any, List
from enum import Enum


class LLMProvider(Enum):
    """Supported LLM providers"""
    GEMINI = "gemini"
    CLAUDE = "claude"


class LangChainService:
    """
    Centralized LangChain orchestration service
    Manages LLM connections, chains, and error handling
    """
    
    def __init__(
        self,
        gemini_api_key: Optional[str] = None,
        claude_api_key: Optional[str] = None,
        provider: Optional[str] = None
    ):
        """
        Initialize LangChain service
        
        Args:
            gemini_api_key: Google Gemini API key
            claude_api_key: Anthropic Claude API key (for fallback)
            provider: Preferred provider ('gemini' or 'claude')
        """
        self.gemini_api_key = gemini_api_key or os.environ.get('GOOGLE_API_KEY')
        self.claude_api_key = claude_api_key or os.environ.get('ANTHROPIC_API_KEY')
        self.provider = provider or os.environ.get('LLM_PROVIDER', 'gemini').lower()
        
        # Initialize LLMs
        self.gemini_llm = None
        self.claude_llm = None
        self.embeddings = None
        
        self._initialize_llms()
    
    def _initialize_llms(self):
        """Initialize LLM connections"""
        # Initialize Gemini
        if self.gemini_api_key:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
                
                model_name = os.environ.get('LLM_MODEL', 'gemini-2.0-flash-exp')
                if model_name not in ['gemini-2.0-flash-exp', 'gemini-1.5-flash', 'gemini-1.5-pro']:
                    model_name = 'gemini-2.0-flash-exp'
                
                self.gemini_llm = ChatGoogleGenerativeAI(
                    model=model_name,
                    temperature=0.3,
                    max_output_tokens=8192,
                    google_api_key=self.gemini_api_key
                )
                
                # Initialize embeddings for methodology matching
                self.embeddings = GoogleGenerativeAIEmbeddings(
                    model="models/embedding-001",
                    google_api_key=self.gemini_api_key
                )
                
                print(f"✅ Gemini LLM initialized: {model_name}")
            except ImportError:
                print("⚠️ langchain-google-genai not installed. Install with: pip install langchain-google-genai")
            except Exception as e:
                print(f"⚠️ Error initializing Gemini: {e}")
        
        # Initialize Claude (fallback)
        if self.claude_api_key:
            try:
                from langchain_anthropic import ChatAnthropic
                
                self.claude_llm = ChatAnthropic(
                    model="claude-3-5-sonnet-20241022",
                    temperature=0.3,
                    max_tokens=4096,
                    anthropic_api_key=self.claude_api_key
                )
                
                print("✅ Claude LLM initialized (fallback)")
            except ImportError:
                print("⚠️ langchain-anthropic not installed. Install with: pip install langchain-anthropic")
            except Exception as e:
                print(f"⚠️ Error initializing Claude: {e}")
    
    def get_llm(self, provider: Optional[str] = None, use_fallback: bool = False):
        """
        Get LLM instance
        
        Args:
            provider: 'gemini' or 'claude' (uses default if None)
            use_fallback: If True, use fallback if primary fails
        
        Returns:
            LLM instance or None
        """
        requested_provider = provider or self.provider
        
        if requested_provider == 'gemini' and self.gemini_llm:
            return self.gemini_llm
        elif requested_provider == 'claude' and self.claude_llm:
            return self.claude_llm
        elif use_fallback:
            # Try fallback
            if requested_provider == 'gemini' and self.claude_llm:
                print("⚠️ Using Claude as fallback (Gemini unavailable)")
                return self.claude_llm
            elif requested_provider == 'claude' and self.gemini_llm:
                print("⚠️ Using Gemini as fallback (Claude unavailable)")
                return self.gemini_llm
        
        return None
    
    def get_embeddings(self):
        """Get embeddings model (for methodology matching)"""
        return self.embeddings
    
    def is_available(self) -> bool:
        """Check if any LLM is available"""
        return self.gemini_llm is not None or self.claude_llm is not None
    
    def create_chain(self, prompt_template, chain_type: str = "llm_chain", **kwargs):
        """
        Create a LangChain chain
        
        Args:
            prompt_template: PromptTemplate instance
            chain_type: Type of chain ('llm_chain', 'sequential', etc.)
            **kwargs: Additional chain parameters
        
        Returns:
            Chain instance
        """
        from langchain.chains import LLMChain, SequentialChain
        
        llm = self.get_llm(use_fallback=True)
        if not llm:
            raise ValueError("No LLM available. Check API keys.")
        
        if chain_type == "llm_chain":
            return LLMChain(llm=llm, prompt=prompt_template, **kwargs)
        elif chain_type == "sequential":
            return SequentialChain(
                chains=[LLMChain(llm=llm, prompt=prompt_template, **kwargs)],
                **kwargs
            )
        else:
            return LLMChain(llm=llm, prompt=prompt_template, **kwargs)
    
    def invoke_with_retry(self, chain, inputs: Dict[str, Any], max_retries: int = 3):
        """
        Invoke chain with retry logic and fallback
        
        Args:
            chain: LangChain chain instance
            inputs: Input dictionary
            max_retries: Maximum retry attempts
        
        Returns:
            Chain output
        """
        import time
        
        for attempt in range(max_retries):
            try:
                result = chain.invoke(inputs)
                return result
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"⚠️ Chain invocation failed (attempt {attempt + 1}/{max_retries}): {e}")
                    print(f"   Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    
                    # Try fallback LLM on retry
                    if attempt == 1 and chain.llm == self.gemini_llm and self.claude_llm:
                        print("   Switching to Claude fallback...")
                        chain.llm = self.claude_llm
                else:
                    raise Exception(f"Chain invocation failed after {max_retries} attempts: {e}")
        
        return None

