"""
Customer Agent
Specialized agent for customer management, authentication, and customer-related operations
"""
import sys
import os
import time
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from loguru import logger

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from .base_agent import BaseAgent, AgentCapability, AgentMessage, WorkflowContext
from tools.mcp_tools import MCPTools


@dataclass
class CustomerProfile:
    """Customer profile information"""
    customer_id: str
    email: str
    name: str
    phone: Optional[str] = None
    addresses: List[Dict[str, Any]] = None
    payment_methods: List[Dict[str, Any]] = None
    preferences: Dict[str, Any] = None
    order_history: List[Dict[str, Any]] = None


class CustomerAgent(BaseAgent):
    """Agent specialized in customer management and authentication"""
    
    def __init__(self, traditional_api_url: str = "http://localhost:4000"):
        capabilities = {
            AgentCapability.CUSTOMER_AUTH,
            AgentCapability.NOTIFICATION_SEND
        }
        super().__init__("customer_agent", capabilities)
        
        # Initialize MCP tools for customer operations
        self.mcp_tools = MCPTools(traditional_api_url)
        
        # Customer session cache (in-memory for demo)
        self.customer_sessions: Dict[str, CustomerProfile] = {}
        
        # System prompt for declarative behavior
        self.system_prompt = """
        You are a Customer Agent specialized in customer management and authentication.
        
        Core Capabilities:
        - Customer authentication and session management
        - Address extraction and completion using MCP tools
        - Customer profile retrieval and management
        - Order confirmations and notifications
        
        Behavioral Guidelines:
        - Always use MCP tools for data operations
        - Extract and enhance address information intelligently
        - Handle partial addresses by completing them with customer data
        - Provide clear feedback for missing information
        - Maintain customer privacy and security
        
        MCP Tools Available:
        - get_customer_by_id: Get customer details from traditional API
        - get_customer_addresses: Get customer address list
        - extract_address_from_text: Extract address from natural language
        - complete_address: Complete partial addresses using customer data
        - validate_address: Validate address format and completeness
        """
    
    async def process_request(self, message: AgentMessage, context: WorkflowContext) -> Dict[str, Any]:
        """Process customer-related requests"""
        action = message.action
        data = message.data
        
        try:
            if action == "authenticate_customer":
                return await self._authenticate_customer(data, context)
            elif action == "get_customer_profile":
                return await self._get_customer_profile(data, context)
            elif action == "get_address":
                return await self._get_address(data, context)
            elif action == "get_location":
                return await self._get_location(data, context)
            elif action == "send_confirmation":
                return await self._send_confirmation(data, context)
            elif action == "notify_changes":
                return await self._notify_changes(data, context)
            elif action == "update_preferences":
                return await self._update_preferences(data, context)
            else:
                raise ValueError(f"Unknown action: {action}")
                
        except Exception as e:
            logger.error(f"Customer agent failed to process {action}: {e}")
            return {"error": str(e), "success": False}
    
    async def _authenticate_customer(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Authenticate customer using MCP tools"""
        # Extract customer identifier from various sources
        customer_email = (
            data.get("email") or 
            data.get("customer_email") or
            context.metadata.get("customer_email") or
            "john@example.com"  # Default for demo
        )
        
        logger.info(f"Authenticating customer: {customer_email}")
        
        try:
            # Use MCP tools to get customer from traditional API
            customers_response = await self.mcp_tools.get_customers(limit=100, search=customer_email)
            
            if not customers_response.get("success"):
                return {
                    "success": False,
                    "error": f"Failed to fetch customer data: {customers_response.get('error')}",
                    "authenticated": False
                }
            
            customers = customers_response.get("data", [])
            customer = next(
                (c for c in customers if c.get("email") == customer_email), 
                None
            )
            
            if customer:
                customer_id = str(customer["id"])
                context.customer_id = customer_id
                
                # Create customer profile
                profile = CustomerProfile(
                    customer_id=customer_id,
                    email=customer.get("email", ""),
                    name=customer.get("name", ""),
                    phone=customer.get("phone"),
                    addresses=customer.get("addresses", []),
                    payment_methods=customer.get("payment_methods", []),
                    preferences=customer.get("preferences", {})
                )
                
                # Store in session cache
                session_id = context.session_id or context.workflow_id
                self.customer_sessions[session_id] = profile
                
                result = {
                    "success": True,
                    "customer_id": customer_id,
                    "name": profile.name,
                    "email": profile.email,
                    "authenticated": True
                }
                
                # Update workflow context
                self.update_workflow_context(context, {
                    "customer_profile": result
                })
                
                logger.info(f"Successfully authenticated customer {profile.name} ({customer_id})")
                return result
            else:
                # Customer not found
                return {
                    "success": False,
                    "error": f"Customer {customer_email} not found",
                    "authenticated": False
                }
                
        except Exception as e:
            logger.error(f"Customer authentication failed: {e}")
            return {"error": str(e), "success": False, "authenticated": False}
    
    async def _get_customer_profile(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Get full customer profile"""
        customer_id = data.get("customer_id") or context.customer_id
        
        if not customer_id:
            return {"error": "Customer ID required", "success": False}
        
        try:
            # Check session cache first
            session_id = context.session_id or context.workflow_id
            if session_id in self.customer_sessions:
                profile = self.customer_sessions[session_id]
                return {
                    "profile": {
                        "customer_id": profile.customer_id,
                        "email": profile.email,
                        "name": profile.name,
                        "phone": profile.phone,
                        "addresses": profile.addresses,
                        "payment_methods": profile.payment_methods,
                        "preferences": profile.preferences
                    },
                    "success": True
                }
            
            # Fallback to API
            customer_data = await self.mcp_tools.get_customer_by_id(customer_id)
            
            if customer_data:
                result = {
                    "profile": customer_data,
                    "success": True
                }
                
                self.update_workflow_context(context, {
                    "full_customer_profile": customer_data
                })
                
                return result
            
            return {"error": "Customer profile not found", "success": False}
            
        except Exception as e:
            logger.error(f"Failed to get customer profile: {e}")
            return {"error": str(e), "success": False}
    
    async def _get_address(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Get customer address for delivery using MCP tools"""
        address_type = data.get("address_type", "home")  # home, work, billing
        customer_id = data.get("customer_id") or context.customer_id
        
        if not customer_id:
            return {"error": "Customer ID required", "success": False}
        
        try:
            # Check if there's extracted address info from the user query
            extracted_address = context.metadata.get("delivery_address")
            
            if extracted_address:
                # Use MCP tools to complete the address
                completion_result = await self.mcp_tools.complete_address(extracted_address, customer_id)
                
                if completion_result.get("success"):
                    address_data = completion_result.get("data", {})
                    completed_address = address_data.get("completed_address", {})
                    missing_fields = address_data.get("missing_fields", [])
                    
                    if len(missing_fields) == 0:
                        # Address is complete
                        result = {
                            "address": completed_address,
                            "address_type": completed_address.get("type", "shipping"),
                            "address_source": "extracted_and_completed",
                            "success": True
                        }
                        
                        self.update_workflow_context(context, {
                            "delivery_address": completed_address
                        })
                        
                        logger.info(f"Completed extracted address: {completed_address.get('street', '')}")
                        return result
                    else:
                        # Address needs completion
                        result = {
                            "address": completed_address,
                            "address_type": "shipping",
                            "address_source": "extracted_incomplete",
                            "needs_completion": True,
                            "missing_fields": missing_fields,
                            "success": True
                        }
                        
                        self.update_workflow_context(context, {
                            "delivery_address": completed_address,
                            "address_needs_completion": True
                        })
                        
                        return result
            
            # Fallback to stored addresses using MCP tools
            addresses_result = await self.mcp_tools.get_customer_addresses(customer_id, address_type)
            
            if not addresses_result.get("success"):
                return {"error": f"Failed to get customer addresses: {addresses_result.get('error')}", "success": False}
            
            addresses = addresses_result.get("data", [])
            
            if addresses:
                # Use the first matching address
                target_address = addresses[0]
                
                result = {
                    "address": target_address,
                    "address_type": target_address.get("type", address_type),
                    "address_source": "stored_profile",
                    "success": True
                }
                
                self.update_workflow_context(context, {
                    "delivery_address": target_address
                })
                
                logger.info(f"Retrieved {address_type} address for customer {customer_id}")
                return result
            
            return {"error": f"No {address_type} address found for customer", "success": False}
            
        except Exception as e:
            logger.error(f"Failed to get customer address: {e}")
            return {"error": str(e), "success": False}
    
    
    async def _get_location(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Get customer location context for shipping calculations"""
        # This could be more sophisticated (IP geolocation, GPS, etc.)
        # For demo, we'll use the customer's default address
        
        return await self._get_address(data, context)
    
    async def _send_confirmation(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Send order confirmation to customer"""
        customer_id = data.get("customer_id") or context.customer_id
        order_data = data.get("order_data") or context.agent_data.get("order_agent", {})
        
        if not customer_id:
            return {"error": "Customer ID required", "success": False}
        
        try:
            # Get customer profile for contact info
            profile_result = await self._get_customer_profile({"customer_id": customer_id}, context)
            
            if not profile_result.get("success"):
                return {"error": "Could not get customer profile", "success": False}
            
            profile = profile_result["profile"]
            customer_email = profile.get("email", "")
            customer_name = profile.get("name", "")
            
            # Create confirmation message
            order_id = order_data.get("order_id", "ORDER_123")
            total = order_data.get("total", 0)
            
            confirmation_details = {
                "recipient": {
                    "email": customer_email,
                    "name": customer_name
                },
                "order": {
                    "order_id": order_id,
                    "total": total,
                    "status": "confirmed"
                },
                "message": f"Dear {customer_name}, your order {order_id} has been confirmed! Total: ${total}",
                "sent_at": time.time(),
                "method": "email"
            }
            
            # In a real system, this would integrate with email service
            logger.info(f"Sending order confirmation to {customer_email} for order {order_id}")
            
            result = {
                "confirmation_sent": True,
                "details": confirmation_details,
                "success": True
            }
            
            self.update_workflow_context(context, {
                "confirmation": confirmation_details
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to send confirmation: {e}")
            return {"error": str(e), "success": False}
    
    async def _notify_changes(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Notify customer of order changes"""
        customer_id = data.get("customer_id") or context.customer_id
        changes = data.get("changes", {})
        
        if not customer_id:
            return {"error": "Customer ID required", "success": False}
        
        try:
            # Get customer profile
            profile_result = await self._get_customer_profile({"customer_id": customer_id}, context)
            
            if not profile_result.get("success"):
                return {"error": "Could not get customer profile", "success": False}
            
            profile = profile_result["profile"]
            
            notification = {
                "customer_id": customer_id,
                "email": profile.get("email", ""),
                "changes": changes,
                "message": f"Your order has been updated: {changes}",
                "sent_at": time.time(),
                "method": "email"
            }
            
            logger.info(f"Notifying customer {customer_id} of changes: {changes}")
            
            result = {
                "notification_sent": True,
                "details": notification,
                "success": True
            }
            
            self.update_workflow_context(context, {
                "change_notification": notification
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to notify changes: {e}")
            return {"error": str(e), "success": False}
    
    async def _update_preferences(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Update customer preferences"""
        customer_id = data.get("customer_id") or context.customer_id
        preferences = data.get("preferences", {})
        
        if not customer_id:
            return {"error": "Customer ID required", "success": False}
        
        try:
            # Update preferences in session cache if available
            session_id = context.session_id or context.workflow_id
            if session_id in self.customer_sessions:
                profile = self.customer_sessions[session_id]
                if profile.preferences:
                    profile.preferences.update(preferences)
                else:
                    profile.preferences = preferences
            
            result = {
                "preferences_updated": True,
                "customer_id": customer_id,
                "preferences": preferences,
                "success": True
            }
            
            self.update_workflow_context(context, {
                "updated_preferences": preferences
            })
            
            logger.info(f"Updated preferences for customer {customer_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to update preferences: {e}")
            return {"error": str(e), "success": False}
    
    def get_capabilities_description(self) -> Dict[str, str]:
        """Get human-readable description of customer agent capabilities"""
        return {
            "authenticate_customer": "Authenticate customer and establish session",
            "get_customer_profile": "Retrieve full customer profile and preferences",
            "get_address": "Get customer delivery addresses (home, work, billing)",
            "get_location": "Get customer location context for shipping",
            "send_confirmation": "Send order confirmations and notifications",
            "notify_changes": "Notify customers of order updates and changes",
            "update_preferences": "Update customer preferences and settings"
        }