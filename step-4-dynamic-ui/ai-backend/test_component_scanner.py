"""
Test script for Component Scanner
Tests component discovery and analysis functionality
"""
import asyncio
import logging
import json
from pathlib import Path

from mcp_ui_server.component_scanner import ComponentScanner
from mcp_ui_server.types import ComponentType, BusinessDomain

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_component_scanner():
    """Test the component scanner functionality"""
    
    # Initialize scanner with the client components directory
    components_root = "../../client/src/components"
    
    if not Path(components_root).exists():
        logger.error(f"Components directory not found: {components_root}")
        return
    
    logger.info("🔍 Initializing Component Scanner...")
    scanner = ComponentScanner(components_root)
    
    # Test 1: Scan all components
    logger.info("📡 Testing: Scan all components")
    registry = scanner.scan_all_components(force_rescan=True)
    
    logger.info(f"✅ Scanned {len(registry.components)} components")
    
    # Test 2: Get registry summary
    logger.info("📊 Testing: Get registry summary")
    summary = scanner.get_registry_summary()
    logger.info(f"Registry Summary: {json.dumps(summary, indent=2, default=str)}")
    
    # Test 3: Search components
    logger.info("🔎 Testing: Search components")
    search_queries = ["card", "order", "button", "customer"]
    
    for query in search_queries:
        results = scanner.search_components(query)
        logger.info(f"Search '{query}': Found {len(results)} components")
        for result in results[:3]:  # Show first 3 results
            logger.info(f"  - {result.name} ({result.component_type.value}): {result.purpose}")
    
    # Test 4: Get components by type
    logger.info("🏗️ Testing: Get components by type")
    for comp_type in ComponentType:
        components = registry.get_by_type(comp_type)
        logger.info(f"{comp_type.value.title()}: {len(components)} components")
        for comp in components[:2]:  # Show first 2
            logger.info(f"  - {comp.name}")
    
    # Test 5: Get components by domain
    logger.info("🏢 Testing: Get components by business domain")
    for domain in BusinessDomain:
        components = registry.get_by_domain(domain)
        if components:  # Only show domains with components
            logger.info(f"{domain.value}: {len(components)} components")
            for comp in components[:2]:  # Show first 2
                logger.info(f"  - {comp.name}")
    
    # Test 6: Workflow component matching
    logger.info("🔀 Testing: Workflow component matching")
    workflows = [
        "Display product information with pricing and add to cart",
        "Show customer order history with status updates",
        "Create a form for user registration",
        "Display admin dashboard with data tables"
    ]
    
    for workflow in workflows:
        suitable_components = scanner.get_components_for_workflow(workflow)
        total_components = sum(len(comps) for comps in suitable_components.values())
        logger.info(f"Workflow: '{workflow[:50]}...'")
        logger.info(f"  Suitable components: {total_components}")
        for type_name, components in suitable_components.items():
            if components:
                logger.info(f"    {type_name}: {[comp.name for comp in components[:3]]}")
    
    # Test 7: Get specific component details
    logger.info("🔍 Testing: Get component details")
    test_components = ["Card", "OrdersTab", "Button"]
    
    for comp_name in test_components:
        component = scanner.get_component_by_name(comp_name)
        if component:
            logger.info(f"Component: {component.name}")
            logger.info(f"  Type: {component.component_type.value}")
            logger.info(f"  Purpose: {component.purpose}")
            logger.info(f"  Props: {len(component.props)}")
            logger.info(f"  Domains: {[d.value for d in component.business_domains]}")
            logger.info(f"  State: {component.has_state}, Effects: {component.has_effects}")
        else:
            logger.info(f"Component '{comp_name}' not found")
    
    logger.info("🎉 Component Scanner testing completed!")

if __name__ == "__main__":
    asyncio.run(test_component_scanner())