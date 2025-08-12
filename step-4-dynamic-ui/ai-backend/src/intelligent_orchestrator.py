"""
Intelligent Tool Orchestrator - LLM-driven tool selection and execution

This module replaces hardcoded term extraction with intelligent LLM-based 
tool orchestration, where the LLM understands all available tools and 
decides which tools to call with appropriate parameters.
"""

import json
import re
import asyncio
from typing import Dict, List, Optional, Any
from loguru import logger

try:
    from shared.observability.langfuse_decorator import observe
except ImportError:
    def observe(as_type: str = "span", **kwargs):
        def decorator(func):
            return func
        return decorator

class IntelligentOrchestrator:
    """
    LLM-driven tool orchestration system that lets the LLM decide 
    which tools to call and how to combine their results
    """
    
    def __init__(self, llm, mcp_tools):
        self.llm = llm
        self.mcp_tools = mcp_tools
        self.available_tools = self._get_tool_definitions()
        
    def _get_tool_definitions(self) -> Dict[str, Any]:
        """Get complete definitions of all available MCP tools"""
        return {
            # Product Tools
            "search_products": {
                "description": "Search for products using natural language queries. Handles semantic search, price constraints, categories, brands.",
                "parameters": {
                    "query": "string - Natural language search query (e.g., 'Find laptops under $2000', 'iPhone 15', 'gaming headphones')",
                    "filters": "object - Optional filters: {category, brand, max_price, min_price}"
                },
                "examples": [
                    "search_products('Find laptops under $2000')",
                    "search_products('iPhone', {'max_price': 1000})",
                    "search_products('gaming headphones by Sony')"
                ]
            },
            "get_products": {
                "description": "Get all products with optional filtering and pagination",
                "parameters": {
                    "category_id": "int - Filter by category ID",
                    "brand": "string - Filter by brand name",
                    "limit": "int - Maximum number of results",
                    "offset": "int - Results offset for pagination"
                },
                "examples": [
                    "get_products()",
                    "get_products(brand='Apple', limit=10)"
                ]
            },
            "get_product_by_id": {
                "description": "Get detailed information for a specific product",
                "parameters": {
                    "product_id": "string - Unique product identifier"
                },
                "examples": ["get_product_by_id('PROD-002')"]
            },
            
            # Customer Tools  
            "get_customer_info": {
                "description": "Get detailed customer information by ID",
                "parameters": {
                    "customer_id": "string - Unique customer identifier"
                },
                "examples": ["get_customer_info('cust_001')"]
            },
            "get_customers": {
                "description": "Search and list customers",
                "parameters": {
                    "limit": "int - Maximum results",
                    "search": "string - Search by name or email"
                },
                "examples": [
                    "get_customers(limit=10)",
                    "get_customers(search='john@example.com')"
                ]
            },
            "update_customer": {
                "description": "Update customer information",
                "parameters": {
                    "customer_id": "string - Customer ID",
                    "updates": "object - Fields to update"
                },
                "examples": ["update_customer('cust_001', {'email': 'new@example.com'})"]
            },
            
            # Order Tools
            "get_customer_orders": {
                "description": "Get order history for a specific customer",
                "parameters": {
                    "customer_id": "string - Customer ID",
                    "limit": "int - Maximum results"
                },
                "examples": ["get_customer_orders('cust_001', limit=5)"]
            },
            "create_order": {
                "description": "Create a new order for a customer",
                "parameters": {
                    "customer_id": "string - Customer ID",
                    "product_id": "string - Product ID to order",
                    "quantity": "int - Quantity (default: 1)",
                    "shipping_address": "string - Delivery address",
                    "payment_method": "string - Payment method",
                    "special_instructions": "string - Special delivery instructions"
                },
                "examples": ["create_order('cust_001', 'PROD-002', 2, 'Home address')"]
            },
            "get_order": {
                "description": "Get detailed order information",
                "parameters": {
                    "order_id": "string - Order ID",
                    "customer_id": "string - Customer ID (optional but helps)"
                },
                "examples": ["get_order('order_123', 'cust_001')"]
            },
            "update_order": {
                "description": "Update an existing order (limited to cancellation)",
                "parameters": {
                    "order_id": "string - Order ID",
                    "updates": "object - Updates to make",
                    "customer_id": "string - Customer ID"
                },
                "examples": ["update_order('order_123', {'status': 'cancelled'}, 'cust_001')"]
            },
            "cancel_order": {
                "description": "Cancel an order",
                "parameters": {
                    "order_id": "string - Order ID",
                    "reason": "string - Cancellation reason"
                },
                "examples": ["cancel_order('order_123', 'Customer requested')"]
            },
            "track_order": {
                "description": "Get order tracking and delivery status",
                "parameters": {
                    "order_id": "string - Order ID",
                    "customer_id": "string - Customer ID"
                },
                "examples": ["track_order('order_123', 'cust_001')"]
            },
            
            # Category Tools
            "get_categories": {
                "description": "Get all product categories",
                "parameters": {},
                "examples": ["get_categories()"]
            }
        }
    
    @observe(as_type="span")
    async def orchestrate_query(self, user_query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Use LLM to intelligently decide which tools to call and how to combine results
        
        Args:
            user_query: User's natural language query
            context: Session context (customer_id, etc.)
            
        Returns:
            Orchestrated response with tool results and reasoning
        """
        try:
            # Phase 1: Planning - Let LLM decide which tools to call
            execution_plan = await self._create_execution_plan(user_query, context)
            
            if not execution_plan.get("tool_calls"):
                return {
                    "success": False,
                    "error": "No tool execution plan generated",
                    "reasoning": execution_plan.get("reasoning", "")
                }
            
            # Phase 2: Execution - Execute the planned tool calls
            tool_results = await self._execute_planned_tools(execution_plan["tool_calls"])
            
            # Phase 3: Synthesis - Let LLM combine results into final response
            final_response = await self._synthesize_response(user_query, execution_plan, tool_results, context)
            
            return {
                "success": True,
                "response": final_response["response"],
                "tool_calls": execution_plan["tool_calls"],
                "tool_results": tool_results,
                "reasoning": execution_plan.get("reasoning", ""),
                "synthesis_reasoning": final_response.get("reasoning", ""),
                "suggested_actions": final_response.get("suggested_actions", [])
            }
            
        except Exception as e:
            logger.error(f"Intelligent orchestration failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "reasoning": "Orchestration system encountered an error"
            }
    
    @observe(as_type="span")
    async def _create_execution_plan(self, user_query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Let LLM create an execution plan by choosing appropriate tools"""
        
        tools_description = self._format_tools_for_llm()
        customer_context = self._format_context_for_llm(context)
        
        prompt = f"""You are an intelligent tool orchestrator for an e-commerce system. Analyze the user query and create an execution plan using the available tools.

USER QUERY: "{user_query}"

CONTEXT:
{customer_context}

AVAILABLE TOOLS:
{tools_description}

TASK: Create an execution plan to fulfill the user's request. You can call multiple tools if needed, and they will be executed in sequence.

RULES:
1. Choose the most appropriate tools for the query
2. Generate proper parameters for each tool call
3. Consider the context (customer_id, session info)
4. If you need customer info but don't have customer_id, plan to get it first
5. For order-related queries, you may need to call multiple tools (get customer, then get orders)
6. For product comparisons, you may need multiple search calls
7. Be intelligent about parameter extraction (prices, brands, categories)

OUTPUT FORMAT (JSON):
{{
    "reasoning": "Explain your analysis of the query and why you chose these tools",
    "tool_calls": [
        {{
            "tool": "tool_name",
            "parameters": {{
                "param1": "value1",
                "param2": "value2"
            }},
            "purpose": "What this tool call is meant to achieve"
        }}
    ],
    "expected_outcome": "What the combined results should provide"
}}

EXAMPLES:

Query: "Find laptops under $2000"
Response: {{
    "reasoning": "User wants to search for laptops with a price constraint. This is a straightforward product search with price filtering.",
    "tool_calls": [
        {{
            "tool": "search_products", 
            "parameters": {{"query": "laptops", "filters": {{"max_price": 2000}}}},
            "purpose": "Find laptops that cost less than $2000"
        }}
    ],
    "expected_outcome": "List of laptops priced under $2000 with details"
}}

Query: "What was my last order?"
Response: {{
    "reasoning": "User wants their most recent order. Need customer ID from context, then get their order history.",
    "tool_calls": [
        {{
            "tool": "get_customer_orders",
            "parameters": {{"customer_id": "{context.get('customer_id', 'UNKNOWN')}", "limit": 1}},
            "purpose": "Get the customer's most recent order"
        }}
    ],
    "expected_outcome": "Details of the customer's most recent order"
}}

Query: "Compare iPhone 15 Pro and Samsung Galaxy S24"
Response: {{
    "reasoning": "User wants to compare two specific products. Need to search for both products individually to get their details.",
    "tool_calls": [
        {{
            "tool": "search_products",
            "parameters": {{"query": "iPhone 15 Pro"}},
            "purpose": "Get details for iPhone 15 Pro"
        }},
        {{
            "tool": "search_products", 
            "parameters": {{"query": "Samsung Galaxy S24"}},
            "purpose": "Get details for Samsung Galaxy S24"
        }}
    ],
    "expected_outcome": "Detailed comparison between the two phones including specs and pricing"
}}

Now create an execution plan for the user query:"""

        try:
            response = await self.llm.ainvoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                return json.loads(json_match.group())
            else:
                logger.warning(f"No JSON found in LLM planning response: {content[:200]}")
                return {"error": "Failed to parse execution plan"}
                
        except Exception as e:
            logger.error(f"Execution planning failed: {e}")
            return {"error": str(e)}
    
    @observe(as_type="span")
    async def _execute_planned_tools(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute the planned tool calls in sequence"""
        results = []
        
        for tool_call in tool_calls:
            tool_name = tool_call.get("tool")
            parameters = tool_call.get("parameters", {})
            purpose = tool_call.get("purpose", "")
            
            logger.info(f"🔧 Executing {tool_name} for: {purpose}")
            
            try:
                # Get the tool method from MCP tools
                if hasattr(self.mcp_tools, tool_name):
                    tool_method = getattr(self.mcp_tools, tool_name)
                    result = await tool_method(**parameters)
                    
                    results.append({
                        "tool": tool_name,
                        "parameters": parameters,
                        "purpose": purpose,
                        "result": result,
                        "success": result.get("success", False)
                    })
                    
                    logger.info(f"✅ {tool_name} completed: {result.get('count', 'N/A')} results")
                else:
                    error_msg = f"Tool '{tool_name}' not found"
                    logger.error(error_msg)
                    results.append({
                        "tool": tool_name,
                        "parameters": parameters,
                        "purpose": purpose,
                        "result": {"success": False, "error": error_msg},
                        "success": False
                    })
                    
            except Exception as e:
                error_msg = f"Tool execution failed: {e}"
                logger.error(f"❌ {tool_name} failed: {error_msg}")
                results.append({
                    "tool": tool_name,
                    "parameters": parameters,
                    "purpose": purpose,
                    "result": {"success": False, "error": error_msg},
                    "success": False
                })
        
        return results
    
    @observe(as_type="span")
    async def _synthesize_response(self, user_query: str, execution_plan: Dict[str, Any], 
                                 tool_results: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Let LLM synthesize tool results into a coherent response"""
        
        # Format tool results for LLM
        results_summary = []
        for result in tool_results:
            tool_data = result["result"]
            if tool_data.get("success"):
                if "data" in tool_data:
                    count = len(tool_data["data"]) if isinstance(tool_data["data"], list) else 1
                    results_summary.append(f"✅ {result['tool']}: Found {count} results")
                else:
                    results_summary.append(f"✅ {result['tool']}: Success")
            else:
                results_summary.append(f"❌ {result['tool']}: {tool_data.get('error', 'Failed')}")
        
        prompt = f"""You are synthesizing results from multiple tool calls to answer the user's query.

USER QUERY: "{user_query}"

EXECUTION PLAN REASONING: {execution_plan.get('reasoning', 'N/A')}

TOOL RESULTS SUMMARY:
{chr(10).join(results_summary)}

DETAILED TOOL RESULTS:
{json.dumps(tool_results, indent=2, default=str)[:3000]}...

TASK: Create a natural, helpful response that:
1. Directly answers the user's question
2. Uses the data from successful tool calls
3. Explains any issues with failed tool calls
4. Suggests next actions the user might want to take
5. Is conversational and user-friendly

OUTPUT FORMAT (JSON):
{{
    "response": "Natural language response to the user",
    "reasoning": "Brief explanation of how you synthesized the results",
    "suggested_actions": ["action1", "action2"],
    "data_used": ["tool1: X results", "tool2: Y results"]
}}

Create the response:"""

        try:
            response = await self.llm.ainvoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback to simple response
                return {
                    "response": content,
                    "reasoning": "Direct LLM response (JSON parsing failed)",
                    "suggested_actions": [],
                    "data_used": []
                }
                
        except Exception as e:
            logger.error(f"Response synthesis failed: {e}")
            return {
                "response": "I was able to gather some information, but had trouble formatting the response. Please try rephrasing your question.",
                "reasoning": f"Synthesis error: {e}",
                "suggested_actions": [],
                "data_used": []
            }
    
    def _format_tools_for_llm(self) -> str:
        """Format available tools in a clear way for the LLM"""
        formatted = []
        for tool_name, tool_info in self.available_tools.items():
            formatted.append(f"• {tool_name}: {tool_info['description']}")
            formatted.append(f"  Parameters: {tool_info['parameters']}")
            if tool_info.get('examples'):
                formatted.append(f"  Examples: {', '.join(tool_info['examples'])}")
            formatted.append("")
        
        return "\n".join(formatted)
    
    def _format_context_for_llm(self, context: Dict[str, Any]) -> str:
        """Format session context for LLM understanding"""
        if not context:
            return "- No context provided"
        
        formatted = []
        for key, value in context.items():
            formatted.append(f"- {key}: {value}")
        
        return "\n".join(formatted)