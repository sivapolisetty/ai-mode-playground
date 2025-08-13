#!/usr/bin/env python3
"""
Check if LangFuse traces are being created correctly
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

def check_langfuse_traces():
    """Check recent traces in LangFuse"""
    
    # LangFuse API configuration
    host = os.getenv('LANGFUSE_HOST', 'http://localhost:3001')
    public_key = os.getenv('LANGFUSE_PUBLIC_KEY', 'pk-lf-6c9dc00f-e286-40ff-a5ea-2a37c3e616c1')
    secret_key = os.getenv('LANGFUSE_SECRET_KEY', 'sk-lf-03aface1-27d1-4982-8a77-2837e679e4ec')
    
    print(f"🔍 Checking LangFuse traces at {host}")
    print(f"📊 Using API keys: {public_key[:10]}...")
    
    try:
        # Check if LangFuse API is accessible
        health_url = f"{host}/api/public/health"
        response = requests.get(health_url, timeout=5)
        
        if response.status_code == 200:
            print("✅ LangFuse API is healthy")
        else:
            print(f"⚠️ LangFuse health check returned {response.status_code}")
        
        # Try to get recent traces (this may require authentication)
        traces_url = f"{host}/api/public/traces"
        headers = {
            'Authorization': f'Basic {public_key}:{secret_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            traces_response = requests.get(traces_url, headers=headers, timeout=5)
            if traces_response.status_code == 200:
                traces_data = traces_response.json()
                print(f"📈 Found {len(traces_data.get('data', []))} traces")
                
                # Show recent traces
                for trace in traces_data.get('data', [])[:5]:
                    print(f"  • {trace.get('id', 'unknown')}: {trace.get('name', 'unnamed')} - {trace.get('timestamp', 'no timestamp')}")
                    
            else:
                print(f"⚠️ Could not fetch traces: {traces_response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Traces endpoint not accessible: {e}")
        
        # Test the observe decorator integration
        print("\n🧪 Testing @observe decorator...")
        try:
            from shared.observability.langfuse_decorator import observe
            
            @observe(name="test_trace")
            def test_function():
                return "Test successful"
            
            result = test_function()
            print(f"✅ @observe decorator test: {result}")
            
        except Exception as e:
            print(f"❌ @observe decorator failed: {e}")
    
    except Exception as e:
        print(f"❌ LangFuse connection failed: {e}")

if __name__ == "__main__":
    check_langfuse_traces()