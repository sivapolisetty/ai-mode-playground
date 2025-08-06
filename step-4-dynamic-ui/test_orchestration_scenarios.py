#!/usr/bin/env python3
"""
Comprehensive Test Script for Intelligent Orchestration System

This script tests 10 diverse query scenarios to validate the LLM-based 
tool orchestration capabilities across different use cases.
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import List, Dict, Any

class OrchestrationTester:
    """Test harness for intelligent orchestration system"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def get_test_queries(self) -> List[Dict[str, Any]]:
        """Define 10 diverse test scenarios"""
        return [
            {
                "id": "simple_product_search",
                "query": "Find laptops under $2000",
                "expected_tools": ["search_products"],
                "expected_ui_type": "product_cards",
                "description": "Simple product search with price constraint"
            },
            {
                "id": "product_comparison", 
                "query": "Compare iPhone 15 Pro and Samsung Galaxy S24",
                "expected_tools": ["search_products", "search_products"],
                "expected_ui_type": "comparison_cards",
                "description": "Multi-tool comparison between specific products"
            },
            {
                "id": "product_details",
                "query": "What's the price and specs of MacBook Air M2?",
                "expected_tools": ["search_products"],
                "expected_ui_type": "product_details",
                "description": "Specific product detail inquiry"
            },
            {
                "id": "category_exploration",
                "query": "Show me all Apple products",
                "expected_tools": ["search_products"],
                "expected_ui_type": "product_grid",
                "description": "Brand-based product filtering"
            },
            {
                "id": "price_range_search",
                "query": "Find smartphones between $500 and $1000",
                "expected_tools": ["search_products"],
                "expected_ui_type": "filtered_products",
                "description": "Price range filtering with product category"
            },
            {
                "id": "customer_orders",
                "query": "Show me my recent orders",
                "expected_tools": ["get_customer_orders"],
                "expected_ui_type": "order_history",
                "description": "Customer order history retrieval",
                "context": {"customer_id": "cust_001"}
            },
            {
                "id": "order_tracking",
                "query": "Track my last order",
                "expected_tools": ["get_customer_orders", "track_order"],
                "expected_ui_type": "order_tracking",
                "description": "Multi-step order tracking workflow",
                "context": {"customer_id": "cust_001"}
            },
            {
                "id": "product_alternatives",
                "query": "Find alternatives to iPhone 15 Pro under $900",
                "expected_tools": ["search_products"],
                "expected_ui_type": "alternative_products",
                "description": "Alternative product search with price constraint"
            },
            {
                "id": "bulk_comparison",
                "query": "Compare all smartphones under $800",
                "expected_tools": ["search_products"],
                "expected_ui_type": "comparison_table",
                "description": "Bulk product comparison with filtering"
            },
            {
                "id": "complex_requirement",
                "query": "I need a laptop for video editing under $1500 with good graphics",
                "expected_tools": ["search_products"],
                "expected_ui_type": "recommended_products",
                "description": "Complex requirement-based product recommendation"
            }
        ]
    
    async def test_single_query(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single query scenario"""
        print(f"\n🧪 Testing: {test_case['id']}")
        print(f"📝 Query: \"{test_case['query']}\"")
        print(f"📋 Description: {test_case['description']}")
        
        start_time = time.time()
        
        try:
            # Prepare request
            payload = {
                "message": test_case["query"],
                "context": {
                    "session_id": f"test_{test_case['id']}",
                    **test_case.get("context", {})
                }
            }
            
            # Make API call
            async with self.session.post(
                f"{self.base_url}/chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"HTTP {response.status}: {error_text}")
                
                result = await response.json()
                execution_time = time.time() - start_time
                
                # Analyze response
                analysis = self.analyze_response(test_case, result, execution_time)
                
                # Print results
                self.print_test_result(test_case, analysis)
                
                return analysis
                
        except Exception as e:
            execution_time = time.time() - start_time
            error_analysis = {
                "test_id": test_case["id"],
                "success": False,
                "error": str(e),
                "execution_time": execution_time,
                "orchestration_used": False,
                "tools_called": [],
                "ui_components": 0,
                "response_quality": "failed"
            }
            
            print(f"❌ TEST FAILED: {str(e)}")
            return error_analysis
    
    def analyze_response(self, test_case: Dict[str, Any], result: Dict[str, Any], execution_time: float) -> Dict[str, Any]:
        """Analyze the API response for test validation"""
        
        # Extract orchestration details
        orchestration = result.get("debug", {}).get("orchestration", {})
        processing_type = result.get("debug", {}).get("processing_type", "unknown")
        tools_used = result.get("debug", {}).get("tools_used", [])
        ui_components = result.get("ui_components", [])
        
        # Validate orchestration
        orchestration_used = processing_type == "orchestration"
        tools_match = self.validate_tools_used(test_case.get("expected_tools", []), tools_used)
        ui_quality = self.assess_ui_quality(ui_components, test_case.get("expected_ui_type", ""))
        response_quality = self.assess_response_quality(result.get("message", ""))
        
        return {
            "test_id": test_case["id"],
            "success": orchestration_used and tools_match["valid"],
            "execution_time": execution_time,
            "orchestration_used": orchestration_used,
            "tools_called": tools_used,
            "expected_tools": test_case.get("expected_tools", []),
            "tools_validation": tools_match,
            "ui_components": len(ui_components),
            "ui_quality": ui_quality,
            "response_quality": response_quality,
            "orchestration_reasoning": orchestration.get("reasoning", ""),
            "synthesis_reasoning": orchestration.get("synthesis_reasoning", ""),
            "raw_response": result
        }
    
    def validate_tools_used(self, expected_tools: List[str], actual_tools: List[str]) -> Dict[str, Any]:
        """Validate that the correct tools were used"""
        if not expected_tools:
            return {"valid": True, "reason": "No specific tools expected"}
        
        # Check if all expected tools are present (order doesn't matter)
        expected_set = set(expected_tools)
        actual_set = set(actual_tools)
        
        if expected_set.issubset(actual_set):
            return {
                "valid": True,
                "reason": f"All expected tools used: {expected_tools}",
                "extra_tools": list(actual_set - expected_set)
            }
        else:
            missing_tools = list(expected_set - actual_set)
            return {
                "valid": False,
                "reason": f"Missing tools: {missing_tools}",
                "missing_tools": missing_tools,
                "extra_tools": list(actual_set - expected_set)
            }
    
    def assess_ui_quality(self, ui_components: List[Dict], expected_type: str) -> Dict[str, Any]:
        """Assess the quality of generated UI components"""
        if not ui_components:
            return {
                "score": "none",
                "reason": "No UI components generated"
            }
        
        # Check for appropriate component types
        component_types = [comp.get("type", "unknown") for comp in ui_components]
        
        # Basic quality indicators
        has_actions = any(comp.get("actions") for comp in ui_components)
        has_proper_props = all(comp.get("props") for comp in ui_components)
        
        score = "good" if has_actions and has_proper_props else "basic"
        
        return {
            "score": score,
            "count": len(ui_components),
            "types": component_types,
            "has_actions": has_actions,
            "has_proper_props": has_proper_props
        }
    
    def assess_response_quality(self, message: str) -> str:
        """Assess the quality of the natural language response"""
        if not message:
            return "empty"
        
        # Basic quality indicators
        length = len(message)
        has_specific_info = any(keyword in message.lower() for keyword in 
                              ["price", "$", "specifications", "features", "compare"])
        
        if length > 100 and has_specific_info:
            return "detailed"
        elif length > 50:
            return "adequate" 
        else:
            return "brief"
    
    def print_test_result(self, test_case: Dict[str, Any], analysis: Dict[str, Any]):
        """Print formatted test results"""
        status = "✅ PASS" if analysis["success"] else "❌ FAIL"
        
        print(f"{status} ({analysis['execution_time']:.1f}s)")
        print(f"   🔧 Tools: {analysis['tools_called']}")
        print(f"   🎯 Expected: {analysis['expected_tools']}")
        print(f"   🎨 UI Components: {analysis['ui_components']} ({analysis['ui_quality']['score']})")
        print(f"   📝 Response: {analysis['response_quality']}")
        print(f"   🧠 Orchestration: {'Yes' if analysis['orchestration_used'] else 'No'}")
        
        if not analysis["success"]:
            if not analysis["orchestration_used"]:
                print(f"   ⚠️  Orchestration not used")
            if not analysis["tools_validation"]["valid"]:
                print(f"   ⚠️  Tool validation: {analysis['tools_validation']['reason']}")
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all test scenarios"""
        print("🚀 Starting Intelligent Orchestration Test Suite")
        print("=" * 60)
        
        test_cases = self.get_test_queries()
        all_results = []
        
        for test_case in test_cases:
            result = await self.test_single_query(test_case)
            all_results.append(result)
            self.test_results.append(result)
            
            # Brief pause between tests
            await asyncio.sleep(1)
        
        # Generate summary report
        summary = self.generate_summary_report(all_results)
        self.print_summary_report(summary)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(all_results),
            "summary": summary,
            "detailed_results": all_results
        }
    
    def generate_summary_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics"""
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r["success"])
        orchestration_used = sum(1 for r in results if r["orchestration_used"])
        
        avg_execution_time = sum(r["execution_time"] for r in results) / total_tests
        ui_components_generated = sum(r["ui_components"] for r in results)
        
        tool_usage = {}
        for result in results:
            for tool in result["tools_called"]:
                tool_usage[tool] = tool_usage.get(tool, 0) + 1
        
        return {
            "pass_rate": f"{passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)",
            "orchestration_rate": f"{orchestration_used}/{total_tests} ({orchestration_used/total_tests*100:.1f}%)",
            "avg_execution_time": f"{avg_execution_time:.1f}s",
            "total_ui_components": ui_components_generated,
            "tool_usage": tool_usage,
            "response_quality": {
                "detailed": sum(1 for r in results if r["response_quality"] == "detailed"),
                "adequate": sum(1 for r in results if r["response_quality"] == "adequate"),
                "brief": sum(1 for r in results if r["response_quality"] == "brief")
            }
        }
    
    def print_summary_report(self, summary: Dict[str, Any]):
        """Print formatted summary report"""
        print("\n" + "=" * 60)
        print("📊 TEST SUITE SUMMARY REPORT")
        print("=" * 60)
        print(f"✅ Pass Rate: {summary['pass_rate']}")
        print(f"🎭 Orchestration Usage: {summary['orchestration_rate']}")
        print(f"⏱️  Average Execution Time: {summary['avg_execution_time']}")
        print(f"🎨 Total UI Components: {summary['total_ui_components']}")
        
        print(f"\n🔧 Tool Usage Frequency:")
        for tool, count in sorted(summary['tool_usage'].items(), key=lambda x: x[1], reverse=True):
            print(f"   {tool}: {count} times")
        
        print(f"\n📝 Response Quality Distribution:")
        quality = summary['response_quality']
        print(f"   Detailed: {quality['detailed']}, Adequate: {quality['adequate']}, Brief: {quality['brief']}")
        
        print("\n🎯 Key Insights:")
        if summary['orchestration_rate'].endswith('100.0%)'):
            print("   • Orchestration system working perfectly across all scenarios")
        else:
            print("   • Some queries fell back to traditional processing")
        
        if summary['total_ui_components'] > 0:
            print(f"   • Generated {summary['total_ui_components']} UI components total")
        
        print("=" * 60)

async def main():
    """Main test execution function"""
    print("🔬 Intelligent Orchestration Test Suite")
    print("Testing LLM-based tool orchestration across diverse scenarios\n")
    
    try:
        async with OrchestrationTester() as tester:
            # Check if server is running
            try:
                async with tester.session.get(f"{tester.base_url}/health") as response:
                    if response.status != 200:
                        raise Exception("Server health check failed")
                print("✅ Server is running and healthy\n")
            except Exception as e:
                print(f"❌ Cannot connect to server at {tester.base_url}")
                print(f"   Error: {e}")
                print("   Please ensure the AI backend is running on port 8001")
                return
            
            # Run all tests
            final_report = await tester.run_all_tests()
            
            # Save detailed results to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = f"orchestration_test_results_{timestamp}.json"
            
            with open(results_file, 'w') as f:
                json.dump(final_report, f, indent=2, default=str)
            
            print(f"\n💾 Detailed results saved to: {results_file}")
            
    except KeyboardInterrupt:
        print("\n🛑 Test suite interrupted by user")
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(main())