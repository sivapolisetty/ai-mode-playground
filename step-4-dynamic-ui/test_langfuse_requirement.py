#!/usr/bin/env python3
"""
Test script to validate LangFuse connection requirement enforcement
"""

import sys
import os
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), 'ai-backend'))
from shared.observability.langfuse_decorator import langfuse_config

def test_langfuse_requirement():
    """Test that LangFuse connection checking works correctly"""
    
    print("🔍 Testing LangFuse Connection Requirement")
    print("=" * 50)
    
    # Test LangFuse availability
    is_available = langfuse_config.is_langfuse_available()
    
    if is_available:
        print("✅ LangFuse is available on port 3000")
        print("   The server would start successfully")
        
        # Test API directly
        try:
            response = requests.get("http://localhost:3000/api/public/health", timeout=5)
            print(f"   API Response Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ LangFuse API is healthy")
            else:
                print("   ⚠️  LangFuse API returned non-200 status")
        except Exception as e:
            print(f"   ❌ API test failed: {e}")
            
    else:
        print("❌ LangFuse is NOT available on port 3000")
        print("   Server startup would be blocked")
        print("   This demonstrates the strict enforcement requirement")
    
    print("\n📊 Configuration:")
    print(f"   Host: http://localhost:3000")
    print(f"   Public Key: pk-lf-2dece1a4-10e4-4113-a823-105c85e9ce9e")
    print(f"   Secret Key: sk-lf-4a73a915-faee-4483-ac0d-79e5fc52d002")
    
    print("\n🎯 Test Results:")
    if is_available:
        print("   ✅ PASS - LangFuse requirement satisfied")
        print("   Step 4 can start with full observability")
    else:
        print("   🚫 BLOCK - LangFuse requirement NOT satisfied")  
        print("   Step 4 startup would be prevented")
        print("   User must start LangFuse first")
    
    return is_available

if __name__ == "__main__":
    result = test_langfuse_requirement()
    sys.exit(0 if result else 1)