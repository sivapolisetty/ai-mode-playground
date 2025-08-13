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
from tools.ui_component_tools import UIComponentTools
from .intent_classifier import IntentClassifier
from .context_resolver import ContextResolver
from .intelligent_orchestrator import IntelligentOrchestrator
from rag_service import RAGService, QueryType
from shared.observability.langfuse_client import langfuse_client
from shared.observability.langfuse_decorator import (
    trace_conversation, trace_agent_operation, trace_tool_execution,
    trace_llm_generation, trace_ui_generation, trace_rag_operation,
    flush_observations, observe
)
from shared.observability.hybrid_tracing import langfuse_trace
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
        self.ui_component_tools = UIComponentTools()
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
        
        # Initialize intelligent query processing
        self.intent_classifier = IntentClassifier(self.llm)
        self.context_resolver = ContextResolver(self.mcp_tools)
        self.intelligent_orchestrator = IntelligentOrchestrator(self.llm, self.mcp_tools)
        self.ui_component_tools = UIComponentTools()
    
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
    
    @langfuse_trace(name="orchestration_processing")
    async def process_query_with_orchestration(self, user_query: str, context: Dict[str, Any] = None, trace_id: str = None) -> Dict[str, Any]:
        """
        Process query using intelligent tool orchestration where LLM decides which tools to call
        
        This is the new approach that replaces hardcoded term extraction with LLM-driven
        tool selection and multi-tool orchestration.
        """
        session_id = context.get("session_id", "default") if context else "default"
        session_state = self.get_session_state(session_id)
        
        try:
            logger.info(f"🎭 Processing query with intelligent orchestration: {user_query}")
            
            # Add session context to orchestrator context
            orchestration_context = {**session_state, **(context or {})}
            
            # Use intelligent orchestrator to plan and execute tools
            orchestration_result = await self.intelligent_orchestrator.orchestrate_query(
                user_query, 
                orchestration_context,
                trace_id=trace_id
            )
            
            if not orchestration_result.get("success"):
                logger.error(f"Orchestration failed: {orchestration_result.get('error')}")
                # Fall back to traditional processing
                return await self.process_query_intelligently(user_query, context, trace_id)
            
            # Update session with any new information
            self.update_session_state(session_id, {
                "last_query": user_query,
                "last_orchestration": orchestration_result["reasoning"]
            })
            
            # Generate UI components based on the results
            ui_components = await self._generate_ui_components_from_orchestration(
                user_query, 
                orchestration_result,
                context,
                trace_id=trace_id
            )
            
            # Log orchestration success
            tool_names = [tc["tool"] for tc in orchestration_result.get("tool_calls", [])]
            logger.info(f"✅ Orchestration successful: {len(tool_names)} tools used: {tool_names}")
            
            return {
                "response_type": "orchestrated_response",
                "message": orchestration_result["response"],
                "ui_components": ui_components,
                "layout_strategy": "enhanced_with_ui" if ui_components else "text_only",
                "user_intent": user_query,
                "orchestration": {
                    "reasoning": orchestration_result["reasoning"],
                    "synthesis_reasoning": orchestration_result["synthesis_reasoning"],
                    "tools_used": tool_names,
                    "tool_results_count": len(orchestration_result.get("tool_results", []))
                },
                "suggested_actions": orchestration_result.get("suggested_actions", []),
                "execution_time": 0  # TODO: Add timing
            }
            
        except Exception as e:
            logger.error(f"Orchestration processing failed: {e}")
            # Fall back to traditional intelligent processing
            return await self.process_query_intelligently(user_query, context, trace_id)
    
    @observe(as_type="span")
    async def process_query_intelligently(self, user_query: str, context: Dict[str, Any] = None, trace_id: str = None) -> Dict[str, Any]:
        """
        Process user query with intelligent intent understanding and context resolution
        
        This method replaces hardcoded routing with LLM-based intent classification
        and dynamic context resolution for temporal references.
        """
        session_id = context.get("session_id", "default") if context else "default"
        session_state = self.get_session_state(session_id)
        
        try:
            logger.info(f"🧠 Processing query intelligently: {user_query}")
            
            # Step 1: Classify intent using LLM
            intent = await self.intent_classifier.classify_intent(
                user_query, 
                {**session_state, **(context or {})}
            )
            
            logger.info(f"Classified intent: {intent['intent_type']} (confidence: {intent.get('confidence', 0)})")
            
            # Step 2: Resolve contextual references
            resolved_context = await self.context_resolver.resolve_references(intent, session_state)
            
            if resolved_context['resolution_status'] != 'success':
                logger.warning(f"Context resolution issues: {resolved_context.get('resolution_errors', [])}")
            
            # Step 3: Build execution context
            execution_context = self.context_resolver.build_execution_context(resolved_context)
            
            # Step 4: Check for missing context - but allow partial context for some operations
            missing_context = self.context_resolver.get_missing_context(resolved_context)
            if missing_context and resolved_context['resolution_status'] == 'failed':
                return await self._handle_missing_context(user_query, intent, missing_context, trace_id)
            
            # Log context resolution results
            logger.info(f"📋 Context resolution: {resolved_context['resolution_status']}, entities: {list(resolved_context.get('resolved_entities', {}).keys())}")
            
            # Step 5: Execute based on intent
            if intent['intent_type'] in ['order_update', 'order_cancel', 'order_status']:
                return await self._handle_order_operations(user_query, intent, execution_context, trace_id)
            elif intent['intent_type'] in ['product_search', 'product_details']:
                return await self._handle_product_operations(user_query, intent, execution_context, trace_id)
            elif intent['intent_type'] in ['customer_update']:
                return await self._handle_customer_operations(user_query, intent, execution_context, trace_id)
            else:
                # Fall back to original processing for other intents
                return await self.process_query(user_query, context, trace_id)
                
        except Exception as e:
            logger.error(f"❌ Intelligent query processing failed: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Fall back to original processing
            logger.info("🔄 Falling back to original processing")
            return await self.process_query(user_query, context, trace_id)
    
    @trace_conversation(name="step4_dynamic_ui_conversation", user_id="anonymous")
    @observe(as_type="span")
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
    
    @observe(as_type="span")
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
    
    @observe(as_type="span")
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
    
    @langfuse_trace(name="tool_execution")
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
                    logger.info(f"🔍 Executing search_products with parameters: {parameters}")
                    logger.info(f"🔍 MCP Tools API URL: {self.mcp_tools.api_url}")
                    result = await self.mcp_tools.search_products(**parameters)
                    logger.info(f"🔍 Search result: {result}")
                    logger.info(f"🔍 Search result count: {result.get('count', 0)} products found")
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
                    success=True,
                    execution_time=tool_duration / 1000,
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
                    success=False,
                    execution_time=tool_duration / 1000,
                    error_message=str(e),
                    metadata={"duration_ms": tool_duration, "error": str(e)}
                )
        
        return results
    
    @observe(as_type="span")
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
    
    @langfuse_trace(name="ui_generation")
    async def generate_ui_response(self, user_query: str, execution_plan: Dict[str, Any], tool_results: List[Dict[str, Any]], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate UI component specifications using intelligent component selection"""
        try:
            if not self.ui_generation_enabled:
                return {
                    "ui_components": [], 
                    "layout_strategy": "text_only",
                    "user_intent": "Text-only response"
                }
            
            # Use intelligent component selection based on query and results  
            ui_components, layout_strategy, user_intent = await self._generate_intelligent_ui_components(
                user_query, execution_plan, tool_results, context or {}
            )
            
            if not ui_components:
                return {
                    "ui_components": [], 
                    "layout_strategy": "text_only",
                    "user_intent": user_intent
                }
            
            # Create validation info
            validation_info = {
                "total_requested": len(ui_components),
                "validated": len(ui_components),  # All components are pre-validated
                "success": True
            }
            
            return {
                "ui_components": ui_components,
                "layout_strategy": layout_strategy,
                "user_intent": user_intent,
                "validation": validation_info
            }
            
        except Exception as e:
            logger.error(f"UI generation failed: {e}")
            return {
                "ui_components": [],
                "layout_strategy": "text_only", 
                "user_intent": f"Error processing query: {user_query}",
                "error": str(e)
            }
    
    @langfuse_trace(name="ui_components_from_orchestration")
    async def _generate_ui_components_from_orchestration(self, user_query: str, orchestration_result: Dict[str, Any], context: Dict[str, Any], trace_id: str = None) -> List[Dict[str, Any]]:
        """Generate UI components based on orchestration results"""
        try:
            tool_results = orchestration_result.get("tool_results", [])
            
            # Extract successful tool results with data
            data_results = []
            for tool_result in tool_results:
                if tool_result.get("success") and "data" in tool_result.get("result", {}):
                    data_results.append(tool_result)
            
            if not data_results:
                return []
            
            # Determine the primary data type and generate appropriate UI components
            primary_data_type = self._determine_primary_data_type(data_results)
            
            if primary_data_type == "products":
                return await self._generate_product_ui_from_orchestration(data_results, user_query)
            elif primary_data_type == "orders":
                return await self._generate_order_ui_from_orchestration(data_results, user_query)
            elif primary_data_type == "customers":
                return await self._generate_customer_ui_from_orchestration(data_results, user_query)
            else:
                return await self._generate_generic_ui_from_orchestration(data_results, user_query)
                
        except Exception as e:
            logger.error(f"UI generation from orchestration failed: {e}")
            return []
    
    def _determine_primary_data_type(self, data_results: List[Dict[str, Any]]) -> str:
        """Determine the primary data type from orchestration results"""
        for result in data_results:
            tool_name = result.get("tool", "")
            if "product" in tool_name.lower():
                return "products"
            elif "order" in tool_name.lower():
                return "orders"
            elif "customer" in tool_name.lower():
                return "customers"
        return "generic"
    
    async def _generate_product_ui_from_orchestration(self, data_results: List[Dict[str, Any]], user_query: str) -> List[Dict[str, Any]]:
        """Generate product UI components from orchestration results"""
        components = []
        
        for result in data_results:
            if "product" in result.get("tool", "").lower():
                products = result.get("result", {}).get("data", [])
                if products:
                    # Generate product cards
                    for product in products[:3]:  # Limit to 3 products
                        components.append({
                            "type": "card",
                            "props": {
                                "title": product.get("name", "Product"),
                                "description": product.get("description", ""),
                                "imageUrl": product.get("imageUrl", ""),
                                "price": f"${product.get('price', 0)}",
                                "metadata": {
                                    "brand": product.get("brand", ""),
                                    "model": product.get("model", "")
                                }
                            },
                            "actions": [
                                {
                                    "type": "button",
                                    "label": "View Details",
                                    "action": "view_product",
                                    "data": {"product_id": product.get("id")}
                                },
                                {
                                    "type": "button", 
                                    "label": "Add to Cart",
                                    "action": "add_to_cart",
                                    "data": {"product_id": product.get("id")}
                                }
                            ]
                        })
        
        return components
    
    async def _generate_order_ui_from_orchestration(self, data_results: List[Dict[str, Any]], user_query: str) -> List[Dict[str, Any]]:
        """Generate order UI components from orchestration results"""
        components = []
        
        for result in data_results:
            if "order" in result.get("tool", "").lower():
                orders = result.get("result", {}).get("data", [])
                if isinstance(orders, list):
                    # Multiple orders
                    for order in orders[:5]:  # Limit to 5 orders
                        components.append({
                            "type": "order_card",
                            "props": {
                                "order_id": order.get("id", ""),
                                "status": order.get("status", ""),
                                "total": f"${order.get('totalAmount', 0)}",
                                "date": order.get("orderDate", ""),
                                "items_count": len(order.get("items", []))
                            },
                            "actions": [
                                {
                                    "type": "button",
                                    "label": "Track Order",
                                    "action": "track_order",
                                    "data": {"order_id": order.get("id")}
                                }
                            ]
                        })
                else:
                    # Single order
                    order = orders
                    components.append({
                        "type": "order_detail",
                        "props": {
                            "order_id": order.get("id", ""),
                            "status": order.get("status", ""),
                            "total": f"${order.get('totalAmount', 0)}",
                            "date": order.get("orderDate", ""),
                            "items": order.get("items", [])
                        }
                    })
        
        return components
    
    async def _generate_customer_ui_from_orchestration(self, data_results: List[Dict[str, Any]], user_query: str) -> List[Dict[str, Any]]:
        """Generate customer UI components from orchestration results"""
        components = []
        
        for result in data_results:
            if "customer" in result.get("tool", "").lower():
                customer_data = result.get("result", {}).get("data", {})
                if customer_data:
                    components.append({
                        "type": "customer_profile",
                        "props": {
                            "name": customer_data.get("name", ""),
                            "email": customer_data.get("email", ""),
                            "address": customer_data.get("address", ""),
                            "phone": customer_data.get("phone", "")
                        },
                        "actions": [
                            {
                                "type": "button",
                                "label": "Edit Profile",
                                "action": "edit_customer",
                                "data": {"customer_id": customer_data.get("id")}
                            }
                        ]
                    })
        
        return components
    
    async def _generate_generic_ui_from_orchestration(self, data_results: List[Dict[str, Any]], user_query: str) -> List[Dict[str, Any]]:
        """Generate generic UI components from orchestration results"""
        components = []
        
        # Simple data display component
        for result in data_results:
            tool_name = result.get("tool", "Unknown")
            result_data = result.get("result", {})
            
            components.append({
                "type": "data_display",
                "props": {
                    "title": f"Results from {tool_name}",
                    "data": result_data.get("data", {}),
                    "count": result_data.get("count", 0)
                }
            })
        
        return components
    
    @observe(as_type="span")
    async def _generate_intelligent_ui_components(self, user_query: str, execution_plan: Dict[str, Any], tool_results: List[Dict[str, Any]], context: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], str, str]:
        """Generate UI components using intelligent component selection"""
        try:
            # Extract data from tool results
            context_data = self._extract_context_data(tool_results, execution_plan)
            
            # Determine the primary workflow from query and results
            workflow_type = self._determine_workflow_type(user_query, execution_plan, tool_results)
            
            # Get suitable components based on workflow and data
            ui_components = []
            
            if workflow_type == "product_display":
                ui_components = self._generate_product_ui_components(context_data)
            elif workflow_type == "order_management":
                ui_components = self._generate_order_ui_components(context_data)
            elif workflow_type == "error_handling":
                ui_components = self._generate_error_ui_components(context_data)
            elif workflow_type == "general_inquiry":
                ui_components = self._generate_general_ui_components(context_data, user_query)
            else:
                # Fallback to workflow-based component selection
                ui_components = self.ui_component_tools.get_components_for_workflow(
                    user_query, context_data
                )
            
            # Determine layout strategy and user intent
            layout_strategy = self._determine_layout_strategy(ui_components, execution_plan)
            user_intent = self._determine_user_intent(user_query, workflow_type, context_data)
            
            return ui_components, layout_strategy, user_intent
            
        except Exception as e:
            logger.error(f"Intelligent UI component generation failed: {e}")
            return [], "text_only", f"Error processing query: {user_query}"
    
    def _extract_context_data(self, tool_results: List[Dict[str, Any]], execution_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant context data from tool results"""
        context_data = {
            "strategy": execution_plan.get("strategy", "unknown"),
            "query_type": execution_plan.get("query_type"),
            "has_data": bool(tool_results)
        }
        
        # Extract product data
        for result in tool_results:
            if result.get("tool") == "search_products" and result.get("success"):
                products = result.get("data", [])
                if products:
                    context_data["products"] = products
                    context_data["product"] = products[0]  # First product for single display
                    context_data["product_count"] = len(products)
        
        # Extract order data  
        for result in tool_results:
            if "order" in result.get("tool", "").lower() and result.get("success"):
                if "data" in result and result["data"]:
                    context_data["order"] = result["data"]
                    context_data["orders"] = [result["data"]] if not isinstance(result["data"], list) else result["data"]
        
        # Extract customer data
        for result in tool_results:
            if "customer" in result.get("tool", "").lower() and result.get("success"):
                if "data" in result:
                    context_data["customer"] = result["data"]
        
        return context_data
    
    def _determine_workflow_type(self, user_query: str, execution_plan: Dict[str, Any], tool_results: List[Dict[str, Any]]) -> str:
        """Determine the primary workflow type for UI generation"""
        query_lower = user_query.lower()
        strategy = execution_plan.get("strategy", "")
        
        # Check for product-related queries
        if any(keyword in query_lower for keyword in ["product", "price", "iphone", "item", "catalog"]):
            return "product_display"
        
        # Check for order-related queries
        if any(keyword in query_lower for keyword in ["order", "purchase", "buy", "cart", "checkout"]):
            return "order_management"
        
        # Check for error conditions
        if strategy == "transactional_fallback" and not any(result.get("success", False) for result in tool_results):
            return "error_handling"
        
        # Check for customer service queries
        if any(keyword in query_lower for keyword in ["customer", "account", "profile", "help"]):
            return "customer_service"
        
        return "general_inquiry"
    
    def _generate_product_ui_components(self, context_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate UI components for product display workflows"""
        if "product" in context_data:
            return self.ui_component_tools.get_components_for_product_display(context_data["product"])
        return []
    
    def _generate_order_ui_components(self, context_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate UI components for order management workflows"""
        if "order" in context_data:
            return self.ui_component_tools.get_components_for_order_management(context_data["order"])
        return []
    
    def _generate_error_ui_components(self, context_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate UI components for error handling scenarios"""
        return [{
            "type": "alert",
            "props": {
                "className": "max-w-md"
            },
            "children": [
                {
                    "type": "alerttitle", 
                    "children": "No Results Found"
                },
                {
                    "type": "alertdescription",
                    "children": "We couldn't find what you're looking for. Please try a different search term or browse our product catalog."
                }
            ],
            "layout": {"position": "inline", "priority": "high"}
        }]
    
    def _generate_general_ui_components(self, context_data: Dict[str, Any], user_query: str) -> List[Dict[str, Any]]:
        """Generate UI components for general inquiries"""
        # Use workflow-based selection as fallback
        return self.ui_component_tools.get_components_for_workflow(user_query, context_data)
    
    def _enhance_components_with_data(self, ui_components: List[Dict[str, Any]], context_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enhance UI components with actual data from context"""
        enhanced_components = []
        
        for component in ui_components:
            enhanced_component = component.copy()
            
            # Enhance product-related components
            if "product" in context_data and component.get("type") in ["card", "badge"]:
                product = context_data["product"]
                if component.get("type") == "card":
                    enhanced_component["props"].update({
                        "title": product.get("name", "Product"),
                        "imageUrl": product.get("imageUrl"),
                        "description": product.get("description", "")
                    })
                    # Add product details as children
                    enhanced_component["children"] = [
                        {
                            "type": "text",
                            "content": f"Price: ${product.get('price', '0.00')}",
                            "className": "product-price"
                        },
                        {
                            "type": "text", 
                            "content": product.get("description", ""),
                            "className": "product-description"
                        }
                    ]
                elif component.get("type") == "badge":
                    enhanced_component["props"]["children"] = f"${product.get('price', '0.00')}"
            
            # Enhance order-related components
            if "order" in context_data and component.get("type") == "card":
                order = context_data["order"]
                enhanced_component["props"].update({
                    "title": f"Order {order.get('id', 'N/A')}",
                    "status": order.get("status", "Unknown")
                })
                enhanced_component["children"] = [
                    {
                        "type": "text",
                        "content": f"Status: {order.get('status', 'Unknown')}",
                        "className": "order-status"
                    },
                    {
                        "type": "text",
                        "content": f"Amount: ${order.get('amount', '0.00')}",
                        "className": "order-amount"
                    }
                ]
            
            enhanced_components.append(enhanced_component)
        
        return enhanced_components
    
    def _determine_layout_strategy(self, ui_components: List[Dict[str, Any]], execution_plan: Dict[str, Any]) -> str:
        """Determine the best layout strategy for the UI components"""
        if not ui_components:
            return "text_only"
        
        component_count = len(ui_components)
        has_complex_components = any(
            comp.get("metadata", {}).get("component_type") in ["organism", "template"] 
            for comp in ui_components
        )
        
        # Use layout strategies that the renderer understands
        if component_count == 1:
            return "single_component"
        elif component_count <= 3:
            return "composition"  # Renderer recognizes this
        elif has_complex_components:
            return "workflow"     # Renderer recognizes this  
        else:
            return "composition"  # Default to composition for multiple components
    
    def _determine_user_intent(self, user_query: str, workflow_type: str, context_data: Dict[str, Any]) -> str:
        """Determine user intent for UI rendering"""
        if workflow_type == "product_display":
            if "product" in context_data:
                return f"View product details for {context_data['product'].get('name', 'product')}"
            return "Browse product information"
        elif workflow_type == "order_management":
            return "Manage order information"
        elif workflow_type == "error_handling":
            return "Handle search error"
        else:
            return f"Handle user query: {user_query[:50]}..."
    
    @observe(as_type="span")
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
    
    @observe(as_type="span")
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
    
    # ========================================
    # Intelligent Query Handlers
    # ========================================
    
    async def _handle_missing_context(self, user_query: str, intent: Dict[str, Any], missing_context: List[str], trace_id: str = None) -> Dict[str, Any]:
        """Handle queries that are missing required context"""
        logger.info(f"Missing context for query: {missing_context}")
        
        missing_context_messages = {
            'customer_authentication': "I need you to be logged in to help with that. Please sign in to your account first.",
            'order_identification': "I couldn't find the specific order you're referring to. Could you provide the order number or be more specific?",
            'product_specification': "I need more details about which product you're interested in. Could you be more specific?",
            'last_order_reference': "I couldn't find your recent orders. Please make sure you're logged in, or specify which order you mean."
        }
        
        messages = [missing_context_messages.get(ctx, f"Missing context: {ctx}") for ctx in missing_context]
        response_message = " ".join(messages)
        
        # Generate helpful UI for missing context
        ui_components = []
        if 'customer_authentication' in missing_context:
            ui_components.append({
                "type": "alert",
                "props": {"variant": "info"},
                "children": [
                    {"type": "alerttitle", "children": "Sign In Required"},
                    {"type": "alertdescription", "children": "Please sign in to access your account information."}
                ]
            })
            ui_components.append({
                "type": "button",
                "props": {"variant": "default", "className": "mt-4"},
                "children": "Sign In",
                "actions": [{"event": "onClick", "action": "navigate", "payload": {"url": "/login"}}]
            })
        
        return {
            "message": response_message,
            "ui_components": ui_components,
            "layout_strategy": "single_component" if ui_components else "text_only",
            "user_intent": f"Handle missing context: {', '.join(missing_context)}",
            "response_type": "context_required",
            "missing_context": missing_context,
            "debug": {"intent": intent, "missing_context": missing_context}
        }
    
    async def _handle_order_operations(self, user_query: str, intent: Dict[str, Any], execution_context: Dict[str, Any], trace_id: str = None) -> Dict[str, Any]:
        """Handle order-related operations (update, cancel, status)"""
        logger.info(f"🔧 Handling order operation: {intent['intent_type']}")
        
        try:
            intent_type = intent['intent_type']
            target_order = execution_context.get('target_order')
            order_id = execution_context.get('order_id')
            customer = execution_context.get('customer')
            
            # If we don't have specific order but have customer, try to get their last order
            if not target_order and not order_id and customer:
                logger.info("🔍 No specific order found, trying to get customer's last order")
                customer_id = customer.get('id') or customer.get('customer_id')
                if customer_id:
                    orders_result = await self.mcp_tools.get_customer_orders(customer_id, limit=1)
                    if orders_result.get('success') and orders_result.get('data'):
                        target_order = orders_result['data'][0] if isinstance(orders_result['data'], list) else orders_result['data']
                        order_id = target_order.get('id')
                        logger.info(f"✅ Found last order: {order_id}")
            
            if not target_order and not order_id:
                logger.warning("❌ Could not identify any order to modify")
                return await self._handle_missing_context(user_query, intent, ['order_identification'], trace_id)
            
            tool_results = []
            
            customer_id = customer.get('id') or customer.get('customer_id') if customer else None
            
            if intent_type == 'order_update':
                # Extract what needs to be updated from the intent
                updates = self._extract_order_updates(intent, user_query)
                if updates:
                    result = await self.mcp_tools.update_order(order_id, updates, customer_id)
                    tool_results.append({"tool": "update_order", **result})
                    
            elif intent_type == 'order_cancel':
                reason = self._extract_cancellation_reason(user_query)
                result = await self.mcp_tools.cancel_order(order_id, reason)
                tool_results.append({"tool": "cancel_order", **result})
                
            elif intent_type == 'order_status':
                result = await self.mcp_tools.track_order(order_id, customer_id)
                tool_results.append({"tool": "track_order", **result})
            
            # Generate response with appropriate UI
            return await self._generate_intelligent_response(user_query, intent, tool_results, execution_context, trace_id)
            
        except Exception as e:
            logger.error(f"Order operation failed: {e}")
            return await self._fallback_response(user_query, f"Sorry, I couldn't complete that order operation: {str(e)}")
    
    async def _handle_product_operations(self, user_query: str, intent: Dict[str, Any], execution_context: Dict[str, Any], trace_id: str = None) -> Dict[str, Any]:
        """Handle product-related operations (search, details)"""
        logger.info(f"Handling product operation: {intent['intent_type']}")
        
        try:
            # Use existing product search logic but with intelligent context
            entity_refs = intent.get('entity_references', [])
            search_query = " ".join(entity_refs) if entity_refs else user_query
            
            # Apply constraints from intent
            filters = {}
            constraints = intent.get('constraints', {})
            if 'max_price' in constraints:
                filters['max_price'] = constraints['max_price']
            if 'min_price' in constraints:
                filters['min_price'] = constraints['min_price']
            if 'category' in constraints:
                filters['category'] = constraints['category']
            
            # Debug logging
            logger.info(f"🔍 Product search - Query: '{search_query}', Filters: {filters}, Entity refs: {entity_refs}, Constraints: {constraints}")
            
            result = await self.mcp_tools.search_products(search_query, filters)
            tool_results = [{"tool": "search_products", **result}]
            
            logger.info(f"📊 Search result: {result.get('success')}, Count: {result.get('count', 0)}")
            
            return await self._generate_intelligent_response(user_query, intent, tool_results, execution_context, trace_id)
            
        except Exception as e:
            logger.error(f"Product operation failed: {e}")
            return await self._fallback_response(user_query, f"Sorry, I couldn't search for products: {str(e)}")
    
    async def _handle_customer_operations(self, user_query: str, intent: Dict[str, Any], execution_context: Dict[str, Any], trace_id: str = None) -> Dict[str, Any]:
        """Handle customer-related operations (profile updates)"""
        logger.info(f"Handling customer operation: {intent['intent_type']}")
        
        try:
            customer = execution_context.get('customer')
            if not customer:
                return await self._handle_missing_context(user_query, intent, ['customer_authentication'], trace_id)
            
            customer_id = customer.get('id') or customer.get('customer_id')
            updates = self._extract_customer_updates(intent, user_query)
            
            if updates:
                result = await self.mcp_tools.update_customer(customer_id, updates)
                tool_results = [{"tool": "update_customer", **result}]
            else:
                # Just get current customer info
                result = await self.mcp_tools.get_customer_info(customer_id)
                tool_results = [{"tool": "get_customer_info", **result}]
            
            return await self._generate_intelligent_response(user_query, intent, tool_results, execution_context, trace_id)
            
        except Exception as e:
            logger.error(f"Customer operation failed: {e}")
            return await self._fallback_response(user_query, f"Sorry, I couldn't complete that customer operation: {str(e)}")
    
    async def _generate_intelligent_response(self, user_query: str, intent: Dict[str, Any], tool_results: List[Dict[str, Any]], execution_context: Dict[str, Any], trace_id: str = None) -> Dict[str, Any]:
        """Generate intelligent response with appropriate UI components"""
        
        # Create execution plan from intent
        execution_plan = {
            "strategy": "intelligent",
            "intent_type": intent['intent_type'],
            "tool_calls": [{"name": result.get("tool", "unknown")} for result in tool_results],
            "confidence": intent.get('confidence', 1.0)
        }
        
        # Generate text response
        response_message = await self._generate_natural_response(user_query, intent, tool_results, execution_context)
        
        # Generate UI components
        ui_response = await self.generate_ui_response(user_query, execution_plan, tool_results, execution_context)
        
        return {
            "message": response_message,
            "ui_components": ui_response.get("ui_components", []),
            "layout_strategy": ui_response.get("layout_strategy", "text_only"),
            "user_intent": ui_response.get("user_intent", intent['intent_type']),
            "response_type": "intelligent_with_ui",
            "intent": intent,
            "execution_context": execution_context,
            "tool_results": tool_results,
            "debug": {
                "intent_type": intent['intent_type'],
                "confidence": intent.get('confidence', 0),
                "tools_used": [r.get("tool") for r in tool_results],
                "ui_generation_enabled": self.ui_generation_enabled
            }
        }
    
    def _extract_order_updates(self, intent: Dict[str, Any], user_query: str) -> Dict[str, Any]:
        """Extract order update fields from intent and query"""
        updates = {}
        query_lower = user_query.lower()
        
        # Address updates
        if any(word in query_lower for word in ['address', 'shipping', 'delivery']):
            # In a real implementation, you'd extract the new address
            # For now, we'll flag it as needing manual input
            updates['_requires_address_input'] = True
        
        # Status updates (usually admin only, but could be cancellation)
        if 'cancel' in query_lower:
            updates['status'] = 'cancelled'
            updates['cancellation_reason'] = 'Customer requested cancellation'
        
        return updates
    
    def _extract_cancellation_reason(self, user_query: str) -> str:
        """Extract cancellation reason from user query"""
        query_lower = user_query.lower()
        
        if 'wrong' in query_lower or 'mistake' in query_lower:
            return "Ordered by mistake"
        elif 'found better' in query_lower or 'cheaper' in query_lower:
            return "Found better option"
        elif 'changed mind' in query_lower:
            return "Changed mind"
        else:
            return "Customer requested cancellation"
    
    def _extract_customer_updates(self, intent: Dict[str, Any], user_query: str) -> Dict[str, Any]:
        """Extract customer update fields from intent and query"""
        updates = {}
        query_lower = user_query.lower()
        
        # Email updates
        if 'email' in query_lower:
            updates['_requires_email_input'] = True
        
        # Address updates
        if 'address' in query_lower:
            updates['_requires_address_input'] = True
        
        # Phone updates
        if 'phone' in query_lower or 'number' in query_lower:
            updates['_requires_phone_input'] = True
        
        return updates
    
    async def _generate_natural_response(self, user_query: str, intent: Dict[str, Any], tool_results: List[Dict[str, Any]], execution_context: Dict[str, Any]) -> str:
        """Generate natural language response based on intent and results"""
        
        intent_type = intent['intent_type']
        success_results = [r for r in tool_results if r.get('success')]
        
        if not success_results:
            return f"I couldn't complete your request. Please try again or contact support."
        
        # Generate intent-specific responses
        if intent_type == 'order_update':
            if any('_requires_' in str(r.get('data', {})) for r in success_results):
                return "I can help you update your order! What would you like to change?"
            else:
                return f"Your order has been updated successfully!"
                
        elif intent_type == 'order_cancel':
            return f"Your order has been cancelled successfully. You should receive a confirmation email shortly."
            
        elif intent_type == 'order_status':
            status_result = success_results[0]
            data = status_result.get('data', {})
            status = data.get('status', 'unknown')
            return f"Your order is currently {status}. {status_result.get('message', '')}"
            
        elif intent_type == 'product_search':
            search_result = success_results[0]
            count = search_result.get('count', 0)
            if count > 0:
                return f"I found {count} products matching your search!"
            else:
                return "I couldn't find any products matching your search. Try different keywords or browse our categories."
                
        else:
            return "I've processed your request successfully!"
    
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