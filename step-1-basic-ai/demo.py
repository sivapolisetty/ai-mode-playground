#!/usr/bin/env python3
"""
Demo script for Step 1: Basic AI Mode
Tests the simplified AI backend with various queries
"""
import asyncio
import json
import httpx
from datetime import datetime

class Step1Demo:
    """Demo class for testing Step 1 implementation"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session_id = f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    async def test_chat(self, message: str, context: dict = None):
        """Test chat endpoint"""
        if context is None:
            context = {}
        
        context["session_id"] = self.session_id
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat",
                    json={"message": message, "context": context},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"error": f"HTTP {response.status_code}: {response.text}"}
            except Exception as e:
                return {"error": str(e)}
    
    async def test_health(self):
        """Test health endpoint"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/health")
                return response.json()
            except Exception as e:
                return {"error": str(e)}
    
    async def test_tools(self):
        """Test tools endpoint"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/tools")
                return response.json()
            except Exception as e:
                return {"error": str(e)}
    
    def print_response(self, title: str, response: dict):
        """Pretty print response"""
        print(f"\n{'='*50}")
        print(f"🔍 {title}")
        print(f"{'='*50}")
        
        if "error" in response:
            print(f"❌ Error: {response['error']}")
            return
        
        if "message" in response:
            print(f"🤖 AI Response: {response['message']}")
        
        if "debug" in response:
            debug = response["debug"]
            print(f"🔧 Tools Used: {debug.get('tools_used', [])}")
            print(f"🧠 LLM Provider: {debug.get('llm_provider', 'unknown')}")
        
        if "timestamp" in response:
            print(f"⏰ Timestamp: {response['timestamp']}")
        
        print(f"{'='*50}")
    
    async def run_demo(self):
        """Run complete demo"""
        print("🚀 Starting Step 1: Basic AI Mode Demo")
        print(f"📡 Backend URL: {self.base_url}")
        print(f"🆔 Session ID: {self.session_id}")
        
        # Test health
        print("\n🔍 Testing Health Check...")
        health = await self.test_health()
        if "error" not in health:
            print(f"✅ Server is healthy")
            print(f"🧠 LLM Provider: {health.get('llm_provider', 'unknown')}")
        else:
            print(f"❌ Health check failed: {health['error']}")
            return
        
        # Test tools
        print("\n🔍 Testing Available Tools...")
        tools = await self.test_tools()
        if "error" not in tools:
            print(f"✅ Found {len(tools.get('tools', []))} available tools")
            for tool in tools.get('tools', []):
                print(f"   • {tool['name']}: {tool['description']}")
        else:
            print(f"❌ Tools check failed: {tools['error']}")
        
        # Demo queries
        demo_queries = [
            {
                "title": "Product Search",
                "message": "Show me iPhone products under $1000",
                "context": {}
            },
            {
                "title": "Browse All Products",
                "message": "What products do you have?",
                "context": {}
            },
            {
                "title": "Customer Information",
                "message": "Show me all customers",
                "context": {}
            },
            {
                "title": "Customer Orders",
                "message": "What are my recent orders?",
                "context": {"customerId": "CUST-001"}
            },
            {
                "title": "Product Categories",
                "message": "What categories do you have?",
                "context": {}
            },
            {
                "title": "Specific Product Search",
                "message": "Find me MacBook Pro laptops",
                "context": {}
            },
            {
                "title": "Price Query",
                "message": "What's the price of iPhone 15 Pro?",
                "context": {}
            }
        ]
        
        print("\n🎯 Running Demo Queries...")
        
        for query in demo_queries:
            print(f"\n📝 Query: {query['message']}")
            if query['context']:
                print(f"🔄 Context: {query['context']}")
            
            response = await self.test_chat(query["message"], query["context"])
            self.print_response(query["title"], response)
            
            # Small delay between queries
            await asyncio.sleep(1)
        
        print("\n✅ Demo completed!")
        print("\nTo test manually, try:")
        print(f"curl -X POST {self.base_url}/chat \\")
        print('  -H "Content-Type: application/json" \\')
        print('  -d \'{"message": "Show me all products"}\'')

async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Step 1 AI Mode Demo")
    parser.add_argument("--url", default="http://localhost:8001", help="Backend URL")
    parser.add_argument("--query", help="Single query to test")
    parser.add_argument("--customer", help="Customer ID for context")
    
    args = parser.parse_args()
    
    demo = Step1Demo(args.url)
    
    if args.query:
        # Single query mode
        context = {}
        if args.customer:
            context["customerId"] = args.customer
        
        print(f"🔍 Testing single query: {args.query}")
        response = await demo.test_chat(args.query, context)
        demo.print_response("Single Query Test", response)
    else:
        # Full demo mode
        await demo.run_demo()

if __name__ == "__main__":
    asyncio.run(main())