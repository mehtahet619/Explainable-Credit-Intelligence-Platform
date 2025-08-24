#!/usr/bin/env python3
"""
Test CredTech API endpoints
"""

import requests
import json
import sys

def test_endpoint(url, description):
    """Test a single API endpoint"""
    try:
        print(f"Testing {description}...")
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {description} - OK")
            print(f"   Response: {json.dumps(data, indent=2, default=str)[:200]}...")
            return True
        else:
            print(f"❌ {description} - Status: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ {description} - Error: {e}")
        return False

def main():
    """Test all API endpoints"""
    print("Testing CredTech API Endpoints")
    print("=" * 35)
    
    base_url = "http://localhost:8000"
    
    endpoints = [
        (f"{base_url}/", "Root endpoint"),
        (f"{base_url}/health", "Health check"),
        (f"{base_url}/companies", "Companies list"),
        (f"{base_url}/dashboard", "Dashboard data"),
        (f"{base_url}/analytics", "Analytics data"),
    ]
    
    passed = 0
    total = len(endpoints)
    
    for url, description in endpoints:
        if test_endpoint(url, description):
            passed += 1
        print()
    
    print("=" * 35)
    print(f"Results: {passed}/{total} endpoints working")
    
    if passed == total:
        print("🎉 All API endpoints are working!")
        return 0
    else:
        print("⚠️  Some endpoints are not working")
        return 1

if __name__ == "__main__":
    sys.exit(main())