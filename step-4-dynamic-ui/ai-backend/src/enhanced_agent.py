"""
Enhanced AI Agent for Step 4 - Dynamic UI Generation
Combines RAG, transactional tools, and dynamic UI generation capabilities
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
from prompts.prompt_manager import prompt_manager

logger = logging_config.get_logger(__name__)

class EnhancedAgent:
    """Enhanced AI agent with RAG and Dynamic UI Generation capabilities"""
    
    def __init__(self, traditional_api_url: str = "http://localhost:4000"):
        self.llm_config = LLMConfig()
        self.llm = self.llm_config.get_llm(temperature=0.1)
        self.response_llm = self.llm_config.get_llm(temperature=0.3)
        self.ui_llm = self.llm_config.get_llm(temperature=0.1)  # Dedicated LLM for UI generation
        self.json_parser = JsonOutputParser()
        
        # Initialize tools and services
        self.mcp_tools = MCPTools(traditional_api_url)
        self.rag_service = RAGService()
        
        # Simple in-memory session storage
        self.sessions = {}
        
        # Query classification thresholds
        self.knowledge_confidence_threshold = 0.7
        self.mixed_query_threshold = 0.5
        
        # UI generation capabilities
        self.component_library = None
        self.ui_generation_enabled = True
        
        # Initialize component library
        self._initialize_ui_capabilities()
    
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
        system_prompt = prompt_manager.get_transactional_system_prompt()
        user_prompt = prompt_manager.get_transactional_user_prompt(user_query, session_state)
        
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
                            trace_id: str = None,
                            context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Format final response combining knowledge, tool results, and UI components
        
        Args:
            execution_plan: Execution plan with strategy
            tool_results: Results from tool execution
            original_query: Original user query
            trace_id: Tracing ID
            context: Additional context for UI generation
            
        Returns:
            Dict containing text response and UI components
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
        prompt = prompt_manager.get_response_generation_prompt(original_query, strategy, context_parts)
        
        try:
            # Generate text response
            messages = [
                SystemMessage(content=prompt_manager.get_response_system_prompt()),
                HumanMessage(content=prompt)
            ]
            
            response = await self.response_llm.ainvoke(messages)
            
            # Handle different response types  
            text_response = ""
            if hasattr(response, 'content'):
                text_response = response.content
            elif isinstance(response, str):
                text_response = response
            else:
                text_response = str(response)
            
            # Generate UI components if beneficial
            ui_spec = {"ui_components": [], "layout_strategy": "text_only"}
            
            if self._should_generate_ui(original_query, execution_plan):
                try:
                    ui_spec = await self.generate_ui_response(
                        original_query, execution_plan, tool_results, context
                    )
                except Exception as ui_error:
                    logger.error(f"UI generation failed: {ui_error}")
                    # Continue with text-only response
            
            return {
                "message": text_response,
                "ui_components": ui_spec.get("ui_components", []),
                "layout_strategy": ui_spec.get("layout_strategy", "text_only"),
                "user_intent": ui_spec.get("user_intent", "unknown"),
                "validation": ui_spec.get("validation", {}),
                "response_type": "enhanced_with_ui"
            }
            
        except Exception as e:
            logger.error(f"Response formatting failed: {e}")
            return {
                "message": "I found some information but had trouble formatting the response. Please try again.",
                "ui_components": [],
                "layout_strategy": "error",
                "response_type": "error"
            }
    
    
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
    
    # ========================================
    # UI Generation Capabilities
    # ========================================
    
    def _initialize_ui_capabilities(self):
        """Initialize UI generation capabilities"""
        try:
            # This will be called async later when needed
            logger.info("UI generation capabilities initialized")
        except Exception as e:
            logger.error(f"Failed to initialize UI capabilities: {e}")
            self.ui_generation_enabled = False
    
    async def _ensure_component_knowledge(self):
        """Ensure agent has up-to-date component library knowledge"""
        try:
            if self.component_library is None:
                library_result = await self.mcp_tools.get_component_library()
                
                if library_result.get("success"):
                    self.component_library = library_result["data"]
                    logger.info(f"Loaded {len(self.component_library)} components for UI generation")
                else:
                    logger.error(f"Failed to load component library: {library_result.get('error')}")
                    self.ui_generation_enabled = False
                    
        except Exception as e:
            logger.error(f"Component library fetch failed: {e}")
            self.ui_generation_enabled = False
    
    async def generate_ui_response(self, user_query: str, execution_plan: Dict[str, Any], tool_results: List[Dict[str, Any]], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate UI component specifications alongside text response"""
        try:
            if not self.ui_generation_enabled:
                return {"ui_components": [], "layout_strategy": "text_only"}
            
            # Ensure we have component knowledge
            await self._ensure_component_knowledge()
            
            if not self.component_library:
                return {"ui_components": [], "layout_strategy": "text_only"}
            
            # Generate UI specification
            ui_spec = await self._generate_ui_specification(user_query, execution_plan, tool_results, context or {})
            
            return ui_spec
            
        except Exception as e:
            logger.error(f"UI generation failed: {e}")
            return {
                "ui_components": [],
                "layout_strategy": "fallback",
                "error": str(e)
            }
    
    async def _generate_ui_specification(self, user_query: str, execution_plan: Dict[str, Any], tool_results: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate UI specification using LLM"""
        try:
            # Prepare component library summary for LLM
            component_summary = self._prepare_component_summary()
            
            # Prepare context and data summary
            data_summary = self._prepare_data_summary(execution_plan, tool_results)
            context_summary = self._prepare_context_summary(context)
            
            # Build LLM prompt for UI generation
            ui_generation_prompt = prompt_manager.get_ui_generation_prompt(
                user_query, context_summary, data_summary, component_summary
            )
            
            # Generate UI specification with LLM
            response = await self.ui_llm.ainvoke(ui_generation_prompt)
            
            # Parse LLM response
            ui_spec = self._parse_ui_specification(response.content if hasattr(response, 'content') else str(response))
            
            # Validate specification
            validated_spec = await self._validate_ui_specification(ui_spec)
            
            return validated_spec
            
        except Exception as e:
            logger.error(f"UI specification generation failed: {e}")
            return {"ui_components": [], "layout_strategy": "error", "error": str(e)}
    
    def _prepare_component_summary(self) -> str:
        """Prepare component library summary for LLM"""
        if not self.component_library:
            return "No components available"
        
        summary_parts = []
        
        # Group by category and limit to most useful components
        categories = {}
        for comp_name, comp_info in self.component_library.items():
            category = comp_info.get("category", "utility")
            if category not in categories:
                categories[category] = []
            categories[category].append({
                "name": comp_name,
                "exports": comp_info.get("exports", [])[:3],  # Top 3 exports
                "use_cases": comp_info.get("recommended_use_cases", [])[:2]  # Top 2 use cases
            })
        
        # Priority order for categories
        priority_categories = ["form", "layout", "data", "feedback", "navigation"]
        
        for category in priority_categories:
            if category in categories:
                summary_parts.append(f"\n{category.upper()}:")
                for comp in categories[category][:3]:  # Top 3 per category
                    summary_parts.append(f"  - {comp['name']}: {', '.join(comp['exports'])}")
        
        return "\n".join(summary_parts)
    
    def _prepare_data_summary(self, execution_plan: Dict[str, Any], tool_results: List[Dict[str, Any]]) -> str:
        """Prepare data summary for UI generation"""
        data_parts = []
        
        # Execution plan info
        strategy = execution_plan.get("strategy", "unknown")
        data_parts.append(f"Query Strategy: {strategy}")
        
        # Tool results summary
        if tool_results:
            data_parts.append(f"\nData Available:")
            for result in tool_results[:3]:  # Top 3 results
                tool_name = result.get("tool", "unknown")
                success = result.get("success", False)
                if success and "data" in result:
                    data = result["data"]
                    if isinstance(data, list):
                        data_parts.append(f"  - {tool_name}: {len(data)} items")
                    elif isinstance(data, dict):
                        data_parts.append(f"  - {tool_name}: {len(data)} fields")
                    else:
                        data_parts.append(f"  - {tool_name}: data available")
        
        return "\n".join(data_parts) if data_parts else "No specific data available"
    
    def _prepare_context_summary(self, context: Dict[str, Any]) -> str:
        """Prepare context information for LLM"""
        context_parts = []
        
        if "customer_id" in context:
            context_parts.append(f"Customer: {context['customer_id']}")
        
        if "session_id" in context:
            context_parts.append(f"Session: {context['session_id']}")
        
        return "\n".join(context_parts) if context_parts else "No additional context"
    
    def _parse_ui_specification(self, llm_response: str) -> Dict[str, Any]:
        """Parse LLM response into UI specification"""
        try:
            import re
            
            # Look for JSON block in response
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                return json.loads(llm_response.strip())
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse UI specification: {e}")
            return {
                "ui_components": [],
                "layout_strategy": "parse_error",
                "error": "Failed to parse LLM response"
            }
    
    async def _validate_ui_specification(self, ui_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Validate UI specification against component library"""
        try:
            validated_components = []
            
            for component_spec in ui_spec.get("ui_components", []):
                component_type = component_spec.get("type")
                
                if component_type and component_type in self.component_library:
                    validated_components.append(component_spec)
                else:
                    logger.warning(f"Unknown component type: {component_type}")
            
            ui_spec["ui_components"] = validated_components
            ui_spec["validation"] = {
                "total_requested": len(ui_spec.get("ui_components", [])),
                "validated": len(validated_components),
                "success": len(validated_components) > 0
            }
            
            return ui_spec
            
        except Exception as e:
            logger.error(f"UI specification validation failed: {e}")
            return ui_spec
    
    def _should_generate_ui(self, user_query: str, execution_plan: Dict[str, Any]) -> bool:
        """Determine if UI generation would be beneficial for this query"""
        if not self.ui_generation_enabled:
            return False
        
        # UI-beneficial query patterns
        ui_triggers = [
            "show", "display", "list", "find", "search", "view", "see",
            "products", "orders", "customers", "buy", "purchase", "cart"
        ]
        
        query_lower = user_query.lower()
        strategy = execution_plan.get("strategy", "")
        
        # Check for UI trigger words
        has_ui_trigger = any(trigger in query_lower for trigger in ui_triggers)
        
        # Check for data-rich strategies
        data_strategies = ["product_search", "order_inquiry", "customer_lookup", "transactional"]
        has_data_strategy = any(strat in strategy for strat in data_strategies)
        
        return has_ui_trigger or has_data_strategy
    
    async def close(self):
        """Cleanup resources"""
        await self.mcp_tools.close()