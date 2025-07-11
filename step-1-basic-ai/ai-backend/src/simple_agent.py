"""
Simple AI Agent for Step 1 - Basic AI Mode
No multi-agent complexity, just basic LangChain orchestration
Enhanced with detailed logging and LangFuse tracing
"""
import json
import time
import sys
import os
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from config.llm_config import LLMConfig
from config.logging_config import logging_config
from tools.mcp_tools import MCPTools
from shared.observability.langfuse_client import langfuse_client

logger = logging_config.get_logger(__name__)

class SimpleAgent:
    """Simple AI agent that routes queries to appropriate tools"""
    
    def __init__(self, traditional_api_url: str = "http://localhost:3000"):
        self.llm_config = LLMConfig()
        self.llm = self.llm_config.get_llm(temperature=0.1)
        self.response_llm = self.llm_config.get_llm(temperature=0.3)
        self.json_parser = JsonOutputParser()
        self.mcp_tools = MCPTools(traditional_api_url)
        
        # Simple in-memory session storage
        self.sessions = {}
    
    def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """Get session state - simple in-memory storage"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "customer_id": None,
                "last_search": None,
                "order_context": None,
                "conversation_history": []
            }
        return self.sessions[session_id]
    
    def update_session_state(self, session_id: str, updates: Dict[str, Any]):
        """Update session state"""
        state = self.get_session_state(session_id)
        state.update(updates)
        logger.info(f"Updated session {session_id}: {updates}")
    
    async def process_query(self, user_query: str, context: Dict[str, Any] = None, trace_id: str = None) -> Dict[str, Any]:
        """Process user query and determine which tools to call"""
        
        session_id = context.get("session_id", "default") if context else "default"
        session_state = self.get_session_state(session_id)
        
        # Add customer_id from context if available
        if context and "customerId" in context:
            session_state["customer_id"] = context["customerId"]
        
        logger.info(
            "Processing query",
            user_query=user_query,
            session_id=session_id,
            trace_id=trace_id,
            customer_id=session_state.get("customer_id"),
            session_state_keys=list(session_state.keys())
        )
        
        start_time = time.time()
        
        try:
            # Create system prompt
            system_prompt = self._create_system_prompt()
            
            # Create user prompt
            user_prompt = f"""
User Query: "{user_query}"
Session Context: {json.dumps(session_state, indent=2)}
Request Context: {json.dumps(context or {}, indent=2)}

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
}}
"""
            
            # Get LLM response
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            llm_start_time = time.time()
            logger.info("Calling LLM", model=self.llm_config.get_info()["model"], prompt_length=len(user_prompt))
            
            response = await self.llm.ainvoke(messages)
            llm_response = response.content
            llm_duration = (time.time() - llm_start_time) * 1000
            
            # Log LLM call to LangFuse
            langfuse_client.log_llm_generation(
                trace_id=trace_id,
                model=self.llm_config.get_info()["model"],
                prompt=user_prompt,
                response=llm_response,
                usage={"total_tokens": len(llm_response.split())},
                metadata={"duration_ms": llm_duration}
            )
            
            logger.info(
                "LLM response received",
                duration_ms=llm_duration,
                response_length=len(llm_response),
                session_id=session_id
            )
            
            # Parse response
            try:
                # Extract JSON from markdown code blocks if present
                json_content = self._extract_json_from_response(llm_response)
                parsed = json.loads(json_content)
                logger.info("LLM response parsed successfully", tool_calls_count=len(parsed.get("tool_calls", [])))
            except json.JSONDecodeError as e:
                logger.warning("Failed to parse LLM response, using fallback", error=str(e), llm_response=llm_response[:200])
                parsed = self._fallback_response(user_query)
            
            # Update session if needed
            if "session_updates" in parsed:
                self.update_session_state(session_id, parsed["session_updates"])
                logger.info("Updated session state", updates=parsed["session_updates"])
            
            total_duration = (time.time() - start_time) * 1000
            logger.info("Query processing completed", total_duration_ms=total_duration, session_id=session_id)
            
            return parsed
            
        except Exception as e:
            total_duration = (time.time() - start_time) * 1000
            logger.error("Query processing failed", error=str(e), duration_ms=total_duration, session_id=session_id)
            
            # Log error to LangFuse
            if trace_id:
                langfuse_client.log_llm_generation(
                    trace_id=trace_id,
                    model=self.llm_config.get_info()["model"],
                    prompt=user_prompt if 'user_prompt' in locals() else user_query,
                    response="",
                    metadata={"error": str(e), "duration_ms": total_duration}
                )
            
            return self._fallback_response(user_query)
    
    async def execute_tools(self, tool_calls: List[Dict[str, Any]], session_id: str = "default", trace_id: str = None) -> List[Dict[str, Any]]:
        """Execute the planned tool calls with detailed logging"""
        results = []
        
        logger.info("Starting tool execution", tool_count=len(tool_calls), session_id=session_id)
        
        for i, tool_call in enumerate(tool_calls, 1):
            tool_name = tool_call["tool"]
            parameters = tool_call["parameters"]
            reasoning = tool_call.get("reasoning", "")
            
            tool_start_time = time.time()
            
            logger.info(
                "Executing tool",
                tool_index=f"{i}/{len(tool_calls)}",
                tool_name=tool_name,
                parameters=parameters,
                reasoning=reasoning,
                session_id=session_id
            )
            
            try:
                if tool_name == "search_products":
                    result = await self.mcp_tools.search_products(**parameters)
                elif tool_name == "get_products":
                    result = await self.mcp_tools.get_products(**parameters)
                elif tool_name == "get_customers":
                    result = await self.mcp_tools.get_customers()
                elif tool_name == "get_customer_orders":
                    result = await self.mcp_tools.get_customer_orders(**parameters)
                elif tool_name == "create_order":
                    result = await self.mcp_tools.create_order(**parameters)
                elif tool_name == "get_categories":
                    result = await self.mcp_tools.get_categories()
                else:
                    result = {"success": False, "error": f"Unknown tool: {tool_name}"}
                
                tool_duration = (time.time() - tool_start_time) * 1000
                result["tool"] = tool_name
                results.append(result)
                
                # Log to LangFuse
                langfuse_client.log_tool_execution(
                    trace_id=trace_id,
                    tool_name=tool_name,
                    input_data=parameters,
                    output_data=result,
                    metadata={"duration_ms": tool_duration, "reasoning": reasoning}
                )
                
                logger.info(
                    "Tool execution completed",
                    tool_name=tool_name,
                    duration_ms=tool_duration,
                    success=result.get("success", False),
                    result_count=result.get("count", 0),
                    session_id=session_id
                )
                
            except Exception as e:
                tool_duration = (time.time() - tool_start_time) * 1000
                error_result = {
                    "success": False,
                    "error": str(e),
                    "tool": tool_name
                }
                results.append(error_result)
                
                # Log error to LangFuse
                langfuse_client.log_tool_execution(
                    trace_id=trace_id,
                    tool_name=tool_name,
                    input_data=parameters,
                    output_data=error_result,
                    metadata={"duration_ms": tool_duration, "error": str(e)}
                )
                
                logger.error(
                    "Tool execution failed",
                    tool_name=tool_name,
                    duration_ms=tool_duration,
                    error=str(e),
                    parameters=parameters,
                    session_id=session_id
                )
        
        logger.info("Tool execution batch completed", total_tools=len(tool_calls), successful_tools=sum(1 for r in results if r.get("success", False)))
        
        return results
    
    async def format_response(self, tool_results: List[Dict[str, Any]], 
                            original_query: str, response_strategy: str, trace_id: str = None) -> str:
        """Format final response to user"""
        
        try:
            # Prepare results summary
            results_summary = []
            for result in tool_results:
                if result.get("success"):
                    data = result.get("data", [])
                    results_summary.append({
                        "tool": result.get("tool"),
                        "count": result.get("count", 0),
                        "data": data[:3] if isinstance(data, list) else data  # Limit for context
                    })
                else:
                    results_summary.append({
                        "tool": result.get("tool"),
                        "error": result.get("error")
                    })
            
            prompt = f"""
