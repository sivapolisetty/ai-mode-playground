#!/usr/bin/env python3
"""
Simple test script to verify LangFuse connection and create a test trace
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
env_file = os.path.join(os.path.dirname(__file__), '.env.langfuse')
if os.path.exists(env_file):
    load_dotenv(env_file)
    print(f"✅ Loaded environment from {env_file}")
else:
    print(f"❌ Environment file not found: {env_file}")

# Add path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from langfuse import Langfuse
    print("✅ LangFuse imported successfully")
    
    # Check environment variables
    host = os.getenv('LANGFUSE_HOST')
    public_key = os.getenv('LANGFUSE_PUBLIC_KEY')
    secret_key = os.getenv('LANGFUSE_SECRET_KEY')
    
    print(f"📋 Configuration:")
    print(f"   Host: {host}")
    print(f"   Public Key: {public_key[:10]}...{public_key[-4:] if public_key else None}")
    print(f"   Secret Key: {secret_key[:10]}...{secret_key[-4:] if secret_key else None}")
    
    if not all([host, public_key, secret_key]):
        print("❌ Missing configuration")
        sys.exit(1)
    
    # Initialize client
    client = Langfuse(
        host=host,
        public_key=public_key,
        secret_key=secret_key
    )
    print("✅ LangFuse client created")
    
    # Test connection
    try:
        client.auth_check()
        print("✅ Authentication successful")
        
        # Create a test trace
        trace_id = "test-trace-001"
        trace = client.trace(
            id=trace_id,
            name="test_connection",
            input="Test message",
            metadata={"test": True}
        )
        print(f"✅ Test trace created: {trace_id}")
        
        # Create a test span
        span = client.span(
            id="test-span-001",
            trace_id=trace_id,
            name="test_operation",
            input="Test operation",
            output="Success"
        )
        print("✅ Test span created")
        
        # Flush to make sure data is sent
        client.flush()
        print("✅ Data flushed to LangFuse")
        
        print(f"\n🎉 LangFuse connection test successful!")
        print(f"   View traces at: {host}/project/traces")
        
    except Exception as auth_error:
        print(f"❌ Authentication failed: {auth_error}")
        sys.exit(1)
        
except ImportError as e:
    print(f"❌ LangFuse not available: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)