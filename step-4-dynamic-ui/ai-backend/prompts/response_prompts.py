"""
Prompts for response generation and formatting
"""

RESPONSE_SYSTEM_PROMPT = """You are a helpful e-commerce assistant. Generate natural, conversational responses that combine knowledge base information with transactional data effectively."""

def get_response_generation_prompt(original_query: str, strategy: str, context_parts: list) -> str:
    """Generate prompt for response formatting"""
    
    return f"""Original Query: "{original_query}"
Strategy: {strategy}
Available Context: {chr(10).join(context_parts)}

Generate a helpful, conversational response that:
1. Directly addresses the user's question
2. Uses information from knowledge base when available
3. Incorporates tool results when relevant
4. Is natural and friendly in tone
5. Provides actionable information

If both knowledge base and tool results are available, synthesize them intelligently.
If only knowledge base is available, provide a complete answer from that.
If only tool results are available, format them conversationally."""