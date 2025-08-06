#!/usr/bin/env python3
"""
Test script to debug intelligent processing issues
"""
import asyncio
import sys
import os

# Add the ai-backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-backend'))

async def test_intelligent_processing():
    try:
        print("🔍 Testing intelligent processing components...")
        
        # Test 1: Import intent classifier
        print("\n1. Testing IntentClassifier import...")
        from src.intent_classifier import IntentClassifier
        print("✅ IntentClassifier imported successfully")
        
        # Test 2: Import context resolver
        print("\n2. Testing ContextResolver import...")
        from src.context_resolver import ContextResolver
        print("✅ ContextResolver imported successfully")
        
        # Test 3: Test LLM initialization
        print("\n3. Testing LLM initialization...")
        from config.llm_config import LLMConfig
        llm_config = LLMConfig()
        llm = llm_config.get_llm()
        print(f"✅ LLM initialized: {type(llm)}")
        
        # Test 4: Test MCP Tools
        print("\n4. Testing MCP Tools...")
        from tools.mcp_tools import MCPTools
        mcp_tools = MCPTools()
        print("✅ MCP Tools initialized")
        
        # Test 5: Initialize intent classifier with LLM
        print("\n5. Testing IntentClassifier with LLM...")
        intent_classifier = IntentClassifier(llm)
        print("✅ IntentClassifier created with LLM")
        
        # Test 6: Initialize context resolver with MCP tools
        print("\n6. Testing ContextResolver with MCP Tools...")
        context_resolver = ContextResolver(mcp_tools)
        print("✅ ContextResolver created with MCP Tools")
        
        # Test 7: Test intent classification
        print("\n7. Testing intent classification...")
        test_query = "I want to change the address of my last order"
        test_context = {"customer_id": "CUST-001", "session_id": "test"}
        
        intent = await intent_classifier.classify_intent(test_query, test_context)
        print(f"✅ Intent classification successful:")
        print(f"   Intent Type: {intent.get('intent_type')}")
        print(f"   Action: {intent.get('action')}")
        print(f"   Target Entity: {intent.get('target_entity')}")
        print(f"   Confidence: {intent.get('confidence')}")
        
        # Test 8: Test context resolution
        print("\n8. Testing context resolution...")
        resolved = await context_resolver.resolve_references(intent, test_context)
        print(f"✅ Context resolution status: {resolved.get('resolution_status')}")
        if resolved.get('resolution_errors'):
            print(f"   Errors: {resolved['resolution_errors']}")
        
        print("\n🎉 All intelligent processing components working!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error in intelligent processing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_intelligent_processing())
    if success:
        print("\n✅ Intelligent processing is ready!")
    else:
        print("\n❌ Intelligent processing has issues that need fixing.")