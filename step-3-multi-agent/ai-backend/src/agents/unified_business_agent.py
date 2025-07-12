"""
Unified Business Agent
Consolidates Customer, Product, Order, and Shipping functionality into a single business-focused agent
"""
import sys
import os
import time
import uuid
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from loguru import logger

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from .base_agent import BaseAgent, AgentCapability, AgentMessage, WorkflowContext
from tools.mcp_tools import MCPTools


class UnifiedBusinessAgent(BaseAgent):
    """
    Unified agent that handles all core business operations using MCP tools
    Replaces CustomerAgent, ProductAgent, OrderAgent, and ShippingAgent
    """
    
    def __init__(self, traditional_api_url: str = "http://localhost:4000"):
        capabilities = {
            AgentCapability.CUSTOMER_AUTH,
            AgentCapability.PRODUCT_SEARCH,
            AgentCapability.INVENTORY_CHECK,
            AgentCapability.ORDER_CREATE,
            AgentCapability.ORDER_UPDATE,
            AgentCapability.SHIPPING_CALC,
            AgentCapability.ADDRESS_VALIDATE,
            AgentCapability.NOTIFICATION_SEND
        }
        super().__init__("unified_business_agent", capabilities)
        
        # Initialize MCP tools for all business operations
        self.mcp_tools = MCPTools(traditional_api_url)
        
        # Minimal state management
        self.customer_sessions: Dict[str, Dict[str, Any]] = {}
        self.inventory_reservations: Dict[str, Dict[str, Any]] = {}
        self.order_sequence = 1000
        
        # Initialize capability registry for LLM-driven orchestration
        self.capability_registry = self._build_capability_registry()
        
        # System prompt for LLM-driven capability orchestration
        self.system_prompt = f"""
        You are an intelligent Unified Business Agent with dynamic capability orchestration.
        
        Your role: Analyze user queries, create execution plans, and orchestrate capabilities intelligently.
        
        AVAILABLE CAPABILITIES:
        {self._format_capabilities_for_llm()}
        
        INTELLIGENCE FRAMEWORK:
        1. ANALYZE: Understand user intent and required information
        2. PLAN: Create step-by-step execution plan using available capabilities  
        3. EXTRACT: Identify entities and parameters for each capability
        4. EXECUTE: Call capabilities with extracted entities
        5. SYNTHESIZE: Combine results into coherent response
        
        CAPABILITY ORCHESTRATION RULES:
        - Always start by understanding what the user wants to achieve
        - Select minimal but sufficient capabilities to fulfill the request
        - Extract precise entities for each capability (product names, customer info, etc.)
        - Chain capabilities when one depends on another's output
        - Handle failures gracefully with alternative approaches
        
        ENTITY EXTRACTION PRINCIPLES:
        - Product queries: Extract clean product names/terms (e.g., "iPhone 15 Pro")
        - Customer queries: Extract customer identifiers, addresses
        - Order queries: Extract order details, modifications needed
        - Be intelligent about synonyms and natural language variations
        
        EXAMPLES:
        Query: "What is the price of iPhone 15 Pro?"
        Plan: 1. search_products(query="iPhone 15 Pro") 2. extract_pricing_from_results
        
        Query: "I want to buy MacBook with express shipping to NYC"  
        Plan: 1. search_products(query="MacBook") 2. extract_address(text="NYC") 3. calculate_shipping 4. create_order
        """
    
    def _build_capability_registry(self) -> Dict[str, Dict[str, Any]]:
        """Build registry of all available capabilities for LLM orchestration"""
        return {
            # Product Capabilities
            "search_products": {
                "description": "Search for products by name, brand, or keywords",
                "parameters": {"query": "string - product search terms"},
                "returns": "List of matching products with details and pricing",
                "examples": ["iPhone 15 Pro", "MacBook", "headphones"]
            },
            "get_product_details": {
                "description": "Get detailed information about a specific product",
                "parameters": {"product_id": "string - product identifier"},
                "returns": "Complete product information including specs and availability"
            },
            
            # Customer Capabilities  
            "authenticate_customer": {
                "description": "Authenticate customer and get profile information",
                "parameters": {"email": "string - customer email or identifier"},
                "returns": "Customer profile with addresses and preferences"
            },
            "get_customer_addresses": {
                "description": "Retrieve stored addresses for a customer",
                "parameters": {"customer_id": "string - customer identifier"},
                "returns": "List of customer's saved addresses"
            },
            
            # Address Capabilities
            "extract_address": {
                "description": "Extract and parse address information from text",
                "parameters": {"text": "string - text containing address information"},
                "returns": "Parsed address components and validation status"
            },
            "complete_address": {
                "description": "Complete partial address with missing information",
                "parameters": {"partial_address": "object - incomplete address data"},
                "returns": "Completed address with missing fields identified"
            },
            
            # Order Capabilities
            "create_order": {
                "description": "Create a new order with products and shipping",
                "parameters": {
                    "products": "array - list of products to order",
                    "customer_id": "string - customer identifier", 
                    "shipping_address": "object - delivery address",
                    "shipping_method": "string - shipping preference"
                },
                "returns": "Created order with order ID and confirmation details"
            },
            "get_customer_orders": {
                "description": "Retrieve order history for a customer",
                "parameters": {"customer_id": "string - customer identifier"},
                "returns": "List of customer's orders with status and details"
            },
            
            # Shipping Capabilities
            "calculate_shipping": {
                "description": "Calculate shipping options and costs",
                "parameters": {
                    "address": "object - destination address",
                    "products": "array - items to ship"
                },
                "returns": "Available shipping methods with costs and delivery times"
            },
            
            # Inventory Capabilities
            "check_inventory": {
                "description": "Check product availability and stock levels",
                "parameters": {"products": "array - products to check"},
                "returns": "Inventory status with availability and quantities"
            }
        }
    
    def _format_capabilities_for_llm(self) -> str:
        """Format capability registry for LLM understanding"""
        formatted = []
        for name, info in self.capability_registry.items():
            formatted.append(f"""
{name}:
  Purpose: {info['description']}
  Parameters: {info['parameters']}
  Returns: {info['returns']}""")
        return "\n".join(formatted)

    async def _execute_with_llm_orchestration(self, action: str, user_query: str, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Execute action using LLM-driven capability orchestration"""
        try:
            # Step 1: LLM analyzes query and creates execution plan
            plan = await self._create_execution_plan(action, user_query, data, context)
            
            if not plan.get("success"):
                return {"error": "Failed to create execution plan", "success": False}
            
            # Step 2: Execute plan steps using LLM-extracted entities
            results = await self._execute_plan(plan, context)
            
            # Step 3: LLM synthesizes final response
            final_result = await self._synthesize_results(action, user_query, results, context)
            
            return final_result
            
        except Exception as e:
            logger.error(f"LLM orchestration failed for {action}: {e}")
            return {"error": str(e), "success": False}

    async def _create_execution_plan(self, action: str, user_query: str, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Use LLM to analyze query and create execution plan"""
        try:
            # Import LLM config
            from config.llm_config import LLMConfig
            llm_config = LLMConfig()
            
            planning_prompt = f"""
            TASK: Create execution plan for action '{action}' based on user query.
            
            USER QUERY: "{user_query}"
            ACTION CONTEXT: {action}
            AVAILABLE CAPABILITIES: {list(self.capability_registry.keys())}
            
            ANALYZE the user query and CREATE a step-by-step execution plan using available capabilities.
            
            For each step, EXTRACT the specific entities and parameters needed.
            
            RETURN a JSON plan with this structure:
            {{
                "success": true,
                "intent": "user's primary goal",
                "steps": [
                    {{
                        "capability": "capability_name",
                        "parameters": {{"key": "extracted_value"}},
                        "description": "what this step accomplishes"
                    }}
                ],
                "entities": {{
                    "product_terms": ["iPhone", "15", "Pro"],
                    "intent_type": "price_inquiry",
                    "other_extracted_info": "..."
                }}
            }}
            
            EXAMPLES:
            Query: "What is the price of iPhone 15 Pro?"
            Plan: {{"intent": "get_product_pricing", "steps": [{{"capability": "search_products", "parameters": {{"query": "iPhone 15 Pro"}}, "description": "Find iPhone 15 Pro product"}}]}}
            
            Query: "Show me MacBook Air pricing" 
            Plan: {{"intent": "get_product_pricing", "steps": [{{"capability": "search_products", "parameters": {{"query": "MacBook Air"}}, "description": "Find MacBook Air products"}}]}}
            
            BE INTELLIGENT about entity extraction. Extract clean, precise terms for each capability.
            """
            
            # Call LLM to create plan
            llm = llm_config.get_llm()
            response = await llm.ainvoke(planning_prompt)
            
            # Parse LLM response as JSON
            import json
            try:
                plan = json.loads(response)
                return plan
            except json.JSONDecodeError:
                # Fallback: extract JSON from response if it's wrapped in text
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    plan = json.loads(json_match.group())
                    return plan
                else:
                    return {"success": False, "error": "Could not parse LLM response as JSON"}
            
        except Exception as e:
            logger.error(f"Plan creation failed: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_plan(self, plan: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Execute the LLM-generated plan step by step"""
        try:
            results = {"steps": [], "success": True}
            
            for step in plan.get("steps", []):
                capability = step.get("capability")
                parameters = step.get("parameters", {})
                description = step.get("description", "")
                
                logger.info(f"Executing capability: {capability} with params: {parameters}")
                
                # Map capability to actual method
                step_result = await self._execute_capability(capability, parameters, context)
                
                results["steps"].append({
                    "capability": capability,
                    "description": description,
                    "parameters": parameters,
                    "result": step_result,
                    "success": step_result.get("success", False)
                })
                
                # Store results in context for next steps
                if step_result.get("success") and step_result.get("data"):
                    context.metadata[f"{capability}_result"] = step_result["data"]
            
            return results
            
        except Exception as e:
            logger.error(f"Plan execution failed: {e}")
            return {"success": False, "error": str(e), "steps": []}

    async def _execute_capability(self, capability: str, parameters: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Execute a specific capability with given parameters"""
        try:
            if capability == "search_products":
                query = parameters.get("query", "")
                result = await self.mcp_tools.search_products(query)
                return result
                
            elif capability == "authenticate_customer":
                email = parameters.get("email", "")
                result = await self.mcp_tools.get_customer_by_email(email)
                return result
                
            elif capability == "extract_address":
                text = parameters.get("text", "")
                result = await self.mcp_tools.extract_address_from_text(text)
                return result
                
            elif capability == "calculate_shipping":
                address = parameters.get("address", {})
                products = parameters.get("products", [])
                result = await self.mcp_tools.calculate_shipping_options(address, products)
                return result
                
            elif capability == "check_inventory":
                products = parameters.get("products", [])
                # Simulate inventory check
                inventory_status = []
                for product in products:
                    inventory_status.append({
                        "product_id": product.get("id"),
                        "in_stock": True,
                        "quantity_available": product.get("stockQuantity", 10)
                    })
                return {"success": True, "data": inventory_status}
                
            elif capability == "create_order":
                order_data = parameters
                result = await self.mcp_tools.create_order(order_data)
                return result
                
            else:
                return {"success": False, "error": f"Unknown capability: {capability}"}
                
        except Exception as e:
            logger.error(f"Capability {capability} execution failed: {e}")
            return {"success": False, "error": str(e)}

    async def _synthesize_results(self, action: str, user_query: str, results: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Use LLM to synthesize final response from execution results"""
        try:
            # For now, return structured results
            # Later we can add LLM synthesis for natural language responses
            
            successful_steps = [step for step in results.get("steps", []) if step.get("success")]
            
            if not successful_steps:
                return {"success": False, "error": "No successful steps in execution plan"}
            
            # Extract key data from successful steps
            synthesized_data = {}
            for step in successful_steps:
                capability = step["capability"]
                result_data = step["result"].get("data", {})
                
                if capability == "search_products":
                    synthesized_data["search_results"] = result_data
                elif capability == "check_inventory":
                    synthesized_data["inventory_status"] = result_data
                elif capability == "authenticate_customer":
                    synthesized_data["customer_profile"] = result_data
                elif capability == "extract_address":
                    synthesized_data["extracted_address"] = result_data
                elif capability == "calculate_shipping":
                    synthesized_data["shipping_options"] = result_data
            
            # Update workflow context
            self.update_workflow_context(context, synthesized_data)
            
            return {
                "success": True,
                "action": action,
                "user_query": user_query,
                "execution_results": results,
                **synthesized_data
            }
            
        except Exception as e:
            logger.error(f"Result synthesis failed: {e}")
            return {"success": False, "error": str(e)}

    async def process_request(self, message: AgentMessage, context: WorkflowContext) -> Dict[str, Any]:
        """Process requests using LLM-driven capability orchestration"""
        action = message.action
        data = message.data
        user_query = context.user_query
        
        try:
            # For specific workflow actions, use LLM-driven approach
            if action in ["search_product", "check_inventory", "authenticate_customer", "get_address", "create_order", "calculate_delivery"]:
                return await self._execute_with_llm_orchestration(action, user_query, data, context)
            
            # Legacy support for direct action calls
            if action == "authenticate_customer":
                return await self._authenticate_customer(data, context)
            elif action == "get_customer_profile":
                return await self._get_customer_profile(data, context)
            elif action == "get_address":
                return await self._get_address(data, context)
            
            # Product operations  
            elif action == "search_product":
                return await self._search_product(data, context)
            elif action == "check_inventory":
                return await self._check_inventory(data, context)
            elif action == "check_availability":
                return await self._check_availability(data, context)
            
            # Order operations
            elif action == "create_order":
                return await self._create_order(data, context)
            elif action == "get_order_details":
                return await self._get_order_details(data, context)
            elif action == "update_order":
                return await self._update_order(data, context)
            
            # Shipping operations
            elif action == "calculate_delivery":
                return await self._calculate_delivery(data, context)
            elif action == "validate_address":
                return await self._validate_address(data, context)
            
            # Notification operations
            elif action == "send_confirmation":
                return await self._send_confirmation(data, context)
            elif action == "send_notification":
                return await self._send_notification(data, context)
            
            # Payment operations
            elif action == "create_gift_card":
                return await self._create_gift_card(data, context)
            elif action == "cancel_order":
                return await self._cancel_order(data, context)
            
            else:
                raise ValueError(f"Unknown action: {action}")
                
        except Exception as e:
            logger.error(f"Unified business agent failed to process {action}: {e}")
            return {"error": str(e), "success": False}
    
    # Customer Operations
    async def _authenticate_customer(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Authenticate customer using MCP tools"""
        customer_email = (
            data.get("email") or 
            data.get("customer_email") or
            context.metadata.get("customer_email") or
            "john@example.com"  # Default for demo
        )
        
        try:
            customers_response = await self.mcp_tools.get_customers(limit=100, search=customer_email)
            
            if not customers_response.get("success"):
                return {
                    "success": False,
                    "error": f"Failed to fetch customer data: {customers_response.get('error')}",
                    "authenticated": False
                }
            
            customers = customers_response.get("data", [])
            customer = next((c for c in customers if c.get("email") == customer_email), None)
            
            if customer:
                customer_id = str(customer["id"])
                context.customer_id = customer_id
                
                result = {
                    "success": True,
                    "customer_id": customer_id,
                    "name": customer.get("name", ""),
                    "email": customer.get("email", ""),
                    "authenticated": True
                }
                
                # Store in session cache
                session_id = context.session_id or context.workflow_id
                self.customer_sessions[session_id] = result
                
                self.update_workflow_context(context, {"customer_profile": result})
                return result
            else:
                return {
                    "success": False,
                    "error": f"Customer {customer_email} not found",
                    "authenticated": False
                }
                
        except Exception as e:
            logger.error(f"Customer authentication failed: {e}")
            return {"error": str(e), "success": False, "authenticated": False}
    
    async def _get_address(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Get customer address using MCP tools with intelligent completion"""
        customer_id = data.get("customer_id") or context.customer_id
        
        if not customer_id:
            return {"error": "Customer ID required", "success": False}
        
        try:
            # Check for extracted address from user query
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
                        self.update_workflow_context(context, {"delivery_address": completed_address})
                        return {
                            "address": completed_address,
                            "address_source": "extracted_and_completed",
                            "success": True
                        }
                    else:
                        # Address needs completion
                        self.update_workflow_context(context, {
                            "delivery_address": completed_address,
                            "address_needs_completion": True
                        })
                        return {
                            "address": completed_address,
                            "needs_completion": True,
                            "missing_fields": missing_fields,
                            "success": True
                        }
            
            # Fallback to stored addresses
            addresses_result = await self.mcp_tools.get_customer_addresses(customer_id)
            
            if addresses_result.get("success"):
                addresses = addresses_result.get("data", [])
                if addresses:
                    target_address = addresses[0]  # Use first available
                    self.update_workflow_context(context, {"delivery_address": target_address})
                    return {
                        "address": target_address,
                        "address_source": "stored_profile",
                        "success": True
                    }
            
            return {"error": "No address found for customer", "success": False}
            
        except Exception as e:
            logger.error(f"Failed to get customer address: {e}")
            return {"error": str(e), "success": False}
    
    # Product Operations
    async def _search_product(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Search products using MCP tools"""
        try:
            product_query = data.get("product_query") or context.user_query
            
            search_result = await self.mcp_tools.search_products(product_query)
            
            if search_result.get("success"):
                products = search_result.get("data", [])
                
                self.update_workflow_context(context, {
                    "search_results": products,
                    "search_query": product_query
                })
                
                return {
                    "success": True,
                    "search_results": products,
                    "count": len(products),
                    "query": product_query
                }
            else:
                return {"error": "Product search failed", "success": False}
                
        except Exception as e:
            logger.error(f"Product search failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _check_inventory(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Check inventory using search results from context"""
        try:
            products = context.agent_data.get("unified_business_agent", {}).get("search_results", [])
            
            if not products:
                return {"error": "No products to check inventory for", "success": False}
            
            inventory_status = []
            for product in products:
                # Simple inventory simulation
                product_id = product.get("id")
                availability = {
                    "product_id": product_id,
                    "in_stock": True,
                    "quantity_available": 10,  # Simulated
                    "estimated_restock": None
                }
                inventory_status.append(availability)
            
            self.update_workflow_context(context, {"inventory_status": inventory_status})
            
            return {
                "success": True,
                "inventory_status": inventory_status,
                "all_in_stock": all(item["in_stock"] for item in inventory_status)
            }
            
        except Exception as e:
            logger.error(f"Inventory check failed: {e}")
            return {"error": str(e), "success": False}
    
    # Order Operations
    async def _create_order(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Create order using MCP tools and context data"""
        try:
            customer_id = data.get("customer_id") or context.customer_id
            
            if not customer_id:
                return {"error": "Customer ID required", "success": False}
            
            # Get product from context
            products = context.agent_data.get("unified_business_agent", {}).get("search_results", [])
            if not products:
                return {"error": "No products found for order", "success": False}
            
            product = products[0]  # Use first product
            product_id = product.get("id")
            
            # Get delivery address from context
            delivery_address = context.agent_data.get("unified_business_agent", {}).get("delivery_address", {})
            shipping_address = f"{delivery_address.get('address', '')}, {delivery_address.get('city', '')}, {delivery_address.get('state', '')}"
            
            # Create order using MCP tools
            order_result = await self.mcp_tools.create_order(
                customer_id=customer_id,
                product_id=product_id,
                quantity=1,
                shipping_address=shipping_address
            )
            
            if order_result.get("success"):
                order_data = order_result.get("data", {})
                order_id = order_data.get("id", f"ORD-{self.order_sequence}")
                self.order_sequence += 1
                
                created_order = {
                    "order_id": order_id,
                    "customer_id": customer_id,
                    "product_name": product.get("name"),
                    "total": order_result.get("total_amount", 0),
                    "status": "CONFIRMED",
                    "estimated_delivery": "2-3 business days"
                }
                
                self.update_workflow_context(context, {"created_order": created_order})
                
                return {
                    "success": True,
                    "created_order": created_order,
                    "order_id": order_id
                }
            else:
                return {"error": "Failed to create order", "success": False}
                
        except Exception as e:
            logger.error(f"Order creation failed: {e}")
            return {"error": str(e), "success": False}
    
    # Shipping Operations
    async def _calculate_delivery(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Calculate delivery using MCP tools"""
        try:
            delivery_address = context.agent_data.get("unified_business_agent", {}).get("delivery_address", {})
            
            if not delivery_address:
                return {"error": "Delivery address required", "success": False}
            
            # Get product info for shipping calculation
            products = context.agent_data.get("unified_business_agent", {}).get("search_results", [])
            items = [{"price": p.get("price", 0), "quantity": 1} for p in products]
            
            shipping_result = await self.mcp_tools.calculate_shipping_options(delivery_address, items)
            
            if shipping_result.get("success"):
                shipping_data = shipping_result.get("data", {})
                shipping_options = shipping_data.get("shipping_options", [])
                
                # Select best option based on user preference
                delivery_preference = context.metadata.get("delivery_preference", "standard")
                selected_option = next(
                    (opt for opt in shipping_options if opt.get("method") == delivery_preference),
                    shipping_options[0] if shipping_options else None
                )
                
                result = {
                    "success": True,
                    "shipping_options": shipping_options,
                    "selected_option": selected_option,
                    "shipping_calculation": {
                        "options": shipping_options,
                        "selected": selected_option
                    }
                }
                
                self.update_workflow_context(context, {"shipping_calculation": result["shipping_calculation"]})
                return result
            else:
                return {"error": "Shipping calculation failed", "success": False}
                
        except Exception as e:
            logger.error(f"Delivery calculation failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _validate_address(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Validate address using MCP tools"""
        try:
            address = data.get("address") or context.metadata.get("delivery_address")
            
            if not address:
                return {"error": "Address required for validation", "success": False}
            
            validation_result = await self.mcp_tools.validate_address(address)
            return validation_result
            
        except Exception as e:
            logger.error(f"Address validation failed: {e}")
            return {"error": str(e), "success": False}
    
    # Notification Operations
    async def _send_confirmation(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Send order confirmation"""
        try:
            customer_profile = context.agent_data.get("unified_business_agent", {}).get("customer_profile", {})
            created_order = context.agent_data.get("unified_business_agent", {}).get("created_order", {})
            
            confirmation_details = {
                "recipient": {
                    "email": customer_profile.get("email"),
                    "name": customer_profile.get("name")
                },
                "order": created_order,
                "message": f"Order {created_order.get('order_id')} confirmed!",
                "sent_at": time.time()
            }
            
            self.update_workflow_context(context, {"confirmation": confirmation_details})
            
            return {
                "success": True,
                "confirmation_sent": True,
                "details": confirmation_details
            }
            
        except Exception as e:
            logger.error(f"Send confirmation failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _send_notification(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Send general notification"""
        try:
            customer_id = data.get("customer_id") or context.customer_id
            message_type = data.get("message_type", "general")
            details = data.get("details", {})
            
            # Get customer profile
            customer_profile = context.agent_data.get("unified_business_agent", {}).get("customer_profile", {})
            
            notification = {
                "customer_id": customer_id,
                "email": customer_profile.get("email"),
                "message_type": message_type,
                "details": details,
                "sent_at": time.time()
            }
            
            self.update_workflow_context(context, {"notification": notification})
            
            return {
                "success": True,
                "notification_sent": True,
                "details": notification
            }
            
        except Exception as e:
            logger.error(f"Send notification failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _create_gift_card(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Create gift card for order cancellation"""
        try:
            amount = data.get("amount", 0)
            customer_id = data.get("customer_id") or context.customer_id
            reason = data.get("reason", "Order cancellation")
            
            # Generate gift card
            gift_card = {
                "gift_card_id": f"GC-{int(time.time())}",
                "amount": amount,
                "customer_id": customer_id,
                "reason": reason,
                "created_at": time.time(),
                "status": "active"
            }
            
            self.update_workflow_context(context, {"gift_card": gift_card})
            
            return {
                "success": True,
                "gift_card_created": True,
                "gift_card": gift_card,
                "message": f"Gift card {gift_card['gift_card_id']} created for ${amount:.2f}"
            }
            
        except Exception as e:
            logger.error(f"Create gift card failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _cancel_order(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Cancel an existing order"""
        try:
            order_id = data.get("order_id")
            reason = data.get("reason", "Customer request")
            
            if not order_id:
                return {"error": "Order ID required for cancellation", "success": False}
            
            # Simulate order cancellation
            cancelled_order = {
                "order_id": order_id,
                "status": "CANCELLED",
                "reason": reason,
                "cancelled_at": time.time()
            }
            
            self.update_workflow_context(context, {"cancelled_order": cancelled_order})
            
            return {
                "success": True,
                "order_cancelled": True,
                "order": cancelled_order,
                "message": f"Order {order_id} has been cancelled"
            }
            
        except Exception as e:
            logger.error(f"Cancel order failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _get_customer_profile(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Get full customer profile using MCP tools"""
        try:
            customer_id = data.get("customer_id") or context.customer_id
            
            if not customer_id:
                return {"error": "Customer ID required", "success": False}
            
            # Check session cache first
            session_id = context.session_id or context.workflow_id
            if session_id in self.customer_sessions:
                profile = self.customer_sessions[session_id]
                return {"profile": profile, "success": True}
            
            # Get from MCP tools
            customer_result = await self.mcp_tools.get_customer_by_id(customer_id)
            
            if customer_result.get("success"):
                profile = customer_result.get("data", {})
                self.update_workflow_context(context, {"full_customer_profile": profile})
                return {"profile": profile, "success": True}
            else:
                return {"error": "Customer profile not found", "success": False}
                
        except Exception as e:
            logger.error(f"Get customer profile failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _check_availability(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Check product availability with enhanced info"""
        try:
            # Get products from previous search
            products = context.agent_data.get("unified_business_agent", {}).get("search_results", [])
            
            if not products:
                return {"error": "No products to check availability for", "success": False}
            
            availability_info = []
            
            for product in products:
                product_info = {
                    "product": product,
                    "availability": {
                        "in_stock": True,
                        "quantity_available": 10,  # Simulated
                        "estimated_restock": None
                    }
                }
                availability_info.append(product_info)
            
            self.update_workflow_context(context, {"availability_info": availability_info})
            
            return {
                "success": True,
                "availability_info": availability_info,
                "all_available": True
            }
            
        except Exception as e:
            logger.error(f"Check availability failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _get_order_details(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Get order details by ID"""
        try:
            order_id = data.get("order_id")
            customer_id = data.get("customer_id") or context.customer_id
            
            if not order_id and not customer_id:
                return {"error": "Order ID or Customer ID required", "success": False}
            
            # Simulate order lookup
            order_details = {
                "order_id": order_id or "ORD-12345",
                "customer_id": customer_id,
                "status": "CONFIRMED",
                "total_amount": 999.99,
                "items": [{"product": "iPhone 15 Pro", "quantity": 1, "price": 999.99}],
                "created_at": time.time() - 7200,  # 2 hours ago
                "shipping_address": "123 Main St, City, State"
            }
            
            self.update_workflow_context(context, {"order_details": order_details})
            
            return {
                "success": True,
                "order": order_details
            }
            
        except Exception as e:
            logger.error(f"Get order details failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _update_order(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Update existing order"""
        try:
            order_id = data.get("order_id")
            updates = data.get("updates", {})
            
            if not order_id:
                return {"error": "Order ID required for update", "success": False}
            
            # Simulate order update
            updated_order = {
                "order_id": order_id,
                "updates_applied": updates,
                "updated_at": time.time(),
                "status": "UPDATED"
            }
            
            self.update_workflow_context(context, {"updated_order": updated_order})
            
            return {
                "success": True,
                "updated_order": updated_order,
                "message": f"Order {order_id} updated successfully"
            }
            
        except Exception as e:
            logger.error(f"Update order failed: {e}")
            return {"error": str(e), "success": False}
    
    def get_capabilities_description(self) -> Dict[str, str]:
        """Get human-readable description of unified business agent capabilities"""
        return {
            "authenticate_customer": "Authenticate customer and establish session",
            "get_customer_profile": "Get full customer profile and preferences",
            "get_address": "Get and complete customer delivery addresses",
            "search_product": "Search for products and check availability", 
            "check_inventory": "Check product inventory and stock levels",
            "check_availability": "Check product availability with detailed info",
            "create_order": "Create orders with full business logic",
            "get_order_details": "Get order information by ID",
            "update_order": "Update existing orders",
            "cancel_order": "Cancel orders and handle refunds",
            "calculate_delivery": "Calculate shipping options and costs",
            "validate_address": "Validate delivery addresses",
            "send_confirmation": "Send order confirmations",
            "send_notification": "Send general customer notifications",
            "create_gift_card": "Create gift cards for cancellations and refunds"
        }