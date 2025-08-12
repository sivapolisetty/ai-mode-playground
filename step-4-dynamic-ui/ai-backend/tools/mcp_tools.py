"""
MCP Tools for Step 4 - Dynamic UI Generation
Enhanced with UI component library capabilities
"""
import httpx
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from .component_scanner import ComponentScanner
from .component_cache import ComponentCache, ComponentWatcher
from shared.observability.langfuse_decorator import trace_tool_execution, observe

logger = logging.getLogger(__name__)

class MCPTools:
    """Enhanced MCP tools with UI component capabilities"""
    
    def __init__(self, traditional_api_url: str = "http://localhost:4000", client_components_path: str = None):
        self.api_url = traditional_api_url
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Initialize component scanning system
        if client_components_path is None:
            # Default path relative to this project
            client_components_path = os.path.join(
                os.path.dirname(__file__), 
                "../../../client/src/components/ui"
            )
        
        self.components_path = Path(client_components_path).resolve()
        self.component_scanner = ComponentScanner(str(self.components_path))
        self.component_cache = ComponentCache()
        
        # Initialize file watcher for automatic cache invalidation
        self.component_watcher = ComponentWatcher(self.component_cache, self.components_path)
        
        logger.info(f"Initialized MCP tools with component path: {self.components_path}")
    
    def _extract_product_terms(self, query: str) -> List[str]:
        """Extract relevant product terms from natural language query, excluding price and constraint terms"""
        import re
        
        # Common stop words and question words to remove
        stop_words = {
            'what', "what's", 'is', 'the', 'price', 'of', 'how', 'much', 'does', 'cost', 
            'show', 'me', 'find', 'search', 'for', 'get', 'buy', 'purchase',
            'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'from',
            'about', 'do', 'you', 'have', 'any', 'can', 'i', 'want', 'need',
            'where', 'when', 'which', 'who', 'why', 'are', 'was', 'were', 'be',
            # Add price constraint words to stop words
            'under', 'below', 'less', 'than', 'up', 'within', 'maximum', 'max',
            'over', 'above', 'more', 'minimum', 'min', 'between'
        }
        
        # Remove price expressions (like $2000, $1,500, etc.)
        query_clean = re.sub(r'\$[\d,]+(?:\.\d{2})?', '', query)
        
        # Split query into words and remove stop words
        words = query_clean.lower().replace('?', '').replace(',', '').split()
        product_terms = [word for word in words if word not in stop_words and len(word) > 1]
        
        return product_terms
    
    def _extract_price_constraints(self, query: str) -> Dict[str, float]:
        """Extract price constraints from natural language query"""
        import re
        constraints = {}
        
        # Look for price amounts in the query
        price_matches = re.findall(r'\$?([\d,]+(?:\.\d{2})?)', query)
        
        if price_matches:
            # Convert to float, removing commas
            price_value = float(price_matches[0].replace(',', ''))
            
            # Determine if it's a max or min constraint based on context
            query_lower = query.lower()
            if any(word in query_lower for word in ['under', 'below', 'less than', 'up to', 'maximum', 'max']):
                constraints['max_price'] = price_value
            elif any(word in query_lower for word in ['over', 'above', 'more than', 'minimum', 'min']):
                constraints['min_price'] = price_value
            elif 'between' in query_lower:
                # Handle "between X and Y" - this is more complex, for now just use as max
                constraints['max_price'] = price_value
                
        return constraints

    @observe(as_type="span")
    async def search_products(self, query: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Search for products by query with enhanced filtering"""
        try:
            response = await self.client.get(f"{self.api_url}/api/products")
            if response.status_code != 200:
                return {"success": False, "error": "Failed to fetch products"}
            
            products = response.json()
            
            # Enhanced search logic with term extraction and price constraints
            matching_products = []
            query_lower = query.lower()
            product_terms = self._extract_product_terms(query)
            price_constraints = self._extract_price_constraints(query)
            
            # Add semantic expansion for common product categories
            if 'laptop' in query_lower or 'laptops' in query_lower:
                product_terms.extend(['macbook', 'notebook', 'computer'])
            if 'phone' in query_lower or 'phones' in query_lower:
                product_terms.extend(['iphone', 'smartphone'])
            if 'headphone' in query_lower or 'headphones' in query_lower:
                product_terms.extend(['earphone', 'headset', 'audio'])
            
            logger.info(f"🔍 Search expanded terms: {product_terms}")
            logger.info(f"💰 Price constraints: {price_constraints}")
            
            for product in products:
                name = product.get('name', '').lower()
                description = product.get('description', '').lower()
                brand = product.get('brand', '').lower()
                category = product.get('category', '').lower()
                model = product.get('model', '').lower() if product.get('model') else ''
                
                # Check for exact substring match first (for simple queries)
                exact_match = (query_lower in name or 
                              query_lower in description or 
                              query_lower in brand or
                              query_lower in category)
                
                # Check for term-based matching (for natural language queries)
                term_matches = 0
                if product_terms:
                    product_text = f"{name} {description} {brand} {category} {model}"
                    for term in product_terms:
                        if term in product_text:
                            term_matches += 1
                
                # Improved matching logic: 
                # - If we have product terms, require at least 1 match (not 60% of total terms including irrelevant ones)
                # - If no product terms, fall back to exact match
                product_match = False
                if product_terms:
                    # Require at least 1 term match if we have relevant product terms
                    product_match = term_matches > 0
                else:
                    # If no specific product terms, use exact substring matching
                    product_match = exact_match
                
                if product_match:
                    matching_products.append(product)
            
            # Apply price constraints extracted from query
            if price_constraints:
                if 'max_price' in price_constraints:
                    matching_products = [p for p in matching_products 
                                       if p.get('price', 0) <= price_constraints['max_price']]
                if 'min_price' in price_constraints:
                    matching_products = [p for p in matching_products 
                                       if p.get('price', 0) >= price_constraints['min_price']]
            
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
                "filters": filters or {},
                "extracted_constraints": price_constraints,
                "search_terms": product_terms
            }
        except Exception as e:
            logger.error(f"Product search failed: {e}")
            return {"success": False, "error": str(e)}
    
    @observe(as_type="span")
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
    
    @trace_tool_execution("get_customer_info")
    @observe(as_type="span")
    async def get_customer_info(self, customer_id: str) -> Dict[str, Any]:
        """Get detailed customer information"""
        try:
            # Since the API doesn't have individual customer endpoint, get all customers and filter
            response = await self.client.get(f"{self.api_url}/api/customers")
            if response.status_code == 200:
                customers = response.json()
                customer = next((c for c in customers if c.get("id") == customer_id), None)
                if customer:
                    return {"success": True, "data": customer}
                else:
                    return {"success": False, "error": "Customer not found"}
            else:
                return {"success": False, "error": f"Failed to fetch customers: {response.status_code}"}
        except Exception as e:
            logger.error(f"Get customer info failed: {e}")
            return {"success": False, "error": str(e)}
    
    @observe(as_type="span")
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
    
    @observe(as_type="span")
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
    
    @observe(as_type="span")
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
    
    @observe(as_type="span")
    async def get_order(self, order_id: str, customer_id: str = None) -> Dict[str, Any]:
        """Get detailed order information by searching through customer orders"""
        try:
            if customer_id:
                # Get orders for specific customer
                response = await self.client.get(f"{self.api_url}/api/customers/{customer_id}/orders")
                if response.status_code == 200:
                    orders = response.json()
                    order = next((o for o in orders if o.get("id") == order_id), None)
                    if order:
                        return {"success": True, "data": order}
                    else:
                        return {"success": False, "error": f"Order {order_id} not found for customer {customer_id}"}
            else:
                # If no customer_id provided, search through all customers (less efficient)
                customers_response = await self.client.get(f"{self.api_url}/api/customers")
                if customers_response.status_code == 200:
                    customers = customers_response.json()
                    for customer in customers:
                        orders_response = await self.client.get(f"{self.api_url}/api/customers/{customer['id']}/orders")
                        if orders_response.status_code == 200:
                            orders = orders_response.json()
                            order = next((o for o in orders if o.get("id") == order_id), None)
                            if order:
                                return {"success": True, "data": order}
                    return {"success": False, "error": f"Order {order_id} not found"}
            
            return {"success": False, "error": f"Failed to search for order: {response.status_code}"}
        except Exception as e:
            logger.error(f"Get order failed: {e}")
            return {"success": False, "error": str(e)}
    
    @observe(as_type="span")
    async def update_order(self, order_id: str, updates: Dict[str, Any], customer_id: str = None) -> Dict[str, Any]:
        """
        Update an existing order - Limited to cancellation since API doesn't support general updates
        
        Args:
            order_id: Order ID to update
            updates: Dict containing fields to update (currently only supports cancellation)
            customer_id: Customer ID to help locate the order
        
        Returns:
            Updated order information or error
        """
        try:
            # First check if order exists and can be modified
            order_response = await self.get_order(order_id, customer_id)
            if not order_response.get("success"):
                return order_response
            
            current_order = order_response["data"]
            
            # Check if order can be modified based on status
            if current_order.get("status") in ["shipped", "delivered", "cancelled"]:
                return {
                    "success": False, 
                    "error": f"Cannot modify order in {current_order['status']} status",
                    "current_status": current_order["status"]
                }
            
            # Since the API doesn't have general order update, we can only cancel
            if updates.get("status") == "cancelled" or "cancel" in str(updates).lower():
                return await self.cancel_order(order_id, updates.get("cancellation_reason", "Customer requested"))
            else:
                # For other updates like address changes, we would need to implement via the API
                # For now, return a message explaining the limitation
                return {
                    "success": False,
                    "error": "Order updates are limited. Currently only cancellation is supported via API. For address changes, please contact customer service.",
                    "current_order": current_order,
                    "requested_updates": updates
                }
                
        except Exception as e:
            logger.error(f"Update order failed: {e}")
            return {"success": False, "error": str(e)}
    
    @observe(as_type="span")
    async def cancel_order(self, order_id: str, reason: str = None) -> Dict[str, Any]:
        """Cancel an order with optional reason using the correct API endpoint"""
        try:
            # Use the correct cancel endpoint
            cancel_data = {}
            if reason:
                cancel_data["reason"] = reason
            
            response = await self.client.patch(
                f"{self.api_url}/api/orders/{order_id}/cancel",
                json=cancel_data
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json(),
                    "message": f"Order {order_id} cancelled successfully",
                    "reason": reason
                }
            elif response.status_code == 404:
                return {
                    "success": False,
                    "error": f"Order {order_id} not found"
                }
            elif response.status_code == 400:
                return {
                    "success": False,
                    "error": f"Cannot cancel order {order_id} - may already be shipped or delivered"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to cancel order: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Cancel order failed: {e}")
            return {"success": False, "error": str(e)}
    
    @trace_tool_execution("track_order")
    @observe(as_type="span")
    async def track_order(self, order_id: str, customer_id: str = None) -> Dict[str, Any]:
        """Get order tracking information"""
        try:
            order_response = await self.get_order(order_id, customer_id)
            if not order_response.get("success"):
                return order_response
            
            order = order_response["data"]
            
            # Generate tracking info based on order status
            tracking_info = {
                "order_id": order_id,
                "status": order.get("status", "unknown"),
                "created_at": order.get("created_at"),
                "updated_at": order.get("updated_at"),
                "estimated_delivery": order.get("estimated_delivery"),
                "tracking_number": order.get("tracking_number"),
                "carrier": order.get("carrier", "Standard Shipping")
            }
            
            # Add status-specific information
            if order["status"] == "shipped":
                tracking_info["shipped_date"] = order.get("shipped_date")
                tracking_info["tracking_url"] = f"https://track.example.com/{order.get('tracking_number', 'N/A')}"
            elif order["status"] == "delivered":
                tracking_info["delivered_date"] = order.get("delivered_date")
            
            return {
                "success": True,
                "data": tracking_info,
                "message": f"Order {order_id} is currently {order['status']}"
            }
            
        except Exception as e:
            logger.error(f"Track order failed: {e}")
            return {"success": False, "error": str(e)}
    
    @observe(as_type="span")
    async def update_customer(self, customer_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update customer information"""
        try:
            # First check if customer exists
            customer_response = await self.get_customer_info(customer_id)
            if not customer_response.get("success"):
                return customer_response
            
            # Send update request
            response = await self.client.patch(
                f"{self.api_url}/api/customers/{customer_id}",
                json=updates
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json(),
                    "message": f"Customer {customer_id} updated successfully",
                    "updated_fields": list(updates.keys())
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to update customer: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Update customer failed: {e}")
            return {"success": False, "error": str(e)}
    
    @observe(as_type="span")
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
    
    @observe(as_type="span")
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
    
    @observe(as_type="span")
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
    
    # ========================================
    # UI Component Library MCP Tools
    # ========================================
    
    @trace_tool_execution("get_component_library")
    @observe(as_type="span")
    async def get_component_library(self) -> Dict[str, Any]:
        """MCP Tool: Get complete UI component library information"""
        try:
            # Get current directory hash for cache validation
            current_hash = self.component_scanner.get_directory_hash()
            
            # Try to get from cache first
            cached_result = await self.component_cache.get_cached_components(
                self.components_path, current_hash
            )
            
            if cached_result:
                return cached_result
            
            # Cache miss - scan components
            scan_result = await self.component_scanner.scan_all_components()
            
            if scan_result.get("success"):
                # Save to cache for future use
                await self.component_cache.save_to_cache(
                    scan_result["data"], 
                    current_hash,
                    scan_result.get("metadata", {})
                )
                
                # Start file watcher if not already running
                if not self.component_watcher.is_watching:
                    await self.component_watcher.start_watching()
            
            return scan_result
            
        except Exception as e:
            logger.error(f"Component library scan failed: {e}")
            return {"success": False, "error": str(e)}
    
    @observe(as_type="span")
    async def get_component_schema(self, component_name: str) -> Dict[str, Any]:
        """MCP Tool: Get detailed schema for specific component"""
        try:
            # Get component library
            library_result = await self.get_component_library()
            
            if not library_result.get("success"):
                return library_result
            
            components = library_result["data"]
            
            if component_name not in components:
                available_components = list(components.keys())
                return {
                    "success": False,
                    "error": f"Component '{component_name}' not found",
                    "available_components": available_components,
                    "suggestion": self._find_similar_component(component_name, available_components)
                }
            
            component_info = components[component_name]
            
            # Enhance with LLM-friendly information
            enhanced_info = {
                "name": component_name,
                "category": component_info.get("category", "utility"),
                "exports": component_info.get("exports", []),
                "props": component_info.get("props", {}),
                "usage_patterns": component_info.get("usage_patterns", []),
                "descriptions": component_info.get("descriptions", {}),
                "recommended_use_cases": self._get_component_use_cases(component_name),
                "composition_examples": self._get_composition_examples(component_name, component_info)
            }
            
            return {
                "success": True,
                "data": enhanced_info,
                "source": library_result.get("source", "unknown")
            }
            
        except Exception as e:
            logger.error(f"Component schema fetch failed: {e}")
            return {"success": False, "error": str(e)}
    
    @observe(as_type="span")
    async def get_ui_patterns(self, intent: str) -> Dict[str, Any]:
        """MCP Tool: Get recommended UI patterns for specific intent"""
        try:
            # Define intent-to-component mappings
            intent_patterns = {
                "product_display": {
                    "single": ["card", "badge", "button"],
                    "multiple": ["card", "pagination", "input"],
                    "description": "Display product information with actions"
                },
                "product_search": {
                    "components": ["input", "button", "select", "checkbox"],
                    "layout": ["form", "accordion", "tabs"],
                    "description": "Search interface with filters and sorting"
                },
                "order_management": {
                    "components": ["table", "badge", "button", "dialog"],
                    "actions": ["alert-dialog", "toast"],
                    "description": "Order listing and management interface"
                },
                "checkout_flow": {
                    "components": ["form", "input", "button", "radio-group"],
                    "validation": ["alert", "progress"],
                    "description": "Multi-step checkout process"
                },
                "customer_profile": {
                    "components": ["form", "input", "textarea", "avatar"],
                    "layout": ["tabs", "card", "separator"],
                    "description": "Customer information management"
                }
            }
            
            # Get matching patterns
            matching_patterns = {}
            intent_lower = intent.lower()
            
            for pattern_name, pattern_info in intent_patterns.items():
                if intent_lower in pattern_name or any(word in pattern_name for word in intent_lower.split()):
                    matching_patterns[pattern_name] = pattern_info
            
            if not matching_patterns:
                # Fallback to general patterns
                matching_patterns = {
                    "general_form": {
                        "components": ["form", "input", "button", "card"],
                        "description": "General purpose form interface"
                    },
                    "general_display": {
                        "components": ["card", "button", "badge"],
                        "description": "General purpose content display"
                    }
                }
            
            return {
                "success": True,
                "data": {
                    "intent": intent,
                    "patterns": matching_patterns,
                    "recommendations": self._generate_pattern_recommendations(intent, matching_patterns)
                }
            }
            
        except Exception as e:
            logger.error(f"UI patterns fetch failed: {e}")
            return {"success": False, "error": str(e)}
    
    @observe(as_type="span")
    async def validate_component_spec(self, component_spec: Dict[str, Any]) -> Dict[str, Any]:
        """MCP Tool: Validate component specification against schema"""
        try:
            component_name = component_spec.get("component")
            
            if not component_name:
                return {
                    "success": False,
                    "error": "Component name is required",
                    "validation_errors": ["Missing 'component' field"]
                }
            
            # Get component schema
            schema_result = await self.get_component_schema(component_name)
            
            if not schema_result.get("success"):
                return schema_result
            
            schema = schema_result["data"]
            validation_errors = []
            warnings = []
            
            # Validate props
            spec_props = component_spec.get("props", {})
            schema_props = schema.get("props", {})
            
            # Check for unknown props
            for prop_name in spec_props:
                if prop_name not in schema_props:
                    warnings.append(f"Unknown prop '{prop_name}' for component '{component_name}'")
            
            # Check for required props (this would need to be enhanced based on actual schema)
            # For now, just basic validation
            
            return {
                "success": True,
                "data": {
                    "component": component_name,
                    "valid": len(validation_errors) == 0,
                    "validation_errors": validation_errors,
                    "warnings": warnings,
                    "schema_compliance": "partial"  # Would need full schema to determine
                }
            }
            
        except Exception as e:
            logger.error(f"Component validation failed: {e}")
            return {"success": False, "error": str(e)}
    
    @observe(as_type="span")
    async def get_cache_status(self) -> Dict[str, Any]:
        """MCP Tool: Get component cache status and statistics"""
        try:
            cache_info = await self.component_cache.get_cache_info()
            return {
                "success": True,
                "data": cache_info
            }
        except Exception as e:
            logger.error(f"Cache status failed: {e}")
            return {"success": False, "error": str(e)}
    
    @observe(as_type="span")
    async def refresh_component_cache(self) -> Dict[str, Any]:
        """MCP Tool: Force refresh component cache"""
        try:
            # Invalidate current cache
            await self.component_cache.invalidate_cache()
            
            # Perform fresh scan
            result = await self.get_component_library()
            
            return {
                "success": True,
                "data": {
                    "message": "Component cache refreshed successfully",
                    "components_found": len(result.get("data", {})) if result.get("success") else 0,
                    "refresh_timestamp": result.get("metadata", {}).get("scan_timestamp")
                }
            }
            
        except Exception as e:
            logger.error(f"Cache refresh failed: {e}")
            return {"success": False, "error": str(e)}
    
    # Helper methods for component tools
    def _find_similar_component(self, component_name: str, available_components: List[str]) -> Optional[str]:
        """Find similar component name for suggestions"""
        component_lower = component_name.lower()
        
        # Simple similarity check
        for available in available_components:
            if component_lower in available.lower() or available.lower() in component_lower:
                return available
        
        return None
    
    def _get_component_use_cases(self, component_name: str) -> List[str]:
        """Get recommended use cases for component"""
        use_cases = {
            "card": ["Product displays", "Information panels", "Content containers"],
            "button": ["Actions", "Form submissions", "Navigation"],
            "input": ["Form fields", "Search bars", "User input"],
            "dialog": ["Confirmations", "Forms", "Detailed views"],
            "table": ["Data display", "Order lists", "Product catalogs"],
            "form": ["User input", "Settings", "Registration"]
        }
        
        return use_cases.get(component_name, ["General purpose UI element"])
    
    def _get_composition_examples(self, component_name: str, component_info: Dict[str, Any]) -> List[str]:
        """Get composition examples for complex components"""
        if component_name == "card" and "CardHeader" in component_info.get("exports", []):
            return [
                "Card + CardHeader + CardContent + CardFooter",
                "Card + CardContent (simple content)",
                "Card + CardHeader + CardContent (header + content)"
            ]
        elif component_name == "form":
            return [
                "Form + Input + Button",
                "Form + Input + Select + Button",
                "Form + Textarea + Checkbox + Button"
            ]
        
        return []
    
    def _generate_pattern_recommendations(self, intent: str, patterns: Dict[str, Any]) -> List[str]:
        """Generate specific recommendations based on intent and patterns"""
        recommendations = []
        
        for pattern_name, pattern_info in patterns.items():
            components = pattern_info.get("components", [])
            if components:
                recommendations.append(
                    f"For {intent}, consider using: {', '.join(components[:3])}"
                )
        
        return recommendations
    
    async def close(self):
        """Close HTTP client and cleanup"""
        await self.client.aclose()
        if self.component_watcher:
            self.component_watcher.stop_watching()