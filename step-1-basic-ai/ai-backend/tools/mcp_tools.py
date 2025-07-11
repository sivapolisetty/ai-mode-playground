"""
MCP Tools for basic e-commerce operations
Simplified version without multi-agent complexity
"""
import httpx
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class MCPTools:
    """Basic MCP tools for e-commerce operations"""
    
    def __init__(self, traditional_api_url: str = "http://localhost:3000"):
        self.api_url = traditional_api_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def search_products(self, query: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Search for products by query"""
        try:
            response = await self.client.get(f"{self.api_url}/api/products")
            if response.status_code != 200:
                return {"success": False, "error": "Failed to fetch products"}
            
            products = response.json()
            
            # Simple search logic
            matching_products = []
            query_lower = query.lower()
            
            for product in products:
                name = product.get('name', '').lower()
                description = product.get('description', '').lower()
                brand = product.get('brand', '').lower()
                
                if (query_lower in name or 
                    query_lower in description or 
                    query_lower in brand):
                    matching_products.append(product)
            
            return {
                "success": True,
                "data": matching_products,
                "count": len(matching_products),
                "query": query
            }
        except Exception as e:
            logger.error(f"Product search failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_products(self, category_id: Optional[int] = None, brand: Optional[str] = None) -> Dict[str, Any]:
        """Get all products with optional filters"""
        try:
            response = await self.client.get(f"{self.api_url}/api/products")
            if response.status_code != 200:
                return {"success": False, "error": "Failed to fetch products"}
            
            products = response.json()
            
            # Apply filters
            if category_id:
                products = [p for p in products if p.get("categoryId") == category_id]
            
            if brand:
                products = [p for p in products if p.get("brand", "").lower() == brand.lower()]
            
            return {
                "success": True,
                "data": products,
                "count": len(products)
            }
        except Exception as e:
            logger.error(f"Get products failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_customers(self) -> Dict[str, Any]:
        """Get all customers"""
        try:
            response = await self.client.get(f"{self.api_url}/api/customers")
            if response.status_code != 200:
                return {"success": False, "error": "Failed to fetch customers"}
            
            customers = response.json()
            return {
                "success": True,
                "data": customers,
                "count": len(customers)
            }
        except Exception as e:
            logger.error(f"Get customers failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_customer_orders(self, customer_id: str) -> Dict[str, Any]:
        """Get orders for a specific customer"""
        try:
            response = await self.client.get(f"{self.api_url}/api/customers/{customer_id}/orders")
            if response.status_code != 200:
                return {"success": False, "error": f"Failed to fetch orders for customer {customer_id}"}
            
            orders = response.json()
            return {
                "success": True,
                "data": orders,
                "count": len(orders),
                "customer_id": customer_id
            }
        except Exception as e:
            logger.error(f"Get customer orders failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_order(self, customer_id: str, product_id: str, quantity: int = 1, 
                          shipping_address: str = None, payment_method: str = "Credit Card") -> Dict[str, Any]:
        """Create a new order"""
        try:
            # Get product details for pricing
            products_response = await self.client.get(f"{self.api_url}/api/products")
            if products_response.status_code != 200:
                return {"success": False, "error": "Failed to fetch product details"}
            
            products = products_response.json()
            product = next((p for p in products if p.get("id") == product_id), None)
            
            if not product:
                return {"success": False, "error": f"Product {product_id} not found"}
            
            # Calculate total
            unit_price = product.get("price", 0)
            total_amount = unit_price * quantity
            
            # Create order data
            order_data = {
                "customerId": customer_id,
                "orderDate": "2024-01-01",  # Simplified for demo
                "totalAmount": total_amount,
                "status": "Pending",
                "shippingAddress": shipping_address or "Default Address",
                "paymentMethod": payment_method,
                "items": [{
                    "productId": product_id,
                    "quantity": quantity,
                    "price": unit_price
                }]
            }
            
            # Create order
            response = await self.client.post(
                f"{self.api_url}/api/orders",
                json=order_data
            )
            
            if response.status_code not in [200, 201]:
                return {"success": False, "error": "Failed to create order"}
            
            created_order = response.json()
            return {
                "success": True,
                "data": created_order,
                "message": f"Order created successfully for {product.get('name')}",
                "order_id": created_order.get('id'),
                "total_amount": total_amount
            }
        except Exception as e:
            logger.error(f"Create order failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_categories(self) -> Dict[str, Any]:
        """Get all product categories"""
        try:
            response = await self.client.get(f"{self.api_url}/api/categories")
            if response.status_code != 200:
                return {"success": False, "error": "Failed to fetch categories"}
            
            categories = response.json()
            return {
                "success": True,
                "data": categories,
                "count": len(categories)
            }
        except Exception as e:
            logger.error(f"Get categories failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()