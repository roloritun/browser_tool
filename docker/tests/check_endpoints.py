#!/usr/bin/env python3
"""
Script to check which API endpoints are available
"""

import requests
import json

def check_available_endpoints():
    """Check which endpoints are available in the API"""
    base_url = "http://localhost:8000"
    
    # Test basic endpoints that should exist
    endpoints_to_test = [
        "/automation/navigate_to",
        "/automation/search_google", 
        "/automation/go_back",
        "/automation/go_forward",
        "/automation/refresh",
        "/automation/wait",
        "/automation/click_element",
        "/automation/input_text",
        "/automation/send_keys",
        "/automation/click_coordinates",
        "/automation/scroll_down",
        "/automation/scroll_up",
        "/automation/scroll_to_top",
        "/automation/scroll_to_bottom",
        "/automation/scroll_to_text",
        "/automation/switch_tab",
        "/automation/open_tab",
        "/automation/open_new_tab",
        "/automation/close_tab",
        "/automation/extract_content",
        "/automation/get_page_content",
        "/automation/take_screenshot",
        "/automation/save_pdf",
        "/automation/get_page_pdf",
        "/automation/generate_pdf",
        "/automation/get_cookies",
        "/automation/set_cookie",
        "/automation/clear_cookies",
        "/automation/switch_to_frame",
        "/automation/set_network_conditions",
        "/automation/drag_drop",
        "/automation/drag_and_drop"
    ]
    
    print("🔍 CHECKING AVAILABLE API ENDPOINTS")
    print("="*60)
    
    available = []
    not_found = []
    
    for endpoint in endpoints_to_test:
        try:
            # Make a simple POST request to see if endpoint exists
            response = requests.post(f"{base_url}{endpoint}", json={})
            if response.status_code != 404:
                available.append(endpoint)
                print(f"✅ {endpoint} - Status: {response.status_code}")
            else:
                not_found.append(endpoint)
                print(f"❌ {endpoint} - Status: 404")
        except Exception as e:
            print(f"⚠️  {endpoint} - Error: {str(e)}")
            not_found.append(endpoint)
    
    print(f"\n📊 SUMMARY:")
    print(f"Available endpoints: {len(available)}")
    print(f"Not found: {len(not_found)}")
    
    if not_found:
        print(f"\n❌ Missing endpoints:")
        for endpoint in not_found:
            print(f"   {endpoint}")

if __name__ == "__main__":
    check_available_endpoints()
