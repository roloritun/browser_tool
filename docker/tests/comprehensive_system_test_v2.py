#!/usr/bin/env python3
"""
Comprehensive System Test for Docker Browser Automation Environment
Tests all major components: supervisorctl, VNC, noVNC, browser automation, and web interfaces
"""

import requests
import subprocess
import time
import json
import sys
from typing import Dict, List, Any

class SystemTester:
    def __init__(self, container_name: str = "browser-automation-test"):
        self.container_name = container_name
        self.base_vnc_url = "http://localhost:6080"
        self.base_api_url = "http://localhost:8001"  # Mapped from internal 8000
        self.results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()
    
    def run_docker_command(self, command: List[str]) -> tuple:
        """Execute docker command and return (success, output)"""
        try:
            result = subprocess.run(
                ["docker", "exec", "-it", self.container_name] + command,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout.strip()
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)
    
    def test_container_running(self):
        """Test if container is running"""
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", f"name={self.container_name}", "--format", "{{.Status}}"],
                capture_output=True,
                text=True
            )
            is_running = "Up" in result.stdout
            self.log_test("Container Running", is_running, result.stdout.strip())
            return is_running
        except Exception as e:
            self.log_test("Container Running", False, str(e))
            return False
    
    def test_supervisorctl_status(self):
        """Test supervisorctl status command"""
        success, output = self.run_docker_command(["supervisorctl", "status"])
        
        if success:
            # Count running services
            running_services = [line for line in output.split('\n') if 'RUNNING' in line]
            expected_services = ['xvfb', 'x11vnc', 'novnc', 'http_server', 'browser_api']
            
            running_count = len(running_services)
            details = f"Found {running_count} running services"
            
            # Accept 5+ running services as good
            self.log_test("Supervisorctl Status", running_count >= 5, details)
            return running_count >= 5
        else:
            self.log_test("Supervisorctl Status", False, output)
            return False
    
    def test_supervisorctl_operations(self):
        """Test supervisorctl restart/stop/start operations"""
        # Test restart
        success, output = self.run_docker_command(["supervisorctl", "restart", "apps:http_server"])
        restart_success = success and "started" in output
        
        # Test stop
        success, output = self.run_docker_command(["supervisorctl", "stop", "apps:http_server"])
        stop_success = success and "stopped" in output
        
        # Test start
        success, output = self.run_docker_command(["supervisorctl", "start", "apps:http_server"])
        start_success = success and "started" in output
        
        overall_success = restart_success and stop_success and start_success
        details = f"Restart: {restart_success}, Stop: {stop_success}, Start: {start_success}"
        
        self.log_test("Supervisorctl Operations", overall_success, details)
        return overall_success
    
    def test_supervisorctl_group_operations(self):
        """Test supervisorctl group operations"""
        success, output = self.run_docker_command(["supervisorctl", "restart", "apps:"])
        group_success = success and "started" in output
        
        details = "Group restart executed" if group_success else "Group restart failed"
        self.log_test("Supervisorctl Group Operations", group_success, details)
        return group_success
    
    def test_novnc_web_interface(self):
        """Test noVNC web interface accessibility"""
        try:
            response = requests.get(f"{self.base_vnc_url}/", timeout=10)
            web_success = response.status_code == 200 and "noVNC" in response.text
            
            # Test VNC connection page
            vnc_response = requests.get(f"{self.base_vnc_url}/vnc.html", timeout=10)
            vnc_success = vnc_response.status_code == 200
            
            overall_success = web_success and vnc_success
            details = f"Main page: {web_success}, VNC page: {vnc_success}"
            
            self.log_test("noVNC Web Interface", overall_success, details)
            return overall_success
        except Exception as e:
            self.log_test("noVNC Web Interface", False, str(e))
            return False
    
    def test_health_check_script(self):
        """Test the health check script"""
        success, output = self.run_docker_command(["/app/health_check.sh"])
        
        health_success = success and "✅" in output and "healthy" in output
        details = output[:100] + "..." if len(output) > 100 else output
        
        self.log_test("Health Check Script", health_success, details)
        return health_success
    
    def test_browser_api_internal(self):
        """Test browser API from inside container"""
        success, output = self.run_docker_command([
            "curl", "-s", "http://localhost:8000/health"
        ])
        
        if success:
            try:
                health_data = json.loads(output)
                api_success = health_data.get("success", False) and health_data.get("status") == "healthy"
                details = f"API Status: {health_data.get('status', 'unknown')}"
            except json.JSONDecodeError:
                api_success = False
                details = "Invalid JSON response"
        else:
            api_success = False
            details = output
        
        self.log_test("Browser API Internal", api_success, details)
        return api_success
    
    def test_browser_api_external(self):
        """Test browser API from external host"""
        try:
            response = requests.get(f"{self.base_api_url}/health", timeout=10)
            
            if response.status_code == 200:
                try:
                    health_data = response.json()
                    api_success = health_data.get("success", False) and health_data.get("status") == "healthy"
                    details = f"External API Status: {health_data.get('status', 'unknown')}"
                except json.JSONDecodeError:
                    api_success = False
                    details = "Invalid JSON response from external API"
            else:
                api_success = False
                details = f"HTTP {response.status_code} from external API"
        except Exception as e:
            api_success = False
            details = f"External API connection failed: {str(e)}"
        
        self.log_test("Browser API External", api_success, details)
        return api_success
    
    def test_browser_api_docs(self):
        """Test browser API documentation endpoint"""
        success, output = self.run_docker_command([
            "curl", "-s", "http://localhost:8000/docs"
        ])
        
        docs_success = success and "swagger" in output.lower()
        details = "Swagger docs accessible" if docs_success else "Docs not accessible"
        
        self.log_test("Browser API Docs", docs_success, details)
        return docs_success
    
    def test_file_server(self):
        """Test the file server on port 8080"""
        try:
            response = requests.get("http://localhost:8081/", timeout=10)
            file_success = response.status_code == 200
            details = f"File server response: HTTP {response.status_code}"
            
            self.log_test("File Server", file_success, details)
            return file_success
        except Exception as e:
            self.log_test("File Server", False, str(e))
            return False
    
    def test_process_monitoring(self):
        """Test process monitoring and PIDs"""
        success, output = self.run_docker_command(["supervisorctl", "pid", "all"])
        
        if success:
            pids = [line.strip() for line in output.split('\n') if line.strip() and line.strip().isdigit()]
            monitoring_success = len(pids) >= 4  # At least 4 processes should be running
            details = f"Found {len(pids)} active processes"
        else:
            monitoring_success = False
            details = "Failed to get process PIDs"
        
        self.log_test("Process Monitoring", monitoring_success, details)
        return monitoring_success
    
    def test_vnc_processes(self):
        """Test VNC-related processes"""
        success, output = self.run_docker_command(["ps", "aux"])
        
        if success:
            vnc_processes = [line for line in output.split('\n') if 'vnc' in line.lower()]
            xvfb_processes = [line for line in output.split('\n') if 'xvfb' in line.lower()]
            
            vnc_success = len(vnc_processes) > 0 and len(xvfb_processes) > 0
            details = f"VNC processes: {len(vnc_processes)}, Xvfb processes: {len(xvfb_processes)}"
        else:
            vnc_success = False
            details = "Failed to list processes"
        
        self.log_test("VNC Processes", vnc_success, details)
        return vnc_success
    
    def test_workspace_setup(self):
        """Test workspace directory setup"""
        success, output = self.run_docker_command(["ls", "-la", "/workspace"])
        
        workspace_success = success and "index.html" in output
        details = "Workspace directory accessible with content" if workspace_success else "Workspace setup issue"
        
        self.log_test("Workspace Setup", workspace_success, details)
        return workspace_success
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return summary"""
        print("🚀 Starting Comprehensive System Test")
        print("=" * 50)
        
        # Run all tests
        test_results = [
            self.test_container_running(),
            self.test_supervisorctl_status(),
            self.test_supervisorctl_operations(),
            self.test_supervisorctl_group_operations(),
            self.test_novnc_web_interface(),
            self.test_health_check_script(),
            self.test_browser_api_internal(),
            self.test_browser_api_external(),
            self.test_browser_api_docs(),
            self.test_file_server(),
            self.test_process_monitoring(),
            self.test_vnc_processes(),
            self.test_workspace_setup()
        ]
        
        # Calculate summary
        total_tests = len(test_results)
        passed_tests = sum(test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        print("=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 EXCELLENT: System is fully functional!")
        elif success_rate >= 75:
            print("✅ GOOD: System is mostly functional with minor issues")
        elif success_rate >= 50:
            print("⚠️  WARNING: System has significant issues")
        else:
            print("❌ CRITICAL: System has major problems")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": success_rate,
            "results": self.results
        }

def main():
    """Main test execution"""
    tester = SystemTester()
    summary = tester.run_all_tests()
    
    # Save results
    with open("/tmp/system_test_results.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print("\n📄 Detailed results saved to: /tmp/system_test_results.json")
    
    # Exit with appropriate code
    sys.exit(0 if summary["success_rate"] >= 75 else 1)

if __name__ == "__main__":
    main()
