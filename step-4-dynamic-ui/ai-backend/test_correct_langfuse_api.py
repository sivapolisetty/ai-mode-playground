#!/usr/bin/env python3
"""
Test correct LangFuse API usage with the most current approach
"""
import os
from dotenv import load_dotenv

# Load environment
env_file = os.path.join(os.path.dirname(__file__), '.env.langfuse')
if os.path.exists(env_file):
    load_dotenv(env_file)

try:
    from langfuse import Langfuse
    
    print("🔧 Testing correct LangFuse API...")
    
    # Initialize client
    client = Langfuse(
        public_key=os.getenv('LANGFUSE_PUBLIC_KEY'),
        secret_key=os.getenv('LANGFUSE_SECRET_KEY'),
        host="http://localhost:3001"
    )
    
    print(f"✅ Client created")
    print(f"Available methods: {[m for m in dir(client) if 'trace' in m.lower() or 'span' in m.lower()]}")
    
    # Test auth
    try:
        client.auth_check()
        print("✅ Authentication successful")
    except Exception as auth_error:
        print(f"⚠️ Auth check failed: {auth_error}")
        # Continue anyway - might still work
    
    # Try to create a trace using the correct API
    print("📝 Creating trace using create_event...")
    
    try:
        # Create an event (which can serve as a trace)
        event = client.create_event(
            name="test_trace_event",
            input="Test message for trace",
            metadata={"test": True}
        )
        print(f"✅ Event created: {event}")
        
        # Try to create a span
        span = client.start_span(
            name="test_span",
            input="Test span input"
        )
        print(f"✅ Span created: {span}")
        
        # Try to create a generation  
        generation = client.start_generation(
            name="test_generation",
            input="Test generation input"
        )
        print(f"✅ Generation created: {generation}")
        
        client.flush()
        print("✅ All data flushed to LangFuse")
        
    except Exception as e:
        print(f"❌ API call failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        
        # Show all available methods for debugging
        print(f"All methods: {[m for m in dir(client) if not m.startswith('_')]}")

except ImportError as e:
    print(f"❌ Cannot import LangFuse: {e}")
except Exception as e:
    print(f"❌ Error: {e}")