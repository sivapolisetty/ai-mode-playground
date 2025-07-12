"""
Multi-Agent Orchestrator
Replaces the enhanced agent with a multi-agent orchestration system
"""
import time
import uuid
from typing import Dict, List, Any, Optional, Tuple
from loguru import logger

from .dynamic_orchestrator import DynamicOrchestrator
from .agents.unified_business_agent import UnifiedBusinessAgent
from .agents.rules_agent import RulesAgent
from config.logging_config import logging_config


class MultiAgentOrchestrator:
    """
    Multi-agent orchestration system that coordinates specialized agents
    to handle complex e-commerce workflows
    """
    
    def __init__(self, traditional_api_url: str = "http://localhost:4000"):
        self.traditional_api_url = traditional_api_url
        
        # Initialize the dynamic orchestrator with strategy engine
        self.orchestrator = DynamicOrchestrator()
        
        # Initialize and register all specialized agents
        self._initialize_agents()
        
        # Session management (inherited from Step 2)
        self.sessions = {}
        
        logger.info("Multi-Agent Orchestrator initialized with specialized agents")
    
    def _initialize_agents(self):
        """Initialize and register simplified agent structure"""
        try:
            # Create simplified agents
            unified_business_agent = UnifiedBusinessAgent(self.traditional_api_url)
            rules_agent = RulesAgent()
            
            # Register agents with orchestrator
            self.orchestrator.register_agent(unified_business_agent)
            self.orchestrator.register_agent(rules_agent)
            
            logger.info("Simplified agent structure registered successfully")
            logger.info(f"  - UnifiedBusinessAgent: {len(unified_business_agent.get_capabilities_description())} capabilities")
            logger.info(f"  - RulesAgent: {len(rules_agent.get_capabilities_description())} capabilities")
            
        except Exception as e:
            logger.error(f"Failed to initialize simplified agents: {e}")
            raise
    
    def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """Get session state - maintains compatibility with Step 2"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "customer_id": None,
                "last_search": None,
                "order_context": None,
                "knowledge_context": None,
                "conversation_history": [],
                "active_workflows": []
            }
        return self.sessions[session_id]
    
    def update_session_state(self, session_id: str, updates: Dict[str, Any]):
        """Update session state"""
        state = self.get_session_state(session_id)
        state.update(updates)
        logger.info(f"Updated session {session_id}: {updates}")
    
    async def process_query(self, user_query: str, context: Dict[str, Any] = None, trace_id: str = None) -> Dict[str, Any]:
        """
        Process user query using multi-agent orchestration
        
        Args:
            user_query: User's natural language query
            context: Additional context
            trace_id: Tracing ID for observability
            
        Returns:
            Multi-agent orchestrated response
        """
        session_id = context.get("session_id", "default") if context else "default"
        session_state = self.get_session_state(session_id)
        
        try:
            logger.info(f"Processing multi-agent query: {user_query}")
            
            # Classify user intent to determine workflow
            workflow_name, workflow_data = await self.orchestrator.classify_user_intent(user_query)
            
            logger.info(f"Classified intent: {workflow_name} with data: {workflow_data}")
            
            # Prepare context data
            context_data = {
                "session_id": session_id,
                "customer_email": context.get("customer_email") if context else None,
                **workflow_data
            }
            
            # Start the appropriate workflow
            workflow_id = await self.orchestrator.start_workflow(
                workflow_name=workflow_name,
                user_query=user_query,
                context_data=context_data
            )
            
            # Get workflow results
            workflow_status = await self.orchestrator.get_workflow_status(workflow_id)
            
            # Update session state
            session_state["active_workflows"].append(workflow_id)
            session_state["conversation_history"].append({
                "query": user_query,
                "workflow": workflow_name,
                "workflow_id": workflow_id,
                "timestamp": time.time()
            })
            
            # Format response based on workflow results
            response = await self._format_multi_agent_response(
                workflow_name, 
                workflow_status, 
                user_query
            )
            
            return {
                "message": response,
                "timestamp": time.time(),
                "session_id": session_id,
                "strategy": f"multi_agent_{workflow_name}",
                "workflow_id": workflow_id,
                "debug": {
                    "workflow_name": workflow_name,
                    "agents_involved": list(workflow_status.get("agent_data", {}).keys()),
                    "workflow_status": workflow_status.get("status"),
                    "completed_steps": workflow_status.get("completed_steps", [])
                }
            }
            
        except Exception as e:
            logger.error(f"Multi-agent query processing failed: {e}")
            
            # Fallback to simple response
            return {
                "message": f"I encountered an issue processing your request: {str(e)}. Please try again.",
                "timestamp": time.time(),
                "session_id": session_id,
                "strategy": "multi_agent_fallback",
                "debug": {
                    "error": str(e),
                    "fallback": True
                }
            }
    
    async def _format_multi_agent_response(self, workflow_name: str, workflow_status: Dict[str, Any], user_query: str) -> str:
        """
        Format response based on multi-agent workflow results
        
        Args:
            workflow_name: Name of executed workflow
            workflow_status: Status and results from workflow
            user_query: Original user query
            
        Returns:
            Formatted natural language response
        """
        try:
            agent_data = workflow_status.get("agent_data", {})
            
            if workflow_name == "place_order":
                return await self._format_place_order_response(agent_data, user_query)
            elif workflow_name == "change_address":
                return await self._format_address_change_response(agent_data, user_query)
            elif workflow_name == "product_inquiry":
                return await self._format_product_inquiry_response(agent_data, user_query)
            else:
                return "I've processed your request using our specialized agents. How else can I help you?"
                
        except Exception as e:
            logger.error(f"Response formatting failed: {e}")
            return "I've completed your request. Is there anything else I can help you with?"
    
    async def _format_place_order_response(self, agent_data: Dict[str, Any], user_query: str) -> str:
        """Format response for place order workflow"""
        try:
            # Get data from simplified agents
            business_data = agent_data.get("unified_business_agent", {})
            rules_data = agent_data.get("rules_agent", {})
            
            # Map unified business agent data to original structure for compatibility
            product_data = {
                "search_results": business_data.get("search_results", []),
                "availability_info": business_data.get("availability_info", [])
            }
            customer_data = {
                "customer_profile": business_data.get("customer_profile", {}),
                "delivery_address": business_data.get("delivery_address", {}),
                "address_needs_completion": business_data.get("address_needs_completion", False)
            }
            order_data = {
                "created_order": business_data.get("created_order", {}),
                "order_details": business_data.get("order_details", {})
            }
            shipping_data = {
                "shipping_calculation": business_data.get("shipping_calculation", {})
            }
            
            # Extract key information
            products = product_data.get("search_results", [])
            customer_profile = customer_data.get("customer_profile", {})
            created_order = order_data.get("created_order", {})
            shipping_calc = shipping_data.get("shipping_calculation", {})
            rules_validation = rules_data.get("rules_validation", {})
            
            # Check if address needs completion
            delivery_address = customer_data.get("delivery_address", {})
            address_needs_completion = customer_data.get("address_needs_completion", False)
            
            if address_needs_completion:
                return await self._format_address_completion_response(delivery_address, products, user_query)
            
            if created_order:
                order_id = created_order.get("order_id")
                total = created_order.get("total", 0)
                delivery_estimate = created_order.get("estimated_delivery", "3-5 business days")
                customer_name = customer_profile.get("name", "Customer")
                
                # Check if express delivery was requested
                if "2 days" in user_query.lower() or "express" in user_query.lower():
                    selected_shipping = shipping_calc.get("selected_option", {})
                    if selected_shipping.get("method") == "express":
                        delivery_note = f"Great news! Your order qualifies for express delivery in {delivery_estimate}."
                    else:
                        delivery_note = f"Express delivery is available for an additional cost. Your current delivery estimate is {delivery_estimate}."
                else:
                    delivery_note = f"Your order will be delivered in {delivery_estimate}."
                
                response = f"Perfect! I've successfully placed your order.\n\n"
                response += f"**Order Details:**\n"
                response += f"- Order ID: {order_id}\n"
                response += f"- Customer: {customer_name}\n"
                response += f"- Total: ${total:.2f}\n"
                response += f"- {delivery_note}\n\n"
                
                if products:
                    product_name = products[0].get("name", "Product")
                    response += f"**Items Ordered:**\n- {product_name}\n\n"
                
                response += "Your order confirmation has been sent to your email. You can track your order status in your account."
                
                return response
            
            else:
                # Order creation failed, provide helpful information
                if not rules_validation.get("validation_passed", True):
                    violations = rules_validation.get("violations", [])
                    violation_messages = [v.get("message", "") for v in violations]
                    return f"I couldn't complete your order due to the following issues:\n\n" + "\n".join(f"- {msg}" for msg in violation_messages)
                
                return "I found the products you're looking for, but encountered an issue creating your order. Please try again or contact support."
            
        except Exception as e:
            logger.error(f"Place order response formatting failed: {e}")
            return "I've processed your order request. Please check your email for confirmation details."
    
    async def _format_address_change_response(self, agent_data: Dict[str, Any], user_query: str) -> str:
        """Format response for address change workflow"""
        try:
            customer_data = agent_data.get("customer_agent", {})
            order_data = agent_data.get("order_agent", {})
            rules_data = agent_data.get("rules_agent", {})
            shipping_data = agent_data.get("shipping_agent", {})
            
            change_policy = rules_data.get("change_policy", {})
            updated_order = order_data.get("updated_order", {})
            
            if not change_policy.get("change_allowed", False):
                policy_details = change_policy.get("policy_details", {})
                return f"I'm sorry, but address changes are not allowed for this order. {policy_details.get('additional_restrictions', [''])[0] if policy_details.get('additional_restrictions') else 'The order may have already shipped or exceeded the change window.'}"
            
            if updated_order:
                order_id = updated_order.get("order_id")
                new_address = updated_order.get("shipping_address", {})
                return f"Successfully updated the delivery address for order {order_id}!\n\nNew delivery address: {new_address.get('address', '')}, {new_address.get('city', '')}, {new_address.get('state', '')} {new_address.get('zip', '')}\n\nYou'll receive an email confirmation with the updated details."
            
            return "I've processed your address change request. You should receive a confirmation email shortly."
            
        except Exception as e:
            logger.error(f"Address change response formatting failed: {e}")
            return "I've processed your address change request."
    
    async def _format_product_inquiry_response(self, agent_data: Dict[str, Any], user_query: str) -> str:
        """Format response for product inquiry workflow"""
        try:
            # Get data from unified business agent (simplified structure)
            business_data = agent_data.get("unified_business_agent", {})
            product_data = {
                "availability_info": business_data.get("availability_info", []),
                "search_results": business_data.get("search_results", [])
            }
            shipping_data = {
                "delivery_estimates": business_data.get("delivery_estimates", {})
            }
            
            # Check for both old and new data formats from unified business agent
            search_results = business_data.get("search_results", [])
            availability_info = business_data.get("availability_info", [])
            inventory_status = business_data.get("inventory_status", [])
            delivery_estimates = business_data.get("delivery_estimates", {})
            
            # Use availability_info if available (preferred), otherwise use search_results
            if availability_info:
                response = "Here's what I found:\n\n"
                
                for item in availability_info[:3]:  # Show top 3 results
                    product = item.get("product", {})
                    availability = item.get("availability", {})
                    
                    product_name = product.get("name", "Product")
                    price = product.get("price", 0)
                    in_stock = availability.get("in_stock", False)
                    qty_available = availability.get("quantity_available", 0)
                    
                    response += f"**{product_name}** - ${price:.2f}\n"
                    
                    if in_stock:
                        response += f"✅ In stock ({qty_available} available)\n"
                        
                        # Add delivery info if available
                        if delivery_estimates:
                            standard_delivery = delivery_estimates.get("standard", {})
                            express_delivery = delivery_estimates.get("express", {})
                            
                            response += f"🚚 Delivery options:\n"
                            response += f"   - Standard: {standard_delivery.get('estimated_days', '5-7 days')} (${standard_delivery.get('cost', 5.99):.2f})\n"
                            response += f"   - Express: {express_delivery.get('estimated_days', '2-3 days')} (${express_delivery.get('cost', 12.99):.2f})\n"
                    else:
                        restock_date = availability.get("estimated_restock", "2-3 days")
                        response += f"❌ Currently out of stock (restock expected: {restock_date})\n"
                    
                    response += "\n"
                
                response += "Would you like me to help you place an order for any of these items?"
                return response
            elif search_results:
                # Fallback to basic search results if no availability_info
                response = "Here's what I found:\n\n"
                
                for product in search_results[:3]:
                    product_name = product.get("name", "Product")
                    price = product.get("price", 0)
                    qty_available = product.get("stockQuantity", 0)
                    
                    response += f"**{product_name}** - ${price:.2f}\n"
                    response += f"✅ In stock ({qty_available} available)\n\n"
                
                response += "Would you like me to help you place an order for any of these items?"
                return response
            
            return "I searched our catalog but couldn't find exact matches for your request. Could you provide more specific details about what you're looking for?"
            
        except Exception as e:
            logger.error(f"Product inquiry response formatting failed: {e}")
            return "I've searched our product catalog for you. Let me know if you need more specific information."
    
    async def _format_address_completion_response(self, address_info: Dict[str, Any], products: List[Dict[str, Any]], user_query: str) -> str:
        """Format response when address needs completion"""
        try:
            # Extract product info for context
            product_name = "your item"
            product_price = 0
            
            if products:
                product = products[0]
                product_name = product.get("name", "iPhone 15 Pro")
                product_price = product.get("price", 0)
            
            response = f"Great! I found the **{product_name}** for you"
            if product_price:
                response += f" at **${product_price:.2f}**"
            response += ". "
            
            # Get address details
            building_name = address_info.get("building_name", "")
            partial_address = address_info.get("address", "")
            missing_fields = address_info.get("missing_fields", [])
            
            if building_name or partial_address:
                response += f"I see you'd like it delivered to **{partial_address}**. "
            
            # Check delivery preference
            if "2 days" in user_query.lower() or "express" in user_query.lower():
                response += "I'll make sure to include express 2-day delivery options! "
            
            response += "\n\nTo complete your order and arrange delivery, I'll need a few more details:\n\n"
            
            # List missing information in a friendly way
            if "city" in missing_fields:
                response += "• **City**: Which city is this address in?\n"
            if "state" in missing_fields:
                response += "• **State**: Which state? (e.g., NY, CA, TX)\n"
            if "apartment_number" in missing_fields:
                response += "• **Apartment/Unit Number**: What's your specific unit number?\n"
            if "zip" in missing_fields:
                response += "• **ZIP Code**: For accurate delivery estimates\n"
            
            response += "\nOnce I have these details, I can:\n"
            response += "✅ Confirm the exact delivery address\n"
            response += "✅ Calculate precise delivery times and costs\n"
            response += "✅ Complete your order immediately\n"
            
            if "2 days" in user_query.lower():
                response += "✅ Ensure 2-day delivery is available to your location\n"
            
            response += "\nJust provide the missing information and I'll get your order processed right away!"
            
            return response
            
        except Exception as e:
            logger.error(f"Address completion response formatting failed: {e}")
            return "I found your product! To complete the order, I'll need some additional address details. Could you provide your complete delivery address including city, state, and ZIP code?"
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get status of a specific workflow"""
        return await self.orchestrator.get_workflow_status(workflow_id)
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow"""
        return await self.orchestrator.cancel_workflow(workflow_id)
    
    def get_agent_status(self, agent_name: str = None) -> Dict[str, Any]:
        """Get status of agents"""
        return self.orchestrator.get_agent_status(agent_name)
    
    def get_orchestrator_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        return self.orchestrator.get_orchestrator_stats()