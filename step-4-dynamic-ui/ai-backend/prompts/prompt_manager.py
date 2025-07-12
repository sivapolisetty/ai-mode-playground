"""
Centralized prompt management for Step 4 Dynamic UI Generation
"""

from .transactional_prompts import TRANSACTIONAL_SYSTEM_PROMPT, get_transactional_user_prompt
from .response_prompts import RESPONSE_SYSTEM_PROMPT, get_response_generation_prompt
from .ui_generation_prompts import get_ui_generation_prompt

class PromptManager:
    """Centralized prompt management class"""
    
    @staticmethod
    def get_transactional_system_prompt() -> str:
        """Get system prompt for transactional analysis"""
        return TRANSACTIONAL_SYSTEM_PROMPT
    
    @staticmethod
    def get_transactional_user_prompt(user_query: str, session_state: dict) -> str:
        """Get user prompt for transactional analysis"""
        return get_transactional_user_prompt(user_query, session_state)
    
    @staticmethod
    def get_response_system_prompt() -> str:
        """Get system prompt for response generation"""
        return RESPONSE_SYSTEM_PROMPT
    
    @staticmethod
    def get_response_generation_prompt(original_query: str, strategy: str, context_parts: list) -> str:
        """Get prompt for response generation"""
        return get_response_generation_prompt(original_query, strategy, context_parts)
    
    @staticmethod
    def get_ui_generation_prompt(user_query: str, context_summary: str, data_summary: str, component_summary: str) -> str:
        """Get prompt for UI component generation"""
        return get_ui_generation_prompt(user_query, context_summary, data_summary, component_summary)

# Convenience instance
prompt_manager = PromptManager()