"""
LLM Configuration for Step 2 - RAG Integration
Extended from Step 1 with additional configurations
"""
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
from langchain_core.language_models import BaseLanguageModel

# Load environment variables
load_dotenv()

class LLMConfig:
    """Configuration manager for LLM providers"""
    
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "ollama").lower()
        self.setup_provider_configs()
    
    def setup_provider_configs(self):
        """Setup configurations for different LLM providers"""
        self.configs = {
            "ollama": {
                "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                "model": os.getenv("OLLAMA_MODEL", "gemma2:12b"),
                "temperature": float(os.getenv("OLLAMA_TEMPERATURE", "0.1")),
                "top_p": float(os.getenv("OLLAMA_TOP_P", "0.9")),
                "max_tokens": int(os.getenv("OLLAMA_MAX_TOKENS", "2048"))
            },
            "openrouter": {
                "api_key": os.getenv("OPENROUTER_API_KEY"),
                "base_url": "https://openrouter.ai/api/v1",
                "model": os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-exp"),
                "temperature": float(os.getenv("OPENROUTER_TEMPERATURE", "0.1")),
                "max_tokens": int(os.getenv("OPENROUTER_MAX_TOKENS", "2048"))
            }
        }
    
    def get_llm(self, temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> BaseLanguageModel:
        """
        Get configured LLM instance
        
        Args:
            temperature: Override default temperature
            max_tokens: Override default max tokens
            
        Returns:
            Configured LLM instance
        """
        if self.provider == "ollama":
            return self._get_ollama_llm(temperature, max_tokens)
        elif self.provider == "openrouter":
            return self._get_openrouter_llm(temperature, max_tokens)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def _get_ollama_llm(self, temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> Ollama:
        """Get Ollama LLM instance"""
        config = self.configs["ollama"]
        
        return Ollama(
            base_url=config["base_url"],
            model=config["model"],
            temperature=temperature or config["temperature"],
            top_p=config["top_p"],
            num_ctx=max_tokens or config["max_tokens"]
        )
    
    def _get_openrouter_llm(self, temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> ChatOpenAI:
        """Get OpenRouter LLM instance"""
        config = self.configs["openrouter"]
        
        if not config["api_key"]:
            raise ValueError("OpenRouter API key not configured")
        
        return ChatOpenAI(
            openai_api_key=config["api_key"],
            openai_api_base=config["base_url"],
            model_name=config["model"],
            temperature=temperature or config["temperature"],
            max_tokens=max_tokens or config["max_tokens"]
        )
    
    def get_info(self) -> Dict[str, Any]:
        """Get current LLM configuration info"""
        config = self.configs.get(self.provider, {})
        
        return {
            "provider": self.provider,
            "model": config.get("model", "unknown"),
            "temperature": config.get("temperature", 0.1),
            "max_tokens": config.get("max_tokens", 2048),
            "base_url": config.get("base_url", "unknown")
        }
    
    def validate_config(self) -> bool:
        """Validate current configuration"""
        if self.provider not in self.configs:
            return False
        
        config = self.configs[self.provider]
        
        if self.provider == "openrouter":
            return bool(config.get("api_key"))
        
        return True