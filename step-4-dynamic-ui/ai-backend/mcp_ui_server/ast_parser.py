"""
AST Parser for TypeScript/JSX component analysis
Extracts component structure, props, and metadata from React components
"""
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from .types import (
    ComponentMetadata, PropDefinition, ComponentType, 
    BusinessDomain, UsagePattern, ComponentScanResult
)

logger = logging.getLogger(__name__)

class ComponentASTParser:
    """Parser for React/TypeScript component files"""
    
    def __init__(self):
        self.business_domain_keywords = {
            BusinessDomain.PRODUCT_CATALOG: ['product', 'catalog', 'item', 'inventory'],
            BusinessDomain.ORDER_MANAGEMENT: ['order', 'cart', 'checkout', 'purchase'],
            BusinessDomain.CUSTOMER_SERVICE: ['customer', 'profile', 'account', 'user'],
            BusinessDomain.ADMIN: ['admin', 'management', 'dashboard'],
            BusinessDomain.PAYMENT: ['payment', 'billing', 'card', 'transaction'],
            BusinessDomain.NAVIGATION: ['nav', 'menu', 'breadcrumb', 'tab'],
            BusinessDomain.FORMS: ['form', 'input', 'field', 'validation'],
            BusinessDomain.DATA_DISPLAY: ['table', 'list', 'grid', 'chart'],
            BusinessDomain.FEEDBACK: ['toast', 'alert', 'modal', 'dialog'],
            BusinessDomain.CORE_UI: ['button', 'card', 'badge', 'avatar']
        }
    
    def scan_component_file(self, file_path: str) -> ComponentScanResult:
        """Scan a single component file and extract metadata"""
        try:
            path = Path(file_path)
            if not path.exists():
                return ComponentScanResult(
                    success=False,
                    error_message=f"File not found: {file_path}"
                )
            
            # Read file content
            content = path.read_text(encoding='utf-8')
            
            # Extract component information
            metadata = self._extract_component_metadata(content, file_path)
            
            return ComponentScanResult(
                success=True,
                component_metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error scanning component {file_path}: {e}")
            return ComponentScanResult(
                success=False,
                error_message=str(e)
            )
    
    def _extract_component_metadata(self, content: str, file_path: str) -> ComponentMetadata:
        """Extract component metadata from file content"""
        
        # Extract basic information
        name = self._extract_component_name(content, file_path)
        exports = self._extract_exports(content)
        dependencies = self._extract_dependencies(content)
        props = self._extract_props(content)
        
        # Classify component
        component_type = self._classify_component_type(name, content, file_path)
        business_domains = self._classify_business_domains(name, content, file_path)
        
        # Extract semantic information
        purpose = self._infer_component_purpose(name, content)
        use_cases = self._infer_use_cases(name, content, component_type)
        
        # Technical analysis
        has_state = self._has_react_state(content)
        has_effects = self._has_react_effects(content)
        has_context = self._has_react_context(content)
        
        return ComponentMetadata(
            name=name,
            file_path=file_path,
            component_type=component_type,
            business_domains=business_domains,
            props=props,
            exports=exports,
            dependencies=dependencies,
            purpose=purpose,
            use_cases=use_cases,
            usage_patterns=[],  # Will be populated by usage analysis
            has_state=has_state,
            has_effects=has_effects,
            has_context=has_context,
            last_scanned=datetime.now(),
            scan_version="1.0.0"
        )
    
    def _extract_component_name(self, content: str, file_path: str) -> str:
        """Extract the main component name"""
        # Try export default pattern
        default_export_match = re.search(r'export\s+default\s+(\w+)', content)
        if default_export_match:
            return default_export_match.group(1)
        
        # Try const/function patterns
        component_patterns = [
            r'(?:const|function)\s+(\w+).*=.*React\.forwardRef',
            r'(?:const|function)\s+(\w+).*=.*\([^)]*\)\s*=>', 
            r'function\s+(\w+)\s*\([^)]*\)',
            r'const\s+(\w+)\s*=\s*React\.forwardRef'
        ]
        
        for pattern in component_patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
        
        # Fallback to filename
        return Path(file_path).stem.replace('-', '').replace('_', '')
    
    def _extract_exports(self, content: str) -> List[str]:
        """Extract all exported components/functions"""
        exports = []
        
        # Named exports
        named_exports = re.findall(r'export\s*\{\s*([^}]+)\s*\}', content)
        for export_group in named_exports:
            names = [name.strip() for name in export_group.split(',')]
            exports.extend(names)
        
        # Direct exports
        direct_exports = re.findall(r'export\s+(?:const|function|class)\s+(\w+)', content)
        exports.extend(direct_exports)
        
        # Default export
        default_export = re.search(r'export\s+default\s+(\w+)', content)
        if default_export:
            exports.append(default_export.group(1))
        
        return list(set(exports))  # Remove duplicates
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract imported React components"""
        dependencies = []
        
        # Extract from import statements
        import_patterns = [
            r'import\s*\{\s*([^}]+)\s*\}\s*from\s*[\'"]@/components',
            r'import\s+(\w+)\s+from\s*[\'"]@/components',
            r'from\s*[\'"]@/components/ui/(\w+)',
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, str):
                    if ',' in match:
                        # Multiple imports
                        deps = [dep.strip() for dep in match.split(',')]
                        dependencies.extend(deps)
                    else:
                        dependencies.append(match.strip())
        
        return list(set(dependencies))
    
    def _extract_props(self, content: str) -> List[PropDefinition]:
        """Extract component props from TypeScript interfaces"""
        props = []
        
        # Find interface definitions  
        interface_pattern = r'interface\s+(\w+)Props\s*\{([^}]+)\}'
        interfaces = re.findall(interface_pattern, content, re.DOTALL)
        
        for interface_name, interface_body in interfaces:
            # Parse individual props
            prop_pattern = r'(\w+)(\?)?:\s*([^;]+);?'
            prop_matches = re.findall(prop_pattern, interface_body)
            
            for prop_name, optional, prop_type in prop_matches:
                props.append(PropDefinition(
                    name=prop_name,
                    type=prop_type.strip(),
                    required=optional != '?',
                    description=None
                ))
        
        # Also check for inline props in function signatures
        func_prop_pattern = r'\(\{\s*([^}]+)\s*\}:[^)]*\)'
        func_matches = re.findall(func_prop_pattern, content)
        
        for prop_group in func_matches:
            prop_names = [name.strip() for name in prop_group.split(',')]
            for prop_name in prop_names:
                if not any(p.name == prop_name for p in props):
                    props.append(PropDefinition(
                        name=prop_name,
                        type='unknown',
                        required=True
                    ))
        
        return props
    
    def _classify_component_type(self, name: str, content: str, file_path: str) -> ComponentType:
        """Classify component using Atomic Design principles"""
        
        # Check file path for hints
        path_lower = file_path.lower()
        if '/ui/' in path_lower:
            # UI components are usually atoms or molecules
            if any(keyword in name.lower() for keyword in ['button', 'input', 'label', 'badge', 'avatar']):
                return ComponentType.ATOM
            else:
                return ComponentType.MOLECULE
        
        # Check component complexity
        jsx_element_count = len(re.findall(r'<\w+', content))
        component_references = len(re.findall(r'<[A-Z]\w+', content))
        
        if jsx_element_count <= 3 and component_references == 0:
            return ComponentType.ATOM
        elif jsx_element_count <= 10 and component_references <= 3:
            return ComponentType.MOLECULE
        elif 'dialog' in name.lower() or 'modal' in name.lower() or 'layout' in name.lower():
            return ComponentType.TEMPLATE
        else:
            return ComponentType.ORGANISM
    
    def _classify_business_domains(self, name: str, content: str, file_path: str) -> List[BusinessDomain]:
        """Classify component business domains"""
        domains = []
        name_lower = name.lower()
        path_lower = file_path.lower()
        content_lower = content.lower()
        
        for domain, keywords in self.business_domain_keywords.items():
            if any(keyword in name_lower or keyword in path_lower for keyword in keywords):
                domains.append(domain)
        
        # Special cases
        if '/admin/' in path_lower:
            domains.append(BusinessDomain.ADMIN)
        if '/customer/' in path_lower:
            domains.append(BusinessDomain.CUSTOMER_SERVICE)
        
        # Default to core UI if no specific domain found
        if not domains:
            domains.append(BusinessDomain.CORE_UI)
        
        return domains
    
    def _infer_component_purpose(self, name: str, content: str) -> str:
        """Infer the purpose of the component"""
        name_lower = name.lower()
        
        # Common patterns
        if 'button' in name_lower:
            return "Interactive button component for user actions"
        elif 'card' in name_lower:
            return "Container component for grouping related content"
        elif 'table' in name_lower or 'tab' in name_lower:
            return "Data display component for structured information"
        elif 'dialog' in name_lower or 'modal' in name_lower:
            return "Overlay component for focused user interaction"
        elif 'form' in name_lower:
            return "Form component for user input collection"
        elif 'order' in name_lower:
            return "Order management component for e-commerce operations"
        elif 'product' in name_lower:
            return "Product display component for catalog functionality"
        else:
            return f"React component for {name.lower()} functionality"
    
    def _infer_use_cases(self, name: str, content: str, component_type: ComponentType) -> List[str]:
        """Infer when this component should be used"""
        use_cases = []
        name_lower = name.lower()
        
        if component_type == ComponentType.ATOM:
            use_cases.append("Basic UI building block")
        elif component_type == ComponentType.MOLECULE:
            use_cases.append("Composed UI element")
        elif component_type == ComponentType.ORGANISM:
            use_cases.append("Complex feature implementation")
        
        # Specific use cases
        if 'order' in name_lower:
            use_cases.extend(["Display order information", "Order management operations"])
        if 'product' in name_lower:
            use_cases.extend(["Show product details", "Product catalog display"])
        if 'customer' in name_lower:
            use_cases.extend(["Customer data management", "Customer service operations"])
        
        return use_cases
    
    def _has_react_state(self, content: str) -> bool:
        """Check if component uses React state"""
        return bool(re.search(r'useState|useReducer|this\.state', content))
    
    def _has_react_effects(self, content: str) -> bool:
        """Check if component uses React effects"""
        return bool(re.search(r'useEffect|useLayoutEffect|componentDidMount', content))
    
    def _has_react_context(self, content: str) -> bool:
        """Check if component uses React context"""
        return bool(re.search(r'useContext|createContext|Context\\.Provider', content))