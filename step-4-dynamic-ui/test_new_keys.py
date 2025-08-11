#!/usr/bin/env python3
"""
Test the new LangFuse API keys to verify traces are sent and visible
"""
import os
from dotenv import load_dotenv

# Load the new environment variables
load_dotenv('.env')

from langfuse import Langfuse, observe
import time

# Initialize with your new keys
langfuse = Langfuse(
    secret_key="sk-lf-9720fd8e-1370-4b4d-adcf-3c83f637ad84",
    public_key="pk-lf-862b860f-83d4-4537-96c1-0cfba9ce0748", 
    host="http://localhost:3001"
)

@observe()
def step4_agent_conversation(user_query: str):
    """Main AI conversation with all components traced"""
    print(f"🎭 Processing: {user_query}")
    
    # Query classification
    classification = classify_user_intent(user_query)
    
    # Tool execution based on classification  
    if "product" in user_query.lower():
        products = execute_product_search("iPhone", {"category": "mobile"})
        
    if "customer" in user_query.lower():
        customer = lookup_customer("john.doe@email.com")
        
    # RAG knowledge search
    if "policy" in user_query.lower():
        policy = search_knowledge_base("return policy")
    
    # Generate final response
    response = generate_ai_response(user_query, classification)
    
    return {
        "message": response,
        "trace_complete": True,
        "components_traced": ["classification", "tools", "rag", "generation"]
    }

@observe()
def classify_user_intent(query: str):
    """Agent query classification"""
    print(f"  🤖 Classifying query...")
    time.sleep(0.1)
    return {"intent": "product_search_with_customer", "confidence": 0.95}

@observe()  
def execute_product_search(search_term: str, filters: dict):
    """MCP tool execution"""
    print(f"  🔧 Searching products: {search_term}")
    time.sleep(0.2)
    return {
        "count": 6,
        "products": [
            {"id": "1", "name": "iPhone 15 Pro", "price": 999},
            {"id": "2", "name": "iPhone 15", "price": 799}
        ]
    }

@observe()
def lookup_customer(email: str):
    """Customer lookup tool"""
    print(f"  👤 Looking up customer: {email}")
    time.sleep(0.1)
    return {"found": False, "message": "Customer not found"}

@observe()
def search_knowledge_base(topic: str):
    """RAG knowledge search"""
    print(f"  📚 Searching knowledge: {topic}")
    time.sleep(0.15)
    return {
        "results": 3,
        "top_result": "30-day return policy applies to all products"
    }

@observe()
def generate_ai_response(query: str, classification: dict):
    """LLM response generation"""
    print(f"  💬 Generating response...")
    time.sleep(0.3)
    return "I found 6 iPhone products for you. Unfortunately, I couldn't find the customer email in our system."

def main():
    print("🧪 TESTING NEW LANGFUSE KEYS")
    print("=" * 40)
    
    # Test authentication first
    try:
        langfuse.auth_check()
        print("✅ Authentication successful!")
    except Exception as e:
        print(f"❌ Auth failed: {e}")
        return
    
    # Run the full traced conversation
    test_query = "Find iPhone products for customer john.doe@email.com and check return policy"
    print(f"\n📋 Test Query: {test_query}")
    
    print(f"\n🚀 Executing traced workflow...")
    result = step4_agent_conversation(test_query)
    
    print(f"\n✅ Conversation completed!")
    print(f"Response: {result['message']}")
    print(f"Traced Components: {result['components_traced']}")
    
    # Flush to ensure all traces are sent
    print(f"\n📤 Flushing traces to LangFuse...")
    langfuse.flush()
    
    print(f"\n🎉 ALL TRACES SENT TO LANGFUSE!")
    print(f"🌐 View your traces at: http://localhost:3001")
    print(f"   Look for traces with these names:")
    print(f"   - step4_agent_conversation (main trace)")
    print(f"   - classify_user_intent")
    print(f"   - execute_product_search") 
    print(f"   - lookup_customer")
    print(f"   - search_knowledge_base")
    print(f"   - generate_ai_response")

if __name__ == "__main__":
    main()