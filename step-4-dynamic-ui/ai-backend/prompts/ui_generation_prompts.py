"""
Prompts for dynamic UI component generation
"""

def get_ui_generation_prompt(user_query: str, context_summary: str, data_summary: str, component_summary: str) -> str:
    """Generate prompt for UI component specification generation"""
    
    return f"""TASK: Generate dynamic UI component specifications for an e-commerce application.

USER QUERY: "{user_query}"

CONTEXT INFORMATION:
{context_summary}

DATA AVAILABLE:
{data_summary}

AVAILABLE UI COMPONENTS:
{component_summary}

INSTRUCTIONS:
1. Analyze the user query and available data to understand what UI would be most helpful
2. Select appropriate components from the available library
3. Generate component specifications that enhance the user experience
4. Focus on making data interactive and actionable
5. Return valid JSON specification only

COMPONENT SPECIFICATION FORMAT:
{{
  "ui_components": [
    {{
      "type": "component_name",
      "props": {{
        "key": "value"
      }},
      "children": "content or data",
      "actions": [
        {{
          "event": "onClick",
          "action": "api_call",
          "payload": {{"endpoint": "/api/...", "data": {{}}}}
        }}
      ],
      "layout": {{
        "position": "inline",
        "priority": "high"
      }}
    }}
  ],
  "layout_strategy": "single_component",
  "user_intent": "intent description"
}}

EXAMPLES:
- Product search queries → Product grid with cards and filters
- Order queries → Order status cards with action buttons  
- Customer queries → Profile forms and information displays

RESPOND WITH VALID JSON ONLY:"""