#!/usr/bin/env python3
"""
Demo: Dynamic UI Generation for Step 4
Demonstrates UI generation logic with mock responses (no LLM required)
"""
import json
from typing import Dict, Any, List

class MockUIGenerator:
    """Mock UI generation to demonstrate the concept"""
    
    def __init__(self):
        # Sample component library (based on our scan results)
        self.component_library = {
            "card": {
                "category": "layout",
                "exports": ["Card", "CardContent", "CardHeader", "CardFooter"],
                "use_cases": ["Product displays", "Information panels", "Content containers"]
            },
            "button": {
                "category": "input", 
                "exports": ["Button"],
                "use_cases": ["Actions", "Form submissions", "Navigation"]
            },
            "input": {
                "category": "form",
                "exports": ["Input"],
                "use_cases": ["Form fields", "Search bars", "User input"]
            },
            "badge": {
                "category": "utility",
                "exports": ["Badge"],
                "use_cases": ["Status indicators", "Labels", "Categories"]
            },
            "select": {
                "category": "form",
                "exports": ["Select", "SelectContent", "SelectItem"],
                "use_cases": ["Dropdowns", "Option selection", "Filters"]
            },
            "pagination": {
                "category": "navigation",
                "exports": ["Pagination", "PaginationContent", "PaginationItem"],
                "use_cases": ["Page navigation", "Data sets", "Lists"]
            }
        }
    
    def should_generate_ui(self, query: str, intent: str) -> bool:
        """Determine if UI generation is beneficial"""
        ui_triggers = ["show", "display", "list", "find", "search", "view", "products", "orders"]
        return any(trigger in query.lower() for trigger in ui_triggers)
    
    def generate_ui_specification(self, query: str, intent: str, context: Dict = None) -> Dict[str, Any]:
        """Generate UI specification based on query intent"""
        
        # Intent-based UI generation
        if intent == "product_search":
            return {
                "ui_components": [
                    {
                        "type": "card",
                        "props": {
                            "className": "product-grid",
                            "variant": "outlined"
                        },
                        "children": "Product Grid Container",
                        "actions": [
                            {
                                "event": "onClick",
                                "action": "view_product",
                                "payload": {"productId": "{{product.id}}"}
                            }
                        ],
                        "layout": {
                            "position": "inline",
                            "priority": "high"
                        }
                    },
                    {
                        "type": "input",
                        "props": {
                            "placeholder": "Search products...",
                            "type": "search"
                        },
                        "actions": [
                            {
                                "event": "onChange",
                                "action": "filter_products",
                                "payload": {"query": "{{input.value}}"}
                            }
                        ],
                        "layout": {
                            "position": "inline",
                            "priority": "high"
                        }
                    },
                    {
                        "type": "select",
                        "props": {
                            "placeholder": "Filter by category"
                        },
                        "actions": [
                            {
                                "event": "onValueChange",
                                "action": "filter_category",
                                "payload": {"category": "{{selected.value}}"}
                            }
                        ],
                        "layout": {
                            "position": "inline",
                            "priority": "medium"
                        }
                    },
                    {
                        "type": "pagination",
                        "props": {
                            "total": 100,
                            "pageSize": 12
                        },
                        "actions": [
                            {
                                "event": "onPageChange",
                                "action": "navigate_page",
                                "payload": {"page": "{{page.number}}"}
                            }
                        ],
                        "layout": {
                            "position": "inline",
                            "priority": "medium"
                        }
                    }
                ],
                "layout_strategy": "composition",
                "user_intent": "product_discovery_and_browsing",
                "success_criteria": "User can search, filter, and navigate product results"
            }
        
        elif intent == "purchase_intent":
            return {
                "ui_components": [
                    {
                        "type": "card",
                        "props": {
                            "className": "product-detail-card"
                        },
                        "children": "Product Details with Purchase Options",
                        "layout": {
                            "position": "modal",
                            "priority": "high"
                        }
                    },
                    {
                        "type": "button",
                        "props": {
                            "variant": "primary",
                            "size": "lg"
                        },
                        "children": "Add to Cart",
                        "actions": [
                            {
                                "event": "onClick",
                                "action": "add_to_cart",
                                "payload": {"productId": "{{product.id}}", "quantity": "{{quantity}}"}
                            }
                        ],
                        "layout": {
                            "position": "inline",
                            "priority": "high"
                        }
                    },
                    {
                        "type": "badge",
                        "props": {
                            "variant": "success"
                        },
                        "children": "In Stock",
                        "layout": {
                            "position": "inline",
                            "priority": "medium"
                        }
                    }
                ],
                "layout_strategy": "single_component",
                "user_intent": "purchase_workflow_initiation",
                "success_criteria": "User can view product details and initiate purchase"
            }
        
        elif intent == "order_tracking":
            return {
                "ui_components": [
                    {
                        "type": "card",
                        "props": {
                            "className": "order-timeline"
                        },
                        "children": "Order Status Timeline",
                        "layout": {
                            "position": "inline",
                            "priority": "high"
                        }
                    },
                    {
                        "type": "badge",
                        "props": {
                            "variant": "info"
                        },
                        "children": "Order Status: Shipped",
                        "layout": {
                            "position": "inline",
                            "priority": "high"
                        }
                    },
                    {
                        "type": "button",
                        "props": {
                            "variant": "outline"
                        },
                        "children": "Track Package",
                        "actions": [
                            {
                                "event": "onClick",
                                "action": "open_tracking",
                                "payload": {"trackingNumber": "{{order.trackingNumber}}"}
                            }
                        ],
                        "layout": {
                            "position": "inline",
                            "priority": "medium"
                        }
                    }
                ],
                "layout_strategy": "workflow",
                "user_intent": "order_status_inquiry",
                "success_criteria": "User can view order status and track shipment"
            }
        
        elif intent == "filtered_search":
            return {
                "ui_components": [
                    {
                        "type": "card",
                        "props": {
                            "className": "search-filters"
                        },
                        "children": "Advanced Search Filters",
                        "layout": {
                            "position": "sidebar",
                            "priority": "high"
                        }
                    },
                    {
                        "type": "input",
                        "props": {
                            "placeholder": "Product name...",
                            "type": "search"
                        },
                        "layout": {
                            "position": "inline",
                            "priority": "high"
                        }
                    },
                    {
                        "type": "select",
                        "props": {
                            "placeholder": "Price range"
                        },
                        "actions": [
                            {
                                "event": "onValueChange",
                                "action": "filter_price",
                                "payload": {"maxPrice": "{{selected.value}}"}
                            }
                        ],
                        "layout": {
                            "position": "inline",
                            "priority": "high"
                        }
                    }
                ],
                "layout_strategy": "composition",
                "user_intent": "advanced_product_filtering",
                "success_criteria": "User can apply multiple filters to find specific products"
            }
        
        else:
            # Fallback for other intents
            return {
                "ui_components": [
                    {
                        "type": "card",
                        "props": {
                            "className": "info-card"
                        },
                        "children": "Information Display",
                        "layout": {
                            "position": "inline",
                            "priority": "medium"
                        }
                    }
                ],
                "layout_strategy": "single_component",
                "user_intent": "general_information",
                "success_criteria": "Display relevant information to user"
            }

