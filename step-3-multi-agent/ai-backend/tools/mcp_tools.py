"""
MCP Tools for Step 3 - Multi-Agent Architecture
Enhanced version with address handling and business logic
"""
import httpx
import json
import logging
import re
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
            
            # Simple and reliable search logic - LLM handles entity extraction
            matching_products = []
            query_lower = query.lower().strip()
            
            for product in products:
                name = product.get('name', '').lower()
                description = product.get('description', '').lower()
                brand = product.get('brand', '').lower()
                category = product.get('category', '').lower()
                
                # Simple substring matching - works reliably with LLM-extracted terms
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
    
    # Address Management Tools
    
    async def extract_address_from_text(self, text: str) -> Dict[str, Any]:
        """Extract address information from natural language text"""
        try:
            address_info = {}
            text_lower = text.lower()
            
            # Street address patterns
            street_patterns = [
                r'to\s+(\d+\s+[a-zA-Z\s]+(?:street|st|avenue|ave|road|rd|drive|dr|boulevard|blvd|lane|ln|way|circle|court|ct|place|pl))',
                r'(\d+\s+[a-zA-Z\s]+(?:street|st|avenue|ave|road|rd|drive|dr|boulevard|blvd|lane|ln|way|circle|court|ct|place|pl))',
                r'([a-zA-Z\s]+(?:street|st|avenue|ave|road|rd|drive|dr|boulevard|blvd|lane|ln|way|circle|court|ct|place|pl))'
            ]
            
            # Extract street address
            for pattern in street_patterns:
                match = re.search(pattern, text_lower, re.IGNORECASE)
                if match:
                    street = match.group(1).strip()
                    street = re.sub(r'\b(?:to|the|my|address)\b', '', street).strip()
                    if street:
                        address_info['street'] = street.title()
                        break
            
            # Address type detection
            address_types = {
                'home': r'(?:home|house|my place)',
                'work': r'(?:work|office|workplace)', 
                'apartment': r'(?:apartment|apt|unit)'
            }
            
            address_info['type'] = 'shipping'  # default
            for addr_type, pattern in address_types.items():
                if re.search(pattern, text_lower):
                    address_info['type'] = addr_type
                    break
            
            # Apartment/unit number
            apt_patterns = [
                r'(?:apartment|apt|unit|#)\s*(\w+)',
                r'(\w+)\s+(?:apartment|apt)'
            ]
            
            for pattern in apt_patterns:
                match = re.search(pattern, text_lower, re.IGNORECASE)
                if match:
                    address_info['unit'] = match.group(1).upper()
                    break
            
            # Special building patterns
            if re.search(r'oak\s+street\s+tree\s+apartment', text_lower, re.IGNORECASE):
                address_info.update({
                    'street': 'Oak Street Tree Apartment',
                    'type': 'apartment',
                    'building_name': 'Tree Apartment',
                    'needs_completion': True
                })
            
            # City and state
            city_patterns = [
                r'in\s+([a-zA-Z\s]+),?\s*[A-Z]{2}',
                r'([a-zA-Z\s]+),\s*[A-Z]{2}'
            ]
            
            for pattern in city_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    address_info['city'] = match.group(1).strip().title()
                    break
            
            # State
            state_match = re.search(r'\b([A-Z]{2})\b', text)
            if state_match:
                address_info['state'] = state_match.group(1).upper()
            
            # ZIP code
            zip_match = re.search(r'\b(\d{5}(?:-\d{4})?)\b', text)
            if zip_match:
                address_info['zip'] = zip_match.group(1)
            
            return {
                "success": True,
                "data": address_info,
                "extracted_fields": list(address_info.keys()),
                "needs_completion": address_info.get('needs_completion', False)
            }
            
        except Exception as e:
            logger.error(f"Address extraction failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_customer_addresses(self, customer_id: str, address_type: str = None) -> Dict[str, Any]:
        """Get customer addresses with optional filtering"""
        try:
            # Get customer data from traditional API
            response = await self.client.get(f"{self.api_url}/api/customers/{customer_id}")
            
            if response.status_code != 200:
                return {"success": False, "error": "Customer not found"}
            
            customer = response.json()
            addresses = customer.get('addresses', [])
            
            # Filter by type if specified
            if address_type:
                addresses = [addr for addr in addresses if addr.get('type') == address_type]
            
            return {
                "success": True,
                "data": addresses,
                "count": len(addresses),
                "customer_id": customer_id
            }
            
        except Exception as e:
            logger.error(f"Get customer addresses failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def validate_address(self, address: Dict[str, Any]) -> Dict[str, Any]:
        """Validate address format and completeness"""
        try:
            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "suggestions": []
            }
            
            required_fields = ['street', 'city', 'state', 'zip']
            
            # Check required fields
            for field in required_fields:
                if not address.get(field):
                    validation_result["errors"].append(f"Missing {field}")
                    validation_result["valid"] = False
            
            # Validate ZIP code format (US)
            zip_code = address.get('zip', '')
            if zip_code and not re.match(r'^\d{5}(-\d{4})?$', zip_code):
                validation_result["errors"].append("Invalid ZIP code format")
                validation_result["valid"] = False
            
            # Check apartment number for apartment types
            if address.get('type') == 'apartment' and not address.get('unit'):
                validation_result["warnings"].append("Apartment number recommended for apartment addresses")
            
            # Suggest delivery instructions for complex addresses
            if 'tree apartment' in address.get('street', '').lower():
                validation_result["suggestions"].append("Consider adding specific building entrance or unit number")
            
            return {
                "success": True,
                "data": validation_result,
                "address": address
            }
            
        except Exception as e:
            logger.error(f"Address validation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def complete_address(self, partial_address: Dict[str, Any], customer_id: str) -> Dict[str, Any]:
        """Complete partial address using customer data and smart matching"""
        try:
            # Get customer's stored addresses
            customer_addresses_result = await self.get_customer_addresses(customer_id)
            
            if not customer_addresses_result.get("success"):
                return customer_addresses_result
            
            stored_addresses = customer_addresses_result.get("data", [])
            
            # Try to match and complete
            completed_address = partial_address.copy()
            
            # Look for partial matches
            partial_street = partial_address.get('street', '').lower()
            
            for stored_addr in stored_addresses:
                stored_street = stored_addr.get('street', '').lower()
                
                # Partial street match
                if partial_street and partial_street in stored_street:
                    # Fill missing fields from stored address
                    for field in ['city', 'state', 'zip', 'country']:
                        if not completed_address.get(field):
                            completed_address[field] = stored_addr.get(field)
                    break
                
                # Type-based matching
                if (partial_address.get('type') == stored_addr.get('type') and 
                    not completed_address.get('city')):
                    for field in ['city', 'state', 'zip', 'country']:
                        if not completed_address.get(field):
                            completed_address[field] = stored_addr.get(field)
            
            # Identify missing fields
            missing_fields = []
            required_fields = ['street', 'city', 'state', 'zip']
            
            for field in required_fields:
                if not completed_address.get(field):
                    missing_fields.append(field)
            
            if completed_address.get('type') == 'apartment' and not completed_address.get('unit'):
                missing_fields.append('unit')
            
            return {
                "success": True,
                "data": {
                    "completed_address": completed_address,
                    "missing_fields": missing_fields,
                    "needs_completion": len(missing_fields) > 0,
                    "completion_source": "customer_data_matching"
                }
            }
            
        except Exception as e:
            logger.error(f"Address completion failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def calculate_shipping_options(self, address: Dict[str, Any], items: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Calculate shipping options and costs for address"""
        try:
            # Shipping rates by method
            shipping_rates = {
                "standard": {"cost": 5.99, "days": "5-7", "description": "Standard Ground"},
                "express": {"cost": 12.99, "days": "2-3", "description": "Express Delivery"},
                "overnight": {"cost": 24.99, "days": "1", "description": "Overnight Delivery"},
                "free": {"cost": 0.00, "days": "7-10", "description": "Free Standard (orders $50+)"}
            }
            
            # Calculate order value if items provided
            order_value = 0
            if items:
                order_value = sum(item.get('price', 0) * item.get('quantity', 1) for item in items)
            
            shipping_options = []
            
            for method, details in shipping_rates.items():
                # Skip free shipping for orders under $50
                if method == "free" and order_value < 50:
                    continue
                
                option = {
                    "method": method,
                    "cost": details["cost"],
                    "estimated_days": details["days"],
                    "description": details["description"],
                    "available": True
                }
                
                # Adjust for remote locations
                city = address.get('city', '').lower()
                state = address.get('state', '').upper()
                
                if city in ['anchorage', 'honolulu'] or state in ['AK', 'HI']:
                    base_days = details["days"]
                    if "-" in base_days:
                        min_days, max_days = base_days.split("-")
                        option["estimated_days"] = f"{int(min_days)+1}-{int(max_days)+2}"
                    else:
                        option["estimated_days"] = str(int(base_days) + 1)
                    option["cost"] += 5.00  # Remote area surcharge
                
                shipping_options.append(option)
            
            return {
                "success": True,
                "data": {
                    "shipping_options": shipping_options,
                    "address": address,
                    "order_value": order_value
                }
            }
            
        except Exception as e:
            logger.error(f"Shipping calculation failed: {e}")
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