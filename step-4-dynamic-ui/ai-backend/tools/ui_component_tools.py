"""
UI Component Tools for Enhanced Agent
Provides intelligent component selection and composition capabilities
"""
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from mcp_ui_server.component_scanner import ComponentScanner
from mcp_ui_server.types import ComponentType, BusinessDomain, ComponentMetadata

logger = logging.getLogger(__name__)

class UIComponentTools:
    """Intelligent UI component selection and generation tools"""
    
    def __init__(self, components_root: str = None):
        """Initialize UI component tools with scanner"""
        if components_root is None:
            # Default to client components directory
            components_root = str(Path(__file__).parent.parent.parent.parent / "client" / "src" / "components")
        
        self.scanner = ComponentScanner(components_root)
        self.registry = None
        self._ensure_registry_loaded()
        
    def _ensure_registry_loaded(self):
        """Ensure component registry is loaded and up-to-date"""
        if self.registry is None or len(self.registry.components) == 0:
            logger.info("Loading component registry...")
            self.registry = self.scanner.scan_all_components()
            logger.info(f"Loaded {len(self.registry.components)} components")
    
    def get_components_for_product_display(self, product_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get suitable components for displaying product information"""
        self._ensure_registry_loaded()
        
        suitable_components = []
        
        # Main product card with proper structure for renderer
        card_component = self.scanner.get_component_by_name("Card")
        if card_component:
            suitable_components.append({
                "type": "card",
                "props": {
                    "className": "product-card max-w-md",
                    "title": product_data.get("name", "Product")
                },
                "children": [
                    # Product image container
                    {
                        "type": "div",
                        "props": {"className": "flex items-center gap-4 mb-4"},
                        "children": [
                            {
                                "type": "div",
                                "props": {
                                    "className": "w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center"
                                },
                                "children": "📱"
                            },
                            {
                                "type": "div",
                                "props": {"className": "flex-1"},
                                "children": [
                                    {
                                        "type": "div",
                                        "props": {"className": "text-sm text-gray-600"},
                                        "children": product_data.get("description", "")
                                    }
                                ]
                            },
                            {
                                "type": "badge",
                                "props": {
                                    "variant": "secondary",
                                    "className": "text-lg font-bold"
                                },
                                "children": f"${product_data.get('price', '0.00')}"
                            }
                        ]
                    },
                    # Action button
                    {
                        "type": "button",
                        "props": {
                            "variant": "default",
                            "className": "w-full"
                        },
                        "children": "Add to Cart",
                        "actions": [{
                            "event": "onClick",
                            "action": "add_to_cart",
                            "payload": {"productId": product_data.get("id")}
                        }]
                    }
                ],
                "layout": {"position": "inline", "priority": "high"}
            })
        
        return suitable_components
    
    def get_components_for_order_management(self, order_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get suitable components for order management workflows"""
        self._ensure_registry_loaded()
        
        # Find order-related components
        order_components = self.registry.get_by_domain(BusinessDomain.ORDER_MANAGEMENT)
        data_display_components = self.registry.get_by_domain(BusinessDomain.DATA_DISPLAY)
        
        suitable_components = []
        
        # Table for order items (if OrdersTab exists)
        orders_tab = self.scanner.get_component_by_name("OrdersTab")
        if orders_tab:
            suitable_components.append({
                "type": "table",
                "component_name": "OrdersTab",
                "purpose": "Order history display",
                "props": {
                    "customerId": order_data.get("customerId"),
                    "orders": [order_data] if order_data else []
                },
                "layout": {"position": "full_width", "priority": "high"},
                "metadata": {
                    "business_domain": "order_management",
                    "component_type": orders_tab.component_type.value
                }
            })
        
        # Card for order summary
        card_component = self.scanner.get_component_by_name("Card")
        if card_component:
            suitable_components.append({
                "type": "card",
                "component_name": "Card",
                "purpose": "Order summary container",
                "props": {
                    "title": f"Order {order_data.get('id', 'N/A')}",
                    "className": "order-summary-card"
                },
                "children": [
                    {
                        "type": "text",
                        "content": f"Status: {order_data.get('status', 'Unknown')}",
                        "className": "order-status"
                    },
                    {
                        "type": "text", 
                        "content": f"Amount: ${order_data.get('amount', '0.00')}",
                        "className": "order-amount"
                    }
                ],
                "layout": {"position": "inline", "priority": "high"},
                "metadata": {
                    "business_domain": "order_management",
                    "component_type": card_component.component_type.value
                }
            })
        
        # Button for order actions
        button_component = self.scanner.get_component_by_name("Button")
        if button_component:
            suitable_components.append({
                "type": "button",
                "component_name": "Button", 
                "purpose": "Order action button",
                "props": {
                    "variant": "outline",
                    "children": "View Details"
                },
                "actions": [{
                    "event": "onClick",
                    "action": "view_order",
                    "payload": {"orderId": order_data.get("id")}
                }],
                "layout": {"position": "inline", "priority": "medium"},
                "metadata": {
                    "business_domain": "order_management",
                    "component_type": button_component.component_type.value
                }
            })
        
        return suitable_components
    
    def get_components_for_workflow(self, workflow_description: str, context_data: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get components suitable for a specific workflow description"""
        self._ensure_registry_loaded()
        
        # Use component scanner's workflow matching
        workflow_components = self.scanner.get_components_for_workflow(workflow_description)
        
        suitable_components = []
        context_data = context_data or {}
        
        # Convert scanner results to UI generation format
        for type_name, components in workflow_components.items():
            for component in components:
                component_config = {
                    "type": self._infer_ui_type(component),
                    "component_name": component.name,
                    "purpose": component.purpose,
                    "props": self._generate_default_props(component, context_data),
                    "layout": self._infer_layout(component),
                    "metadata": {
                        "business_domain": [d.value for d in component.business_domains],
                        "component_type": component.component_type.value,
                        "use_cases": component.use_cases
                    }
                }
                
                # Add actions if component supports them
                if self._component_supports_actions(component):
                    component_config["actions"] = self._generate_default_actions(component, context_data)
                
                suitable_components.append(component_config)
        
        return suitable_components
    
    def get_component_composition_suggestions(self, components: List[str]) -> Dict[str, Any]:
        """Suggest how to compose multiple components together"""
        self._ensure_registry_loaded()
        
        suggestions = {
            "composition_strategy": "hierarchical",
            "layout_recommendations": [],
            "data_flow": [],
            "interaction_patterns": []
        }
        
        # Analyze component types and relationships
        component_metadata = []
        for comp_name in components:
            comp = self.scanner.get_component_by_name(comp_name)
            if comp:
                component_metadata.append(comp)
        
        if not component_metadata:
            return suggestions
        
        # Determine composition strategy based on component types
        has_template = any(comp.component_type == ComponentType.TEMPLATE for comp in component_metadata)
        has_organism = any(comp.component_type == ComponentType.ORGANISM for comp in component_metadata)
        
        if has_template:
            suggestions["composition_strategy"] = "template_based"
            suggestions["layout_recommendations"].append("Use template as container for other components")
        elif has_organism:
            suggestions["composition_strategy"] = "organism_centered"
            suggestions["layout_recommendations"].append("Center design around organism component")
        else:
            suggestions["composition_strategy"] = "molecular_composition"
            suggestions["layout_recommendations"].append("Compose molecules and atoms in logical groups")
        
        # Suggest data flow patterns
        stateful_components = [comp for comp in component_metadata if comp.has_state]
        if stateful_components:
            suggestions["data_flow"].append(f"State management handled by: {[comp.name for comp in stateful_components]}")
        
        # Suggest interaction patterns
        for comp in component_metadata:
            if "button" in comp.name.lower():
                suggestions["interaction_patterns"].append(f"{comp.name}: Primary user interaction point")
            elif "form" in comp.name.lower():
                suggestions["interaction_patterns"].append(f"{comp.name}: Data input component")
            elif "dialog" in comp.name.lower() or "modal" in comp.name.lower():
                suggestions["interaction_patterns"].append(f"{comp.name}: Focus management component")
        
        return suggestions
    
    def _infer_ui_type(self, component: ComponentMetadata) -> str:
        """Infer UI type from component metadata"""
        name_lower = component.name.lower()
        
        if "button" in name_lower:
            return "button"
        elif "card" in name_lower:
            return "card"
        elif "table" in name_lower or "tab" in name_lower:
            return "table"
        elif "form" in name_lower:
            return "form"
        elif "dialog" in name_lower or "modal" in name_lower:
            return "dialog"
        elif "alert" in name_lower:
            return "alert"
        elif "badge" in name_lower:
            return "badge"
        elif "input" in name_lower:
            return "input"
        else:
            return "container"
    
    def _generate_default_props(self, component: ComponentMetadata, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sensible default props for a component"""
        props = {}
        
        # Add common props based on component type
        if component.component_type == ComponentType.ATOM:
            props["className"] = f"{component.name.lower()}-component"
        
        # Add context-specific props
        if "product" in context_data:
            product = context_data["product"]
            if "card" in component.name.lower():
                props["title"] = product.get("name", "Product")
            elif "badge" in component.name.lower():
                props["children"] = f"${product.get('price', '0.00')}"
        
        if "order" in context_data:
            order = context_data["order"]
            if "card" in component.name.lower():
                props["title"] = f"Order {order.get('id', 'N/A')}"
        
        return props
    
    def _infer_layout(self, component: ComponentMetadata) -> Dict[str, Any]:
        """Infer appropriate layout for component"""
        layout = {"priority": "medium"}
        
        if component.component_type == ComponentType.TEMPLATE:
            layout.update({"position": "full_width", "priority": "high"})
        elif component.component_type == ComponentType.ORGANISM:
            layout.update({"position": "center", "priority": "high"})
        elif component.component_type == ComponentType.MOLECULE:
            layout.update({"position": "inline", "priority": "medium"})
        else:  # ATOM
            layout.update({"position": "inline", "priority": "low"})
        
        return layout
    
    def _component_supports_actions(self, component: ComponentMetadata) -> bool:
        """Check if component typically supports user actions"""
        action_keywords = ["button", "link", "tab", "dialog", "form"]
        return any(keyword in component.name.lower() for keyword in action_keywords)
    
    def _generate_default_actions(self, component: ComponentMetadata, context_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate default actions for interactive components"""
        actions = []
        
        if "button" in component.name.lower():
            if "product" in context_data:
                actions.append({
                    "event": "onClick",
                    "action": "add_to_cart",
                    "payload": {"productId": context_data["product"].get("id")}
                })
            else:
                actions.append({
                    "event": "onClick", 
                    "action": "navigate",
                    "payload": {"route": "/"}
                })
        
        elif "tab" in component.name.lower():
            actions.append({
                "event": "onTabChange",
                "action": "switch_view",
                "payload": {"view": "default"}
            })
        
        return actions
    
    def get_registry_summary(self) -> Dict[str, Any]:
        """Get summary of available components"""
        self._ensure_registry_loaded()
        return self.scanner.get_registry_summary()
        
    def get_components_for_order_display(self, order_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate OrderCard component for displaying order information"""
        self._ensure_registry_loaded()
        
        # Generate OrderCard using the shared business component
        order_component = {
            "type": "card",  # Will be detected as OrderCard by smart component detection
            "props": {
                "id": order_data.get("id", "Unknown"),
                "status": order_data.get("status", "pending"),
                "total": order_data.get("total", order_data.get("totalAmount", 0)),
                "createdAt": order_data.get("orderDate", order_data.get("createdAt", "")),
                "trackingNumber": order_data.get("trackingNumber"),
                "items": [
                    {
                        "id": item.get("id", ""),
                        "product_name": item.get("product", {}).get("name", item.get("product_name", "Unknown Product")),
                        "quantity": item.get("quantity", 1),
                        "price": item.get("price", 0),
                        "total": item.get("price", 0) * item.get("quantity", 1),
                        "imageUrl": item.get("product", {}).get("imageUrl", item.get("imageUrl", "/placeholder-product.jpg")),
                        "brand": item.get("product", {}).get("brand", item.get("brand"))
                    } for item in order_data.get("orderItems", [])
                ]
            },
            "actions": []
        }
        
        # Add contextual actions based on order status
        status = order_data.get("status", "pending")
        
        # Always add view details
        order_component["actions"].append({
            "type": "button",
            "label": "View Details", 
            "action": "view_order",
            "data": {"order_id": order_data.get("id")}
        })
        
        # Add tracking if available
        if order_data.get("trackingNumber"):
            order_component["actions"].append({
                "type": "button",
                "label": "Track Package",
                "action": "track_order", 
                "data": {
                    "order_id": order_data.get("id"),
                    "tracking_number": order_data.get("trackingNumber")
                }
            })
        
        # Add cancel option for pending orders
        if status in ["pending", "processing"] and order_data.get("canCancel", True):
            order_component["actions"].append({
                "type": "button",
                "label": "Cancel Order",
                "action": "cancel_order",
                "data": {"order_id": order_data.get("id")}
            })
        
        # Add return option for delivered orders
        if status == "delivered" and order_data.get("canReturn", True):
            order_component["actions"].append({
                "type": "button", 
                "label": "Return Items",
                "action": "return_order",
                "data": {"order_id": order_data.get("id")}
            })
        
        return [order_component]
        
    def get_components_for_address_management(self, address_data: Dict[str, Any] = None, context: str = "view") -> List[Dict[str, Any]]:
        """Generate address management components (cards, forms, lists)"""
        self._ensure_registry_loaded()
        
        if context == "form" or context == "edit":
            # Return AddressForm for editing/creating addresses
            return [{
                "type": "address_form",
                "props": {
                    "mode": "edit" if address_data else "create",
                    "initialData": address_data or {},
                    "title": "Edit Address" if address_data else "Add New Address"
                },
                "actions": []
            }]
        
        elif context == "list":
            # Return AddressList for managing multiple addresses
            addresses = address_data.get("addresses", []) if address_data else []
            return [{
                "type": "address_list", 
                "props": {
                    "addresses": addresses,
                    "title": "My Addresses",
                    "description": "Manage your shipping and billing addresses",
                    "showAddButton": True
                },
                "actions": []
            }]
        
        else:
            # Return AddressCard for displaying single address
            if not address_data:
                return []
                
            address_component = {
                "type": "address_card",
                "props": {
                    "id": address_data.get("id"),
                    "label": address_data.get("label", "Address"),
                    "recipientName": address_data.get("recipientName"),
                    "street": address_data.get("street", f"{address_data.get('addressLine1', '')}{', ' + address_data.get('addressLine2', '') if address_data.get('addressLine2') else ''}"),
                    "city": address_data.get("city", ""),
                    "state": address_data.get("state", ""),
                    "zipCode": address_data.get("zipCode", address_data.get("postalCode", "")),
                    "country": address_data.get("country", "United States"),
                    "phone": address_data.get("phone"),
                    "isDefault": address_data.get("isDefault", False),
                    "type": address_data.get("type", "both")
                },
                "actions": []
            }
            
            # Add contextual actions
            address_component["actions"].extend([
                {
                    "type": "button",
                    "label": "Edit",
                    "action": "edit_address",
                    "data": {"address_id": address_data.get("id")}
                },
                {
                    "type": "button", 
                    "label": "Delete",
                    "action": "delete_address",
                    "data": {"address_id": address_data.get("id")}
                }
            ])
            
            # Add set default option if not already default
            if not address_data.get("isDefault", False):
                address_component["actions"].insert(1, {
                    "type": "button",
                    "label": "Set Default",
                    "action": "set_default_address", 
                    "data": {"address_id": address_data.get("id")}
                })
            
            return [address_component]
            
    def get_components_for_cart_display(self, cart_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate CartItem components for shopping cart display"""
        self._ensure_registry_loaded()
        
        cart_items = cart_data.get('items', []) if cart_data else []
        components = []
        
        for item in cart_items:
            cart_item_component = {
                "type": "cart_item",
                "props": {
                    "id": item.get("id", item.get("productId")),
                    "cartItemId": item.get("cartItemId"),
                    "name": item.get("name", item.get("product_name", "Unknown Item")),
                    "price": item.get("price", 0),
                    "quantity": item.get("quantity", 1),
                    "imageUrl": item.get("imageUrl", item.get("image_url", "/placeholder-product.jpg")),
                    "brand": item.get("brand", "Unknown Brand")
                },
                "actions": []
            }
            
            # Add contextual actions for cart items
            cart_item_component["actions"].extend([
                {
                    "type": "button",
                    "label": "Update Quantity",
                    "action": "update_quantity",
                    "data": {"cart_item_id": item.get("cartItemId"), "product_id": item.get("id")}
                },
                {
                    "type": "button", 
                    "label": "Remove from Cart",
                    "action": "remove_from_cart",
                    "data": {"cart_item_id": item.get("cartItemId"), "product_id": item.get("id")}
                }
            ])
            
            components.append(cart_item_component)
        
        return components