def demo_ui_generation():
    """Demo the UI generation system"""
    print("🎨 Dynamic UI Generation Demo")
    print("=" * 50)
    
    generator = MockUIGenerator()
    
    # Test queries
    test_queries = [
        {
            "query": "Show me iPhone products",
            "intent": "product_search"
        },
        {
            "query": "I want to buy this laptop",
            "intent": "purchase_intent"
        },
        {
            "query": "Track my recent orders", 
            "intent": "order_tracking"
        },
        {
            "query": "Find wireless headphones under $100",
            "intent": "filtered_search"
        },
        {
            "query": "What are your return policies?",
            "intent": "policy_inquiry"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: {test_case['intent']}")
        print(f"   Query: \"{test_case['query']}\"")
        
        # Check if UI should be generated
        should_generate = generator.should_generate_ui(test_case['query'], test_case['intent'])
        print(f"   🎨 Generate UI: {'Yes' if should_generate else 'No'}")
        
        if should_generate:
            # Generate UI specification
            ui_spec = generator.generate_ui_specification(
                test_case['query'], 
                test_case['intent']
            )
            
            ui_components = ui_spec['ui_components']
            layout_strategy = ui_spec['layout_strategy']
            user_intent = ui_spec['user_intent']
            
            print(f"   📱 Components: {len(ui_components)}")
            print(f"   📐 Layout: {layout_strategy}")
            print(f"   🎯 Intent: {user_intent}")
            
            # Show component breakdown
            component_types = [comp['type'] for comp in ui_components]
            print(f"   🔧 Types: {', '.join(component_types)}")
            
            # Count interactive components
            interactive_count = sum(1 for comp in ui_components if comp.get('actions'))
            print(f"   ⚡ Interactive: {interactive_count}/{len(ui_components)}")
            
            results.append({
                'query': test_case['query'],
                'intent': test_case['intent'],
                'ui_generated': True,
                'component_count': len(ui_components),
                'layout_strategy': layout_strategy,
                'interactive_components': interactive_count
            })
        else:
            print(f"   📝 Text-only response")
            results.append({
                'query': test_case['query'],
                'intent': test_case['intent'],
                'ui_generated': False
            })
    
    # Summary
    print(f"\n📊 Demo Results Summary")
    print("=" * 30)
    
    ui_generated_count = sum(1 for r in results if r.get('ui_generated', False))
    total_components = sum(r.get('component_count', 0) for r in results)
    total_interactive = sum(r.get('interactive_components', 0) for r in results)
    
    print(f"📈 Statistics:")
    print(f"   • Queries tested: {len(test_queries)}")
    print(f"   • UI generated: {ui_generated_count}")
    print(f"   • Total components: {total_components}")
    print(f"   • Interactive components: {total_interactive}")
    print(f"   • UI generation rate: {ui_generated_count/len(test_queries)*100:.1f}%")
    
    # Show detailed example
    print(f"\n🔍 Detailed Example - Product Search UI:")
    product_search_ui = generator.generate_ui_specification("Show me iPhone products", "product_search")
    print(json.dumps(product_search_ui, indent=2))
    
    print(f"\n✅ Demo completed successfully!")
    print(f"🎯 This demonstrates how Step 4 generates dynamic UI specifications")
    print(f"🔗 Next: Implement client-side Dynamic UI Renderer to consume these specs")

if __name__ == "__main__":
    demo_ui_generation()