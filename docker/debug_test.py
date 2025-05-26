#!/usr/bin/env python3
"""
Debug test for specific failing endpoints
"""
import requests
import time

BASE_URL = "http://localhost:8000"

def test_endpoint(name, endpoint, data=None, method="POST"):
    """Test a single endpoint"""
    print(f"\n🧪 Testing {name}...")
    
    try:
        if method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json=data or {})
        else:
            response = requests.get(f"{BASE_URL}{endpoint}")
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            success = result.get('success', False)
            message = result.get('message', 'No message')
            error = result.get('error', '')
            
            if success:
                print(f"   ✅ {name} - SUCCESS: {message}")
                return True
            else:
                print(f"   ⚠️  {name} - FAILED: {message}")
                if error:
                    print(f"   Error: {error}")
                return False
        else:
            print(f"   ❌ {name} - HTTP {response.status_code}: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ {name} - Exception: {str(e)}")
        return False

def main():
    print("🔍 DEBUG TEST FOR FAILING ENDPOINTS")
    print("="*50)
    
    # Wait for API to be ready
    print("⏳ Waiting for API to be ready...")
    time.sleep(2)
    
    # Test basic navigation first
    test_endpoint("Navigate to Test Page", "/automation/navigate_to", {"url": "https://httpbin.org/html"})
    
    # Test the failing endpoints one by one
    test_endpoint("Send Keys", "/automation/send_keys", {"keys": "Tab"})
    test_endpoint("Click Coordinates", "/automation/click_coordinates", {"x": 100, "y": 100})
    test_endpoint("Drag and Drop", "/automation/drag_and_drop", {"source_selector": "body", "target_selector": "body"})

if __name__ == "__main__":
    main()
