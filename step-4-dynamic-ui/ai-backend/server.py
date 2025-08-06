"""
Step 4: Dynamic UI Generation Server
Enhanced FastAPI server with RAG capabilities and Dynamic UI Generation
"""
import os
import time
import logging
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../rag-service'))

from src.enhanced_agent import EnhancedAgent
from config.llm_config import LLMConfig
from config.logging_config import logging_config
from rag_service import RAGService
from shared.observability.langfuse_client import langfuse_client

# Load environment variables
load_dotenv()

# Get logger
logger = logging_config.get_logger(__name__)

# Initialize components
llm_config = LLMConfig()
agent = EnhancedAgent(os.getenv("TRADITIONAL_API_URL", "http://localhost:4000"))
rag_service = RAGService()

# FastAPI app
app = FastAPI(
    title="AI Mode Backend - Step 4 (Dynamic UI Generation)",
    description="Enhanced AI mode with RAG capabilities and LLM-powered dynamic UI generation",
    version="4.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class ChatRequest(BaseModel):
    message: str
    context: Dict[str, Any] = {}

class KnowledgeSearchRequest(BaseModel):
    query: str
    type: str = "auto"  # auto, faq, business_rules
    limit: int = 5

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Mode Backend - Step 4 (Dynamic UI Generation)",
        "version": "4.0.0",
        "llm_info": llm_config.get_info(),
        "features": [
            "Enhanced AI agent with RAG capabilities",
            "FAQ knowledge base search",
            "Business rules integration",
            "Query classification and routing",
            "Hybrid transactional + knowledge responses",
            "LLM-powered dynamic UI generation",
            "Component library integration",
            "UI component specifications",
            "Multi-level component caching"
        ]
    }

