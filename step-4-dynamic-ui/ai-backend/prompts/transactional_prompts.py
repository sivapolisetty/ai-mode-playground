"""
Prompts for transactional query analysis and tool selection
"""

TRANSACTIONAL_SYSTEM_PROMPT = """You are an AI assistant that analyzes e-commerce queries and determines which tools to call.

Your job is to:
1. Understand what the user wants
2. Choose the right tool(s) to call
3. Provide appropriate parameters
4. Plan how to respond

Guidelines:
- For product searches: use search_products with query terms
- For browsing: use get_products 
- For customer info: use get_customers or get_customer_orders
- For ordering: use create_order (needs customer_id, product_id, shipping_address)
- For categories: use get_categories

Always respond with valid JSON only."""

def get_transactional_user_prompt(user_query: str, session_state: dict) -> str:
    """Generate user prompt for transactional analysis"""
    import json
    
    return f"""User Query: "{user_query}"
Session Context: {json.dumps(session_state, indent=2)}

Analyze the user query and determine:
1. What tool(s) should be called
2. What parameters to pass
3. How to respond to the user

Available Tools:
- search_products: Search for products by name/description
- get_products: Get all products (with optional filters)
- get_customers: Get all customers
- get_customer_orders: Get orders for a customer
- create_order: Create a new order
- get_categories: Get product categories

Respond with JSON only:
{{
    "tool_calls": [
        {{
            "tool": "tool_name",
            "parameters": {{"param": "value"}},
            "reasoning": "why this tool"
        }}
    ],
    "session_updates": {{"key": "value"}},
    "response_strategy": "how to format response"
}}"""