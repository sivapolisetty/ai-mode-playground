#!/usr/bin/env python3
"""
Test direct usage of LangFuse observe decorator to verify traces are sent
"""
import os
import time
from dotenv import load_dotenv

# Load environment from .env file
load_dotenv()

# Set environment variables if not already set
os.environ.setdefault('LANGFUSE_HOST', 'http://localhost:3001')
os.environ.setdefault('LANGFUSE_PUBLIC_KEY', 'pk-lf-5f319c65-bd95-474f-ae5f-3f126c1e6447')
os.environ.setdefault('LANGFUSE_SECRET_KEY', 'sk-lf-2250eaa2-4ea1-447a-a55a-0f272092579d')

print("Environment variables set:")
print(f"  LANGFUSE_HOST: {os.environ.get('LANGFUSE_HOST')}")
print(f"  LANGFUSE_PUBLIC_KEY: {os.environ.get('LANGFUSE_PUBLIC_KEY')[:20]}...")
print(f"  LANGFUSE_SECRET_KEY: {os.environ.get('LANGFUSE_SECRET_KEY')[:20]}...")

from langfuse import observe, Langfuse

# Initialize client to verify connection
langfuse = Langfuse()

@observe()
def step4_agent_workflow(user_query: str):
    """Main conversation flow with nested operations"""
    print(f"🎭 Processing: {user_query}")
    
    # Simulate query classification
    query_type = classify_query(user_query)
    
    # Simulate tool execution
    if "product" in user_query.lower():
        products = search_products("iPhone")
    
    # Simulate RAG search
    if "policy" in user_query.lower():
        policy = search_knowledge("return policy")
    
    # Generate response
    response = generate_response(user_query)
    
    return {
        "message": response,
        "query_type": query_type,
        "tools_used": ["search_products", "search_knowledge"]
    }

@observe()
def classify_query(query: str):
    """Classify the user query"""
    print(f"  🤖 Classifying query...")
    time.sleep(0.1)  # Simulate processing
    return "product_search"

@observe()
def search_products(search_term: str):
    """Execute product search tool"""
    print(f"  🔧 Searching products: {search_term}")
    time.sleep(0.2)  # Simulate API call
    return [
        {"id": "1", "name": "iPhone 15 Pro", "price": 999},
        {"id": "2", "name": "iPhone 15", "price": 799}
    ]

@observe()
def search_knowledge(topic: str):
    """Search knowledge base"""
    print(f"  📚 Searching knowledge: {topic}")
    time.sleep(0.1)  # Simulate vector search
    return "30-day return policy for all products"

@observe()
def generate_response(query: str):
    """Generate AI response"""
    print(f"  💬 Generating response...")
    time.sleep(0.3)  # Simulate LLM call
    return "I found 2 iPhone products for you. The iPhone 15 Pro is $999 and the iPhone 15 is $799."

if __name__ == "__main__":
    print("\n🚀 Testing Direct LangFuse @observe Integration")
    print("=" * 50)
    
    # Test query
    test_query = "Show me iPhone products and what's your return policy?"
    print(f"Query: {test_query}\n")
    
    # Execute the workflow
    result = step4_agent_workflow(test_query)
    
    print(f"\n✅ Workflow completed!")
    print(f"Response: {result['message']}")
    print(f"Query Type: {result['query_type']}")
    print(f"Tools Used: {result['tools_used']}")
    
    # Flush to ensure traces are sent
    print("\n📤 Flushing traces to LangFuse...")
    langfuse.flush()
    
    print("✅ Traces flushed!")
    print(f"\n🌐 View traces at: http://localhost:3001")
    print("   Look for traces with names:")
    print("   - step4_agent_workflow")
    print("   - classify_query")
    print("   - search_products")
    print("   - search_knowledge")
    print("   - generate_response")