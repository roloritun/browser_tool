#!/usr/bin/env python3
"""
Test script to verify API endpoints work with typed models
"""

import requests
import json
import time

def test_health_endpoint():
    """Test the health check endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Health endpoint working:", response.json())
            return True
        else:
            print("❌ Health endpoint failed:", response.status_code)
            return False
    except Exception as e:
        print("❌ Health endpoint error:", str(e))
        return False

def test_typed_endpoints():
    """Test API endpoints with typed models"""
    print("\nTesting typed API endpoints...")
    
    # Test navigation endpoint with typed model
    navigation_data = {
        "url": "https://www.google.com"
    }
    
    print("Testing navigate_to endpoint with typed model...")
    try:
        response = requests.post(
            "http://localhost:8000/automation/navigate_to",
            json=navigation_data
        )
        print(f"Navigate response status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ Navigate endpoint working with typed model")
            print(f"Success: {result.get('success', False)}")
            print(f"Message: {result.get('message', 'No message')}")
            return True
        else:
            print("❌ Navigate endpoint failed:", response.text)
            return False
    except Exception as e:
        print("❌ Navigate endpoint error:", str(e))
        return False

def test_scroll_endpoint():
    """Test scroll endpoint with typed model"""
    print("\nTesting scroll endpoint with typed model...")
    
    scroll_data = {
        "amount": 300
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/automation/scroll_down",
            json=scroll_data
        )
        print(f"Scroll response status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ Scroll endpoint working with typed model")
            print(f"Success: {result.get('success', False)}")
            return True
        else:
            print("❌ Scroll endpoint failed:", response.text)
            return False
    except Exception as e:
        print("❌ Scroll endpoint error:", str(e))
        return False

def test_no_params_endpoint():
    """Test endpoint that uses NoParamsAction"""
    print("\nTesting go_back endpoint with NoParamsAction...")
    
    # NoParamsAction should work with empty dict
    data = {}
    
    try:
        response = requests.post(
            "http://localhost:8000/automation/go_back",
            json=data
        )
        print(f"Go back response status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ NoParamsAction endpoint working")
            print(f"Success: {result.get('success', False)}")
            return True
        else:
            print("❌ NoParamsAction endpoint failed:", response.text)
            return False
    except Exception as e:
        print("❌ NoParamsAction endpoint error:", str(e))
        return False

def main():
    """Main test function"""
    print("🧪 Testing Browser Automation API with Typed Models")
    print("=" * 50)
    
    # Wait a moment for the API to be ready
    print("Waiting for API to be ready...")
    time.sleep(2)
    
    results = []
    
    # Test health endpoint first
    results.append(test_health_endpoint())
    
    # Only test other endpoints if health check passes
    if results[0]:
        results.append(test_typed_endpoints())
        results.append(test_scroll_endpoint())
        results.append(test_no_params_endpoint())
    else:
        print("❌ Skipping other tests because health check failed")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    passed = sum(results)
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Typed models are working correctly.")
        return True
    else:
        print("❌ Some tests failed. Check the logs above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
