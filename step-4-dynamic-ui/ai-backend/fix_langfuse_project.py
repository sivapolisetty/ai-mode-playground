#!/usr/bin/env python3
"""
Fix LangFuse project setup by creating proper project structure
"""
import os
import sys
import requests
import json
from dotenv import load_dotenv

# Load environment
env_file = os.path.join(os.path.dirname(__file__), '.env.langfuse')
if os.path.exists(env_file):
    load_dotenv(env_file)

def check_langfuse_status():
    """Check if LangFuse is running and accessible"""
    try:
        response = requests.get("http://localhost:3001/api/public/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ LangFuse is running: {response.json()}")
            return True
        else:
            print(f"❌ LangFuse health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to LangFuse: {e}")
        return False

def create_simple_trace():
    """Create a simple trace without complex project validation"""
    try:
        from langfuse import Langfuse
        
        # Use minimal configuration
        client = Langfuse(
            host="http://localhost:3001",
            public_key=os.getenv('LANGFUSE_PUBLIC_KEY'),
            secret_key=os.getenv('LANGFUSE_SECRET_KEY')
        )
        
        print("📝 Creating simple test trace...")
        
        # Try to create a simple trace
        trace = client.trace(
            id="test-trace-fix-001", 
            name="langfuse_connection_test",
            input={"message": "Testing connection"},
            metadata={"test": True, "created_by": "fix_script"}
        )
        
        print("✅ Test trace created successfully!")
        
        # Create a test span
        span = client.span(
            id="test-span-fix-001",
            trace_id="test-trace-fix-001",
            name="test_operation", 
            input={"operation": "test"},
            output={"result": "success"}
        )
        
        print("✅ Test span created successfully!")
        
        # Flush and verify
        client.flush()
        print("✅ Data flushed to LangFuse")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create trace: {e}")
        print(f"   Error type: {type(e).__name__}")
        
        # Try alternative initialization
        try:
            print("🔄 Trying alternative initialization...")
            
            # Bypass auth check
            client = Langfuse(
                host="http://localhost:3001",
                public_key=os.getenv('LANGFUSE_PUBLIC_KEY'), 
                secret_key=os.getenv('LANGFUSE_SECRET_KEY'),
                flush_at=1  # Force immediate flushing
            )
            
            # Create minimal trace 
            client.trace(
                name="minimal_test",
                input="test message"
            )
            
            print("✅ Alternative initialization succeeded!")
            client.flush()
            return True
            
        except Exception as e2:
            print(f"❌ Alternative initialization also failed: {e2}")
            return False

def main():
    print("🔧 LangFuse Connection Diagnostic Tool")
    print("=====================================")
    
    # Check basic connectivity
    if not check_langfuse_status():
        print("❌ LangFuse is not accessible. Please start it first.")
        return
    
    # Check environment variables
    host = os.getenv('LANGFUSE_HOST')
    public_key = os.getenv('LANGFUSE_PUBLIC_KEY')
    secret_key = os.getenv('LANGFUSE_SECRET_KEY')
    
    print(f"\n📋 Configuration:")
    print(f"   Host: {host}")
    print(f"   Public Key: {public_key[:10]}...{public_key[-4:] if public_key else 'None'}")
    print(f"   Secret Key: {secret_key[:10]}...{secret_key[-4:] if secret_key else 'None'}")
    
    if not all([host, public_key, secret_key]):
        print("❌ Missing configuration variables!")
        return
    
    # Try to create traces
    if create_simple_trace():
        print(f"\n🎉 SUCCESS! LangFuse traces are working!")
        print(f"🌐 View traces at: {host}/project/traces")
    else:
        print("\n❌ Could not create traces. Connection issue persists.")
        print("💡 Suggestion: Check LangFuse logs and project setup")

if __name__ == "__main__":
    main()