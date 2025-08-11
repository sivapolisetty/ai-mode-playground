#!/usr/bin/env python3
"""
Test direct trace ingestion to LangFuse using the correct API format
"""
import requests
import json
import uuid
from datetime import datetime
import time

def test_direct_ingestion():
    """Test sending traces directly to LangFuse ingestion API"""
    
    # LangFuse credentials - Updated with new keys
    public_key = "pk-lf-862b860f-83d4-4537-96c1-0cfba9ce0748"
    secret_key = "sk-lf-9720fd8e-1370-4b4d-adcf-3c83f637ad84"
    host = "http://localhost:3001"
    
    # Create a test trace
    trace_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    trace_data = {
        "id": trace_id,
        "timestamp": timestamp,
        "type": "trace-create",
        "body": {
            "id": trace_id,
            "timestamp": timestamp,
            "name": "step4_test_conversation",
            "input": "Show me iPhone products",
            "metadata": {
                "user_id": "test-user",
                "session_id": "test-session",
                "step": "4_dynamic_ui"
            }
        }
    }
    
    # Create a test span
    span_id = str(uuid.uuid4())
    span_data = {
        "id": span_id,
        "timestamp": timestamp,
        "type": "span-create",
        "body": {
            "id": span_id,
            "traceId": trace_id,
            "timestamp": timestamp,
            "name": "search_products",
            "input": "iPhone",
            "output": {
                "count": 6,
                "products": ["iPhone 15", "iPhone 14"]
            },
            "metadata": {
                "tool": "mcp_search_products"
            }
        }
    }
    
    # Batch payload
    payload = {
        "batch": [trace_data, span_data],
        "metadata": {
            "batch_id": str(uuid.uuid4()),
            "sdk_version": "python-3.1.3"
        }
    }
    
    # Headers with authorization
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {public_key}",
        "X-Langfuse-Sdk-Name": "python",
        "X-Langfuse-Sdk-Version": "3.1.3",
        "X-Langfuse-Public-Key": public_key,
    }
    
    print("🚀 Testing Direct LangFuse Ingestion")
    print("=" * 40)
    print(f"Host: {host}")
    print(f"Trace ID: {trace_id}")
    print(f"Span ID: {span_id}")
    
    try:
        response = requests.post(
            f"{host}/api/public/ingestion",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 207:  # Multi-status - partial success
            print("✅ Traces sent successfully!")
            print(f"🌐 View at: {host}/trace/{trace_id}")
            return True
        elif response.status_code == 200:
            print("✅ Traces sent successfully!")
            print(f"🌐 View at: {host}/trace/{trace_id}")
            return True
        else:
            print(f"❌ Failed to send traces")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def test_simple_health_check():
    """Test if LangFuse is accessible"""
    try:
        response = requests.get("http://localhost:3001/api/public/health", timeout=5)
        print(f"Health check: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

if __name__ == "__main__":
    if not test_simple_health_check():
        print("❌ LangFuse not accessible")
        exit(1)
    
    success = test_direct_ingestion()
    
    if success:
        print("\n🎉 SUCCESS! Traces should be visible in LangFuse")
        print("If you can't see them, there may be a frontend/database issue")
    else:
        print("\n❌ Failed to send traces to LangFuse")