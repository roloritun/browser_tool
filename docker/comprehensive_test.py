#!/usr/bin/env python3
"""
Comprehensive test script for all Browser Automation API endpoints with typed models
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

class APITester:
    def __init__(self):
        self.passed_tests = 0
        self.total_tests = 0
        self.results = []
    
    def test_endpoint(self, name, endpoint, data=None, method="POST"):
        """Generic test method for API endpoints"""
        self.total_tests += 1
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
                
                if success:
                    print(f"   ✅ {name} - SUCCESS: {message}")
                    self.passed_tests += 1
                    self.results.append((name, True, message))
                    return True
                else:
                    print(f"   ⚠️  {name} - API returned success=false: {message}")
                    self.results.append((name, False, message))
                    return False
            else:
                error_msg = response.text[:200] + "..." if len(response.text) > 200 else response.text
                print(f"   ❌ {name} - HTTP {response.status_code}: {error_msg}")
                self.results.append((name, False, f"HTTP {response.status_code}"))
                return False
                
        except Exception as e:
            print(f"   ❌ {name} - Exception: {str(e)}")
            self.results.append((name, False, str(e)))
            return False
    
    def test_health(self):
        """Test health endpoint"""
        return self.test_endpoint("Health Check", "/health", method="GET")
    
    def test_navigation_endpoints(self):
        """Test navigation-related endpoints"""
        print("\n" + "="*60)
        print("🗺️  TESTING NAVIGATION ENDPOINTS")
        print("="*60)
        
        # Test navigate_to with GoToUrlAction
        self.test_endpoint(
            "Navigate to URL", 
            "/automation/navigate_to",
            {"url": "https://httpbin.org/html"}
        )
        
        # Test search_google with SearchGoogleAction
        self.test_endpoint(
            "Google Search", 
            "/automation/search_google",
            {"query": "python automation"}
        )
        
        # Test wait with WaitAction
        self.test_endpoint(
            "Wait Action", 
            "/automation/wait",
            {"duration": 1}
        )
        
        # Test go_back with NoParamsAction
        self.test_endpoint(
            "Go Back", 
            "/automation/go_back"
        )
        
        # Test go_forward with NoParamsAction
        self.test_endpoint(
            "Go Forward", 
            "/automation/go_forward"
        )
        
        # Test refresh with NoParamsAction
        self.test_endpoint(
            "Refresh Page", 
            "/automation/refresh"
        )
    
    def test_interaction_endpoints(self):
        """Test interaction-related endpoints"""
        print("\n" + "="*60)
        print("🎯 TESTING INTERACTION ENDPOINTS")
        print("="*60)
        
        # First navigate to a test page
        self.test_endpoint(
            "Navigate to Test Page", 
            "/automation/navigate_to",
            {"url": "https://httpbin.org/forms/post"}
        )
        
        # Test click_element with ClickElementAction
        self.test_endpoint(
            "Click Element", 
            "/automation/click_element",
            {"selector": "input[name='custname']"}
        )
        
        # Test input_text with InputTextAction
        self.test_endpoint(
            "Input Text", 
            "/automation/input_text",
            {"selector": "input[name='custname']", "text": "Test User"}
        )
        
        # Test send_keys with SendKeysAction
        self.test_endpoint(
            "Send Keys", 
            "/automation/send_keys",
            {"keys": "Tab"}
        )
        
        # Test click_coordinates with ClickCoordinatesAction
        self.test_endpoint(
            "Click Coordinates", 
            "/automation/click_coordinates",
            {"x": 100, "y": 100}
        )
    
    def test_scroll_endpoints(self):
        """Test scrolling-related endpoints"""
        print("\n" + "="*60)
        print("📜 TESTING SCROLL ENDPOINTS")
        print("="*60)
        
        # Test scroll_down with ScrollAction
        self.test_endpoint(
            "Scroll Down", 
            "/automation/scroll_down",
            {"amount": 300}
        )
        
        # Test scroll_up with ScrollAction
        self.test_endpoint(
            "Scroll Up", 
            "/automation/scroll_up",
            {"amount": 200}
        )
        
        # Test scroll_to_top with NoParamsAction
        self.test_endpoint(
            "Scroll to Top", 
            "/automation/scroll_to_top"
        )
        
        # Test scroll_to_bottom with NoParamsAction
        self.test_endpoint(
            "Scroll to Bottom", 
            "/automation/scroll_to_bottom"
        )
        
        # Test scroll_to_text with ScrollToTextAction
        self.test_endpoint(
            "Scroll to Text", 
            "/automation/scroll_to_text",
            {"text": "Customer"}
        )
    
    def test_tab_management_endpoints(self):
        """Test tab management endpoints"""
        print("\n" + "="*60)
        print("📑 TESTING TAB MANAGEMENT ENDPOINTS")
        print("="*60)
        
        # Test open_new_tab with OpenTabAction
        self.test_endpoint(
            "Open New Tab", 
            "/automation/open_new_tab",
            {"url": "https://httpbin.org/json"}
        )
        
        # Test switch_tab with SwitchTabAction (assume tab index 1 exists)
        self.test_endpoint(
            "Switch Tab", 
            "/automation/switch_tab",
            {"tab_index": 1}
        )
        
        # Test close_tab with CloseTabAction
        self.test_endpoint(
            "Close Tab", 
            "/automation/close_tab",
            {"tab_index": 1}
        )
    
    def test_content_endpoints(self):
        """Test content extraction endpoints"""
        print("\n" + "="*60)
        print("📄 TESTING CONTENT ENDPOINTS")
        print("="*60)
        
        # Test get_page_content with ExtractContentAction
        self.test_endpoint(
            "Get Page Content", 
            "/automation/get_page_content",
            {"include_html": True, "include_text": True}
        )
        
        # Test take_screenshot with NoParamsAction
        self.test_endpoint(
            "Take Screenshot", 
            "/automation/take_screenshot"
        )
        
        # Test get_page_pdf with PDFOptionsAction
        self.test_endpoint(
            "Get Page PDF", 
            "/automation/get_page_pdf",
            {"format": "A4", "print_background": True}
        )
    
    def test_cookie_endpoints(self):
        """Test cookie management endpoints"""
        print("\n" + "="*60)
        print("🍪 TESTING COOKIE ENDPOINTS")
        print("="*60)
        
        # Test set_cookie with SetCookieAction
        self.test_endpoint(
            "Set Cookie", 
            "/automation/set_cookie",
            {"name": "test_cookie", "value": "test_value", "domain": "httpbin.org"}
        )
        
        # Test get_cookies with NoParamsAction
        self.test_endpoint(
            "Get Cookies", 
            "/automation/get_cookies"
        )
        
        # Test clear_cookies with NoParamsAction
        self.test_endpoint(
            "Clear Cookies", 
            "/automation/clear_cookies"
        )
    
    def test_advanced_endpoints(self):
        """Test advanced feature endpoints"""
        print("\n" + "="*60)
        print("⚙️  TESTING ADVANCED ENDPOINTS")
        print("="*60)
        
        # First navigate to a page with frames for frame testing
        self.test_endpoint(
            "Navigate to Frame Test Page", 
            "/automation/navigate_to",
            {"url": "https://www.w3schools.com/html/html_iframe.asp"}
        )
        
        # Test switch_to_frame with SwitchToFrameAction (use first iframe if any)
        self.test_endpoint(
            "Switch to Frame", 
            "/automation/switch_to_frame",
            {"frame_selector": "0"}  # Try switching to first frame by index
        )
        
        # Test set_network_conditions with SetNetworkConditionsAction
        self.test_endpoint(
            "Set Network Conditions", 
            "/automation/set_network_conditions",
            {"offline": False, "download_throughput": 1000000, "upload_throughput": 1000000, "latency": 100}
        )
        
        # Navigate back to httpbin page for drag and drop test
        self.test_endpoint(
            "Navigate for Drag Drop Test", 
            "/automation/navigate_to",
            {"url": "https://httpbin.org/html"}
        )
        
        # Test drag_and_drop with DragDropAction
        self.test_endpoint(
            "Drag and Drop", 
            "/automation/drag_and_drop",
            {"source_selector": "body", "target_selector": "body"}
        )
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("="*80)
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {(self.passed_tests / self.total_tests * 100):.1f}%")
        
        if self.passed_tests == self.total_tests:
            print("\n🎉 ALL TESTS PASSED! 🎉")
            print("✅ The typed API models are working correctly!")
        else:
            print(f"\n⚠️  {self.total_tests - self.passed_tests} tests failed.")
            print("\nFailed tests:")
            for name, success, message in self.results:
                if not success:
                    print(f"   ❌ {name}: {message}")
        
        print("\n" + "="*80)

def main():
    """Main test function"""
    print("🧪 COMPREHENSIVE BROWSER AUTOMATION API TEST")
    print("Testing all endpoints with typed Pydantic models")
    print("="*80)
    
    # Wait for API to be ready
    print("⏳ Waiting for API to be ready...")
    time.sleep(3)
    
    tester = APITester()
    
    # Run all test suites
    tester.test_health()
    tester.test_navigation_endpoints()
    tester.test_interaction_endpoints()
    tester.test_scroll_endpoints()
    tester.test_tab_management_endpoints()
    tester.test_content_endpoints()
    tester.test_cookie_endpoints()
    tester.test_advanced_endpoints()
    
    # Print final summary
    tester.print_summary()
    
    # Return success/failure
    return tester.passed_tests == tester.total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
