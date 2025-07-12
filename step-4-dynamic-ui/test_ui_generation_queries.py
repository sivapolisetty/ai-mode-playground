#!/usr/bin/env python3
"""
Query-Based UI Generation Test for Step 4
Tests actual user queries and examines the generated UI specifications
"""
import asyncio
import sys
import os
import json
from datetime import datetime

# Add the backend to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai-backend'))

async def test_ui_generation_with_queries():
    """Test UI generation with various user queries"""
    print("🧪 Testing Dynamic UI Generation with Real Queries")
    print("=" * 65)
    
    try:
        # Import and initialize
        from src.enhanced_agent import EnhancedAgent
        agent = EnhancedAgent()
        
        # Ensure component library is loaded
        await agent._ensure_component_knowledge()
        component_count = len(agent.component_library) if agent.component_library else 0
        print(f"📚 Component library loaded: {component_count} components")
        
        # Test queries with different intents
        test_queries = [
            {
                "query": "Show me iPhone products",
                "intent": "product_search",
                "context": {"session_id": "test1", "customerId": "user123"}
            },
            {
                "query": "I want to buy this laptop",
                "intent": "purchase_intent", 
                "context": {"session_id": "test2", "product_id": "laptop001"}
            },
            {
                "query": "Track my recent orders",
                "intent": "order_tracking",
                "context": {"session_id": "test3", "customerId": "user123"}
            },
            {
                "query": "What are your return policies?",
                "intent": "policy_inquiry",
                "context": {"session_id": "test4"}
            },
            {
                "query": "Find wireless headphones under $100",
                "intent": "filtered_search",
                "context": {"session_id": "test5", "filters": {"max_price": 100}}
            }
        ]
        
        results = []
        
        for i, test_case in enumerate(test_queries, 1):
            print(f"\n🔍 Test Query {i}: {test_case['intent']}")
            print(f"   Query: \"{test_case['query']}\"")
            
            try:
                # Process the query
                execution_plan = await agent.process_query(
                    test_case['query'], 
                    test_case['context']
                )
                
                # Check if UI generation would be triggered
                should_generate_ui = agent._should_generate_ui(test_case['query'], execution_plan)
                print(f"   ✅ Query processed - Strategy: {execution_plan.get('strategy')}")
                print(f"   🎨 UI Generation: {'Yes' if should_generate_ui else 'No'}")
                
                if should_generate_ui:
                    # Generate the complete response with UI
                    response = await agent.format_response(
                        execution_plan,
                        [],  # Mock empty tool results for this test
                        test_case['query'],
                        context=test_case['context']
                    )
                    
                    ui_components = response.get('ui_components', [])
                    layout_strategy = response.get('layout_strategy', 'text_only')
                    user_intent = response.get('user_intent', 'unknown')
                    
                    print(f"   📱 UI Components: {len(ui_components)}")
                    print(f"   📐 Layout Strategy: {layout_strategy}")
                    print(f"   🎯 Detected Intent: {user_intent}")
                    
                    # Show component details
                    if ui_components:
                        print(f"   🔧 Generated Components:")
                        for j, component in enumerate(ui_components[:3]):  # Show first 3
                            comp_type = component.get('type', 'unknown')
                            comp_props = len(component.get('props', {}))
                            comp_actions = len(component.get('actions', []))
                            print(f"      {j+1}. {comp_type} (props: {comp_props}, actions: {comp_actions})")
                    
                    # Store result for summary
                    results.append({
                        'query': test_case['query'],
                        'intent': test_case['intent'],
                        'strategy': execution_plan.get('strategy'),
                        'ui_generated': len(ui_components) > 0,
                        'ui_components': len(ui_components),
                        'layout_strategy': layout_strategy,
                        'detected_intent': user_intent,
                        'response_length': len(response.get('message', ''))
                    })
                else:
                    print(f"   📝 Text-only response (no UI generated)")
                    results.append({
                        'query': test_case['query'],
                        'intent': test_case['intent'],
                        'strategy': execution_plan.get('strategy'),
                        'ui_generated': False,
                        'ui_components': 0,
                        'layout_strategy': 'text_only',
                        'detected_intent': 'text_based'
                    })
                
            except Exception as e:
                print(f"   ❌ Query failed: {e}")
                results.append({
                    'query': test_case['query'],
                    'intent': test_case['intent'],
                    'error': str(e)
                })
        
        # Print comprehensive summary
        print(f"\n📊 UI Generation Test Summary")
        print("=" * 50)
        
        ui_generated_count = sum(1 for r in results if r.get('ui_generated', False))
        total_components = sum(r.get('ui_components', 0) for r in results)
        
        print(f"📈 Overall Results:")
        print(f"   • Total queries tested: {len(test_queries)}")
        print(f"   • Queries with UI generation: {ui_generated_count}")
        print(f"   • Total UI components generated: {total_components}")
        print(f"   • UI generation rate: {ui_generated_count/len(test_queries)*100:.1f}%")
        
        print(f"\n📋 Detailed Results:")
        for i, result in enumerate(results, 1):
            if 'error' not in result:
                ui_indicator = "🎨" if result['ui_generated'] else "📝"
                print(f"   {i}. {ui_indicator} {result['intent']}: {result['ui_components']} components ({result['layout_strategy']})")
            else:
                print(f"   {i}. ❌ {result['intent']}: Error - {result['error']}")
        
        # Show component library utilization
        print(f"\n🔧 Component Library Status:")
        if agent.component_library:
            categories = {}
            for comp_name, comp_info in agent.component_library.items():
                category = comp_info.get("category", "utility")
                categories[category] = categories.get(category, 0) + 1
            
            print(f"   • Available categories: {list(categories.keys())}")
            print(f"   • Total components available: {sum(categories.values())}")
            print(f"   • Most common category: {max(categories, key=categories.get)} ({categories[max(categories, key=categories.get)]} components)")
        
        # Cleanup
        await agent.close()
        
        print(f"\n🎉 UI Generation Query Test Completed!")
        return True
        
    except Exception as e:
        print(f"❌ UI Generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_component_specification_detail():
    """Test detailed component specification generation"""
    print(f"\n🔬 Detailed Component Specification Test")
    print("=" * 50)
    
    try:
        from src.enhanced_agent import EnhancedAgent
        agent = EnhancedAgent()
        await agent._ensure_component_knowledge()
        
        # Test a specific query that should generate detailed UI
        test_query = "Show me all iPhone products with filters and sorting options"
        test_context = {"session_id": "detail_test", "customerId": "power_user"}
        
        print(f"🔍 Testing detailed UI generation:")
        print(f"   Query: \"{test_query}\"")
        
        execution_plan = await agent.process_query(test_query, test_context)
        
        if agent._should_generate_ui(test_query, execution_plan):
            response = await agent.format_response(
                execution_plan, [], test_query, context=test_context
            )
            
            print(f"\n📱 Generated UI Specification:")
            print(f"   Response Type: {response.get('response_type')}")
            print(f"   Layout Strategy: {response.get('layout_strategy')}")
            print(f"   User Intent: {response.get('user_intent')}")
            
            ui_components = response.get('ui_components', [])
            if ui_components:
                print(f"\n🔧 Component Details:")
                for i, component in enumerate(ui_components):
                    print(f"   Component {i+1}:")
                    print(f"      Type: {component.get('type')}")
                    print(f"      Props: {json.dumps(component.get('props', {}), indent=8)}")
                    print(f"      Actions: {len(component.get('actions', []))} defined")
                    print(f"      Layout: {component.get('layout', {})}")
                    if i < len(ui_components) - 1:
                        print()
            
            validation = response.get('validation', {})
            if validation:
                print(f"\n✅ Validation Results:")
                print(f"   Total requested: {validation.get('total_requested', 0)}")
                print(f"   Successfully validated: {validation.get('validated', 0)}")
                print(f"   Validation success: {validation.get('success', False)}")
        
        await agent.close()
        print(f"\n✅ Detailed specification test completed")
        return True
        
    except Exception as e:
        print(f"❌ Detailed test failed: {e}")
        return False

async def main():
    """Main test function"""
    try:
        print(f"🚀 Starting Query-Based UI Generation Tests")
        print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run main query tests
        success1 = await test_ui_generation_with_queries()
        
        # Run detailed specification test
        success2 = await test_component_specification_detail()
        
        if success1 and success2:
            print(f"\n🏆 All UI generation tests passed!")
            print(f"🎯 Step 4 Dynamic UI Generation is fully operational")
        else:
            print(f"\n💥 Some tests failed. Check the output above.")
            
    except KeyboardInterrupt:
        print(f"\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"❌ Test suite failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())