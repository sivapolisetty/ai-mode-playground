"""
Shipping Agent
Specialized agent for delivery calculations, address validation, and shipping logistics
"""
import sys
import os
from typing import Dict, Any, List, Optional, Set
from loguru import logger

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from .base_agent import BaseAgent, AgentCapability, AgentMessage, WorkflowContext


class ShippingAgent(BaseAgent):
    """Agent specialized in shipping and delivery logistics"""
    
    def __init__(self):
        capabilities = {
            AgentCapability.SHIPPING_CALC,
            AgentCapability.ADDRESS_VALIDATE
        }
        super().__init__("shipping_agent", capabilities)
        
        # Shipping rates by method
        self.shipping_rates = {
            "standard": {"cost": 5.99, "days": "5-7", "description": "Standard Ground"},
            "express": {"cost": 12.99, "days": "2-3", "description": "Express Delivery"},
            "overnight": {"cost": 24.99, "days": "1", "description": "Overnight Delivery"},
            "free": {"cost": 0.00, "days": "7-10", "description": "Free Standard (orders $50+)"}
        }
        
        # System prompt for declarative behavior
        self.system_prompt = """
        You are a Shipping Agent specialized in delivery calculations and logistics.
        
        Core Capabilities:
        - Calculate shipping costs and delivery times using MCP tools
        - Validate delivery addresses for shipping feasibility
        - Provide delivery estimates based on location and service level
        - Handle address changes and delivery recalculations
        
        Behavioral Guidelines:
        - Always use MCP tools for address validation and shipping calculations
        - Provide accurate delivery estimates based on location and service type
        - Handle remote locations with appropriate surcharges and delays
        - Offer multiple shipping options when available
        - Validate addresses before providing delivery estimates
        
        MCP Tools Available:
        - calculate_shipping_options: Calculate shipping costs and times for address
        - validate_address: Validate address format and deliverability
        - extract_address_from_text: Extract addresses from natural language
        
        Shipping Methods:
        - Standard: 5-7 days, $5.99
        - Express: 2-3 days, $12.99  
        - Overnight: 1 day, $24.99
        - Free: 7-10 days, $0 (orders $50+)
        
        Special Handling:
        - Remote locations (AK, HI): +1-2 days, +$5 surcharge
        - Free shipping threshold: $50+ order value
        """
    
    async def process_request(self, message: AgentMessage, context: WorkflowContext) -> Dict[str, Any]:
        """Process shipping-related requests"""
        action = message.action
        data = message.data
        
        try:
            if action == "calculate_delivery":
                return await self._calculate_delivery(data, context)
            elif action == "estimate_delivery":
                return await self._estimate_delivery(data, context)
            elif action == "validate_new_address":
                return await self._validate_address(data, context)
            elif action == "recalculate_delivery":
                return await self._recalculate_delivery(data, context)
            else:
                raise ValueError(f"Unknown action: {action}")
                
        except Exception as e:
            logger.error(f"Shipping agent failed to process {action}: {e}")
            return {"error": str(e), "success": False}
    
    async def _calculate_delivery(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Calculate delivery options and costs"""
        try:
            # Get delivery address from context
            delivery_address = context.agent_data.get("customer_agent", {}).get("delivery_address", {})
            delivery_preference = context.metadata.get("delivery_preference", "standard")
            
            if not delivery_address:
                return {"error": "Delivery address required", "success": False}
            
            # Get product weight/size (simplified)
            products = context.agent_data.get("product_agent", {}).get("search_results", [])
            
            # Calculate shipping options
            shipping_options = []
            
            # Check if eligible for free shipping (orders $50+)
            order_subtotal = sum(float(p.get("price", 0)) for p in products)
            
            for method, details in self.shipping_rates.items():
                if method == "free" and order_subtotal < 50:
                    continue  # Skip free shipping for orders under $50
                
                option = {
                    "method": method,
                    "cost": details["cost"],
                    "estimated_days": details["days"],
                    "description": details["description"],
                    "available": True
                }
                
                # Check delivery preference
                if method == delivery_preference or (delivery_preference == "express" and method in ["express", "overnight"]):
                    option["recommended"] = True
                
                shipping_options.append(option)
            
            # Select best option based on preference
            selected_option = None
            if delivery_preference == "express" or "2 days" in context.user_query.lower():
                selected_option = next((opt for opt in shipping_options if opt["method"] == "express"), shipping_options[0])
            else:
                # Default to cheapest option
                selected_option = min(shipping_options, key=lambda x: x["cost"])
            
            result = {
                "shipping_options": shipping_options,
                "selected_option": selected_option,
                "delivery_address": delivery_address,
                "estimated_delivery": selected_option["estimated_days"] + " business days",
                "delivery_cost": selected_option["cost"],
                "success": True
            }
            
            # Update workflow context
            self.update_workflow_context(context, {
                "shipping_calculation": result,
                "delivery_cost": selected_option["cost"],
                "estimated_delivery": result["estimated_delivery"]
            })
            
            logger.info(f"Calculated delivery: {selected_option['description']} - ${selected_option['cost']}")
            return result
            
        except Exception as e:
            logger.error(f"Delivery calculation failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _estimate_delivery(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Estimate delivery time to a location"""
        try:
            location = data.get("location") or context.agent_data.get("customer_agent", {}).get("delivery_address", {})
            
            if not location:
                return {"error": "Location required for delivery estimate", "success": False}
            
            # Simplified estimation based on location
            city = location.get("city", "").lower()
            state = location.get("state", "").lower()
            
            # Adjust delivery times based on location
            delivery_estimates = {}
            for method, details in self.shipping_rates.items():
                base_days = details["days"]
                
                # Add extra day for remote areas (simplified logic)
                if city in ["anchorage", "honolulu"] or state in ["ak", "hi"]:
                    if "-" in base_days:
                        min_days, max_days = base_days.split("-")
                        base_days = f"{int(min_days)+1}-{int(max_days)+2}"
                    else:
                        base_days = str(int(base_days) + 1)
                
                delivery_estimates[method] = {
                    "method": method,
                    "estimated_days": base_days,
                    "cost": details["cost"],
                    "description": details["description"]
                }
            
            result = {
                "delivery_estimates": delivery_estimates,
                "location": location,
                "success": True
            }
            
            self.update_workflow_context(context, {
                "delivery_estimates": delivery_estimates
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Delivery estimation failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _validate_address(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Validate shipping address"""
        try:
            address = data.get("address", {})
            
            if not address:
                return {"error": "Address required for validation", "success": False}
            
            # Simple validation (in production, would use address validation service)
            required_fields = ["address", "city", "state", "zip", "country"]
            missing_fields = [field for field in required_fields if not address.get(field)]
            
            if missing_fields:
                return {
                    "valid": False,
                    "error": f"Missing required fields: {', '.join(missing_fields)}",
                    "success": False
                }
            
            # Validate zip code format (US)
            zip_code = address.get("zip", "")
            if address.get("country", "").upper() == "US":
                if not (zip_code.isdigit() and len(zip_code) == 5):
                    return {
                        "valid": False,
                        "error": "Invalid US zip code format",
                        "success": False
                    }
            
            # Address is valid
            validated_address = {
                **address,
                "validated": True,
                "deliverable": True
            }
            
            result = {
                "valid": True,
                "address": validated_address,
                "success": True
            }
            
            self.update_workflow_context(context, {
                "validated_address": validated_address
            })
            
            logger.info(f"Validated address: {address.get('city')}, {address.get('state')}")
            return result
            
        except Exception as e:
            logger.error(f"Address validation failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _recalculate_delivery(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Recalculate delivery after address change"""
        try:
            new_address = data.get("new_address") or context.agent_data.get("shipping_agent", {}).get("validated_address")
            
            if not new_address:
                return {"error": "New address required for recalculation", "success": False}
            
            # Validate new address first
            validation_result = await self._validate_address({"address": new_address}, context)
            
            if not validation_result.get("success") or not validation_result.get("valid"):
                return validation_result
            
            # Recalculate delivery with new address
            # Temporarily update context with new address
            original_address = context.agent_data.get("customer_agent", {}).get("delivery_address")
            context.agent_data.setdefault("customer_agent", {})["delivery_address"] = new_address
            
            delivery_result = await self._calculate_delivery(data, context)
            
            # Restore original address in context
            if original_address:
                context.agent_data["customer_agent"]["delivery_address"] = original_address
            
            if delivery_result.get("success"):
                result = {
                    "recalculated": True,
                    "new_address": new_address,
                    "new_delivery_cost": delivery_result["delivery_cost"],
                    "new_estimated_delivery": delivery_result["estimated_delivery"],
                    "shipping_options": delivery_result["shipping_options"],
                    "success": True
                }
                
                self.update_workflow_context(context, {
                    "recalculated_delivery": result
                })
                
                return result
            
            return delivery_result
            
        except Exception as e:
            logger.error(f"Delivery recalculation failed: {e}")
            return {"error": str(e), "success": False}
    
    def get_capabilities_description(self) -> Dict[str, str]:
        """Get human-readable description of shipping agent capabilities"""
        return {
            "calculate_delivery": "Calculate shipping costs and delivery options",
            "estimate_delivery": "Estimate delivery times to specific locations",
            "validate_new_address": "Validate shipping addresses for deliverability",
            "recalculate_delivery": "Recalculate shipping after address changes"
        }