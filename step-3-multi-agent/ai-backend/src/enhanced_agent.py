"""
Enhanced AI Agent for Step 2 - RAG Integration
Combines transactional tools with knowledge base search
"""
import json
import time
import sys
import os
from typing import Dict, Any, List, Optional, Tuple
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../rag-service'))

from config.llm_config import LLMConfig
from config.logging_config import logging_config
from tools.mcp_tools import MCPTools
from rag_service import RAGService, QueryType
from shared.observability.langfuse_client import langfuse_client

logger = logging_config.get_logger(__name__)

class EnhancedAgent:
    """Enhanced AI agent with RAG capabilities"""
    
    def __init__(self, traditional_api_url: str = "http://localhost:4000"):
        self.llm_config = LLMConfig()
        self.llm = self.llm_config.get_llm(temperature=0.1)
        self.response_llm = self.llm_config.get_llm(temperature=0.3)
        self.json_parser = JsonOutputParser()
        
        # Initialize tools and services
        self.mcp_tools = MCPTools(traditional_api_url)
        self.rag_service = RAGService()
        
        # Simple in-memory session storage
        self.sessions = {}
        
        # Query classification thresholds
        self.knowledge_confidence_threshold = 0.7
        self.mixed_query_threshold = 0.5
    
    def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """Get session state - simple in-memory storage"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "customer_id": None,
                "last_search": None,
                "order_context": None,
                "knowledge_context": None,
                "conversation_history": []
            }
        return self.sessions[session_id]
    
    def update_session_state(self, session_id: str, updates: Dict[str, Any]):
        """Update session state"""
        state = self.get_session_state(session_id)
        state.update(updates)
        logger.info(f"Updated session {session_id}: {updates}")
    
    async def process_query(self, user_query: str, context: Dict[str, Any] = None, trace_id: str = None) -> Dict[str, Any]:
        """
        Process user query with enhanced RAG capabilities
        
        Args:
            user_query: User's query
            context: Additional context
            trace_id: Tracing ID for observability
            
        Returns:
            Processing plan with tools and knowledge
        """
        session_id = context.get("session_id", "default") if context else "default"
        session_state = self.get_session_state(session_id)
        
        # Add customer_id from context if available
        if context and "customerId" in context:
            session_state["customer_id"] = context["customerId"]
        
        logger.info(
            "Processing enhanced query",
            user_query=user_query,
            session_id=session_id,
            trace_id=trace_id,
            customer_id=session_state.get("customer_id")
        )
        
        start_time = time.time()
        
        try:
            # Step 1: Query RAG service for knowledge base search
            rag_response = await self.rag_service.process_query(user_query, context)
            
            # Step 2: Determine query routing strategy
            routing_decision = await self.determine_routing_strategy(
                user_query, rag_response, session_state, trace_id
            )
            
            # Step 3: Create execution plan based on routing
            execution_plan = await self.create_execution_plan(
                user_query, routing_decision, rag_response, session_state, trace_id
            )
            
            # Update session with knowledge context
            if rag_response.results:
                session_state["knowledge_context"] = {
                    "query": user_query,
                    "results": [r.metadata for r in rag_response.results],
                    "confidence": rag_response.confidence
                }
            
            total_duration = (time.time() - start_time) * 1000
            logger.info("Enhanced query processing completed", 
                       total_duration_ms=total_duration, 
                       session_id=session_id,
                       query_type=rag_response.query_type.value,
                       routing_strategy=routing_decision["strategy"])
            
            return execution_plan
            
        except Exception as e:
            total_duration = (time.time() - start_time) * 1000
            logger.error("Enhanced query processing failed", 
                        error=str(e), 
                        duration_ms=total_duration, 
                        session_id=session_id)
            
            # Log error to LangFuse
            if trace_id:
                langfuse_client.log_llm_generation(
                    trace_id=trace_id,
                    model=self.llm_config.get_info()["model"],
                    prompt=user_query,
                    response="",
                    metadata={"error": str(e), "duration_ms": total_duration}
                )
            
            return self._fallback_response(user_query)
    
    async def determine_routing_strategy(self, 
                                       user_query: str, 
                                       rag_response, 
                                       session_state: Dict[str, Any],
                                       trace_id: str = None) -> Dict[str, Any]:
        """
        Determine how to route the query based on RAG results and context
        
        Args:
            user_query: User's query
            rag_response: Response from RAG service
            session_state: Current session state
            trace_id: Tracing ID
            
        Returns:
            Routing decision with strategy and reasoning
        """
        # Analyze RAG results
        has_knowledge_results = len(rag_response.results) > 0
        knowledge_confidence = rag_response.confidence
        query_type = rag_response.query_type
        
        # Determine routing strategy
        if query_type == QueryType.TRANSACTIONAL:
            strategy = "transactional_only"
            reasoning = "Query is purely transactional - route to MCP tools"
        elif query_type == QueryType.FAQ and has_knowledge_results and knowledge_confidence > self.knowledge_confidence_threshold:
            strategy = "knowledge_only"
            reasoning = "High confidence FAQ match - use knowledge base only"
        elif query_type == QueryType.BUSINESS_RULE and has_knowledge_results:
            strategy = "knowledge_with_context"
            reasoning = "Business rule query - use knowledge base with session context"
        elif query_type == QueryType.MIXED or (has_knowledge_results and knowledge_confidence > self.mixed_query_threshold):
            strategy = "hybrid"
            reasoning = "Mixed query - combine knowledge base with transactional tools"
        else:
            strategy = "transactional_fallback"
            reasoning = "Low confidence knowledge match - fallback to transactional tools"
        
        routing_decision = {
            "strategy": strategy,
            "reasoning": reasoning,
            "query_type": query_type.value,
            "knowledge_confidence": knowledge_confidence,
            "has_knowledge_results": has_knowledge_results,
            "knowledge_results_count": len(rag_response.results)
        }
        
        logger.info("Routing decision made", **routing_decision)
        return routing_decision
    
    async def create_execution_plan(self, 
                                  user_query: str,
                                  routing_decision: Dict[str, Any],
                                  rag_response,
                                  session_state: Dict[str, Any],
                                  trace_id: str = None) -> Dict[str, Any]:
        """
        Create execution plan based on routing decision
        
        Args:
            user_query: User's query
            routing_decision: Routing strategy decision
            rag_response: RAG service response
            session_state: Session state
            trace_id: Tracing ID
            
        Returns:
            Execution plan with tools and knowledge
        """
        strategy = routing_decision["strategy"]
        
        if strategy == "knowledge_only":
            return await self._create_knowledge_only_plan(user_query, rag_response, trace_id)
        elif strategy == "transactional_only":
            return await self._create_transactional_plan(user_query, session_state, trace_id)
        elif strategy == "hybrid":
            return await self._create_hybrid_plan(user_query, rag_response, session_state, trace_id)
        elif strategy == "knowledge_with_context":
            return await self._create_knowledge_context_plan(user_query, rag_response, session_state, trace_id)
        else:  # transactional_fallback
            return await self._create_transactional_plan(user_query, session_state, trace_id)
    
    async def _create_knowledge_only_plan(self, user_query: str, rag_response, trace_id: str = None) -> Dict[str, Any]:
        """Create plan for knowledge-only responses"""
        return {
            "strategy": "knowledge_only",
            "tool_calls": [],
            "knowledge_results": [
                {
                    "type": result.type,
                    "content": result.content,
                    "metadata": result.metadata,
                    "score": result.score
                } for result in rag_response.results
            ],
            "response_strategy": "Use knowledge base results to answer user question directly",
            "session_updates": {},
            "context": rag_response.context
        }
    
    async def _create_transactional_plan(self, user_query: str, session_state: Dict[str, Any], trace_id: str = None) -> Dict[str, Any]:
        """Create plan for transactional queries (same as Step 1)"""
        # Use LLM to determine transactional tools
        system_prompt = self._create_transactional_system_prompt()
        
        user_prompt = f"""
