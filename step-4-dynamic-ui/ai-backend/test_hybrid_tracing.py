#!/usr/bin/env python3
"""
Test hybrid LangFuse tracing approach
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from shared.observability.langfuse_client import langfuse_client
from shared.observability.hybrid_tracing import langfuse_trace

@langfuse_trace(name="test_hybrid_function")
async def test_hybrid_function(message: str, trace_id: str = None):
    """Test function with hybrid tracing"""
    print(f"Processing with trace_id: {trace_id}")
    await asyncio.sleep(0.1)
    return {"result": f"Processed: {message}", "success": True}

@langfuse_trace(name="nested_hybrid_function")  
async def nested_hybrid_function(data, trace_id: str = None):
    """Nested function to test hierarchy"""
    print(f"Nested processing with trace_id: {trace_id}")
    await asyncio.sleep(0.05)
    return {"nested_result": "done"}

async def main():
    """Test hybrid tracing"""
    print("Testing hybrid LangFuse tracing...")
    
    try:
        # Create a manual trace like the server does
        trace_id = langfuse_client.create_trace(
            user_message="Test hybrid tracing",
            session_id="test_session",
            metadata={"test": True}
        )
        
        if trace_id:
            print(f"✅ Created trace: {trace_id}")
            
            # Call functions with trace_id - they should create spans
            result1 = await test_hybrid_function("Hello Hybrid", trace_id=trace_id)
            print(f"Result 1: {result1}")
            
            result2 = await nested_hybrid_function(result1, trace_id=trace_id)
            print(f"Result 2: {result2}")
            
            # Complete the trace
            langfuse_client.log_conversation_end(
                trace_id=trace_id,
                response="Test completed successfully",
                response_type="test",
                total_execution_time=0.2,
                components_summary={"test_functions": 2},
                metadata={"success": True}
            )
            
            # Flush to ensure data is sent
            langfuse_client.flush()
            
            print("✅ Hybrid tracing test completed!")
            print(f"Check LangFuse dashboard for trace: {trace_id}")
            
        else:
            print("❌ Failed to create trace")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())