@app.get("/health")
async def health_check():
    """Enhanced health check endpoint"""
    # Check RAG service health
    rag_health = await rag_service.health_check()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "llm_provider": llm_config.provider,
        "version": "4.0.0",
        "services": {
            "rag_service": rag_health,
            "ui_generation": "enabled"
        }
    }

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Enhanced chat endpoint with RAG capabilities"""
    session_id = request.context.get("session_id", f"session_{int(time.time())}")
    
    # Create LangFuse trace
    trace_id = langfuse_client.create_trace(
        user_message=request.message,
        session_id=session_id,
        metadata=request.context
    )
    
    try:
        logger.info(f"Enhanced chat request: {request.message}")
        
        # Process query with enhanced agent - try orchestration first, then intelligent processing
        response_data = await agent.process_query_with_orchestration(request.message, request.context, trace_id)
        
        # Check if orchestration succeeded
        if response_data.get("response_type") == "orchestrated_response":
            # Orchestration succeeded, use the response directly
            logger.info(f"✅ Using orchestration response")
            # Add required fields for LangFuse compatibility
            execution_plan = response_data.get("orchestration", {})
            tool_results = []  # Tool results are embedded in orchestration response
        elif response_data.get("response_type") in ["intelligent_with_ui", "context_required"]:
            # Intelligent processing succeeded, use the response directly
            logger.info(f"✅ Using intelligent response: {response_data.get('response_type')}")
            # Add required fields for LangFuse compatibility
            execution_plan = response_data.get("intent", {})
            tool_results = response_data.get("tool_results", [])
        else:
            # Intelligent processing fell back, try the old system as backup
            logger.info("🔄 Intelligent processing fell back, using traditional processing")
            execution_plan = response_data  # The fallback returns traditional format
            
            # Execute transactional tools if needed
            tool_results = []
            if execution_plan.get("tool_calls"):
                tool_results = await agent.execute_tools(
                    execution_plan["tool_calls"], 
                    session_id, 
                    trace_id
                )
            
            # Format response combining knowledge, tool results, and UI components
            response_data = await agent.format_response(
                execution_plan,
                tool_results, 
                request.message,
                trace_id,
                request.context
            )
        
        # Update LangFuse trace with final output
        langfuse_client.log_conversation_end(
            trace_id=trace_id,
            response=response_data.get("message", ""),
            response_type=response_data.get("response_type", "text_only"),
            total_execution_time=0,
            components_summary={
                "strategy": execution_plan.get("strategy"),
                "knowledge_results_count": len(execution_plan.get("knowledge_results", [])),
                "tool_results_count": len(tool_results),
                "ui_components_count": len(response_data.get("ui_components", [])),
                "total_components": len(response_data.get("ui_components", []))
            },
            metadata={
                "success": True,
                "response_type": response_data.get("response_type", "text_only")
            }
        )
        
        # Flush LangFuse data
        langfuse_client.flush()
        
        return {
            "message": response_data.get("message", ""),
            "ui_components": response_data.get("ui_components", []),
            "layout_strategy": response_data.get("layout_strategy", "text_only"),
            "user_intent": response_data.get("user_intent", "unknown"),
            "response_type": response_data.get("response_type", "text_only"),
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "strategy": execution_plan.get("strategy"),
            "debug": {
                "tools_used": [tc["tool"] for tc in execution_plan.get("tool_calls", [])] if "tool_calls" in execution_plan else response_data.get("orchestration", {}).get("tools_used", []),
                "knowledge_results": len(execution_plan.get("knowledge_results", [])),
                "llm_provider": llm_config.provider,
                "query_type": execution_plan.get("query_type"),
                "ui_generation_enabled": True,
                "validation": response_data.get("validation", {}),
                "processing_type": "orchestration" if response_data.get("response_type") == "orchestrated_response" else "traditional",
                "orchestration": response_data.get("orchestration", {}) if response_data.get("response_type") == "orchestrated_response" else None
            }
        }
        
    except Exception as e:
        logger.error(f"Enhanced chat processing failed: {e}")
        langfuse_client.log_conversation_end(
            trace_id=trace_id,
            response=f"Error: {str(e)}",
            response_type="error",
            total_execution_time=0,
            components_summary={"error": True},
            metadata={"success": False, "error": str(e)}
        )
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/knowledge/search")
async def knowledge_search_endpoint(request: KnowledgeSearchRequest):
    """Direct knowledge base search endpoint"""
    try:
        logger.info(f"Knowledge search request: {request.query} (type: {request.type})")
        
        if request.type == "faq":
            results = await rag_service.search_faq(request.query, request.limit)
        elif request.type == "business_rules":
            results = await rag_service.search_business_rules(request.query, request.limit)
        else:  # auto
            rag_response = await rag_service.process_query(request.query)
            results = rag_response.results
        
        return {
            "query": request.query,
            "type": request.type,
            "results": [
                {
                    "id": result.id,
                    "type": result.type,
                    "content": result.content,
                    "metadata": result.metadata,
                    "score": result.score
                } for result in results
            ],
            "count": len(results),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Knowledge search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/knowledge/suggestions")
async def get_knowledge_suggestions(query: str, limit: int = 3):
    """Get suggested questions from knowledge base"""
    try:
        suggestions = await rag_service.get_similar_questions(query, limit)
        
        return {
            "query": query,
            "suggestions": suggestions,
            "count": len(suggestions),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Knowledge suggestions failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools")
async def get_available_tools():
    """Get available tools including RAG capabilities"""
    return {
        "transactional_tools": [
            {
                "name": "search_products",
                "description": "Search for products by name, description, or brand",
                "parameters": {
                    "query": "string",
                    "filters": "object (optional)"
                }
            },
            {
                "name": "get_products", 
                "description": "Get all products with optional filters",
                "parameters": {
                    "category_id": "int (optional)", 
                    "brand": "string (optional)",
                    "limit": "int (optional)",
                    "offset": "int (optional)"
                }
            },
            {
                "name": "get_customers",
                "description": "Get all customers with search and pagination",
                "parameters": {
                    "limit": "int (optional)",
                    "search": "string (optional)"
                }
            },
            {
                "name": "get_customer_orders",
                "description": "Get orders for a specific customer",
                "parameters": {
                    "customer_id": "string",
                    "limit": "int (optional)"
                }
            },
            {
                "name": "create_order",
                "description": "Create a new order",
                "parameters": {
                    "customer_id": "string",
                    "product_id": "string",
                    "quantity": "int (optional)",
                    "shipping_address": "string (optional)",
                    "payment_method": "string (optional)",
                    "special_instructions": "string (optional)"
                }
            },
            {
                "name": "get_categories",
                "description": "Get all product categories",
                "parameters": {}
            }
        ],
        "knowledge_tools": [
            {
                "name": "faq_search",
                "description": "Search FAQ knowledge base",
                "parameters": {
                    "query": "string",
                    "limit": "int (optional)"
                }
            },
            {
                "name": "business_rules_search",
                "description": "Search business rules knowledge base",
                "parameters": {
                    "query": "string",
                    "limit": "int (optional)"
                }
            },
            {
                "name": "hybrid_search",
                "description": "Search both FAQ and business rules",
                "parameters": {
                    "query": "string",
                    "limit": "int (optional)"
                }
            }
        ],
        "ui_tools": [
            {
                "name": "get_component_library",
                "description": "Get complete UI component library with all available components",
                "parameters": {}
            },
            {
                "name": "get_component_schema",
                "description": "Get detailed schema for specific component",
                "parameters": {
                    "component_name": "string"
                }
            },
            {
                "name": "get_ui_patterns",
                "description": "Get recommended UI patterns for specific intent",
                "parameters": {
                    "intent": "string"
                }
            },
            {
                "name": "validate_component_spec",
                "description": "Validate component specification against schema",
                "parameters": {
                    "component_spec": "object"
                }
            },
            {
                "name": "get_cache_status",
                "description": "Get component cache status and statistics",
                "parameters": {}
            },
            {
                "name": "refresh_component_cache",
                "description": "Force refresh component cache",
                "parameters": {}
            }
        ],
        "query_types": [
            "transactional",
            "faq",
            "business_rule",
            "mixed"
        ],
        "response_types": [
            "text_only",
            "enhanced_with_ui",
            "error"
        ]
    }

@app.get("/knowledge/stats")
async def get_knowledge_stats():
    """Get knowledge base statistics"""
    try:
        health_info = await rag_service.health_check()
        
        return {
            "status": health_info["status"],
            "collections": health_info.get("collections", {}),
            "stats": health_info.get("stats", {}),
            "embedding_model": health_info.get("embedding_model"),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Knowledge stats failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# UI Generation Endpoints
# ========================================

@app.get("/ui/components")
async def get_component_library():
    """Get complete UI component library"""
    try:
        logger.info("Component library request")
        
        # Access MCP tools through the agent
        result = await agent.mcp_tools.get_component_library()
        
        if result.get("success"):
            return {
                "success": True,
                "components": result["data"],
                "source": result.get("source", "unknown"),
                "component_count": len(result["data"]),
                "metadata": result.get("metadata", {}),
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Component library fetch failed"))
            
    except Exception as e:
        logger.error(f"Component library fetch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ui/components/{component_name}")
async def get_component_schema(component_name: str):
    """Get detailed schema for specific component"""
    try:
        logger.info(f"Component schema request: {component_name}")
        
        result = await agent.mcp_tools.get_component_schema(component_name)
        
        if result.get("success"):
            return {
                "success": True,
                "component": result["data"],
                "source": result.get("source", "unknown"),
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail=result.get("error", f"Component '{component_name}' not found"))
            
    except Exception as e:
        logger.error(f"Component schema fetch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ui/patterns")
async def get_ui_patterns(intent: str):
    """Get recommended UI patterns for specific intent"""
    try:
        logger.info(f"UI patterns request: {intent}")
        
        result = await agent.mcp_tools.get_ui_patterns(intent)
        
        if result.get("success"):
            return {
                "success": True,
                "intent": intent,
                "patterns": result["data"]["patterns"],
                "recommendations": result["data"]["recommendations"],
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "UI patterns fetch failed"))
            
    except Exception as e:
        logger.error(f"UI patterns fetch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ui/cache/status")
async def get_component_cache_status():
    """Get component cache status and statistics"""
    try:
        logger.info("Component cache status request")
        
        result = await agent.mcp_tools.get_cache_status()
        
        if result.get("success"):
            return {
                "success": True,
                "cache_info": result["data"],
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Cache status fetch failed"))
            
    except Exception as e:
        logger.error(f"Cache status fetch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ui/cache/refresh")
async def refresh_component_cache():
    """Force refresh component cache"""
    try:
        logger.info("Component cache refresh request")
        
        result = await agent.mcp_tools.refresh_component_cache()
        
        if result.get("success"):
            return {
                "success": True,
                "message": "Component cache refreshed successfully",
                "refresh_info": result["data"],
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Cache refresh failed"))
            
    except Exception as e:
        logger.error(f"Cache refresh failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class UIValidationRequest(BaseModel):
    component_spec: Dict[str, Any]

@app.post("/ui/validate")
async def validate_component_spec(request: UIValidationRequest):
    """Validate component specification against schema"""
    try:
        logger.info(f"Component validation request: {request.component_spec.get('type', 'unknown')}")
        
        result = await agent.mcp_tools.validate_component_spec(request.component_spec)
        
        if result.get("success"):
            return {
                "success": True,
                "validation": result["data"],
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Validation failed"),
                "validation_errors": result.get("validation_errors", []),
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Component validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await agent.close()

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8003"))
    
    logger.info("🚀 Starting AI Mode Backend - Step 4 (Dynamic UI Generation)")
    logger.info(f"   Port: {port}")
    logger.info(f"   LLM Provider: {llm_config.provider}")
    logger.info(f"   LLM Info: {llm_config.get_info()}")
    logger.info("   Features: Enhanced AI agent with RAG capabilities and Dynamic UI Generation")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )