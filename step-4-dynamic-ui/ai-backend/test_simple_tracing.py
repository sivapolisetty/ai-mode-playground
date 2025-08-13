#!/usr/bin/env python3
"""
Simple test to check if LangFuse tracing works correctly
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from shared.observability.langfuse_decorator import observe

@observe(name="test_function")
async def test_function(message: str):
    """Test function with observe decorator"""
    print(f"Processing: {message}")
    await asyncio.sleep(0.1)  # Simulate work
    return {"result": f"Processed: {message}", "success": True}

@observe(name="nested_function")  
async def nested_function(data):
    """Nested function to test hierarchy"""
    print(f"Nested processing: {data}")
    await asyncio.sleep(0.05)
    return {"nested_result": "done"}

@observe(name="main_workflow")
async def main_workflow():
    """Main workflow that calls other functions"""
    print("Starting main workflow...")
    
    # Call test function
    result1 = await test_function("Hello World")
    print(f"Result 1: {result1}")
    
    # Call nested function
    result2 = await nested_function(result1)
    print(f"Result 2: {result2}")
    
    return {"workflow_complete": True, "results": [result1, result2]}

async def main():
    """Run the test"""
    print("Testing LangFuse tracing...")
    
    try:
        result = await main_workflow()
        print(f"Final result: {result}")
        
        print("\n✅ Test completed successfully!")
        print("Check LangFuse dashboard at http://localhost:3001 for traces")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())