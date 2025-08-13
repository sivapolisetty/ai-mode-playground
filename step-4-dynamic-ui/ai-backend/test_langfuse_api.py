#!/usr/bin/env python3
"""
Test LangFuse API to understand proper span creation
"""

import asyncio
import sys
import os
import time
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from shared.observability.langfuse_client import langfuse_client

async def test_langfuse_api():
    """Test the correct LangFuse API for creating traces and spans"""
    
    print("🔍 Testing LangFuse API Structure")
    print("=" * 50)
    
    try:
        # Step 1: Create a trace like the server does
        print("1️⃣ Creating main trace...")
        trace_id = langfuse_client.create_trace(
            user_message="Test API structure",
            session_id="api_test_session",
            metadata={"test": "api_structure"}
        )
        
        if not trace_id:
            print("❌ Failed to create trace")
            return
            
        print(f"✅ Created trace: {trace_id}")
        
        # Step 2: Test different span creation approaches
        print("\n2️⃣ Testing span creation approaches...")
        
        # Approach 1: Direct client.span() call
        try:
            print("   Testing direct client.span()...")
            start_time = time.time()
            
            span_result = langfuse_client.client.span(
                trace_id=trace_id,
                name="test_direct_span",
                input={"method": "direct", "test": True},
                output={"result": "direct span test"},
                metadata={
                    "approach": "direct_client_span",
                    "execution_time_ms": 50
                },
                start_time=start_time,
                end_time=time.time()
            )
            
            print(f"   ✅ Direct span result: {type(span_result)}")
            if hasattr(span_result, 'id'):
                print(f"   📊 Span ID: {span_result.id}")
            
        except Exception as e:
            print(f"   ❌ Direct span failed: {e}")
        
        # Approach 2: Using langfuse_client methods
        try:
            print("   Testing langfuse_client.log_tool_execution()...")
            
            langfuse_client.log_tool_execution(
                trace_id=trace_id,
                tool_name="test_tool",
                input_data={"query": "test", "params": {"limit": 5}},
                output_data={"results": [{"id": 1, "name": "test"}], "count": 1},
                success=True,
                execution_time=0.1,
                metadata={"approach": "log_tool_execution"}
            )
            
            print("   ✅ Tool execution logged")
            
        except Exception as e:
            print(f"   ❌ Tool execution logging failed: {e}")
        
        # Approach 3: Test agent operation logging
        try:
            print("   Testing langfuse_client.log_agent_decision()...")
            
            langfuse_client.log_agent_decision(
                trace_id=trace_id,
                query_type="product_search",
                confidence=0.95,
                reasoning="User query contains product terms",
                metadata={"approach": "log_agent_decision"}
            )
            
            print("   ✅ Agent decision logged")
            
        except Exception as e:
            print(f"   ❌ Agent decision logging failed: {e}")
        
        # Approach 4: Test UI generation logging
        try:
            print("   Testing langfuse_client.log_ui_generation()...")
            
            langfuse_client.log_ui_generation(
                trace_id=trace_id,
                user_intent="test UI generation",
                ui_components=[{"type": "card", "props": {"title": "Test"}}],
                layout_strategy="test_layout",
                generation_success=True,
                validation_results={"valid": True},
                metadata={"approach": "log_ui_generation"}
            )
            
            print("   ✅ UI generation logged")
            
        except Exception as e:
            print(f"   ❌ UI generation logging failed: {e}")
        
        # Step 3: Test different span timing approaches
        print("\n3️⃣ Testing span timing...")
        
        try:
            start_time = time.time()
            await asyncio.sleep(0.1)  # Simulate work
            end_time = time.time()
            
            span_result = langfuse_client.client.span(
                trace_id=trace_id,
                name="test_timing_span",
                input={"timing": "test"},
                output={"duration": end_time - start_time},
                start_time=start_time,
                end_time=end_time
            )
            
            print(f"   ✅ Timing span created: {type(span_result)}")
            
        except Exception as e:
            print(f"   ❌ Timing span failed: {e}")
        
        # Step 4: Complete the trace
        print("\n4️⃣ Completing trace...")
        
        langfuse_client.log_conversation_end(
            trace_id=trace_id,
            response="API test completed successfully",
            response_type="test",
            total_execution_time=1.0,
            components_summary={
                "spans_created": 4,
                "approaches_tested": ["direct", "tool_execution", "agent_decision", "ui_generation"]
            },
            metadata={"test_completed": True}
        )
        
        # Flush data
        langfuse_client.flush()
        
        print("✅ Test completed successfully!")
        print(f"🔍 Check LangFuse dashboard for trace: {trace_id}")
        print("   This trace should show multiple spans with different approaches")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_langfuse_api())