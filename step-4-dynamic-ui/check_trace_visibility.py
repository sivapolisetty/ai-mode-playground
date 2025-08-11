#!/usr/bin/env python3
"""
Check if the latest traces are visible in LangFuse
"""
import requests
import base64
import json

def check_traces():
    """Check what traces are visible in LangFuse"""
    
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
    
    print("🔍 CHECKING LANGFUSE TRACES")
    print("=" * 30)
    
    try:
        response = requests.get(f"{host}/api/public/traces", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            traces = data.get('data', [])
            
            print(f"✅ Found {len(traces)} traces total")
            print(f"\n📋 Recent traces:")
            
            # Show recent traces
            for i, trace in enumerate(traces[:5]):  # Show last 5
                trace_id = trace.get('id', 'no-id')
                name = trace.get('name', 'unnamed')
                timestamp = trace.get('timestamp', 'no-time')
                
                print(f"  {i+1}. {name}")
                print(f"     ID: {trace_id}")
                print(f"     Time: {timestamp}")
                print(f"     URL: {host}/project/cme69v2i5000610rxp11ozgcv/traces/{trace_id}")
                print()
            
            # Check for our specific trace ID
            target_trace_id = "8553bfc2-8cf5-4c06-a8db-c2466fc6dbfc"
            found_target = False
            
            for trace in traces:
                if trace.get('id') == target_trace_id:
                    found_target = True
                    print(f"🎯 FOUND TARGET TRACE: {target_trace_id}")
                    print(f"   Name: {trace.get('name')}")
                    print(f"   Input: {trace.get('input', 'no input')}")
                    break
            
            if not found_target:
                print(f"⚠️  Target trace {target_trace_id} not found yet")
                print("   It may still be processing...")
            
            return len(traces)
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return 0
            
    except Exception as e:
        print(f"❌ Failed: {e}")
        return 0

if __name__ == "__main__":
    trace_count = check_traces()
    
    if trace_count > 0:
        print(f"\n🎉 SUCCESS! {trace_count} traces are visible")
        print(f"🌐 View in dashboard: http://localhost:3001")
        print("   Your traces should now be visible!")
    else:
        print(f"\n❌ No traces visible - check configuration")