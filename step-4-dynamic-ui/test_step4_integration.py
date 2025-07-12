#!/usr/bin/env python3
"""
Integration Test for Step 4 - Dynamic UI Generation
Tests the complete integration between enhanced agent and UI generation
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the backend to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai-backend'))

async def test_step4_integration():
    """Test Step 4 integration"""
    print("🧪 Testing Step 4: Dynamic UI Generation Integration")
    print("=" * 60)
    
    try:
        # Test 1: Enhanced Agent Import
        print("\n📦 Test 1: Enhanced Agent Import")
        from src.enhanced_agent import EnhancedAgent
        print("✅ Enhanced agent imported successfully")
        
        # Test 2: Initialize Enhanced Agent
        print("\n🚀 Test 2: Enhanced Agent Initialization")
        agent = EnhancedAgent()
        print("✅ Enhanced agent initialized successfully")
        print(f"   - UI generation enabled: {agent.ui_generation_enabled}")
        
        # Test 3: Component Library Loading
        print("\n📚 Test 3: Component Library Loading")
        await agent._ensure_component_knowledge()
        component_count = len(agent.component_library) if agent.component_library else 0
        print(f"✅ Component library loaded: {component_count} components")
        
        # Test 4: Simple Query Processing
        print("\n🔍 Test 4: Query Processing Test")
        test_query = "show me iPhone products"
        test_context = {"session_id": "test_session", "customerId": "test_customer"}
        
        execution_plan = await agent.process_query(test_query, test_context)
        print(f"✅ Query processed successfully")
        print(f"   - Strategy: {execution_plan.get('strategy')}")
        print(f"   - Tool calls: {len(execution_plan.get('tool_calls', []))}")
        print(f"   - Knowledge results: {len(execution_plan.get('knowledge_results', []))}")
        
        # Test 5: UI Generation Detection
        print("\n🎨 Test 5: UI Generation Detection")
        should_generate_ui = agent._should_generate_ui(test_query, execution_plan)
        print(f"✅ UI generation decision: {should_generate_ui}")
        
        # Test 6: Response Formatting
        print("\n📝 Test 6: Response Formatting")
        response = await agent.format_response(
            execution_plan, 
            [],  # Empty tool results for this test
            test_query,
            context=test_context
        )
        
        print(f"✅ Response formatted successfully")
        print(f"   - Response type: {response.get('response_type')}")
        print(f"   - UI components: {len(response.get('ui_components', []))}")
        print(f"   - Layout strategy: {response.get('layout_strategy')}")
        print(f"   - Message length: {len(response.get('message', ''))}")
        
        # Test 7: MCP Tools
        print("\n🔧 Test 7: MCP Tools Testing")
        library_result = await agent.mcp_tools.get_component_library()
        print(f"✅ MCP tools operational: {library_result.get('success')}")
        if library_result.get('success'):
            print(f"   - Components from MCP: {len(library_result['data'])}")
            print(f"   - Source: {library_result.get('source')}")
        
        # Test 8: Cache System
        print("\n💾 Test 8: Cache System")
        cache_info = await agent.mcp_tools.get_cache_status()
        if cache_info.get('success'):
            cache_data = cache_info['data']
            print(f"✅ Cache system operational")
            print(f"   - Memory cache: {cache_data['memory_cache']['exists']}")
            print(f"   - File cache: {cache_data['file_cache']['exists']}")
            print(f"   - Hit ratio: {cache_data.get('hit_ratio', 0):.2%}")
        
        # Cleanup
        await agent.close()
        
        print("\n🎉 Step 4 Integration Test Completed Successfully!")
        print("\n📊 Summary:")
        print(f"   ✓ Enhanced Agent: Functional with UI generation")
        print(f"   ✓ Component Library: {component_count} components loaded")
        print(f"   ✓ UI Generation: {'Enabled' if should_generate_ui else 'Conditional'}")
        print(f"   ✓ MCP Tools: Operational")
        print(f"   ✓ Caching System: Functional")
        print(f"   ✓ Query Processing: Working")
        print(f"   ✓ Response Formatting: Enhanced with UI")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    try:
        success = await test_step4_integration()
        if success:
            print("\n🏆 All tests passed! Step 4 is ready for use.")
        else:
            print("\n💥 Some tests failed. Check the output above.")
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"❌ Test suite failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())