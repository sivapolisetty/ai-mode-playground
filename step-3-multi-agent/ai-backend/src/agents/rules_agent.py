"""
Rules Agent
Specialized agent for business rules validation and policy enforcement using RAG
"""
import sys
import os
from typing import Dict, Any, List, Optional, Set
from loguru import logger

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../rag-service'))

from .base_agent import BaseAgent, AgentCapability, AgentMessage, WorkflowContext
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../rag-service'))
from rag_service import RAGService
from ..strategy_engine import StrategyEngine, StrategyContext


class RulesAgent(BaseAgent):
    """Agent specialized in business rules validation using RAG"""
    
    def __init__(self):
        capabilities = {
            AgentCapability.RULES_VALIDATE
        }
        super().__init__("rules_agent", capabilities)
        
        # Initialize RAG service for rules lookup
        self.rag_service = RAGService()
        
        # Initialize dynamic strategy engine
        knowledge_path = os.path.join(os.path.dirname(__file__), '../../../knowledge/business_strategies.json')
        self.strategy_engine = StrategyEngine(knowledge_path)
        
        # Common validation rules (hardcoded for demo)
        self.validation_rules = {
            "min_order_value": 0.01,
            "max_order_value": 10000.00,
            "max_quantity_per_item": 10,
            "address_change_window_hours": 24,
            "cancellation_window_hours": 48
        }
        
        # System prompt for declarative behavior
        self.system_prompt = """
        You are a Rules Agent specialized in business rules validation using RAG.
        
        Core Capabilities:
        - Validate orders against business rules using RAG knowledge base
        - Check policy compliance for order changes and cancellations
        - Provide rule-based recommendations and constraints
        - Access business rules knowledge through RAG service
        
        Behavioral Guidelines:
        - Always consult RAG service for comprehensive business rules
        - Validate all business constraints before approving operations
        - Provide clear explanations for rule violations
        - Handle edge cases with appropriate fallback rules
        - Maintain consistency in rule application across workflows
        
        RAG Tools Available:
        - RAG Service: Search business rules knowledge base
        - Rule validation for orders, changes, and policies
        - Context-aware rule interpretation
        
        Default Validation Rules:
        - Minimum order value: $0.01
        - Maximum order value: $10,000
        - Maximum quantity per item: 10
        - Address change window: 24 hours
        - Cancellation window: 48 hours
        
        Rule Categories:
        - Order validation rules
        - Payment and pricing rules
        - Shipping and delivery rules  
        - Customer account rules
        - Inventory and availability rules
        """
    
    async def process_request(self, message: AgentMessage, context: WorkflowContext) -> Dict[str, Any]:
        """Process rules validation requests"""
        action = message.action
        data = message.data
        
        try:
            if action == "validate_order":
                return await self._validate_order(data, context)
            elif action == "check_change_policy":
                return await self._check_change_policy(data, context)
            elif action == "validate_business_rule":
                return await self._validate_business_rule(data, context)
            elif action == "check_policy":
                return await self._check_policy(data, context)
            elif action == "evaluate_address_change_strategy":
                return await self._evaluate_address_change_strategy(data, context)
            else:
                raise ValueError(f"Unknown action: {action}")
                
        except Exception as e:
            logger.error(f"Rules agent failed to process {action}: {e}")
            return {"error": str(e), "success": False}
    
    async def _validate_order(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Validate order against business rules"""
        try:
            validation_results = []
            
            # Get order data from context
            product_data = context.agent_data.get("product_agent", {})
            customer_data = context.agent_data.get("customer_agent", {})
            shipping_data = context.agent_data.get("shipping_agent", {})
            
            search_results = product_data.get("search_results", [])
            inventory_status = product_data.get("inventory_status", [])
            
            # Rule 1: Check minimum order value
            if search_results:
                total_value = sum(float(p.get("price", 0)) for p in search_results)
                if total_value < self.validation_rules["min_order_value"]:
                    validation_results.append({
                        "rule": "min_order_value",
                        "valid": False,
                        "message": f"Order value ${total_value:.2f} below minimum ${self.validation_rules['min_order_value']:.2f}"
                    })
                else:
                    validation_results.append({
                        "rule": "min_order_value", 
                        "valid": True,
                        "message": f"Order value ${total_value:.2f} meets minimum requirement"
                    })
                
                # Rule 2: Check maximum order value
                if total_value > self.validation_rules["max_order_value"]:
                    validation_results.append({
                        "rule": "max_order_value",
                        "valid": False,
                        "message": f"Order value ${total_value:.2f} exceeds maximum ${self.validation_rules['max_order_value']:.2f}"
                    })
                else:
                    validation_results.append({
                        "rule": "max_order_value",
                        "valid": True,
                        "message": f"Order value ${total_value:.2f} within limits"
                    })
            
            # Rule 3: Check inventory availability
            for item in inventory_status:
                available_qty = item.get("available_quantity", 0)
                if available_qty <= 0:
                    validation_results.append({
                        "rule": "inventory_availability",
                        "valid": False,
                        "message": f"Product {item.get('product_id')} out of stock"
                    })
                else:
                    validation_results.append({
                        "rule": "inventory_availability",
                        "valid": True,
                        "message": f"Product {item.get('product_id')} available ({available_qty} units)"
                    })
            
            # Rule 4: Check shipping address requirements using RAG
            delivery_address = customer_data.get("delivery_address", {})
            if delivery_address:
                address_validation = await self._check_shipping_policy(delivery_address, context)
                validation_results.append(address_validation)
            
            # Overall validation result
            all_valid = all(result["valid"] for result in validation_results)
            
            result = {
                "validation_passed": all_valid,
                "rules_checked": validation_results,
                "violations": [r for r in validation_results if not r["valid"]],
                "success": True
            }
            
            # Update workflow context
            self.update_workflow_context(context, {
                "rules_validation": result
            })
            
            if all_valid:
                logger.info("Order validation passed all business rules")
            else:
                violations = [r["message"] for r in validation_results if not r["valid"]]
                logger.warning(f"Order validation failed: {violations}")
            
            return result
            
        except Exception as e:
            logger.error(f"Order validation failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _check_change_policy(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Check if order changes are allowed based on business rules"""
        try:
            # Get order details from context
            order_details = context.agent_data.get("order_agent", {}).get("order_details", {})
            
            if not order_details:
                return {"error": "Order details required for policy check", "success": False}
            
            order_created_at = order_details.get("created_at", 0)
            current_time = data.get("current_time", __import__("time").time())
            hours_since_order = (current_time - order_created_at) / 3600
            
            # Check time-based rules
            address_change_allowed = hours_since_order <= self.validation_rules["address_change_window_hours"]
            
            # Use RAG to check specific address change policies
            rag_result = await self._query_rag_for_policy("address change policy", context)
            
            policy_details = {
                "address_change_allowed": address_change_allowed,
                "hours_since_order": round(hours_since_order, 2),
                "time_limit_hours": self.validation_rules["address_change_window_hours"],
                "rag_policy": rag_result.get("policy_info", ""),
                "additional_restrictions": []
            }
            
            # Add order status restrictions
            order_status = order_details.get("status", "pending")
            if order_status in ["shipped", "delivered"]:
                policy_details["address_change_allowed"] = False
                policy_details["additional_restrictions"].append(f"Cannot change address for {order_status} orders")
            
            result = {
                "change_allowed": policy_details["address_change_allowed"],
                "policy_details": policy_details,
                "success": True
            }
            
            # Update workflow context
            self.update_workflow_context(context, {
                "change_policy": result
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Policy check failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _validate_business_rule(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Validate specific business rule using RAG"""
        try:
            rule_query = data.get("rule_query", "")
            rule_context = data.get("context", {})
            
            if not rule_query:
                return {"error": "Rule query required", "success": False}
            
            # Query RAG for business rule
            rag_result = await self._query_rag_for_policy(rule_query, context)
            
            if rag_result.get("success"):
                rule_info = rag_result.get("policy_info", "")
                confidence = rag_result.get("confidence", 0.0)
                
                result = {
                    "rule_found": True,
                    "rule_info": rule_info,
                    "confidence": confidence,
                    "query": rule_query,
                    "applicable": confidence > 0.5,
                    "success": True
                }
                
                self.update_workflow_context(context, {
                    "business_rule_validation": result
                })
                
                return result
            
            return {"error": "Could not find relevant business rule", "success": False}
            
        except Exception as e:
            logger.error(f"Business rule validation failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _check_policy(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Generic policy check using RAG"""
        try:
            policy_query = data.get("policy_query", context.user_query)
            
            # Query RAG for policy information
            rag_result = await self._query_rag_for_policy(policy_query, context)
            
            return rag_result
            
        except Exception as e:
            logger.error(f"Policy check failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _check_shipping_policy(self, address: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Check shipping policies for the given address"""
        try:
            # Query RAG for shipping restrictions
            state = address.get("state", "")
            country = address.get("country", "")
            
            shipping_query = f"shipping restrictions {state} {country}"
            rag_result = await self._query_rag_for_policy(shipping_query, context)
            
            # Basic address validation
            valid = True
            message = "Shipping address accepted"
            
            # Check for restricted areas (simplified)
            if country.upper() not in ["US", "USA", "UNITED STATES"]:
                valid = False
                message = "Currently only shipping within the United States"
            
            return {
                "rule": "shipping_policy",
                "valid": valid,
                "message": message,
                "rag_info": rag_result.get("policy_info", "")
            }
            
        except Exception as e:
            logger.error(f"Shipping policy check failed: {e}")
            return {
                "rule": "shipping_policy",
                "valid": True,
                "message": "Could not verify shipping policy",
                "error": str(e)
            }
    
    async def _query_rag_for_policy(self, query: str, context: WorkflowContext) -> Dict[str, Any]:
        """Query RAG service for policy information"""
        try:
            # Use RAG service to search business rules
            rag_response = await self.rag_service.process_query(query)
            
            if rag_response.results:
                # Get the best matching result
                best_result = rag_response.results[0]
                
                policy_info = {
                    "policy_info": best_result.content,
                    "confidence": best_result.score,
                    "source": best_result.metadata.get("source", "business_rules"),
                    "query": query,
                    "success": True
                }
                
                logger.info(f"Found policy info for '{query}' with confidence {best_result.score:.2f}")
                return policy_info
            
            return {
                "policy_info": "No relevant policy found",
                "confidence": 0.0,
                "query": query,
                "success": False
            }
            
        except Exception as e:
            logger.error(f"RAG policy query failed: {e}")
            return {
                "policy_info": "Could not query policy database",
                "confidence": 0.0,
                "query": query,
                "error": str(e),
                "success": False
            }
    
    async def _evaluate_address_change_strategy(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """
        Evaluate dynamic business strategies for address changes using strategy engine
        This replaces hard-coded workflows with flexible, text-based business strategies
        """
        try:
            # Extract context information
            order_data = data.get('order_data', {})
            customer_data = context.agent_data.get('customer_agent', {})
            requested_changes = data.get('requested_changes', {})
            
            # Create strategy context
            strategy_context = StrategyContext(
                user_query=context.user_query,
                order_data=order_data,
                customer_data=customer_data,
                current_situation=data.get('current_situation', {}),
                requested_changes=requested_changes
            )
            
            # Evaluate strategies using strategy engine
            selected_strategy = await self.strategy_engine.evaluate_strategies(strategy_context)
            
            if not selected_strategy:
                return {
                    "success": False,
                    "error": "No applicable strategy found for address change request"
                }
            
            # Execute the selected strategy
            execution_plan = await self.strategy_engine.execute_strategy(selected_strategy, strategy_context)
            
            result = {
                "success": True,
                "strategy_selected": selected_strategy['name'],
                "strategy_description": selected_strategy['description'],
                "execution_plan": execution_plan,
                "business_rationale": f"Selected '{selected_strategy['name']}' strategy based on current order status and business rules",
                "next_steps": execution_plan.get('agent_instructions', [])
            }
            
            # Update workflow context with strategy decision
            self.update_workflow_context(context, {
                "selected_strategy": selected_strategy,
                "execution_plan": execution_plan
            })
            
            logger.info(f"Address change strategy selected: {selected_strategy['name']}")
            return result
            
        except Exception as e:
            logger.error(f"Strategy evaluation failed: {e}")
            return {
                "success": False,
                "error": f"Strategy evaluation failed: {str(e)}",
                "fallback_required": True
            }

    def get_capabilities_description(self) -> Dict[str, str]:
        """Get human-readable description of rules agent capabilities"""
        return {
            "validate_order": "Validate orders against business rules and policies",
            "check_change_policy": "Check if order changes are allowed based on timing and status",
            "validate_business_rule": "Validate specific business rules using knowledge base",
            "check_policy": "Generic policy checking using RAG knowledge base",
            "evaluate_address_change_strategy": "Dynamically evaluate business strategies for address changes"
        }