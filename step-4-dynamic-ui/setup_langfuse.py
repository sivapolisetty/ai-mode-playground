#!/usr/bin/env python3
"""
Setup LangFuse with initial configuration and get API keys
"""
import requests
import json
import time

def wait_for_langfuse():
    """Wait for LangFuse to be fully ready"""
    print("⏳ Waiting for LangFuse to be ready...")
    
    for i in range(30):  # Wait up to 30 seconds
        try:
            response = requests.get("http://localhost:3001/api/public/health", timeout=5)
            if response.status_code == 200:
                print("✅ LangFuse is ready!")
                return True
        except:
            pass
        
        print(f"   Attempt {i+1}/30...")
        time.sleep(1)
    
    print("❌ LangFuse did not become ready")
    return False

def check_frontend():
    """Check if the frontend is accessible"""
    try:
        response = requests.get("http://localhost:3001", timeout=10)
        print(f"Frontend status: {response.status_code}")
        
        # Check if it's the loading page or actual dashboard
        if "Loading" in response.text:
            print("⚠️  Frontend is still loading...")
            return False
        elif "sign-in" in response.text.lower() or "login" in response.text.lower():
            print("✅ Frontend is ready - shows sign-in page")
            return True
        else:
            print("📄 Frontend response received")
            return True
            
    except Exception as e:
        print(f"❌ Frontend not accessible: {e}")
        return False

def main():
    print("🔧 LangFuse Setup Script")
    print("=" * 30)
    
    if not wait_for_langfuse():
        return False
    
    # Give it a bit more time to fully initialize
    print("⏳ Waiting for full initialization...")
    time.sleep(10)
    
    if not check_frontend():
        print("⚠️  Frontend may still be initializing")
    
    print(f"\n📋 LangFuse Setup Instructions:")
    print("=" * 35)
    print("1. Open http://localhost:3001 in your browser")
    print("2. Create an account or sign in")  
    print("3. Create a project called 'Step 4 Dynamic UI'")
    print("4. Go to Settings -> API Keys")
    print("5. Create new API keys")
    print("6. Update .env.langfuse with the new keys:")
    print("   LANGFUSE_PUBLIC_KEY=pk-lf-...")
    print("   LANGFUSE_SECRET_KEY=sk-lf-...")
    
    print(f"\n🌐 LangFuse Dashboard: http://localhost:3001")
    
    # Try to get some information about the current state
    try:
        # Check if there are any existing API endpoints we can query
        endpoints_to_check = [
            "/api/public/projects",
            "/api/auth/session",
        ]
        
        for endpoint in endpoints_to_check:
            try:
                response = requests.get(f"http://localhost:3001{endpoint}", timeout=5)
                print(f"📍 {endpoint}: {response.status_code}")
                if response.status_code < 400:
                    print(f"   Response: {response.text[:100]}...")
            except:
                pass
                
    except Exception as e:
        print(f"Debug info failed: {e}")
    
    return True

if __name__ == "__main__":
    success = main()
    
    if success:
        print(f"\n✅ Setup complete! Follow the instructions above to get API keys.")
        print("   Then run the trace test again to verify traces are working.")
    else:
        print(f"\n❌ Setup failed. Check LangFuse container logs.")
        print("   docker logs step-4-dynamic-ui-langfuse-1")