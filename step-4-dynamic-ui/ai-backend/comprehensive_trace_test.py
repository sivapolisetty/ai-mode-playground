#!/usr/bin/env python3
"""
Comprehensive test to verify all agent and tool interactions are being traced
"""
import requests
import json
import time

def test_comprehensive_query():
    """Test a complex query that triggers all major components"""
    
    print("🧪 COMPREHENSIVE LANGFUSE TRACING TEST")
    print("=" * 50)
    
    # Complex query that should trigger multiple agents and tools
    test_query = {
        "message": "I need to find MacBook Pro for customer john.doe@email.com, check our return policy, and create an order",
        "context": {
            "session_id": "comprehensive-test-session",
            "user_id": "test-user-comprehensive"
        }
    }
    
    print(f"📋 Test Query: {test_query['message']}")
    print(f"📍 Session: {test_query['context']['session_id']}")
    
    try:
        print("\n🚀 Sending request to AI Backend...")
        start_time = time.time()
        
        response = requests.post(
            "http://localhost:8001/chat",
            headers={"Content-Type": "application/json"},
            json=test_query,
            timeout=120
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ REQUEST SUCCESSFUL ({execution_time:.2f}s)")
            print("\n📊 TRACE ANALYSIS:")
            print("=" * 30)
            
            # Extract key information
            trace_id = result.get("trace_id")
            tools_used = result.get("debug", {}).get("tools_used", [])
            processing_type = result.get("debug", {}).get("processing_type")
            response_type = result.get("response_type")
            
            print(f"🏷️  Trace ID: {trace_id}")
            print(f"🔧 Tools Used: {tools_used}")
            print(f"⚙️  Processing: {processing_type}")
            print(f"📝 Response Type: {response_type}")
            
            print(f"\n💬 AI Response: {result.get('message', '')[:200]}{'...' if len(result.get('message', '')) > 200 else ''}")
            
            # Analyze what should be traced
            print(f"\n🔍 EXPECTED TRACES IN LANGFUSE:")
            print("=" * 35)
            
            print("📍 Main Conversation Trace:")
            print(f"   - ID: {trace_id}")
            print(f"   - Name: step4_dynamic_ui_conversation")
            print(f"   - Session: {test_query['context']['session_id']}")
            
            print("\n🤖 Agent Operation Spans:")
            print(f"   - query_classification (routing strategy)")
            print(f"   - intelligent_orchestrator (tool planning)")
            
            print(f"\n🔧 Tool Execution Spans:")
            for tool in tools_used:
                print(f"   - {tool} (MCP tool call)")
            
            print(f"\n🔍 RAG Operation Spans (if knowledge queries):")
            print(f"   - search_faq (FAQ knowledge base)")
            print(f"   - search_business_rules (business rules)")
            
            print(f"\n🎨 UI Generation Spans (if UI components):")
            if result.get("ui_components"):
                print(f"   - ui_generation (dynamic component creation)")
                print(f"   - Components: {len(result.get('ui_components', []))} generated")
            else:
                print(f"   - No UI components generated for this query")
                
            print(f"\n🌐 View All Traces: http://localhost:3001/project/traces")
            print(f"🔗 Direct Link: http://localhost:3001/project/traces/{trace_id}")
            
            return True
            
        else:
            print(f"❌ REQUEST FAILED: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ REQUEST TIMED OUT (>120s)")
        return False
    except Exception as e:
        print(f"❌ REQUEST ERROR: {e}")
        return False

def check_langfuse_status():
    """Check if LangFuse is accessible"""
    try:
        response = requests.get("http://localhost:3001/api/public/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ LangFuse Status: {health}")
            return True
        else:
            print(f"❌ LangFuse not healthy: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ LangFuse not accessible: {e}")
        return False

def check_ai_backend():
    """Check if AI backend is running"""
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            print("✅ AI Backend is running")
            return True
        else:
            print(f"❌ AI Backend not healthy: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ AI Backend not accessible: {e}")
        return False

if __name__ == "__main__":
    print("🏥 Pre-flight Checks")
    print("=" * 20)
    
    langfuse_ok = check_langfuse_status()
    backend_ok = check_ai_backend()
    
    if not langfuse_ok:
        print("\n⚠️  LangFuse not accessible - traces may not be visible in dashboard")
        print("   But @observe decorators will still create traces locally")
    
    if not backend_ok:
        print("\n❌ AI Backend not running. Please start it first:")
        print("   source .env.langfuse && venv/bin/python ai-backend/server.py")
        exit(1)
    
    print(f"\n{'✅ All systems ready!' if langfuse_ok and backend_ok else '⚠️  Partial systems ready'}")
    
    # Run the comprehensive test
    success = test_comprehensive_query()
    
    if success:
        print(f"\n🎉 COMPREHENSIVE TRACE TEST COMPLETED!")
        print("   All agent and tool interactions should be visible in LangFuse")
    else:
        print(f"\n❌ Test failed - check system status")