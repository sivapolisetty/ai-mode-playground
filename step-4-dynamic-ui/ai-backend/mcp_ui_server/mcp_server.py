"""
MCP UI Server - Model Context Protocol server for component intelligence
Exposes component registry and scanning capabilities via MCP protocol
"""
import asyncio
import logging
from typing import Any, Sequence, Dict, List
from pathlib import Path

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

from .component_scanner import ComponentScanner
from .types import ComponentType, BusinessDomain

logger = logging.getLogger(__name__)

class MCPUIServer:
    """MCP Server for UI Component Intelligence"""
    
    def __init__(self, components_root: str):
        """Initialize MCP UI Server with component root directory"""
        self.scanner = ComponentScanner(components_root)
        self.server = Server("ui-component-server")
        self._setup_tools()
    
    def _setup_tools(self):
        """Setup MCP tools for component operations"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available component intelligence tools"""
            return [
                types.Tool(
                    name="scan_components",
                    description="Scan and analyze all React components in the project",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "force_rescan": {
                                "type": "boolean",
                                "description": "Force rescan of all components ignoring cache",
                                "default": False
                            }
                        },
                        "required": []
                    }
                ),
                types.Tool(
                    name="get_component_registry",
                    description="Get complete component registry with metadata",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                types.Tool(
                    name="search_components",
                    description="Search components by name, purpose, or functionality",
                    inputSchema={
                        "type": "object", 
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for component discovery"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="get_components_by_type",
                    description="Get components filtered by type (atom, molecule, organism, template)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "component_type": {
                                "type": "string",
                                "enum": ["atom", "molecule", "organism", "template"],
                                "description": "Component type to filter by"
                            }
                        },
                        "required": ["component_type"]
                    }
                ),
                types.Tool(
                    name="get_components_by_domain",
                    description="Get components filtered by business domain",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "domain": {
                                "type": "string",
                                "enum": ["core_ui", "product_catalog", "order_management", 
                                        "customer_service", "admin", "payment", "navigation", 
                                        "forms", "data_display", "feedback"],
                                "description": "Business domain to filter by"
                            }
                        },
                        "required": ["domain"]
                    }
                ),
                types.Tool(
                    name="get_workflow_components",
                    description="Get components suitable for a specific workflow or use case",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workflow_description": {
                                "type": "string",
                                "description": "Description of the workflow or feature to implement"
                            }
                        },
                        "required": ["workflow_description"]
                    }
                ),
                types.Tool(
                    name="get_component_details",
                    description="Get detailed metadata for a specific component",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "component_name": {
                                "type": "string",
                                "description": "Name of the component to get details for"
                            }
                        },
                        "required": ["component_name"]
                    }
                ),
                types.Tool(
                    name="analyze_component_usage",
                    description="Analyze how components can be composed together",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "components": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of component names to analyze for composition"
                            }
                        },
                        "required": ["components"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            """Handle tool calls for component operations"""
            
            try:
                if name == "scan_components":
                    force_rescan = arguments.get("force_rescan", False)
                    registry = self.scanner.scan_all_components(force_rescan=force_rescan)
                    summary = self.scanner.get_registry_summary()
                    
                    return [types.TextContent(
                        type="text",
                        text=f"Component scan completed successfully!\\n\\n" +
                             f"Summary:\\n" +
                             f"- Total components: {summary['total_components']}\\n" +
                             f"- Component types: {summary['component_types']}\\n" +
                             f"- Business domains: {summary['business_domains']}\\n" +
                             f"- Last scan: {summary['last_scan']}"
                    )]
                
                elif name == "get_component_registry":
                    summary = self.scanner.get_registry_summary()
                    components_detail = []
                    
                    for file_path, component in self.scanner.registry.components.items():
                        components_detail.append({
                            "name": component.name,
                            "type": component.component_type.value,
                            "domains": [d.value for d in component.business_domains],
                            "purpose": component.purpose,
                            "props_count": len(component.props),
                            "has_state": component.has_state,
                            "file_path": component.file_path
                        })
                    
                    return [types.TextContent(
                        type="text", 
                        text=f"Component Registry:\\n\\n" +
                             f"Registry Summary: {summary}\\n\\n" +
                             f"Components Detail: {components_detail}"
                    )]
                
                elif name == "search_components":
                    query = arguments["query"]
                    results = self.scanner.search_components(query)
                    
                    if not results:
                        return [types.TextContent(
                            type="text",
                            text=f"No components found matching query: '{query}'"
                        )]
                    
                    result_text = f"Found {len(results)} components matching '{query}':\\n\\n"
                    for component in results:
                        result_text += f"**{component.name}** ({component.component_type.value})\\n"
                        result_text += f"Purpose: {component.purpose}\\n"
                        result_text += f"Domains: {[d.value for d in component.business_domains]}\\n"
                        result_text += f"Props: {len(component.props)} props\\n"
                        result_text += f"File: {component.file_path}\\n\\n"
                    
                    return [types.TextContent(type="text", text=result_text)]
                
                elif name == "get_components_by_type":
                    component_type = ComponentType(arguments["component_type"])
                    components = self.scanner.registry.get_by_type(component_type)
                    
                    result_text = f"Components of type '{component_type.value}' ({len(components)} found):\\n\\n"
                    for component in components:
                        result_text += f"- **{component.name}**: {component.purpose}\\n"
                    
                    return [types.TextContent(type="text", text=result_text)]
                
                elif name == "get_components_by_domain":
                    domain = BusinessDomain(arguments["domain"])  
                    components = self.scanner.registry.get_by_domain(domain)
                    
                    result_text = f"Components in '{domain.value}' domain ({len(components)} found):\\n\\n"
                    for component in components:
                        result_text += f"- **{component.name}** ({component.component_type.value}): {component.purpose}\\n"
                    
                    return [types.TextContent(type="text", text=result_text)]
                
                elif name == "get_workflow_components":
                    workflow = arguments["workflow_description"]
                    components = self.scanner.get_components_for_workflow(workflow)
                    
                    result_text = f"Components suitable for workflow: '{workflow}'\\n\\n"
                    
                    for type_name, type_components in components.items():
                        if type_components:
                            result_text += f"**{type_name.title()}:**\\n"
                            for component in type_components:
                                result_text += f"- {component.name}: {component.purpose}\\n"
                            result_text += "\\n"
                    
                    return [types.TextContent(type="text", text=result_text)]
                
                elif name == "get_component_details":
                    component_name = arguments["component_name"]
                    component = self.scanner.get_component_by_name(component_name)
                    
                    if not component:
                        return [types.TextContent(
                            type="text",
                            text=f"Component '{component_name}' not found"
                        )]
                    
                    # Build detailed component information
                    detail_text = f"**{component.name}** Component Details\\n\\n"
                    detail_text += f"Type: {component.component_type.value}\\n"
                    detail_text += f"Purpose: {component.purpose}\\n"
                    detail_text += f"Business Domains: {[d.value for d in component.business_domains]}\\n"
                    detail_text += f"File: {component.file_path}\\n\\n"
                    
                    # Props information
                    if component.props:
                        detail_text += f"**Props ({len(component.props)}):**\\n"
                        for prop in component.props:
                            required_indicator = " (required)" if prop.required else " (optional)"
                            detail_text += f"- {prop.name}: {prop.type}{required_indicator}\\n"
                        detail_text += "\\n"
                    
                    # Technical features
                    detail_text += f"**Technical Features:**\\n"
                    detail_text += f"- Uses State: {component.has_state}\\n"
                    detail_text += f"- Uses Effects: {component.has_effects}\\n"
                    detail_text += f"- Uses Context: {component.has_context}\\n\\n"
                    
                    # Dependencies
                    if component.dependencies:
                        detail_text += f"**Dependencies:**\\n"
                        for dep in component.dependencies:
                            detail_text += f"- {dep}\\n"
                        detail_text += "\\n"
                    
                    # Use cases
                    if component.use_cases:
                        detail_text += f"**Use Cases:**\\n"
                        for use_case in component.use_cases:
                            detail_text += f"- {use_case}\\n"
                    
                    return [types.TextContent(type="text", text=detail_text)]
                
                elif name == "analyze_component_usage":
                    component_names = arguments["components"]
                    analysis_text = f"Component Composition Analysis for: {', '.join(component_names)}\\n\\n"
                    
                    # Get component details
                    components = []
                    for name in component_names:
                        comp = self.scanner.get_component_by_name(name)
                        if comp:
                            components.append(comp)
                        else:
                            analysis_text += f"⚠️ Component '{name}' not found\\n"
                    
                    if not components:
                        return [types.TextContent(type="text", text=analysis_text + "No valid components found.")]
                    
                    # Analyze composition possibilities
                    analysis_text += f"**Composition Analysis:**\\n"
                    for component in components:
                        analysis_text += f"- {component.name} ({component.component_type.value}): {component.purpose}\\n"
                    
                    analysis_text += "\\n**Recommended Usage:**\\n"
                    analysis_text += "These components can be composed together in UI generation to create comprehensive interfaces.\\n"
                    
                    return [types.TextContent(type="text", text=analysis_text)]
                
                else:
                    return [types.TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
                    
            except Exception as e:
                logger.error(f"Error handling tool call {name}: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Error executing {name}: {str(e)}"
                )]
    
    async def run(self):
        """Run the MCP server"""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream, 
                InitializationOptions(
                    server_name="ui-component-server",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )

async def main():
    """Main entry point for MCP UI Server"""
    # Default components root - adjust path as needed
    components_root = "../../../client/src/components"
    
    if not Path(components_root).exists():
        logger.error(f"Components root directory not found: {components_root}")
        return
    
    server = MCPUIServer(components_root)
    await server.run()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())