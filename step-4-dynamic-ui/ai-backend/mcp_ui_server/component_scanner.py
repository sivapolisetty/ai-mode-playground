"""
Component Scanner - Main orchestrator for component discovery and analysis
"""
import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .types import ComponentRegistry, ComponentMetadata, ComponentScanResult
from .ast_parser import ComponentASTParser

logger = logging.getLogger(__name__)

class ComponentScanner:
    """Main component scanning and registry management"""
    
    def __init__(self, components_root: str, cache_dir: str = None):
        """
        Initialize component scanner
        
        Args:
            components_root: Root directory containing React components
            cache_dir: Directory to cache scan results
        """
        self.components_root = Path(components_root)
        self.cache_dir = Path(cache_dir) if cache_dir else Path("./component_cache")
        self.ast_parser = ComponentASTParser()
        
        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing registry if available
        self.registry = self._load_registry()
        
    def scan_all_components(self, force_rescan: bool = False) -> ComponentRegistry:
        """
        Scan all components in the components directory
        
        Args:
            force_rescan: If True, rescan all files regardless of cache
        """
        logger.info(f"Starting component scan of {self.components_root}")
        
        # Find all component files
        component_files = self._find_component_files()
        logger.info(f"Found {len(component_files)} component files")
        
        scanned_components = {}
        scan_stats = {
            "total_files": len(component_files),
            "successful_scans": 0,
            "failed_scans": 0,
            "skipped_scans": 0
        }
        
        for file_path in component_files:
            try:
                # Check if we need to rescan this file
                if not force_rescan and self._should_skip_file(file_path):
                    scan_stats["skipped_scans"] += 1
                    # Use cached version
                    if file_path in self.registry.components:
                        scanned_components[file_path] = self.registry.components[file_path]
                    continue
                
                # Scan the component file
                result = self.ast_parser.scan_component_file(str(file_path))
                
                if result.success and result.component_metadata:
                    scanned_components[file_path] = result.component_metadata
                    scan_stats["successful_scans"] += 1
                    logger.debug(f"Successfully scanned: {result.component_metadata.name}")
                else:
                    scan_stats["failed_scans"] += 1
                    logger.warning(f"Failed to scan {file_path}: {result.error_message}")
                    
            except Exception as e:
                scan_stats["failed_scans"] += 1
                logger.error(f"Error processing {file_path}: {e}")
        
        # Create updated registry
        self.registry = ComponentRegistry(
            components=scanned_components,
            scan_metadata=scan_stats,
            last_updated=datetime.now()
        )
        
        # Cache the results
        self._save_registry()
        
        logger.info(f"Component scan completed: {scan_stats}")
        return self.registry
    
    def get_component_by_name(self, name: str) -> Optional[ComponentMetadata]:
        """Get component metadata by name"""
        for component in self.registry.components.values():
            if component.name.lower() == name.lower():
                return component
        return None
    
    def search_components(self, query: str) -> List[ComponentMetadata]:
        """Search components by name, purpose, or use cases"""
        query_lower = query.lower()
        results = []
        
        for component in self.registry.components.values():
            # Search in name
            if query_lower in component.name.lower():
                results.append(component)
                continue
            
            # Search in purpose
            if query_lower in component.purpose.lower():
                results.append(component)
                continue
            
            # Search in use cases
            if any(query_lower in use_case.lower() for use_case in component.use_cases):
                results.append(component)
                continue
        
        return results
    
    def get_components_for_workflow(self, workflow_description: str) -> Dict[str, List[ComponentMetadata]]:
        """
        Get components suitable for a specific workflow
        Returns categorized components by type
        """
        workflow_lower = workflow_description.lower()
        suitable_components = {
            "atoms": [],
            "molecules": [],
            "organisms": [],
            "templates": []
        }
        
        # Analyze workflow for component needs
        workflow_keywords = self._extract_workflow_keywords(workflow_description)
        
        for component in self.registry.components.values():
            # Check if component is relevant to workflow
            relevance_score = self._calculate_workflow_relevance(component, workflow_keywords)
            
            if relevance_score > 0.3:  # Threshold for relevance
                type_key = component.component_type.value + "s"
                suitable_components[type_key].append(component)
        
        return suitable_components
    
    def get_registry_summary(self) -> Dict[str, Any]:
        """Get summary statistics of the component registry"""
        if not self.registry.components:
            return {"message": "No components scanned yet"}
        
        from collections import Counter
        
        # Component type distribution
        type_counts = Counter(comp.component_type.value for comp in self.registry.components.values())
        
        # Business domain distribution
        domain_counts = Counter()
        for comp in self.registry.components.values():
            for domain in comp.business_domains:
                domain_counts[domain.value] += 1
        
        # Technical feature distribution
        technical_stats = {
            "stateful_components": sum(1 for comp in self.registry.components.values() if comp.has_state),
            "components_with_effects": sum(1 for comp in self.registry.components.values() if comp.has_effects),
            "context_consumers": sum(1 for comp in self.registry.components.values() if comp.has_context)
        }
        
        return {
            "total_components": len(self.registry.components),
            "component_types": dict(type_counts),
            "business_domains": dict(domain_counts),
            "technical_features": technical_stats,
            "last_scan": self.registry.last_updated.isoformat(),
            "scan_metadata": self.registry.scan_metadata
        }
    
    def _find_component_files(self) -> List[Path]:
        """Find all React component files"""
        component_files = []
        
        # Supported file extensions
        extensions = ['.tsx', '.ts', '.jsx', '.js']
        
        # Recursively find component files
        for ext in extensions:
            component_files.extend(self.components_root.rglob(f'*{ext}'))
        
        # Filter out non-component files
        filtered_files = []
        for file_path in component_files:
            # Skip test files, story files, etc.
            if any(exclude in file_path.name.lower() for exclude in ['test', 'spec', 'story', 'stories']):
                continue
            
            # Skip index files (usually just re-exports)
            if file_path.name.lower() in ['index.ts', 'index.tsx', 'index.js', 'index.jsx']:
                continue
            
            filtered_files.append(file_path)
        
        return filtered_files
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped (already cached and unchanged)"""
        if str(file_path) not in self.registry.components:
            return False
        
        # Check file modification time
        file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        cached_component = self.registry.components[str(file_path)]
        
        return file_mtime <= cached_component.last_scanned
    
    def _extract_workflow_keywords(self, workflow_description: str) -> List[str]:
        """Extract keywords from workflow description for component matching"""
        import re
        
        # Remove common stop words and extract meaningful terms
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        
        # Extract words and filter
        words = re.findall(r'\b\w{3,}\b', workflow_description.lower())
        keywords = [word for word in words if word not in stop_words]
        
        return keywords
    
    def _calculate_workflow_relevance(self, component: ComponentMetadata, workflow_keywords: List[str]) -> float:
        """Calculate how relevant a component is to a workflow"""
        relevance_score = 0.0
        
        # Check component name
        component_name_words = component.name.lower().split()
        name_matches = sum(1 for keyword in workflow_keywords if any(keyword in word for word in component_name_words))
        relevance_score += name_matches * 0.4
        
        # Check purpose
        purpose_matches = sum(1 for keyword in workflow_keywords if keyword in component.purpose.lower())
        relevance_score += purpose_matches * 0.3
        
        # Check use cases
        use_case_matches = sum(1 for keyword in workflow_keywords 
                              for use_case in component.use_cases 
                              if keyword in use_case.lower())
        relevance_score += use_case_matches * 0.2
        
        # Check business domains
        domain_matches = sum(1 for keyword in workflow_keywords 
                            for domain in component.business_domains 
                            if keyword in domain.value)
        relevance_score += domain_matches * 0.1
        
        # Normalize score
        return min(relevance_score / len(workflow_keywords) if workflow_keywords else 0, 1.0)
    
    def _load_registry(self) -> ComponentRegistry:
        """Load component registry from cache"""
        cache_file = self.cache_dir / "component_registry.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                
                # TODO: Properly deserialize ComponentRegistry from JSON
                # For now, return empty registry
                logger.info("Loaded cached component registry")
                
            except Exception as e:
                logger.warning(f"Failed to load cached registry: {e}")
        
        # Return empty registry
        return ComponentRegistry(
            components={},
            scan_metadata={},
            last_updated=datetime.now()
        )
    
    def _save_registry(self):
        """Save component registry to cache"""
        cache_file = self.cache_dir / "component_registry.json"
        
        try:
            # TODO: Properly serialize ComponentRegistry to JSON
            # For now, save basic summary
            summary = self.get_registry_summary()
            
            with open(cache_file, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
            
            logger.info(f"Saved component registry to {cache_file}")
            
        except Exception as e:
            logger.error(f"Failed to save registry: {e}")