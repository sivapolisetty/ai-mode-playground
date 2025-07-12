#!/usr/bin/env python3
"""
Dynamic Strategy Demo
Demonstrates how text-based business strategies replace hard-coded workflows
"""
import json
import asyncio
from typing import Dict, Any

# Simulate the strategy evaluation process
class StrategyDemo:
    
    def __init__(self):
        # Load business strategies from knowledge base
        self.strategies = {
            "standard_change": {
                "name": "Standard Address Change",
                "conditions": ["Order status is PENDING or CONFIRMED", "Within 24 hours of order"],
                "actions": ["Validate new address", "Update order", "Send confirmation"]
            },
            "cancel_reorder": {
                "name": "Cancel and Reorder with Gift Card", 
                "conditions": ["Direct change not possible", "Order shipped or outside window"],
                "actions": ["Cancel order", "Issue gift card", "Create new order", "Apply gift card"]
            }
        }
    
    def demonstrate_scenarios(self):
        """Show different scenarios and how strategies are selected"""
        
        scenarios = [
            {
                "name": "Recent Order - Standard Change",
                "order_status": "CONFIRMED",
                "order_age_hours": 2,
                "user_request": "I want to change delivery address to Oak Street Tree Apartment",
                "expected_strategy": "standard_change"
            },
            {
                "name": "Shipped Order - Cancel/Reorder Strategy", 
                "order_status": "SHIPPED",
                "order_age_hours": 48,
                "user_request": "Change delivery to different address",
                "expected_strategy": "cancel_reorder"
            }
        ]
        
        print("🚀 Dynamic Strategy Engine Demo")
        print("=" * 50)
        
        for scenario in scenarios:
            print(f"\n📋 Scenario: {scenario['name']}")
            print(f"   Order Status: {scenario['order_status']}")
            print(f"   Order Age: {scenario['order_age_hours']} hours")
            print(f"   User Request: {scenario['user_request']}")
            
            # Evaluate which strategy applies
            selected_strategy = self.evaluate_strategy(scenario)
            strategy_details = self.strategies[selected_strategy]
            
            print(f"\n✅ Selected Strategy: {strategy_details['name']}")
            print(f"   Conditions Met: {', '.join(strategy_details['conditions'])}")
            print(f"   Actions to Execute:")
            for i, action in enumerate(strategy_details['actions'], 1):
                print(f"      {i}. {action}")
            
            print("-" * 50)
    
    def evaluate_strategy(self, scenario: Dict[str, Any]) -> str:
        """Simple strategy evaluation logic"""
        status = scenario["order_status"]
        age_hours = scenario["order_age_hours"]
        
        # Check if standard change is possible
        if status in ["PENDING", "CONFIRMED"] and age_hours <= 24:
            return "standard_change"
        else:
            return "cancel_reorder"
    
    def show_business_owner_benefits(self):
        """Show how product owners can update strategies without code changes"""
        
        print("\n🎯 Business Owner Benefits")
        print("=" * 50)
        
        print("""
1. **Text-Based Strategies**: Business rules defined in plain English JSON
   - No code changes needed
   - Product owners can update strategies directly
   - Version controlled business logic

2. **Flexible Conditions**: Natural language conditions like:
   - "Order status is PENDING or CONFIRMED" 
   - "Within 24 hours of order placement"
   - "New address is valid and deliverable"

3. **Dynamic Actions**: Strategy actions in business terms:
   - "Cancel the existing order"
   - "Issue gift card for full amount"  
   - "Create new order with desired address"
   - "Apply gift card as payment method"

4. **Easy Updates**: Add new strategies by updating JSON:
        """)
        
        new_strategy = {
            "id": "priority_customer_strategy",
            "name": "Priority Customer Expedited Change",
            "conditions": [
                "Customer has premium status",
                "Order value over $500"
            ],
            "actions": [
                "Override standard change restrictions",
                "Apply expedited processing",
                "Waive any change fees",
                "Guarantee delivery date"
            ]
        }
        
        print("   ```json")
        print(json.dumps(new_strategy, indent=4))
        print("   ```")
        
        print("""
5. **No Hard-Coded Workflows**: 
   - Agents interpret strategies dynamically
   - Business logic lives in knowledge base
   - Strategies can reference other business rules
   - Context-aware decision making
        """)

if __name__ == "__main__":
    demo = StrategyDemo()
    demo.demonstrate_scenarios()
    demo.show_business_owner_benefits()