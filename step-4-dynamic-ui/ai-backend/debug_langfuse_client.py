#!/usr/bin/env python3
"""
Debug the LangFuse client to see what methods are available
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from shared.observability.langfuse_client import langfuse_client

def debug_langfuse_client():
    """Debug LangFuse client methods and state"""
    
    print("🔍 Debugging LangFuse Client")
    print("=" * 50)
    
    print(f"Client enabled: {langfuse_client.enabled}")
    print(f"Client object: {langfuse_client.client}")
    print(f"Session ID: {langfuse_client.session_id}")
    
    if langfuse_client.client:
        print("\n📋 Available client methods:")
        methods = [method for method in dir(langfuse_client.client) if not method.startswith('_')]
        for method in sorted(methods):
            print(f"  • {method}")
        
        # Test trace creation
        print("\n🧪 Testing trace creation...")
        try:
            trace_id = langfuse_client.create_trace(
                user_message="Debug test",
                session_id="debug_session"
            )
            print(f"✅ Trace created: {trace_id}")
            
            # Test if we can access the trace
            if hasattr(langfuse_client.client, 'trace'):
                print("✅ Client has 'trace' method")
            
            if hasattr(langfuse_client.client, 'span'):
                print("✅ Client has 'span' method")
            
            # Try different span creation approaches
            print("\n🔧 Testing span creation methods...")
            
            # Method 1: Direct span call
            try:
                if hasattr(langfuse_client.client, 'span'):
                    span_result = langfuse_client.client.span(
                        trace_id=trace_id,
                        name="debug_span",
                        input="test input",
                        output="test output"
                    )
                    print(f"✅ Direct span creation: {span_result}")
            except Exception as e:
                print(f"❌ Direct span failed: {e}")
            
            # Method 2: Check if we need to use trace object
            try:
                if hasattr(langfuse_client.client, 'trace') and trace_id:
                    # Try to get the trace object
                    trace_obj = getattr(langfuse_client.client, f"_traces", {}).get(trace_id)
                    print(f"Trace object: {trace_obj}")
            except Exception as e:
                print(f"❌ Trace object access failed: {e}")
            
            # Complete the trace
            langfuse_client.log_conversation_end(
                trace_id=trace_id,
                response="Debug test completed",
                response_type="debug",
                total_execution_time=0.1,
                components_summary={"debug": True},
                metadata={"test": True}
            )
            
            langfuse_client.flush()
            print("✅ Debug trace completed and flushed")
            
        except Exception as e:
            print(f"❌ Trace creation failed: {e}")
            import traceback
            traceback.print_exc()
    
    else:
        print("❌ No LangFuse client available")

if __name__ == "__main__":
    debug_langfuse_client()