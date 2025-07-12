"""
Step 2: RAG Integration Server
Enhanced FastAPI server with RAG capabilities
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
    title="AI Mode Backend - Step 2 (RAG Integration)",
    description="Enhanced AI mode with RAG capabilities for FAQ and business rules",
    version="2.0.0"
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
        "message": "AI Mode Backend - Step 2 (RAG Integration)",
        "version": "2.0.0",
        "llm_info": llm_config.get_info(),
        "features": [
            "Enhanced AI agent with RAG capabilities",
            "FAQ knowledge base search",
            "Business rules integration",
            "Query classification and routing",
            "Hybrid transactional + knowledge responses"
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
        "version": "2.0.0",
        "services": {
            "rag_service": rag_health
        }
    }

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Enhanced chat endpoint with RAG capabilities"""
    session_id = request.context.get("session_id", f"session_{int(time.time())}")
    
    # Create LangFuse trace
    trace_id = langfuse_client.create_trace(
        session_id=session_id,
        user_input=request.message,
        metadata=request.context
    )
    
    try:
        logger.info(f"Enhanced chat request: {request.message}")
        
        # Process query with enhanced agent
        execution_plan = await agent.process_query(request.message, request.context, trace_id)
        
        # Execute transactional tools if needed
        tool_results = []
        if execution_plan.get("tool_calls"):
            tool_results = await agent.execute_tools(
                execution_plan["tool_calls"], 
                session_id, 
                trace_id
            )
        
        # Format response combining knowledge and tool results
        response_message = await agent.format_response(
            execution_plan,
            tool_results, 
            request.message,
            trace_id
        )
        
        # Update LangFuse trace with final output
        langfuse_client.update_trace(trace_id, response_message, {
            "success": True,
            "strategy": execution_plan.get("strategy"),
            "knowledge_results_count": len(execution_plan.get("knowledge_results", [])),
            "tool_results_count": len(tool_results)
        })
        
        # Flush LangFuse data
        langfuse_client.flush()
        
        return {
            "message": response_message,
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "strategy": execution_plan.get("strategy"),
            "debug": {
                "tools_used": [tc["tool"] for tc in execution_plan.get("tool_calls", [])],
                "knowledge_results": len(execution_plan.get("knowledge_results", [])),
                "llm_provider": llm_config.provider,
                "query_type": execution_plan.get("query_type")
            }
        }
        
    except Exception as e:
        logger.error(f"Enhanced chat processing failed: {e}")
        langfuse_client.update_trace(trace_id, "", {"success": False, "error": str(e)})
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
        "query_types": [
            "transactional",
            "faq",
            "business_rule",
            "mixed"
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

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await agent.close()

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8002"))
    
    logger.info("🚀 Starting AI Mode Backend - Step 2 (RAG Integration)")
    logger.info(f"   Port: {port}")
    logger.info(f"   LLM Provider: {llm_config.provider}")
    logger.info(f"   LLM Info: {llm_config.get_info()}")
    logger.info("   Features: Enhanced AI agent with RAG capabilities")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )