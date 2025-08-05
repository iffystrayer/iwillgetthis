#!/usr/bin/env python3
"""
Quick test script to verify the fixed login functionality.
"""

import requests
import time
import json

def test_backend_health():
    """Test if backend is responding"""
    try:
        response = requests.get("http://127.0.0.1:30641/api/v1/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def test_login_functionality():
    """Test the login endpoint"""
    try:
        # Test login
        login_data = {
            "username": "admin@aegis-platform.com",
            "password": "admin123"
        }
        
        response = requests.post(
            "http://127.0.0.1:30641/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Login successful!")
            print(f"   - Access Token: {result.get('access_token', 'N/A')[:50]}...")
            print(f"   - User: {result.get('user', {}).get('email', 'N/A')}")
            print(f"   - Role: {result.get('user', {}).get('roles', [{}])[0].get('name', 'N/A')}")
            return True
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Login test error: {e}")
        return False

def main():
    print("🧪 Testing Aegis Platform Login Fix...")
    print("=" * 50)
    
    print("1. Testing backend health...")
    if test_backend_health():
        print("✅ Backend is healthy")
    else:
        print("❌ Backend is not responding")
        print("   Please ensure backend is running on port 30641")
        return
    
    print("\n2. Testing login functionality...")
    success = test_login_functionality()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Login fix is working correctly.")
        print("📝 Frontend should now redirect to dashboard after login.")
    else:
        print("❌ Tests failed. Please check the backend logs.")

if __name__ == "__main__":
    main()