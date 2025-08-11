#!/usr/bin/env python3
"""
Debug LangFuse project access and create traces in the correct project
"""
import requests
import json
from datetime import datetime

def debug_langfuse_projects():
    """Check what projects exist and which one we should use"""
    
    # Your API keys
    public_key = "pk-lf-862b860f-83d4-4537-96c1-0cfba9ce0748"
    secret_key = "sk-lf-9720fd8e-1370-4b4d-adcf-3c83f637ad84"
    host = "http://localhost:3001"
    
    print("🔍 DEBUGGING LANGFUSE PROJECT ACCESS")
    print("=" * 45)
    
    # Check what endpoints we can access
    endpoints = [
        "/api/public/health",
        "/api/public/projects", 
        "/api/public/sessions",
        "/api/public/traces",
        "/api/public/ingestion"
    ]
    
    headers = {
        "Authorization": f"Bearer {public_key}",
        "X-Langfuse-Public-Key": public_key,
        "Content-Type": "application/json"
    }
    
    for endpoint in endpoints:
        try:
            if endpoint == "/api/public/ingestion":
                # POST request for ingestion
                response = requests.post(f"{host}{endpoint}", headers=headers, json={"batch": []})
            else:
                # GET request for others
                response = requests.get(f"{host}{endpoint}", headers=headers, timeout=5)
            
            print(f"📍 {endpoint}: {response.status_code}")
            
            if response.status_code < 400:
                try:
                    data = response.json()
                    print(f"   ✅ Response: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"   ✅ Response: {response.text[:100]}...")
            else:
                print(f"   ❌ Error: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    # Try to create a simple trace using different approaches
    print(f"\n🧪 Testing Trace Creation Methods")
    print("=" * 35)
    
    # Method 1: Direct ingestion with minimal data
    print("Method 1: Minimal ingestion")
    try:
        minimal_trace = {
            "batch": [{
                "id": "debug-trace-001",
                "type": "trace-create", 
                "timestamp": datetime.now().isoformat() + "Z",
                "body": {
                    "name": "debug-test",
                    "input": "test message"
                }
            }]
        }
        
        response = requests.post(
            f"{host}/api/public/ingestion",
            headers=headers,
            json=minimal_trace
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
    except Exception as e:
        print(f"   Error: {e}")
    
    # Method 2: Try without project specification
    print("\nMethod 2: Without project ID")
    try:
        simple_headers = {
            "Authorization": f"Bearer {public_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{host}/api/public/ingestion",
            headers=simple_headers,
            json=minimal_trace
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    debug_langfuse_projects()