User Query: "{user_query}"
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
}}
"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        llm_start_time = time.time()
        response = await self.llm.ainvoke(messages)
        
        # Handle different response types
        if hasattr(response, 'content'):
            llm_response = response.content
        elif isinstance(response, str):
            llm_response = response
        else:
            llm_response = str(response)
            
        llm_duration = (time.time() - llm_start_time) * 1000
        
        # Log LLM call to LangFuse
        langfuse_client.log_llm_generation(
            trace_id=trace_id,
            model=self.llm_config.get_info()["model"],
            prompt=user_prompt,
            response=llm_response,
            usage={"total_tokens": len(llm_response.split())},
            metadata={"duration_ms": llm_duration, "strategy": "transactional"}
        )
        
        try:
            json_content = self._extract_json_from_response(llm_response)
            parsed = json.loads(json_content)
            parsed["strategy"] = "transactional_only"
            parsed["knowledge_results"] = []
            parsed["context"] = ""
            return parsed
        except json.JSONDecodeError:
            return self._fallback_response(user_query)
    
    async def _create_hybrid_plan(self, user_query: str, rag_response, session_state: Dict[str, Any], trace_id: str = None) -> Dict[str, Any]:
        """Create plan for hybrid queries (knowledge + transactional)"""
        # Get transactional plan
        transactional_plan = await self._create_transactional_plan(user_query, session_state, trace_id)
        
        # Combine with knowledge results
        return {
            "strategy": "hybrid",
            "tool_calls": transactional_plan.get("tool_calls", []),
            "knowledge_results": [
                {
                    "type": result.type,
                    "content": result.content,
                    "metadata": result.metadata,
                    "score": result.score
                } for result in rag_response.results
            ],
            "response_strategy": "Combine knowledge base information with transactional tool results",
            "session_updates": transactional_plan.get("session_updates", {}),
            "context": rag_response.context
        }
    
    async def _create_knowledge_context_plan(self, user_query: str, rag_response, session_state: Dict[str, Any], trace_id: str = None) -> Dict[str, Any]:
        """Create plan for knowledge queries that need session context"""
        return {
            "strategy": "knowledge_with_context",
            "tool_calls": [],
            "knowledge_results": [
                {
                    "type": result.type,
                    "content": result.content,
                    "metadata": result.metadata,
                    "score": result.score
                } for result in rag_response.results
            ],
            "response_strategy": "Use knowledge base results with session context for personalized response",
            "session_updates": {},
            "context": rag_response.context,
            "session_context": session_state
        }
    
    async def execute_tools(self, tool_calls: List[Dict[str, Any]], session_id: str = "default", trace_id: str = None) -> List[Dict[str, Any]]:
        """Execute transactional tools (same as Step 1)"""
        results = []
        
        logger.info("Starting tool execution", tool_count=len(tool_calls), session_id=session_id)
        
        for i, tool_call in enumerate(tool_calls, 1):
            tool_name = tool_call["tool"]
            parameters = tool_call["parameters"]
            reasoning = tool_call.get("reasoning", "")
            
            tool_start_time = time.time()
            
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
        
        return results
    
    async def format_response(self, 
                            execution_plan: Dict[str, Any],
                            tool_results: List[Dict[str, Any]], 
                            original_query: str, 
                            trace_id: str = None) -> str:
        """
        Format final response combining knowledge and tool results
        
        Args:
            execution_plan: Execution plan with strategy
            tool_results: Results from tool execution
            original_query: Original user query
            trace_id: Tracing ID
            
        Returns:
            Formatted response string
        """
        strategy = execution_plan.get("strategy", "transactional_only")
        knowledge_results = execution_plan.get("knowledge_results", [])
        knowledge_context = execution_plan.get("context", "")
        
        # Prepare context for response generation
        context_parts = []
        
        # Add knowledge context if available
        if knowledge_context:
            context_parts.append(f"Knowledge Base Information:\n{knowledge_context}")
        
        # Add tool results if available
        if tool_results:
            tool_context = []
            for result in tool_results:
                if result.get("success"):
                    data = result.get("data", [])
                    tool_context.append(f"Tool: {result.get('tool')} returned {result.get('count', 0)} results")
                    if isinstance(data, list) and data:
                        # Add sample data for context
                        tool_context.append(f"Sample data: {str(data[0])[:200]}...")
            
            if tool_context:
                context_parts.append(f"Tool Results:\n{chr(10).join(tool_context)}")
        
        # Create response generation prompt
        prompt = f"""
Original Query: "{original_query}"
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
If only tool results are available, format them conversationally.
"""
        
        try:
            messages = [
                SystemMessage(content="You are a helpful e-commerce assistant. Generate natural, conversational responses that combine knowledge base information with transactional data effectively."),
                HumanMessage(content=prompt)
            ]
            
            response = await self.response_llm.ainvoke(messages)
            
            # Handle different response types
            if hasattr(response, 'content'):
                return response.content
            elif isinstance(response, str):
                return response
            else:
                return str(response)
            
        except Exception as e:
            logger.error(f"Response formatting failed: {e}")
            return "I found some information but had trouble formatting the response. Please try again."
    
    def _create_transactional_system_prompt(self) -> str:
        """Create system prompt for transactional analysis"""
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
        """Extract JSON content from LLM response"""
        response = response.strip()
        
        if response.startswith('```json'):
            end_index = response.find('```', 7)
            if end_index != -1:
                response = response[7:end_index].strip()
        elif response.startswith('```'):
            end_index = response.find('```', 3)
            if end_index != -1:
                response = response[3:end_index].strip()
        
        return response
    
    def _fallback_response(self, query: str) -> Dict[str, Any]:
        """Fallback response when processing fails"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["search", "find", "show", "product", "iphone", "laptop"]):
            return {
                "strategy": "transactional_fallback",
                "tool_calls": [{
                    "tool": "search_products",
                    "parameters": {"query": query},
                    "reasoning": "Fallback product search"
                }],
                "knowledge_results": [],
                "response_strategy": "Show matching products",
                "context": ""
            }
        else:
            return {
                "strategy": "transactional_fallback",
                "tool_calls": [{
                    "tool": "get_products",
                    "parameters": {},
                    "reasoning": "Fallback general query"
                }],
                "knowledge_results": [],
                "response_strategy": "Show product catalog",
                "context": ""
            }
    
    async def close(self):
        """Cleanup resources"""
        await self.mcp_tools.close()