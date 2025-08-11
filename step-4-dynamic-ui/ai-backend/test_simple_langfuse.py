#!/usr/bin/env python3
"""
Simple LangFuse test to create traces using the @observe decorator approach
"""
import os
import sys
import uuid
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
env_file = os.path.join(os.path.dirname(__file__), '.env.langfuse')
if os.path.exists(env_file):
    load_dotenv(env_file)

# Add path for imports  
sys.path.append(os.path.dirname(__file__))

try:
    from langfuse import observe
    print("✅ LangFuse observe decorator imported successfully")
    
    @observe(name="test_function", as_type="span")
    def test_function(message: str):
        """Simple test function with tracing"""
        print(f"Processing: {message}")
        return f"Processed: {message}"
    
    @observe(name="test_conversation", as_type="trace")  
    def test_conversation():
        """Test conversation with nested operations"""
        print("Starting test conversation...")
        
        result1 = test_function("Hello LangFuse")
        result2 = test_function("Testing traces")
        
        return {
            "message": "Test conversation completed",
            "results": [result1, result2],
            "timestamp": datetime.now().isoformat(),
            "trace_id": str(uuid.uuid4())
        }
    
    if __name__ == "__main__":
        print("🚀 Running LangFuse @observe decorator test...")
        
        # Run the test
        result = test_conversation()
        print(f"✅ Test completed: {result}")
        
        # Try to flush any pending observations
        try:
            from langfuse import Langfuse
            client = Langfuse()
            client.flush()
            print("✅ Flushed observations to LangFuse")
        except Exception as e:
            print(f"⚠️  Could not flush to LangFuse: {e}")
        
        print(f"🎉 Decorator test successful! Check traces at: http://localhost:3001")
        
except ImportError as e:
    print(f"❌ Could not import LangFuse decorators: {e}")
except Exception as e:
    print(f"❌ Error during test: {e}")