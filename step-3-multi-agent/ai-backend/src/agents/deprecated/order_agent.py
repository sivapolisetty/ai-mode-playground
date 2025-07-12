"""
Order Agent
Specialized agent for order lifecycle management, creation, and processing
"""
import sys
import os
import time
import uuid
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
from loguru import logger

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from .base_agent import BaseAgent, AgentCapability, AgentMessage, WorkflowContext
from tools.mcp_tools import MCPTools


class OrderStatus(Enum):
    """Order status enumeration"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


@dataclass
class OrderItem:
    """Order item details"""
    product_id: str
    product_name: str
    quantity: int
    unit_price: float
    total_price: float


@dataclass
class Order:
    """Order details"""
    order_id: str
    customer_id: str
    items: List[OrderItem]
    subtotal: float
    shipping_cost: float
    tax: float
    total: float
    status: OrderStatus
    shipping_address: Dict[str, Any]
    billing_address: Dict[str, Any]
    payment_method: Dict[str, Any]
    created_at: float
    updated_at: float
    estimated_delivery: Optional[str] = None
    tracking_number: Optional[str] = None


class OrderAgent(BaseAgent):
    """Agent specialized in order lifecycle management"""
    
    def __init__(self, traditional_api_url: str = "http://localhost:4000"):
        capabilities = {
            AgentCapability.ORDER_CREATE,
            AgentCapability.ORDER_UPDATE
        }
        super().__init__("order_agent", capabilities)
        
        # Initialize MCP tools for order operations
        self.mcp_tools = MCPTools(traditional_api_url)
        
        # In-memory order storage (in production, this would be a database)
        self.orders: Dict[str, Order] = {}
        
        # Order sequence counter for demo
        self.order_sequence = 1000
        
        # System prompt for declarative behavior
        self.system_prompt = """
        You are an Order Agent specialized in order lifecycle management.
        
        Core Capabilities:
        - Order creation and validation using MCP tools
        - Order status tracking and updates
        - Order modifications and cancellations
        - Integration with customer, product, and shipping data
        
        Behavioral Guidelines:
        - Always use MCP tools for order data operations
        - Validate all order data before processing
        - Calculate accurate pricing including taxes and shipping
        - Maintain order state and history properly
        - Handle order modifications with business rule compliance
        
        MCP Tools Available:
        - create_order: Create new orders with customer and product data
        - get_customer_orders: Get orders for specific customers
        - get_product_by_id: Get product details for order items
        - get_customer_by_id: Get customer details for order validation
        
        Order Status Values:
        - PENDING: Order created, awaiting payment
        - CONFIRMED: Payment confirmed, processing
        - SHIPPED: Order dispatched for delivery
        - DELIVERED: Order successfully delivered
        - CANCELLED: Order cancelled by customer or system
        """
    
    async def process_request(self, message: AgentMessage, context: WorkflowContext) -> Dict[str, Any]:
        """Process order-related requests"""
        action = message.action
        data = message.data
        
        try:
            if action == "create_order":
                return await self._create_order(data, context)
            elif action == "get_order_details":
                return await self._get_order_details(data, context)
            elif action == "update_order":
                return await self._update_order(data, context)
            elif action == "update_order_status":
                return await self._update_order_status(data, context)
            elif action == "cancel_order":
                return await self._cancel_order(data, context)
            elif action == "calculate_totals":
                return await self._calculate_totals(data, context)
            elif action == "get_order_history":
                return await self._get_order_history(data, context)
            else:
                raise ValueError(f"Unknown action: {action}")
                
        except Exception as e:
            logger.error(f"Order agent failed to process {action}: {e}")
            return {"error": str(e), "success": False}
    
    async def _create_order(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Create a new order"""
        try:
            # Extract data from workflow context
            customer_data = context.agent_data.get("customer_agent", {})
            product_data = context.agent_data.get("product_agent", {})
            shipping_data = context.agent_data.get("shipping_agent", {})
            
            customer_id = customer_data.get("customer_profile", {}).get("customer_id") or context.customer_id
            
            if not customer_id:
                return {"error": "Customer ID required for order creation", "success": False}
            
            # Get product information
            search_results = product_data.get("search_results", [])
            inventory_reservation = product_data.get("inventory_reservation", {})
            
            if not search_results:
                return {"error": "No products found for order", "success": False}
            
            # Create order items from selected products
            order_items = []
            subtotal = 0.0
            
            # For demo, we'll use the first product from search results
            selected_product = search_results[0] if search_results else None
            quantity = data.get("quantity", 1)
            
            if selected_product:
                unit_price = float(selected_product.get("price", 0))
                total_price = unit_price * quantity
                
                order_item = OrderItem(
                    product_id=selected_product["id"],
                    product_name=selected_product["name"],
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=total_price
                )
                order_items.append(order_item)
                subtotal += total_price
            
            # Get shipping information
            delivery_address = context.agent_data.get("customer_agent", {}).get("delivery_address", {})
            shipping_cost = shipping_data.get("delivery_cost", 0.0)
            
            # Calculate tax (simple 8.5% for demo)
            tax_rate = 0.085
            tax = subtotal * tax_rate
            
            # Calculate total
            total = subtotal + shipping_cost + tax
            
            # Generate order ID
            order_id = f"ORD-{self.order_sequence}"
            self.order_sequence += 1
            
            # Create order object
            order = Order(
                order_id=order_id,
                customer_id=customer_id,
                items=order_items,
                subtotal=subtotal,
                shipping_cost=shipping_cost,
                tax=tax,
                total=total,
                status=OrderStatus.PENDING,
                shipping_address=delivery_address,
                billing_address=delivery_address,  # Same as shipping for demo
                payment_method={"type": "credit_card", "last_four": "1234"},  # Mock payment
                created_at=time.time(),
                updated_at=time.time(),
                estimated_delivery=shipping_data.get("estimated_delivery", "3-5 business days")
            )
            
            # Store order
            self.orders[order_id] = order
            
            # Create order data for response
            order_data = {
                "order_id": order_id,
                "customer_id": customer_id,
                "items": [
                    {
                        "product_id": item.product_id,
                        "product_name": item.product_name,
                        "quantity": item.quantity,
                        "unit_price": item.unit_price,
                        "total_price": item.total_price
                    } for item in order_items
                ],
                "subtotal": subtotal,
                "shipping_cost": shipping_cost,
                "tax": tax,
                "total": total,
                "status": order.status.value,
                "shipping_address": delivery_address,
                "estimated_delivery": order.estimated_delivery,
                "created_at": order.created_at
            }
            
            # Update order status to confirmed
            order.status = OrderStatus.CONFIRMED
            order.updated_at = time.time()
            
            result = {
                "order_created": True,
                "order": order_data,
                "success": True
            }
            
            # Update workflow context
            self.update_workflow_context(context, {
                "created_order": order_data,
                "order_id": order_id
            })
            
            logger.info(f"Created order {order_id} for customer {customer_id} with total ${total:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Order creation failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _get_order_details(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Get order details by order ID"""
        order_id = data.get("order_id")
        
        if not order_id:
            return {"error": "Order ID required", "success": False}
        
        try:
            # Check local storage first
            if order_id in self.orders:
                order = self.orders[order_id]
                
                order_details = {
                    "order_id": order.order_id,
                    "customer_id": order.customer_id,
                    "items": [
                        {
                            "product_id": item.product_id,
                            "product_name": item.product_name,
                            "quantity": item.quantity,
                            "unit_price": item.unit_price,
                            "total_price": item.total_price
                        } for item in order.items
                    ],
                    "subtotal": order.subtotal,
                    "shipping_cost": order.shipping_cost,
                    "tax": order.tax,
                    "total": order.total,
                    "status": order.status.value,
                    "shipping_address": order.shipping_address,
                    "billing_address": order.billing_address,
                    "payment_method": order.payment_method,
                    "created_at": order.created_at,
                    "updated_at": order.updated_at,
                    "estimated_delivery": order.estimated_delivery,
                    "tracking_number": order.tracking_number
                }
                
                result = {
                    "order": order_details,
                    "success": True
                }
                
                # Update workflow context
                self.update_workflow_context(context, {
                    "order_details": order_details
                })
                
                return result
            
            # Try to get from traditional API
            try:
                orders_response = await self.mcp_tools.get_customer_orders(
                    customer_id=context.customer_id or "1",
                    limit=100
                )
                
                orders = orders_response.get("orders", [])
                order = next((o for o in orders if str(o.get("id")) == order_id), None)
                
                if order:
                    result = {
                        "order": order,
                        "success": True
                    }
                    
                    self.update_workflow_context(context, {
                        "order_details": order
                    })
                    
                    return result
                    
            except Exception as e:
                logger.warning(f"Could not fetch from traditional API: {e}")
            
            return {"error": f"Order {order_id} not found", "success": False}
            
        except Exception as e:
            logger.error(f"Failed to get order details: {e}")
            return {"error": str(e), "success": False}
    
    async def _update_order(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Update order details (e.g., address, items)"""
        order_id = data.get("order_id") or context.agent_data.get("order_agent", {}).get("order_id")
        updates = data.get("updates", {})
        
        if not order_id:
            return {"error": "Order ID required", "success": False}
        
        try:
            if order_id not in self.orders:
                return {"error": f"Order {order_id} not found", "success": False}
            
            order = self.orders[order_id]
            
            # Update allowed fields
            if "shipping_address" in updates:
                order.shipping_address = updates["shipping_address"]
                logger.info(f"Updated shipping address for order {order_id}")
            
            if "estimated_delivery" in updates:
                order.estimated_delivery = updates["estimated_delivery"]
                logger.info(f"Updated delivery estimate for order {order_id}")
            
            if "shipping_cost" in updates:
                old_total = order.total
                order.shipping_cost = float(updates["shipping_cost"])
                order.total = order.subtotal + order.shipping_cost + order.tax
                logger.info(f"Updated shipping cost for order {order_id}: ${old_total:.2f} -> ${order.total:.2f}")
            
            order.updated_at = time.time()
            
            # Create updated order data
            updated_order = {
                "order_id": order.order_id,
                "customer_id": order.customer_id,
                "total": order.total,
                "shipping_cost": order.shipping_cost,
                "shipping_address": order.shipping_address,
                "estimated_delivery": order.estimated_delivery,
                "updated_at": order.updated_at,
                "updates_applied": list(updates.keys())
            }
            
            result = {
                "order_updated": True,
                "order": updated_order,
                "changes": updates,
                "success": True
            }
            
            # Update workflow context
            self.update_workflow_context(context, {
                "updated_order": updated_order,
                "order_changes": updates
            })
            
            logger.info(f"Successfully updated order {order_id}")
            return result
            
        except Exception as e:
            logger.error(f"Order update failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _update_order_status(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Update order status"""
        order_id = data.get("order_id")
        new_status = data.get("status")
        
        if not order_id or not new_status:
            return {"error": "Order ID and status required", "success": False}
        
        try:
            if order_id not in self.orders:
                return {"error": f"Order {order_id} not found", "success": False}
            
            order = self.orders[order_id]
            old_status = order.status.value
            
            # Validate status transition
            try:
                new_status_enum = OrderStatus(new_status)
                order.status = new_status_enum
                order.updated_at = time.time()
                
                result = {
                    "status_updated": True,
                    "order_id": order_id,
                    "old_status": old_status,
                    "new_status": new_status,
                    "updated_at": order.updated_at,
                    "success": True
                }
                
                self.update_workflow_context(context, {
                    "status_update": result
                })
                
                logger.info(f"Updated order {order_id} status: {old_status} -> {new_status}")
                return result
                
            except ValueError:
                return {"error": f"Invalid status: {new_status}", "success": False}
            
        except Exception as e:
            logger.error(f"Status update failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _cancel_order(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Cancel an order"""
        order_id = data.get("order_id")
        reason = data.get("reason", "Customer requested cancellation")
        
        if not order_id:
            return {"error": "Order ID required", "success": False}
        
        try:
            if order_id not in self.orders:
                return {"error": f"Order {order_id} not found", "success": False}
            
            order = self.orders[order_id]
            
            # Check if order can be cancelled
            if order.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
                return {"error": f"Cannot cancel order in {order.status.value} status", "success": False}
            
            order.status = OrderStatus.CANCELLED
            order.updated_at = time.time()
            
            result = {
                "order_cancelled": True,
                "order_id": order_id,
                "reason": reason,
                "cancelled_at": order.updated_at,
                "success": True
            }
            
            self.update_workflow_context(context, {
                "cancellation": result
            })
            
            logger.info(f"Cancelled order {order_id}: {reason}")
            return result
            
        except Exception as e:
            logger.error(f"Order cancellation failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _calculate_totals(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Calculate order totals (subtotal, tax, shipping, total)"""
        items = data.get("items", [])
        shipping_cost = data.get("shipping_cost", 0.0)
        tax_rate = data.get("tax_rate", 0.085)  # 8.5% default
        
        try:
            subtotal = 0.0
            
            for item in items:
                quantity = item.get("quantity", 1)
                unit_price = float(item.get("unit_price", 0))
                subtotal += quantity * unit_price
            
            tax = subtotal * tax_rate
            total = subtotal + shipping_cost + tax
            
            calculation = {
                "subtotal": round(subtotal, 2),
                "shipping_cost": round(shipping_cost, 2),
                "tax": round(tax, 2),
                "tax_rate": tax_rate,
                "total": round(total, 2)
            }
            
            result = {
                "calculation": calculation,
                "success": True
            }
            
            self.update_workflow_context(context, {
                "order_totals": calculation
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Total calculation failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _get_order_history(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Get order history for a customer"""
        customer_id = data.get("customer_id") or context.customer_id
        limit = data.get("limit", 10)
        
        if not customer_id:
            return {"error": "Customer ID required", "success": False}
        
        try:
            # Get orders from local storage
            customer_orders = [
                order for order in self.orders.values() 
                if order.customer_id == customer_id
            ]
            
            # Sort by creation date (newest first)
            customer_orders.sort(key=lambda x: x.created_at, reverse=True)
            
            # Limit results
            customer_orders = customer_orders[:limit]
            
            # Convert to dict format
            order_history = []
            for order in customer_orders:
                order_summary = {
                    "order_id": order.order_id,
                    "total": order.total,
                    "status": order.status.value,
                    "created_at": order.created_at,
                    "item_count": len(order.items)
                }
                order_history.append(order_summary)
            
            result = {
                "order_history": order_history,
                "customer_id": customer_id,
                "total_orders": len(order_history),
                "success": True
            }
            
            self.update_workflow_context(context, {
                "order_history": order_history
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get order history: {e}")
            return {"error": str(e), "success": False}
    
    def get_capabilities_description(self) -> Dict[str, str]:
        """Get human-readable description of order agent capabilities"""
        return {
            "create_order": "Create new orders with items, pricing, and customer details",
            "get_order_details": "Retrieve complete order information by order ID", 
            "update_order": "Update order details like shipping address or delivery",
            "update_order_status": "Update order status (pending, confirmed, shipped, etc.)",
            "cancel_order": "Cancel orders with reason tracking",
            "calculate_totals": "Calculate order subtotals, tax, shipping, and totals",
            "get_order_history": "Retrieve customer order history and summaries"
        }