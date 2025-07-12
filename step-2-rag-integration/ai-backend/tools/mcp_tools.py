"""
MCP Tools for Step 2 - RAG Integration
Enhanced version with additional capabilities
"""
import httpx
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class MCPTools:
    """Enhanced MCP tools for e-commerce operations"""
    
    def __init__(self, traditional_api_url: str = "http://localhost:4000"):
        self.api_url = traditional_api_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def search_products(self, query: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Search for products by query with enhanced filtering"""
        try:
            response = await self.client.get(f"{self.api_url}/api/products")
            if response.status_code != 200:
                return {"success": False, "error": "Failed to fetch products"}
            
            products = response.json()
            
            # Enhanced search logic
            matching_products = []
            query_lower = query.lower()
            
            for product in products:
                name = product.get('name', '').lower()
                description = product.get('description', '').lower()
                brand = product.get('brand', '').lower()
                category = product.get('category', '').lower()
                
                # Check for matches
                if (query_lower in name or 
                    query_lower in description or 
                    query_lower in brand or
                    query_lower in category):
                    matching_products.append(product)
            
            # Apply additional filters if provided
            if filters:
                if 'category' in filters:
                    matching_products = [p for p in matching_products 
                                       if p.get('category', '').lower() == filters['category'].lower()]
                if 'brand' in filters:
                    matching_products = [p for p in matching_products 
                                       if p.get('brand', '').lower() == filters['brand'].lower()]
                if 'max_price' in filters:
                    matching_products = [p for p in matching_products 
                                       if p.get('price', 0) <= filters['max_price']]
                if 'min_price' in filters:
                    matching_products = [p for p in matching_products 
                                       if p.get('price', 0) >= filters['min_price']]
            
            return {
                "success": True,
                "data": matching_products,
                "count": len(matching_products),
                "query": query,
                "filters": filters or {}
            }
        except Exception as e:
            logger.error(f"Product search failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_products(self, category_id: Optional[int] = None, brand: Optional[str] = None, 
                          limit: Optional[int] = None, offset: Optional[int] = None) -> Dict[str, Any]:
        """Get all products with enhanced filtering and pagination"""
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
            
            # Apply pagination
            total_count = len(products)
            if offset:
                products = products[offset:]
            if limit:
                products = products[:limit]
            
            return {
                "success": True,
                "data": products,
                "count": len(products),
                "total_count": total_count,
                "filters": {
                    "category_id": category_id,
                    "brand": brand,
                    "limit": limit,
                    "offset": offset
                }
            }
        except Exception as e:
            logger.error(f"Get products failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_customers(self, limit: Optional[int] = None, search: Optional[str] = None) -> Dict[str, Any]:
        """Get customers with search and pagination"""
        try:
            response = await self.client.get(f"{self.api_url}/api/customers")
            if response.status_code != 200:
                return {"success": False, "error": "Failed to fetch customers"}
            
            customers = response.json()
            
            # Apply search filter
            if search:
                search_lower = search.lower()
                customers = [c for c in customers 
                           if search_lower in c.get('name', '').lower() or 
                              search_lower in c.get('email', '').lower()]
            
            # Apply limit
            total_count = len(customers)
            if limit:
                customers = customers[:limit]
            
            return {
                "success": True,
                "data": customers,
                "count": len(customers),
                "total_count": total_count,
                "search": search,
                "limit": limit
            }
        except Exception as e:
            logger.error(f"Get customers failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_customer_orders(self, customer_id: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """Get orders for a specific customer with pagination"""
        try:
            response = await self.client.get(f"{self.api_url}/api/customers/{customer_id}/orders")
            if response.status_code != 200:
                return {"success": False, "error": f"Failed to fetch orders for customer {customer_id}"}
            
            orders = response.json()
            
            # Apply limit
            total_count = len(orders)
            if limit:
                orders = orders[:limit]
            
            return {
                "success": True,
                "data": orders,
                "count": len(orders),
                "total_count": total_count,
                "customer_id": customer_id,
                "limit": limit
            }
        except Exception as e:
            logger.error(f"Get customer orders failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_order(self, customer_id: str, product_id: str, quantity: int = 1, 
                          shipping_address: str = None, payment_method: str = "Credit Card",
                          special_instructions: str = None) -> Dict[str, Any]:
        """Create a new order with enhanced options"""
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
                "orderDate": "2024-01-15",  # Enhanced with current date
                "totalAmount": total_amount,
                "status": "Pending",
                "shippingAddress": shipping_address or "Default Address",
                "paymentMethod": payment_method,
                "specialInstructions": special_instructions,
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
                "total_amount": total_amount,
                "product_details": {
                    "name": product.get('name'),
                    "price": unit_price,
                    "quantity": quantity
                }
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
    
    async def get_product_by_id(self, product_id: str) -> Dict[str, Any]:
        """Get specific product by ID"""
        try:
            response = await self.client.get(f"{self.api_url}/api/products")
            if response.status_code != 200:
                return {"success": False, "error": "Failed to fetch products"}
            
            products = response.json()
            product = next((p for p in products if p.get("id") == product_id), None)
            
            if not product:
                return {"success": False, "error": f"Product {product_id} not found"}
            
            return {
                "success": True,
                "data": product,
                "product_id": product_id
            }
        except Exception as e:
            logger.error(f"Get product by ID failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_customer_by_id(self, customer_id: str) -> Dict[str, Any]:
        """Get specific customer by ID"""
        try:
            response = await self.client.get(f"{self.api_url}/api/customers")
            if response.status_code != 200:
                return {"success": False, "error": "Failed to fetch customers"}
            
            customers = response.json()
            customer = next((c for c in customers if c.get("id") == customer_id), None)
            
            if not customer:
                return {"success": False, "error": f"Customer {customer_id} not found"}
            
            return {
                "success": True,
                "data": customer,
                "customer_id": customer_id
            }
        except Exception as e:
            logger.error(f"Get customer by ID failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()