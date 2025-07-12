"""
Product Agent
Specialized agent for product catalog management, inventory checking, and product recommendations
"""
import sys
import os
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from loguru import logger

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from .base_agent import BaseAgent, AgentCapability, AgentMessage, WorkflowContext
from tools.mcp_tools import MCPTools


@dataclass
class ProductSearchResult:
    """Result from product search"""
    id: str
    name: str
    price: float
    category: str
    in_stock: bool
    stock_quantity: int
    variants: List[Dict[str, Any]]
    estimated_delivery: str


@dataclass
class InventoryReservation:
    """Inventory reservation details"""
    product_id: str
    quantity: int
    reserved_until: float
    reservation_id: str


class ProductAgent(BaseAgent):
    """Agent specialized in product catalog and inventory management"""
    
    def __init__(self, traditional_api_url: str = "http://localhost:4000"):
        capabilities = {
            AgentCapability.PRODUCT_SEARCH,
            AgentCapability.INVENTORY_CHECK
        }
        super().__init__("product_agent", capabilities)
        
        # Initialize MCP tools for product operations
        self.mcp_tools = MCPTools(traditional_api_url)
        
        # Inventory reservations (in-memory for demo)
        self.reservations: Dict[str, InventoryReservation] = {}
        
        # System prompt for declarative behavior
        self.system_prompt = """
        You are a Product Agent specialized in product catalog and inventory management.
        
        Core Capabilities:
        - Product search and discovery using MCP tools
        - Inventory checking and availability validation
        - Product recommendations based on user preferences
        - Inventory reservation for order processing
        
        Behavioral Guidelines:
        - Always use MCP tools for product data operations
        - Provide accurate product information and pricing
        - Handle inventory checks with real-time data
        - Make intelligent recommendations based on search queries
        - Maintain inventory reservations for order flow
        
        MCP Tools Available:
        - search_products: Find products by query with filtering
        - get_products: Get all products with optional filters
        - get_product_by_id: Get specific product details
        - get_categories: Get all product categories
        
        Product Categories:
        - Smartphones: iPhone, Samsung Galaxy, Google Pixel
        - Laptops: MacBook, ThinkPad, Surface, Dell
        - Headphones: AirPods, Sony, Bose  
        - Tablets: iPad, Surface, Galaxy Tab
        """
        
    async def process_request(self, message: AgentMessage, context: WorkflowContext) -> Dict[str, Any]:
        """Process product-related requests"""
        action = message.action
        data = message.data
        
        try:
            if action == "search_product":
                return await self._search_product(data, context)
            elif action == "check_inventory":
                return await self._check_inventory(data, context)
            elif action == "check_availability":
                return await self._check_availability(data, context)
            elif action == "reserve_inventory":
                return await self._reserve_inventory(data, context)
            elif action == "get_product_details":
                return await self._get_product_details(data, context)
            elif action == "recommend_products":
                return await self._recommend_products(data, context)
            else:
                raise ValueError(f"Unknown action: {action}")
                
        except Exception as e:
            logger.error(f"Product agent failed to process {action}: {e}")
            return {"error": str(e), "success": False}
    
    async def _search_product(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Search for products based on query"""
        query = data.get("product_query", context.user_query)
        limit = data.get("limit", 10)
        
        logger.info(f"Searching products for query: {query}")
        
        try:
            # Use MCP tools to search products
            search_results = await self.mcp_tools.search_products(
                query=query,
                limit=limit,
                category=data.get("category"),
                min_price=data.get("min_price"),
                max_price=data.get("max_price")
            )
            
            # Enhance results with stock information
            enhanced_results = []
            for product in search_results.get("products", []):
                enhanced_product = {
                    "id": product["id"],
                    "name": product["name"],
                    "price": product["price"],
                    "category": product.get("category", ""),
                    "description": product.get("description", ""),
                    "image_url": product.get("image_url", ""),
                    "in_stock": product.get("stock_quantity", 0) > 0,
                    "stock_quantity": product.get("stock_quantity", 0)
                }
                enhanced_results.append(enhanced_product)
            
            result = {
                "products": enhanced_results,
                "total_found": len(enhanced_results),
                "query": query,
                "success": True
            }
            
            # Update workflow context
            self.update_workflow_context(context, {
                "search_results": enhanced_results,
                "search_query": query
            })
            
            logger.info(f"Found {len(enhanced_results)} products for query: {query}")
            return result
            
        except Exception as e:
            logger.error(f"Product search failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _check_inventory(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Check inventory for specific products"""
        # Get products from previous search or specific product IDs
        products = data.get("products") or context.agent_data.get("product_agent", {}).get("search_results", [])
        
        if not products:
            return {"error": "No products specified for inventory check", "success": False}
        
        inventory_status = []
        
        for product in products:
            product_id = product.get("id") if isinstance(product, dict) else product
            
            try:
                # Get detailed product info including stock
                product_details = await self.mcp_tools.get_product_by_id(product_id)
                
                if product_details:
                    stock_info = {
                        "product_id": product_id,
                        "name": product_details.get("name", ""),
                        "in_stock": product_details.get("stock_quantity", 0) > 0,
                        "stock_quantity": product_details.get("stock_quantity", 0),
                        "reserved_quantity": sum(
                            r.quantity for r in self.reservations.values() 
                            if r.product_id == product_id
                        ),
                        "available_quantity": max(0, product_details.get("stock_quantity", 0) - sum(
                            r.quantity for r in self.reservations.values() 
                            if r.product_id == product_id
                        ))
                    }
                    inventory_status.append(stock_info)
                    
            except Exception as e:
                logger.error(f"Failed to check inventory for product {product_id}: {e}")
                inventory_status.append({
                    "product_id": product_id,
                    "error": str(e),
                    "in_stock": False
                })
        
        result = {
            "inventory_status": inventory_status,
            "total_checked": len(inventory_status),
            "success": True
        }
        
        # Update workflow context
        self.update_workflow_context(context, {
            "inventory_status": inventory_status
        })
        
        logger.info(f"Checked inventory for {len(inventory_status)} products")
        return result
    
    async def _check_availability(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Check product availability with detailed information"""
        # First search for the product
        search_result = await self._search_product(data, context)
        
        if not search_result.get("success"):
            return search_result
        
        products = search_result.get("products", [])
        
        if not products:
            return {
                "available": False,
                "message": "Product not found",
                "success": True
            }
        
        # Check inventory for found products
        inventory_result = await self._check_inventory({"products": products}, context)
        
        availability_info = []
        for product in products:
            # Find corresponding inventory status
            inventory_item = next(
                (item for item in inventory_result.get("inventory_status", []) 
                 if item["product_id"] == product["id"]), 
                None
            )
            
            if inventory_item:
                availability_info.append({
                    "product": product,
                    "availability": {
                        "in_stock": inventory_item["in_stock"],
                        "quantity_available": inventory_item.get("available_quantity", 0),
                        "estimated_restock": "2-3 days" if not inventory_item["in_stock"] else None
                    }
                })
        
        result = {
            "availability": availability_info,
            "success": True
        }
        
        # Update workflow context
        self.update_workflow_context(context, {
            "availability_info": availability_info
        })
        
        return result
    
    async def _reserve_inventory(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Reserve inventory for a customer"""
        import time
        import uuid
        
        product_id = data.get("product_id")
        quantity = data.get("quantity", 1)
        customer_id = data.get("customer_id") or context.customer_id
        
        if not product_id:
            return {"error": "Product ID required for reservation", "success": False}
        
        try:
            # Check current availability
            inventory_check = await self._check_inventory({"products": [product_id]}, context)
            
            if not inventory_check.get("success"):
                return {"error": "Failed to check inventory", "success": False}
            
            inventory_status = inventory_check.get("inventory_status", [])
            if not inventory_status:
                return {"error": "Product not found", "success": False}
            
            available_quantity = inventory_status[0].get("available_quantity", 0)
            
            if available_quantity < quantity:
                return {
                    "error": f"Insufficient inventory. Available: {available_quantity}, Requested: {quantity}",
                    "success": False
                }
            
            # Create reservation
            reservation_id = str(uuid.uuid4())
            reservation = InventoryReservation(
                product_id=product_id,
                quantity=quantity,
                reserved_until=time.time() + 900,  # 15 minutes
                reservation_id=reservation_id
            )
            
            self.reservations[reservation_id] = reservation
            
            result = {
                "reservation_id": reservation_id,
                "product_id": product_id,
                "quantity": quantity,
                "reserved_until": reservation.reserved_until,
                "success": True
            }
            
            # Update workflow context
            self.update_workflow_context(context, {
                "inventory_reservation": result
            })
            
            logger.info(f"Reserved {quantity} units of product {product_id} for customer {customer_id}")
            return result
            
        except Exception as e:
            logger.error(f"Inventory reservation failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _get_product_details(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Get detailed product information"""
        product_id = data.get("product_id")
        
        if not product_id:
            return {"error": "Product ID required", "success": False}
        
        try:
            product_details = await self.mcp_tools.get_product_by_id(product_id)
            
            if not product_details:
                return {"error": "Product not found", "success": False}
            
            # Enhance with availability info
            enhanced_details = {
                **product_details,
                "availability": {
                    "in_stock": product_details.get("stock_quantity", 0) > 0,
                    "stock_quantity": product_details.get("stock_quantity", 0),
                    "reserved_quantity": sum(
                        r.quantity for r in self.reservations.values() 
                        if r.product_id == product_id
                    )
                }
            }
            
            result = {
                "product": enhanced_details,
                "success": True
            }
            
            # Update workflow context
            self.update_workflow_context(context, {
                "product_details": enhanced_details
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get product details: {e}")
            return {"error": str(e), "success": False}
    
    async def _recommend_products(self, data: Dict[str, Any], context: WorkflowContext) -> Dict[str, Any]:
        """Recommend products based on query or category"""
        category = data.get("category")
        query = data.get("query", context.user_query)
        limit = data.get("limit", 5)
        
        try:
            recommendations = []
            
            # Simple recommendation logic based on categories
            if category and category.lower() in self.product_categories:
                for brand in self.product_categories[category.lower()]:
                    search_result = await self._search_product(
                        {"product_query": brand, "limit": 2}, 
                        context
                    )
                    if search_result.get("success"):
                        recommendations.extend(search_result.get("products", [])[:2])
            else:
                # Fallback to general search
                search_result = await self._search_product(
                    {"product_query": query, "limit": limit}, 
                    context
                )
                if search_result.get("success"):
                    recommendations = search_result.get("products", [])
            
            result = {
                "recommendations": recommendations[:limit],
                "based_on": category or query,
                "success": True
            }
            
            # Update workflow context
            self.update_workflow_context(context, {
                "recommendations": recommendations[:limit]
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Product recommendation failed: {e}")
            return {"error": str(e), "success": False}
    
    def get_capabilities_description(self) -> Dict[str, str]:
        """Get human-readable description of product agent capabilities"""
        return {
            "product_search": "Search products by name, category, or keywords",
            "inventory_check": "Check real-time inventory levels and availability",
            "check_availability": "Comprehensive availability check with details",
            "reserve_inventory": "Reserve products for customers during checkout",
            "get_product_details": "Get detailed product information and specifications",
            "recommend_products": "Provide product recommendations based on preferences"
        }