Original Query: "{original_query}"
Response Strategy: {response_strategy}
Tool Results: {json.dumps(results_summary, indent=2)}

Format a helpful, conversational response. Be natural and friendly.
Include relevant details from the tool results.
If no results found, be helpful and suggest alternatives.
"""
            
            messages = [
                SystemMessage(content="You are a helpful e-commerce assistant. Format responses naturally and conversationally."),
                HumanMessage(content=prompt)
            ]
            
            response = await self.response_llm.ainvoke(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"Response formatting failed: {e}")
            return "I found some information but had trouble formatting the response. Please try again."
    
    def _create_system_prompt(self) -> str:
        """Create system prompt for query analysis"""
        return """You are an AI assistant that analyzes e-commerce queries and determines which tools to call.

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
    
    def _extract_json_from_response(self, response: str) -> str:
        """Extract JSON content from LLM response, handling markdown code blocks"""
        # Remove any markdown code block formatting
        response = response.strip()
        
        # Check if response is wrapped in markdown code blocks
        if response.startswith('```json'):
            # Find the end of the code block
            end_index = response.find('```', 7)  # Start after '```json'
            if end_index != -1:
                response = response[7:end_index].strip()
        elif response.startswith('```'):
            # Generic code block
            end_index = response.find('```', 3)
            if end_index != -1:
                response = response[3:end_index].strip()
        
        return response
    
    def _fallback_response(self, query: str) -> Dict[str, Any]:
        """Fallback response when LLM fails"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["search", "find", "show", "product", "iphone", "laptop"]):
            return {
                "tool_calls": [{
                    "tool": "search_products",
                    "parameters": {"query": query},
                    "reasoning": "Fallback product search"
                }],
                "response_strategy": "Show matching products"
            }
        elif "customer" in query_lower:
            return {
                "tool_calls": [{
                    "tool": "get_customers",
                    "parameters": {},
                    "reasoning": "Fallback customer query"
                }],
                "response_strategy": "Show customer list"
            }
        else:
            return {
                "tool_calls": [{
                    "tool": "get_products",
                    "parameters": {},
                    "reasoning": "Fallback general query"
                }],
                "response_strategy": "Show product catalog"
            }
    
    async def close(self):
        """Cleanup resources"""
        await self.mcp_tools.close()