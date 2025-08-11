# Prompts Documentation

This folder contains all LLM prompts used in the Step 4 Dynamic UI Generation system, organized by functionality.

## Structure

```
prompts/
├── __init__.py                 # Module initialization
├── prompt_manager.py           # Centralized prompt management
├── transactional_prompts.py    # Prompts for tool selection and analysis  
├── response_prompts.py         # Prompts for response generation
├── ui_generation_prompts.py    # Prompts for UI component generation
└── README.md                   # This documentation
```

## Usage

```python
from prompts.prompt_manager import prompt_manager

# Get system prompt for transactional analysis
system_prompt = prompt_manager.get_transactional_system_prompt()

# Get user prompt for transactional analysis
user_prompt = prompt_manager.get_transactional_user_prompt(query, session_state)

# Get prompt for response generation
response_prompt = prompt_manager.get_response_generation_prompt(query, strategy, context)

# Get prompt for UI generation
ui_prompt = prompt_manager.get_ui_generation_prompt(query, context, data, components)
```

## Prompt Categories

### 1. Transactional Prompts (`transactional_prompts.py`)
- **Purpose**: Analyze user queries and determine which tools to call
- **System Prompt**: Defines the AI's role as e-commerce query analyzer
- **User Prompt**: Template for tool selection with available tools and JSON format

### 2. Response Prompts (`response_prompts.py`)
- **Purpose**: Generate natural, conversational responses
- **System Prompt**: Defines the AI as helpful e-commerce assistant
- **Generation Prompt**: Template for combining knowledge base and tool results

### 3. UI Generation Prompts (`ui_generation_prompts.py`)
- **Purpose**: Generate dynamic UI component specifications
- **Generation Prompt**: Template for creating interactive UI components based on query and data

## Benefits of Centralized Prompts

1. **Maintainability**: Easy to update prompts without touching agent code
2. **Consistency**: Standardized prompt formats across the system
3. **Testing**: Can test prompts independently of agent logic
4. **Versioning**: Track prompt changes and performance impact
5. **Reusability**: Share prompts between different agents

## Best Practices

- Keep prompts focused on specific tasks
- Use clear, structured templates
- Include examples in prompts when helpful
- Maintain consistent JSON format requirements
- Document prompt purpose and expected outputs