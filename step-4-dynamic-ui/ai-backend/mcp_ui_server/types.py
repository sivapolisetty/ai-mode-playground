"""
Type definitions for MCP UI Component Server
"""
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime

class ComponentType(Enum):
    """Component classification based on Atomic Design principles"""
    ATOM = "atom"           # Basic building blocks (Button, Input, Label)
    MOLECULE = "molecule"   # Simple groups of atoms (Card, FormField)
    ORGANISM = "organism"   # Complex UI components (ProductGrid, OrderTable)
    TEMPLATE = "template"   # Page-level components (Layout, Modal)

class BusinessDomain(Enum):
    """Business domain classification for components"""
    CORE_UI = "core_ui"                    # Basic UI elements
    PRODUCT_CATALOG = "product_catalog"    # Product-related components
    ORDER_MANAGEMENT = "order_management"  # Order-related components
    CUSTOMER_SERVICE = "customer_service"  # Customer management
    ADMIN = "admin"                        # Admin functionality
    PAYMENT = "payment"                    # Payment processing
    NAVIGATION = "navigation"              # Navigation elements
    FORMS = "forms"                        # Form components
    DATA_DISPLAY = "data_display"          # Tables, lists, cards
    FEEDBACK = "feedback"                  # Toasts, alerts, modals

@dataclass
class PropDefinition:
    """Definition of a component prop"""
    name: str
    type: str
    required: bool
    default_value: Optional[Any] = None
    description: Optional[str] = None

@dataclass
class UsagePattern:
    """How a component is typically used"""
    context: str                    # Where it's used (grid_item, modal_content, etc.)
    frequency: int                  # How often it's used in this context
    co_used_with: List[str]        # Components often used together
    
@dataclass
class ComponentMetadata:
    """Complete metadata for a UI component"""
    # Basic Information
    name: str
    file_path: str
    component_type: ComponentType
    business_domains: List[BusinessDomain]
    
    # Structure Information
    props: List[PropDefinition]
    exports: List[str]              # All exported components from file
    dependencies: List[str]         # Imported components
    
    # Semantic Information
    purpose: str                    # What this component does
    use_cases: List[str]           # When to use this component
    usage_patterns: List[UsagePattern]
    
    # Technical Information 
    has_state: bool                # Uses useState, etc.
    has_effects: bool              # Uses useEffect, etc.
    has_context: bool              # Uses React context
    
    # Metadata
    last_scanned: datetime
    scan_version: str
    
@dataclass 
class ComponentRegistry:
    """Central registry of all discovered components"""
    components: Dict[str, ComponentMetadata]
    scan_metadata: Dict[str, Any]
    last_updated: datetime
    
    def get_by_type(self, component_type: ComponentType) -> List[ComponentMetadata]:
        """Get components by type"""
        return [comp for comp in self.components.values() 
                if comp.component_type == component_type]
    
    def get_by_domain(self, domain: BusinessDomain) -> List[ComponentMetadata]:
        """Get components by business domain"""
        return [comp for comp in self.components.values() 
                if domain in comp.business_domains]
    
    def get_for_use_case(self, use_case: str) -> List[ComponentMetadata]:
        """Get components suitable for a specific use case"""
        return [comp for comp in self.components.values() 
                if use_case.lower() in [uc.lower() for uc in comp.use_cases]]

@dataclass
class ComponentScanResult:
    """Result of scanning a component file"""
    success: bool
    component_metadata: Optional[ComponentMetadata] = None
    error_message: Optional[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []