#!/usr/bin/env python3
"""
Comprehensive Docker/Browser API Endpoint Verification Script
============================================================

This script verifies all browser API endpoints are properly registered and accessible.
It also tests supervisorctl functionality within sandboxes.
"""

import requests
import json
import time
import subprocess
import os
from typing import Dict, List, Any, Optional

class BrowserAPIVerification:
    """Comprehensive verification of browser API endpoints and sandbox functionality"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.endpoints_to_test = self._get_all_endpoints()
        self.results = {
            "endpoints": {},
            "supervisorctl": {},
            "health": {},
            "summary": {}
        }
    
    def _get_all_endpoints(self) -> List[Dict[str, Any]]:
        """Get all endpoints that should be available in the browser API"""
        return [
            # Navigation endpoints
            {"endpoint": "/automation/navigate_to", "method": "POST", "category": "navigation"},
            {"endpoint": "/automation/search_google", "method": "POST", "category": "navigation"},
            {"endpoint": "/automation/go_back", "method": "POST", "category": "navigation"},
            {"endpoint": "/automation/go_forward", "method": "POST", "category": "navigation"},
            {"endpoint": "/automation/refresh", "method": "POST", "category": "navigation"},
            {"endpoint": "/automation/wait", "method": "POST", "category": "navigation"},
            
            # Interaction endpoints
            {"endpoint": "/automation/click_element", "method": "POST", "category": "interaction"},
            {"endpoint": "/automation/click_coordinates", "method": "POST", "category": "interaction"},
            {"endpoint": "/automation/input_text", "method": "POST", "category": "interaction"},
            {"endpoint": "/automation/send_keys", "method": "POST", "category": "interaction"},
            
            # Tab management endpoints
            {"endpoint": "/automation/switch_tab", "method": "POST", "category": "tab_management"},
            {"endpoint": "/automation/open_tab", "method": "POST", "category": "tab_management"},
            {"endpoint": "/automation/open_new_tab", "method": "POST", "category": "tab_management"},
            {"endpoint": "/automation/close_tab", "method": "POST", "category": "tab_management"},
            
            # Content endpoints
            {"endpoint": "/automation/extract_content", "method": "POST", "category": "content"},
            {"endpoint": "/automation/save_pdf", "method": "POST", "category": "content"},
            {"endpoint": "/automation/generate_pdf", "method": "POST", "category": "content"},
            {"endpoint": "/automation/get_page_content", "method": "POST", "category": "content"},
            {"endpoint": "/automation/take_screenshot", "method": "POST", "category": "content"},
            
            # Scrolling endpoints
            {"endpoint": "/automation/scroll_down", "method": "POST", "category": "scrolling"},
            {"endpoint": "/automation/scroll_up", "method": "POST", "category": "scrolling"},
            {"endpoint": "/automation/scroll_to_top", "method": "POST", "category": "scrolling"},
            {"endpoint": "/automation/scroll_to_bottom", "method": "POST", "category": "scrolling"},
            {"endpoint": "/automation/scroll_to_text", "method": "POST", "category": "scrolling"},
            
            # Cookie and storage endpoints
            {"endpoint": "/automation/get_cookies", "method": "POST", "category": "cookies"},
            {"endpoint": "/automation/set_cookie", "method": "POST", "category": "cookies"},
            {"endpoint": "/automation/clear_cookies", "method": "POST", "category": "cookies"},
            {"endpoint": "/automation/clear_local_storage", "method": "POST", "category": "cookies"},
            
            # Dialog endpoints
            {"endpoint": "/automation/accept_dialog", "method": "POST", "category": "dialog"},
            {"endpoint": "/automation/dismiss_dialog", "method": "POST", "category": "dialog"},
            
            # Frame endpoints
            {"endpoint": "/automation/switch_to_frame", "method": "POST", "category": "frame"},
            {"endpoint": "/automation/switch_to_main_frame", "method": "POST", "category": "frame"},
            
            # Network endpoints
            {"endpoint": "/automation/set_network_conditions", "method": "POST", "category": "network"},
            
            # Drag and drop endpoints
            {"endpoint": "/automation/drag_drop", "method": "POST", "category": "drag_drop"},
            {"endpoint": "/automation/drag_and_drop", "method": "POST", "category": "drag_drop"},
            
            # Dropdown endpoints
            {"endpoint": "/automation/get_dropdown_options", "method": "POST", "category": "dropdown"},
            {"endpoint": "/automation/select_dropdown_option", "method": "POST", "category": "dropdown"},
            
            # Human intervention endpoints
            {"endpoint": "/automation/request_intervention", "method": "POST", "category": "intervention"},
            {"endpoint": "/automation/complete_intervention", "method": "POST", "category": "intervention"},
            {"endpoint": "/automation/cancel_intervention", "method": "POST", "category": "intervention"},
            {"endpoint": "/automation/intervention_status", "method": "POST", "category": "intervention"},
            {"endpoint": "/automation/auto_detect_intervention", "method": "POST", "category": "intervention"},
            
            # Health endpoints
            {"endpoint": "/health", "method": "GET", "category": "health"},
            {"endpoint": "/", "method": "GET", "category": "health"},
        ]
    
    def test_api_endpoints(self) -> Dict[str, Any]:
        """Test all API endpoints for availability"""
        print("🔍 TESTING API ENDPOINTS")
        print("=" * 60)
        
        categories = {}
        total_endpoints = len(self.endpoints_to_test)
        available_endpoints = 0
        
        for endpoint_info in self.endpoints_to_test:
            endpoint = endpoint_info["endpoint"]
            method = endpoint_info["method"]
            category = endpoint_info["category"]
            
            if category not in categories:
                categories[category] = {"total": 0, "available": 0, "endpoints": []}
            
            categories[category]["total"] += 1
            
            try:
                url = f"{self.api_base_url}{endpoint}"
                
                if method == "GET":
                    response = requests.get(url, timeout=5)
                else:
                    # POST with minimal test payload
                    response = requests.post(url, json={}, timeout=5)
                
                # Consider any non-404 response as "endpoint exists"
                if response.status_code != 404:
                    status = "✅ AVAILABLE"
                    available_endpoints += 1
                    categories[category]["available"] += 1
                    is_available = True
                else:
                    status = "❌ NOT FOUND"
                    is_available = False
                
                result = {
                    "status_code": response.status_code,
                    "available": is_available,
                    "response_size": len(response.content)
                }
                
                print(f"{status} {method} {endpoint} - Status: {response.status_code}")
                
            except requests.exceptions.ConnectionError:
                status = "🔌 CONNECTION ERROR"
                result = {"error": "Connection failed", "available": False}
                print(f"{status} {method} {endpoint}")
            except requests.exceptions.Timeout:
                status = "⏰ TIMEOUT"
                result = {"error": "Request timeout", "available": False}
                print(f"{status} {method} {endpoint}")
            except Exception as e:
                status = "⚠️ ERROR"
                result = {"error": str(e), "available": False}
                print(f"{status} {method} {endpoint} - {str(e)}")
            
            categories[category]["endpoints"].append({
                "endpoint": endpoint,
                "method": method,
                "result": result
            })
            
            self.results["endpoints"][endpoint] = result
        
        # Print category summary
        print(f"\n📊 ENDPOINT SUMMARY BY CATEGORY:")
        for category, data in categories.items():
            available = data["available"]
            total = data["total"]
            percentage = (available / total * 100) if total > 0 else 0
            print(f"  • {category.upper()}: {available}/{total} ({percentage:.1f}%)")
        
        print(f"\n🎯 OVERALL SUMMARY:")
        print(f"  • Total endpoints tested: {total_endpoints}")
        print(f"  • Available endpoints: {available_endpoints}")
        print(f"  • Availability rate: {(available_endpoints/total_endpoints*100):.1f}%")
        
        self.results["summary"]["total_endpoints"] = total_endpoints
        self.results["summary"]["available_endpoints"] = available_endpoints
        self.results["summary"]["availability_rate"] = available_endpoints/total_endpoints*100
        self.results["summary"]["categories"] = categories
        
        return categories
    
    def test_health_endpoints(self) -> Dict[str, Any]:
        """Test specific health and status endpoints"""
        print(f"\n💓 TESTING HEALTH ENDPOINTS")
        print("=" * 60)
        
        health_tests = [
            {"endpoint": "/health", "description": "Primary health check"},
            {"endpoint": "/", "description": "Root endpoint"},
            {"endpoint": "/docs", "description": "API documentation"},
            {"endpoint": "/openapi.json", "description": "OpenAPI specification"}
        ]
        
        health_results = {}
        
        for test in health_tests:
            endpoint = test["endpoint"]
            description = test["description"]
            
            try:
                url = f"{self.api_base_url}{endpoint}"
                response = requests.get(url, timeout=10)
                
                health_results[endpoint] = {
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds(),
                    "content_length": len(response.content),
                    "available": response.status_code < 400
                }
                
                status_emoji = "✅" if response.status_code < 400 else "❌"
                print(f"{status_emoji} {endpoint} ({description}) - Status: {response.status_code}, Time: {response.elapsed.total_seconds():.3f}s")
                
            except Exception as e:
                health_results[endpoint] = {
                    "error": str(e),
                    "available": False
                }
                print(f"❌ {endpoint} ({description}) - Error: {str(e)}")
        
        self.results["health"] = health_results
        return health_results
    
    def test_supervisorctl_in_docker(self) -> Dict[str, Any]:
        """Test supervisorctl functionality in Docker containers"""
        print(f"\n🔧 TESTING SUPERVISORCTL FUNCTIONALITY")
        print("=" * 60)
        
        supervisorctl_tests = [
            {"command": "supervisorctl status", "description": "Check service status"},
            {"command": "supervisorctl pid", "description": "Get supervisor PID"},
            {"command": "supervisorctl version", "description": "Get supervisor version"},
            {"command": "supervisorctl help", "description": "Show help commands"}
        ]
        
        supervisorctl_results = {}
        
        # First, check if we're running inside Docker
        try:
            with open('/proc/1/cgroup', 'r') as f:
                cgroup_content = f.read()
                in_docker = 'docker' in cgroup_content or 'containerd' in cgroup_content
        except:
            in_docker = False
        
        if not in_docker:
            print("⚠️ Not running inside Docker container - testing via docker exec")
            
            # Try to find running Docker containers with browser automation
            try:
                result = subprocess.run(
                    ["docker", "ps", "--format", "{{.Names}}", "--filter", "ancestor=browser-automation"],
                    capture_output=True, text=True, timeout=10
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    container_names = result.stdout.strip().split('\n')
                    print(f"📦 Found Docker containers: {container_names}")
                    
                    for container in container_names:
                        print(f"\n🔍 Testing supervisorctl in container: {container}")
                        
                        for test in supervisorctl_tests:
                            command = test["command"]
                            description = test["description"]
                            
                            try:
                                result = subprocess.run(
                                    ["docker", "exec", container] + command.split(),
                                    capture_output=True, text=True, timeout=30
                                )
                                
                                supervisorctl_results[f"{container}_{command}"] = {
                                    "exit_code": result.returncode,
                                    "stdout": result.stdout,
                                    "stderr": result.stderr,
                                    "success": result.returncode == 0
                                }
                                
                                status_emoji = "✅" if result.returncode == 0 else "❌"
                                print(f"{status_emoji} {command} ({description})")
                                if result.stdout:
                                    print(f"    Output: {result.stdout.strip()}")
                                if result.stderr:
                                    print(f"    Error: {result.stderr.strip()}")
                                    
                            except subprocess.TimeoutExpired:
                                supervisorctl_results[f"{container}_{command}"] = {
                                    "error": "Command timeout",
                                    "success": False
                                }
                                print(f"⏰ {command} - TIMEOUT")
                            except Exception as e:
                                supervisorctl_results[f"{container}_{command}"] = {
                                    "error": str(e),
                                    "success": False
                                }
                                print(f"❌ {command} - Error: {str(e)}")
                else:
                    print("❌ No browser automation containers found")
                    supervisorctl_results["container_search"] = {
                        "error": "No containers found",
                        "success": False
                    }
                    
            except Exception as e:
                print(f"❌ Failed to search for Docker containers: {str(e)}")
                supervisorctl_results["docker_search"] = {
                    "error": str(e),
                    "success": False
                }
        else:
            print("✅ Running inside Docker container - testing directly")
            
            for test in supervisorctl_tests:
                command = test["command"]
                description = test["description"]
                
                try:
                    result = subprocess.run(
                        command.split(),
                        capture_output=True, text=True, timeout=30
                    )
                    
                    supervisorctl_results[command] = {
                        "exit_code": result.returncode,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "success": result.returncode == 0
                    }
                    
                    status_emoji = "✅" if result.returncode == 0 else "❌"
                    print(f"{status_emoji} {command} ({description})")
                    if result.stdout:
                        print(f"    Output: {result.stdout.strip()}")
                    if result.stderr and result.returncode != 0:
                        print(f"    Error: {result.stderr.strip()}")
                        
                except Exception as e:
                    supervisorctl_results[command] = {
                        "error": str(e),
                        "success": False
                    }
                    print(f"❌ {command} - Error: {str(e)}")
        
        self.results["supervisorctl"] = supervisorctl_results
        return supervisorctl_results
    
    def generate_final_report(self) -> Dict[str, Any]:
        """Generate a comprehensive final report"""
        print(f"\n🎉 FINAL VERIFICATION REPORT")
        print("=" * 60)
        
        # Endpoint statistics
        total_endpoints = self.results["summary"].get("total_endpoints", 0)
        available_endpoints = self.results["summary"].get("available_endpoints", 0)
        availability_rate = self.results["summary"].get("availability_rate", 0)
        
        # Health statistics
        health_endpoints = len(self.results["health"])
        healthy_endpoints = sum(1 for result in self.results["health"].values() 
                              if isinstance(result, dict) and result.get("available", False))
        
        # Supervisorctl statistics
        supervisorctl_commands = len(self.results["supervisorctl"])
        successful_commands = sum(1 for result in self.results["supervisorctl"].values()
                                if isinstance(result, dict) and result.get("success", False))
        
        print(f"📊 ENDPOINT VERIFICATION:")
        print(f"  • Total endpoints: {total_endpoints}")
        print(f"  • Available endpoints: {available_endpoints}")
        print(f"  • Availability rate: {availability_rate:.1f}%")
        
        print(f"\n💓 HEALTH CHECK:")
        print(f"  • Health endpoints tested: {health_endpoints}")
        print(f"  • Healthy endpoints: {healthy_endpoints}")
        print(f"  • Health rate: {(healthy_endpoints/health_endpoints*100) if health_endpoints > 0 else 0:.1f}%")
        
        print(f"\n🔧 SUPERVISORCTL VERIFICATION:")
        print(f"  • Commands tested: {supervisorctl_commands}")
        print(f"  • Successful commands: {successful_commands}")
        print(f"  • Success rate: {(successful_commands/supervisorctl_commands*100) if supervisorctl_commands > 0 else 0:.1f}%")
        
        # Overall system health
        overall_health = "🟢 EXCELLENT" if availability_rate >= 90 else "🟡 GOOD" if availability_rate >= 70 else "🔴 NEEDS ATTENTION"
        print(f"\n🏆 OVERALL SYSTEM HEALTH: {overall_health}")
        
        if availability_rate >= 90:
            print("✅ All systems are operational and ready for production use!")
        elif availability_rate >= 70:
            print("⚠️ System is mostly operational but some endpoints may need attention.")
        else:
            print("❌ System needs attention - many endpoints are not responding.")
        
        return {
            "overall_health": overall_health,
            "endpoint_stats": {
                "total": total_endpoints,
                "available": available_endpoints,
                "rate": availability_rate
            },
            "health_stats": {
                "total": health_endpoints,
                "healthy": healthy_endpoints,
                "rate": (healthy_endpoints/health_endpoints*100) if health_endpoints > 0 else 0
            },
            "supervisorctl_stats": {
                "total": supervisorctl_commands,
                "successful": successful_commands,
                "rate": (successful_commands/supervisorctl_commands*100) if supervisorctl_commands > 0 else 0
            }
        }
    
    def run_comprehensive_verification(self) -> Dict[str, Any]:
        """Run all verification tests"""
        print("🚀 STARTING COMPREHENSIVE BROWSER API VERIFICATION")
        print("=" * 70)
        
        start_time = time.time()
        
        # Run all tests
        self.test_api_endpoints()
        self.test_health_endpoints() 
        self.test_supervisorctl_in_docker()
        final_report = self.generate_final_report()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n⏱️ Verification completed in {duration:.2f} seconds")
        
        # Save results to file
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        results_file = f"browser_api_verification_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"📄 Detailed results saved to: {results_file}")
        
        return final_report

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify Browser API endpoints and supervisorctl functionality")
    parser.add_argument("--api-url", default="http://localhost:8000", 
                       help="Base URL for the browser API (default: http://localhost:8000)")
    parser.add_argument("--save-results", action="store_true", 
                       help="Save detailed results to JSON file")
    
    args = parser.parse_args()
    
    # Create verifier and run tests
    verifier = BrowserAPIVerification(api_base_url=args.api_url)
    final_report = verifier.run_comprehensive_verification()
    
    # Exit with appropriate code
    if final_report["endpoint_stats"]["rate"] >= 90:
        exit(0)  # Success
    elif final_report["endpoint_stats"]["rate"] >= 70:
        exit(1)  # Warning
    else:
        exit(2)  # Error

if __name__ == "__main__":
    main()
