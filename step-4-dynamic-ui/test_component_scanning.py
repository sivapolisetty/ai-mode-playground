#!/usr/bin/env python3
"""
Test Script for Component Scanning System
Tests the MCP component tools without requiring full server setup
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the backend to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai-backend'))

from tools.component_scanner import ComponentScanner
from tools.component_cache import ComponentCache
from tools.mcp_tools import MCPTools

async def test_component_scanning():
    """Test the component scanning system"""
    print("🧪 Testing Component Scanning System")
    print("=" * 50)
    
    # Test 1: Component Scanner
    print("\n📁 Test 1: Component Scanner")
    try:
        # Use the actual client path
        client_path = os.path.join(os.path.dirname(__file__), "../client/src/components/ui")
        scanner = ComponentScanner(client_path)
        
        print(f"Scanning components in: {client_path}")
        result = await scanner.scan_all_components()
        
        if result.get("success"):
            components = result["data"]
            metadata = result.get("metadata", {})
            
            print(f"✅ Found {len(components)} components")
            print(f"⏱️  Scan time: {metadata.get('scan_time', 0):.2f}s")
            
            # Show component categories
            categories = metadata.get("categories", {})
            print(f"📂 Component categories:")
            for category, comps in categories.items():
                print(f"   - {category}: {len(comps)} components")
            
            # Show sample components
            print(f"\n🔍 Sample components:")
            for i, (name, info) in enumerate(list(components.items())[:3]):
                exports = info.get("exports", [])
                category = info.get("category", "unknown")
                print(f"   - {name} ({category}): {len(exports)} exports")
        else:
            print(f"❌ Scan failed: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Scanner test failed: {e}")
    
    # Test 2: Component Cache
    print("\n💾 Test 2: Component Cache")
    try:
        cache = ComponentCache(".test_cache")
        
        # Test cache info
        cache_info = await cache.get_cache_info()
        print(f"📊 Cache statistics:")
        print(f"   - Memory cache exists: {cache_info['memory_cache']['exists']}")
        print(f"   - File cache exists: {cache_info['file_cache']['exists']}")
        print(f"   - Hit ratio: {cache_info.get('hit_ratio', 0):.2%}")
        
        print("✅ Cache system operational")
        
    except Exception as e:
        print(f"❌ Cache test failed: {e}")
    
    # Test 3: MCP Tools Integration
    print("\n🔧 Test 3: MCP Tools Integration")
    try:
        mcp_tools = MCPTools(client_components_path=client_path)
        
        # Test component library fetch
        print("Fetching component library...")
        library_result = await mcp_tools.get_component_library()
        
        if library_result.get("success"):
            components = library_result["data"]
            source = library_result.get("source", "unknown")
            
            print(f"✅ Component library loaded from {source}")
            print(f"📦 Components available: {len(components)}")
            
            # Test component schema fetch
            if components:
                first_component = list(components.keys())[0]
                print(f"\n🔍 Testing component schema for: {first_component}")
                
                schema_result = await mcp_tools.get_component_schema(first_component)
                if schema_result.get("success"):
                    schema = schema_result["data"]
                    print(f"✅ Schema loaded:")
                    print(f"   - Category: {schema.get('category')}")
                    print(f"   - Exports: {len(schema.get('exports', []))}")
                    print(f"   - Use cases: {len(schema.get('recommended_use_cases', []))}")
                else:
                    print(f"❌ Schema fetch failed: {schema_result.get('error')}")
            
            # Test UI patterns
            print(f"\n🎨 Testing UI patterns for 'product_display'")
            patterns_result = await mcp_tools.get_ui_patterns("product_display")
            if patterns_result.get("success"):
                patterns = patterns_result["data"]["patterns"]
                print(f"✅ Found {len(patterns)} patterns")
                for pattern_name in list(patterns.keys())[:2]:
                    print(f"   - {pattern_name}")
            else:
                print(f"❌ Patterns fetch failed: {patterns_result.get('error')}")
            
        else:
            print(f"❌ Library fetch failed: {library_result.get('error')}")
        
        await mcp_tools.close()
        
    except Exception as e:
        print(f"❌ MCP tools test failed: {e}")
    
    print("\n🎉 Component scanning tests completed!")

async def main():
    """Main test function"""
    try:
        await test_component_scanning()
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"❌ Test suite failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())