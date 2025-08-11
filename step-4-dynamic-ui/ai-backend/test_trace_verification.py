#!/usr/bin/env python3
"""
Test script to verify traces are being created with @observe decorators
"""
import os
import sys
import asyncio
import uuid
from datetime import datetime

# Add paths
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load environment
from dotenv import load_dotenv
env_file = os.path.join(os.path.dirname(__file__), '.env.langfuse')
if os.path.exists(env_file):
    load_dotenv(env_file)

# Test trace creation with our decorator system
from shared.observability.langfuse_decorator import (
    trace_conversation, trace_agent_operation, trace_tool_execution,
    trace_rag_operation, flush_observations
)

print("🧪 Testing LangFuse @observe decorators...")

@trace_conversation(name="test_conversation", user_id="test-user", session_id="test-session")
async def test_conversation():
    print("📋 Starting test conversation")
    
    # Test agent operation
    result1 = await test_agent_operation("Test user query")
    
    # Test tool execution
    result2 = await test_tool_call("search_products", {"query": "iPhone"})
    
    # Test RAG operation  
    result3 = await test_rag_search("business_rules", "pricing policy")
    
    return {
        "message": "Test conversation completed successfully",
        "trace_id": str(uuid.uuid4()),
        "results": [result1, result2, result3],
        "timestamp": datetime.now().isoformat()
    }

@trace_agent_operation("query_classification", "span")
async def test_agent_operation(query: str):
    print(f"🤖 Agent processing: {query}")
    await asyncio.sleep(0.1)  # Simulate processing
    return {"decision": "product_search", "confidence": 0.95}

@trace_tool_execution("search_products")
async def test_tool_call(tool_name: str, params: dict):
    print(f"🔧 Tool execution: {tool_name} with {params}")
    await asyncio.sleep(0.2)  # Simulate tool call
    return {"count": 6, "results": ["iPhone 15", "iPhone 14", "iPhone 13"]}

@trace_rag_operation("business_rules")  
async def test_rag_search(collection: str, query: str):
    print(f"🔍 RAG search in {collection}: {query}")
    await asyncio.sleep(0.1)  # Simulate vector search
    return {"results": 3, "top_match": "Premium pricing applies to Pro models"}

async def main():
    print("🚀 Running comprehensive trace test...")
    
    try:
        # Run the test conversation
        result = await test_conversation()
        print(f"✅ Test completed: {result['message']}")
        print(f"📍 Trace ID: {result['trace_id']}")
        
        # Flush observations
        flush_observations()
        print("✅ Flushed observations")
        
        print("\n🎉 All traces should be visible in LangFuse:")
        print("   - Main conversation trace")
        print("   - Query classification span")  
        print("   - Tool execution spans")
        print("   - RAG operation spans")
        print(f"\n🌐 View at: http://localhost:3001/project/traces")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())