#!/usr/bin/env python3
"""
Fix LangFuse trace ingestion with correct project ID and authentication
"""
import requests
import json
import uuid
import base64
from datetime import datetime

def create_working_trace():
    """Create a trace that actually works with LangFuse"""
    
    # Your API keys  
    public_key = "pk-lf-862b860f-83d4-4537-96c1-0cfba9ce0748"
    secret_key = "sk-lf-9720fd8e-1370-4b4d-adcf-3c83f637ad84"
    host = "http://localhost:3001"
    project_id = "cme69v2i5000610rxp11ozgcv"  # From debug output
    
    print("🔧 CREATING WORKING LANGFUSE TRACE")
    print("=" * 40)
    print(f"Project ID: {project_id}")
    
    # Create proper basic auth header
    auth_string = f"{public_key}:{secret_key}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    # Headers with basic auth
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {auth_b64}"
    }
    
    # Create a proper trace payload
    trace_id = str(uuid.uuid4())
    span_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    # Main trace
    trace_event = {
        "id": trace_id,
        "timestamp": timestamp,
        "type": "trace-create",
        "body": {
            "id": trace_id,
            "name": "step4_agent_conversation",
            "timestamp": timestamp,
            "input": "Show me iPhone products for customer test@email.com",
            "metadata": {
                "user_id": "test-user",
                "session_id": "fix-test-session",
                "step": "4_dynamic_ui",
                "project_id": project_id
            }
        }
    }
    
    # Agent operation span
    span_event = {
        "id": span_id,
        "timestamp": timestamp,
        "type": "span-create", 
        "body": {
            "id": span_id,
            "traceId": trace_id,
            "name": "search_products_tool",
            "timestamp": timestamp,
            "input": {"query": "iPhone", "filters": {}},
            "output": {
                "count": 6,
                "products": ["iPhone 15 Pro", "iPhone 15", "iPhone 14"]
            },
            "metadata": {
                "tool_type": "mcp_search",
                "execution_time_ms": 150
            }
        }
    }
    
    # Batch payload
    payload = {
        "batch": [trace_event, span_event],
        "metadata": {
            "sdk_name": "step4-dynamic-ui",
            "sdk_version": "1.0.0",
            "project_id": project_id
        }
    }
    
    print(f"Trace ID: {trace_id}")
    print(f"Span ID: {span_id}")
    
    try:
        print(f"\n📤 Sending to LangFuse...")
        response = requests.post(
            f"{host}/api/public/ingestion",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 207:
            if result.get("successes"):
                print(f"\n✅ SUCCESS! {len(result['successes'])} traces created")
                print(f"🌐 View trace: {host}/project/{project_id}/traces/{trace_id}")
                return True
            elif result.get("errors"):
                print(f"\n❌ Errors occurred:")
                for error in result["errors"]:
                    print(f"   - {error['id']}: {error['error']}")
        
        return False
        
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def verify_trace_visibility():
    """Check if we can see traces via API"""
    
    public_key = "pk-lf-862b860f-83d4-4537-96c1-0cfba9ce0748"
    secret_key = "sk-lf-9720fd8e-1370-4b4d-adcf-3c83f637ad84"
    host = "http://localhost:3001"
    
    # Basic auth
    auth_string = f"{public_key}:{secret_key}"
    auth_b64 = base64.b64encode(auth_string.encode('ascii')).decode('ascii')
    
    headers = {
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"\n🔍 Checking trace visibility...")
        response = requests.get(f"{host}/api/public/traces", headers=headers, timeout=5)
        
        print(f"Traces API Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data.get('data', []))} traces")
            
            for trace in data.get('data', [])[:3]:  # Show first 3
                print(f"  - {trace.get('name', 'unnamed')}: {trace.get('id', 'no-id')}")
                
        else:
            print(f"Error: {response.text[:100]}")
            
    except Exception as e:
        print(f"Verification failed: {e}")

if __name__ == "__main__":
    success = create_working_trace()
    
    if success:
        verify_trace_visibility()
        print(f"\n🎉 Trace creation successful!")
        print(f"   Check your LangFuse dashboard: http://localhost:3001")
    else:
        print(f"\n❌ Trace creation failed - check logs above")