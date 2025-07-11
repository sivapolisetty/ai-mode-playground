"""
LLM Configuration with support for Ollama (local) and OpenRouter (cloud)
"""
import os
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

class LLMConfig:
    """Handles LLM configuration and initialization"""
    
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "ollama")
        
    def get_llm(self, temperature: float = 0.1) -> ChatOpenAI:
        """Get configured LLM based on provider"""
        
        if self.provider == "ollama":
            return self._get_ollama_llm(temperature)
        elif self.provider == "openrouter":
            return self._get_openrouter_llm(temperature)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def _get_ollama_llm(self, temperature: float) -> ChatOpenAI:
        """Configure Ollama LLM"""
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL", "gemma3:12b")
        
        return ChatOpenAI(
            model=model,
            base_url=f"{base_url}/v1",
            api_key="ollama",  # Ollama doesn't require real API key
            temperature=temperature,
            max_tokens=1000
        )
    
    def _get_openrouter_llm(self, temperature: float) -> ChatOpenAI:
        """Configure OpenRouter LLM"""
        api_key = os.getenv("OPENROUTER_API_KEY")
        model = os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash")
        
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY is required for OpenRouter provider")
        
        return ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=temperature,
            max_tokens=1000
        )
    
    def get_info(self) -> Dict[str, Any]:
        """Get LLM configuration info"""
        if self.provider == "ollama":
            return {
                "provider": "ollama",
                "model": os.getenv("OLLAMA_MODEL", "gemma:12b"),
                "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                "cost": "free",
                "privacy": "local"
            }
        else:
            return {
                "provider": "openrouter",
                "model": os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash"),
                "base_url": "https://openrouter.ai/api/v1",
                "cost": "pay-per-use",
                "privacy": "cloud"
            }