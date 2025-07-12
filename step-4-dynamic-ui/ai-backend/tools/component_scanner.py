"""
Component Scanner for Dynamic UI Generation
Scans client UI component library and extracts component schemas
"""
import os
import re
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ComponentScanner:
    """Scans and analyzes UI component library for LLM consumption"""
    
    def __init__(self, components_path: str):
        self.components_path = Path(components_path)
        self.component_registry = {}
        self.last_scan_time = None
        
        # Component type mappings for better LLM understanding
        self.component_categories = {
            'layout': ['card', 'sheet', 'drawer', 'accordion', 'tabs', 'separator'],
            'form': ['button', 'input', 'textarea', 'checkbox', 'radio-group', 'select', 'form'],
            'feedback': ['alert', 'toast', 'progress', 'skeleton'],
            'navigation': ['breadcrumb', 'menubar', 'navigation-menu', 'pagination'],
            'overlay': ['dialog', 'popover', 'tooltip', 'hover-card', 'context-menu'],
            'data': ['table', 'chart', 'avatar'],
            'media': ['carousel', 'aspect-ratio'],
            'input': ['calendar', 'slider', 'switch', 'toggle', 'input-otp']
        }
    
    async def scan_all_components(self) -> Dict[str, Any]:
        """Scan entire /components/ui/ directory for component information"""
        try:
            start_time = time.time()
            components = {}
            
            if not self.components_path.exists():
                return {
                    "success": False,
                    "error": f"Components path {self.components_path} does not exist"
                }
            
            # Walk through all .tsx files in components/ui/
            for file_path in self.components_path.glob("**/*.tsx"):
                if file_path.is_file():
                    component_info = await self.analyze_component_file(file_path)
                    if component_info:
                        components[component_info["name"]] = component_info
            
            scan_time = time.time() - start_time
            self.last_scan_time = time.time()
            
            logger.info(f"Scanned {len(components)} components in {scan_time:.2f}s")
            
            return {
                "success": True,
                "data": components,
                "metadata": {
                    "total_components": len(components),
                    "scan_time": scan_time,
                    "scan_timestamp": self.last_scan_time,
                    "components_path": str(self.components_path),
                    "categories": self._categorize_components(components)
                }
            }
            
        except Exception as e:
            logger.error(f"Component scan failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def analyze_component_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Extract component information from .tsx file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            component_name = file_path.stem
            
            component_info = {
                "name": component_name,
                "file_path": str(file_path.relative_to(self.components_path.parent)),
                "exports": [],
                "props": {},
                "interfaces": {},
                "descriptions": {},
                "usage_patterns": [],
                "category": self._get_component_category(component_name)
            }
            
            # Extract exports (Card, CardHeader, CardContent, etc.)
            exports = self.extract_exports(content)
            component_info["exports"] = exports
            
            # Extract TypeScript interfaces for props
            interfaces = self.extract_interfaces(content)
            component_info["interfaces"] = interfaces
            
            # Extract component props from React.forwardRef or function definitions
            props = self.extract_component_props(content, exports)
            component_info["props"] = props
            
            # Extract JSDoc comments for descriptions
            descriptions = self.extract_descriptions(content)
            component_info["descriptions"] = descriptions
            
            # Generate usage patterns for LLM
            usage_patterns = self.generate_usage_patterns(component_name, exports, props)
            component_info["usage_patterns"] = usage_patterns
            
            return component_info
            
        except Exception as e:
            logger.error(f"Failed to analyze {file_path}: {e}")
            return None
    
    def extract_exports(self, content: str) -> List[str]:
        """Extract all exported components from file"""
        exports = []
        
        # Pattern 1: export { Card, CardHeader, CardFooter }
        export_block_pattern = r'export\s*{\s*([^}]+)\s*}'
        matches = re.findall(export_block_pattern, content)
        for match in matches:
            # Split by comma and clean up
            items = [item.strip() for item in match.split(',')]
            exports.extend(items)
        
        # Pattern 2: export const Card = React.forwardRef<...>
        export_const_pattern = r'export\s+const\s+(\w+)\s*='
        matches = re.findall(export_const_pattern, content)
        exports.extend(matches)
        
        # Pattern 3: export function ComponentName
        export_function_pattern = r'export\s+function\s+(\w+)'
        matches = re.findall(export_function_pattern, content)
        exports.extend(matches)
        
        return list(set(exports))  # Remove duplicates
    
    def extract_interfaces(self, content: str) -> Dict[str, Any]:
        """Extract TypeScript interfaces for component props"""
        interfaces = {}
        
        # Pattern: interface CardProps extends React.HTMLAttributes<HTMLDivElement>
        interface_pattern = r'interface\s+(\w+)\s*(?:extends\s+([^{]+))?\s*{\s*([^}]*)\s*}'
        
        matches = re.findall(interface_pattern, content, re.DOTALL)
        
        for interface_name, extends_clause, interface_body in matches:
            props = self.parse_interface_props(interface_body)
            interfaces[interface_name] = {
                "name": interface_name,
                "extends": extends_clause.strip() if extends_clause else None,
                "properties": props
            }
        
        return interfaces
    
    def parse_interface_props(self, interface_body: str) -> Dict[str, Any]:
        """Parse individual props from interface body"""
        props = {}
        
        # Split by lines and parse each property
        lines = interface_body.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('//') or line.startswith('/*'):
                continue
            
            # Parse: propertyName?: string;
            prop_pattern = r'(\w+)(\??):\s*([^;]+);?'
            match = re.match(prop_pattern, line)
            
            if match:
                prop_name, optional, prop_type = match.groups()
                props[prop_name] = {
                    "type": prop_type.strip(),
                    "optional": bool(optional),
                    "description": ""
                }
        
        return props
    
    def extract_component_props(self, content: str, exports: List[str]) -> Dict[str, Any]:
        """Extract props from React.forwardRef definitions"""
        props = {}
        
        for export_name in exports:
            # Pattern: const Card = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>
            pattern = rf'{export_name}\s*=\s*React\.forwardRef<([^,]+),\s*([^>]+)>'
            match = re.search(pattern, content)
            
            if match:
                ref_type, props_type = match.groups()
                props[export_name] = {
                    "ref_type": ref_type.strip(),
                    "props_type": props_type.strip(),
                    "base_props": self._extract_base_props(props_type.strip())
                }
        
        return props
    
    def _extract_base_props(self, props_type: str) -> Dict[str, Any]:
        """Extract base HTML element props"""
        base_props = {}
        
        # Common patterns
        if "React.HTMLAttributes" in props_type:
            # Extract element type from React.HTMLAttributes<HTMLDivElement>
            element_match = re.search(r'HTML(\w+)Element', props_type)
            element_type = element_match.group(1) if element_match else "Generic"
            
            base_props = {
                "className": {"type": "string", "optional": True},
                "children": {"type": "React.ReactNode", "optional": True},
                "onClick": {"type": "() => void", "optional": True},
                "element_type": element_type
            }
        
        return base_props
    
    def extract_descriptions(self, content: str) -> Dict[str, str]:
        """Extract JSDoc comments and descriptions"""
        descriptions = {}
        
        # Pattern: /** Description */ followed by component
        jsdoc_pattern = r'/\*\*\s*\n?\s*\*?\s*([^*]+?)\s*\*?\s*\*/\s*(?:export\s+)?(?:const|function)\s+(\w+)'
        
        matches = re.findall(jsdoc_pattern, content, re.DOTALL)
        
        for description, component_name in matches:
            # Clean up the description
            clean_desc = description.strip().replace('*', '').strip()
            descriptions[component_name] = clean_desc
        
        return descriptions
    
    def generate_usage_patterns(self, component_name: str, exports: List[str], props: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate usage patterns for LLM understanding"""
        patterns = []
        
        # Generate basic usage pattern for each export
        for export_name in exports:
            pattern = {
                "component": export_name,
                "basic_usage": f"<{export_name}>content</{export_name}>",
                "with_props": f"<{export_name} className=\"custom-class\">content</{export_name}>",
                "description": f"{export_name} component from {component_name} library"
            }
            
            # Add specific patterns based on component type
            if component_name == "button":
                pattern["variants"] = [
                    f"<{export_name} variant=\"default\">Click me</{export_name}>",
                    f"<{export_name} variant=\"destructive\" size=\"sm\">Delete</{export_name}>",
                    f"<{export_name} disabled>Disabled</{export_name}>"
                ]
            elif component_name == "card":
                pattern["composition"] = [
                    "Card + CardHeader + CardContent + CardFooter",
                    "Commonly used for product displays, forms, information panels"
                ]
            
            patterns.append(pattern)
        
        return patterns
    
    def _get_component_category(self, component_name: str) -> str:
        """Categorize component for better LLM understanding"""
        for category, components in self.component_categories.items():
            if component_name in components:
                return category
        return "utility"
    
    def _categorize_components(self, components: Dict[str, Any]) -> Dict[str, List[str]]:
        """Organize components by category"""
        categories = {}
        
        for comp_name, comp_info in components.items():
            category = comp_info.get("category", "utility")
            if category not in categories:
                categories[category] = []
            categories[category].append(comp_name)
        
        return categories
    
    def get_directory_hash(self) -> str:
        """Generate hash of all component files for change detection"""
        if not self.components_path.exists():
            return ""
        
        file_hashes = []
        
        for file_path in self.components_path.glob("**/*.tsx"):
            if file_path.is_file():
                # Get file modification time and size
                stat = file_path.stat()
                file_info = f"{file_path}:{stat.st_mtime}:{stat.st_size}"
                file_hashes.append(file_info)
        
        # Create hash of all file info
        combined = "|".join(sorted(file_hashes))
        return hashlib.md5(combined.encode()).hexdigest()