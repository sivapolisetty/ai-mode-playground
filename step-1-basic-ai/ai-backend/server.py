"""
Step 1: Basic AI Mode Server
Simple FastAPI server with LangChain orchestration
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

from src.simple_agent import SimpleAgent
from config.llm_config import LLMConfig
from shared.observability.langfuse_client import langfuse_client

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize components
llm_config = LLMConfig()
agent = SimpleAgent(os.getenv("TRADITIONAL_API_URL", "http://localhost:4000"))

# FastAPI app
app = FastAPI(
    title="AI Mode Backend - Step 1",
    description="Basic AI mode with simple LangChain orchestration",
    version="1.0.0"
)

# CORS middleware - Permissive for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class ChatRequest(BaseModel):
    message: str
    context: Dict[str, Any] = {}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Mode Backend - Step 1",
        "version": "1.0.0",
        "llm_info": llm_config.get_info()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "llm_provider": llm_config.provider,
        "version": "1.0.0"
    }

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint with LangFuse observability"""
    session_id = request.context.get("session_id", f"session_{int(time.time())}")
    
    # Create LangFuse trace
    trace_id = langfuse_client.create_trace(
        session_id=session_id,
        user_input=request.message,
        metadata=request.context
    )
    
    try:
        logger.info(f"Chat request: {request.message}")
        
        # Process query with agent
        plan = await agent.process_query(request.message, request.context, trace_id)
        
        # Execute tools
        tool_results = await agent.execute_tools(plan.get("tool_calls", []), session_id, trace_id)
        
        # Format response
        response_message = await agent.format_response(
            tool_results, 
            request.message, 
            plan.get("response_strategy", "Provide helpful information"),
            trace_id
        )
        
        # Update LangFuse trace with final output
        langfuse_client.update_trace(trace_id, response_message, {"success": True})
        
        # Flush LangFuse data to ensure it's sent
        langfuse_client.flush()
        
        return {
            "message": response_message,
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "debug": {
                "tools_used": [tc["tool"] for tc in plan.get("tool_calls", [])],
                "llm_provider": llm_config.provider
            }
        }
        
    except Exception as e:
        logger.error(f"Chat processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools")
async def get_available_tools():
    """Get available tools"""
    return {
        "tools": [
            {
                "name": "search_products",
                "description": "Search for products by name, description, or brand",
                "parameters": {"query": "string"}
            },
            {
                "name": "get_products", 
                "description": "Get all products with optional filters",
                "parameters": {"category_id": "int (optional)", "brand": "string (optional)"}
            },
            {
                "name": "get_customers",
                "description": "Get all customers",
                "parameters": {}
            },
            {
                "name": "get_customer_orders",
                "description": "Get orders for a specific customer",
                "parameters": {"customer_id": "string"}
            },
            {
                "name": "create_order",
                "description": "Create a new order",
                "parameters": {
                    "customer_id": "string",
                    "product_id": "string",
                    "quantity": "int (optional)",
                    "shipping_address": "string (optional)",
                    "payment_method": "string (optional)"
                }
            },
            {
                "name": "get_categories",
                "description": "Get all product categories",
                "parameters": {}
            }
        ]
    }

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await agent.close()

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8001))
    
    logger.info("🚀 Starting AI Mode Backend - Step 1")
    logger.info(f"   Port: {port}")
    logger.info(f"   LLM Provider: {llm_config.provider}")
    logger.info(f"   LLM Info: {llm_config.get_info()}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )