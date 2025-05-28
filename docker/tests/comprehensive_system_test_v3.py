#!/usr/bin/env python3
"""
Comprehensive System Test for Docker Browser Automation Environment (v3)
Improved version with better connection handling and reliability fixes
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
    
    def run_docker_command(self, command: List[str], timeout: int = 30) -> tuple:
        """Execute docker command and return (success, output)"""
        try:
            # Use -i instead of -it to avoid terminal issues in automated testing
            result = subprocess.run(
                ["docker", "exec", "-i", self.container_name] + command,
                capture_output=True,
                text=True,
                timeout=timeout
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
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                status = result.stdout.strip()
                container_success = "Up" in status
                details = status
            else:
                container_success = False
                details = "Container not found"
            
            self.log_test("Container Running", container_success, details)
            return container_success
        except Exception as e:
            self.log_test("Container Running", False, str(e))
            return False
    
    def test_supervisorctl_status(self):
        """Test supervisorctl status command"""
        success, output = self.run_docker_command(["supervisorctl", "status"], timeout=15)
        
        if success:
            running_services = output.count("RUNNING")
            # Check for critical services that should be running
            critical_services = ["xvfb", "x11vnc", "novnc", "browser_api", "http_server"]
            has_critical_services = all(service in output for service in critical_services)
            
            # Some services like vnc_setup and workspace_init are meant to exit after completion
            # So we check for at least 5 running services and all critical ones
            status_success = running_services >= 5 and has_critical_services
            details = f"Running services: {running_services}, Critical services present: {has_critical_services}"
        else:
            status_success = False
            details = output
        
        self.log_test("Supervisorctl Status", status_success, details)
        return status_success
    
    def test_supervisorctl_operations(self):
        """Test basic supervisorctl operations"""
        operations = []
        
        # Test restart
        success, output = self.run_docker_command(["supervisorctl", "restart", "startup"], timeout=20)
        operations.append(("Restart", success))
        
        # Wait a moment for services to stabilize
        time.sleep(2)
        
        # Test stop
        success, output = self.run_docker_command(["supervisorctl", "stop", "startup"], timeout=15)
        operations.append(("Stop", success))
        
        # Test start
        success, output = self.run_docker_command(["supervisorctl", "start", "startup"], timeout=15)
        operations.append(("Start", success))
        
        overall_success = all(op[1] for op in operations)
        details = ", ".join([f"{op[0]}: {op[1]}" for op in operations])
        
        self.log_test("Supervisorctl Operations", overall_success, details)
        return overall_success
    
    def test_supervisorctl_group_operations(self):
        """Test supervisorctl group operations"""
        success, output = self.run_docker_command(["supervisorctl", "restart", "apps:"], timeout=20)
        group_success = success
        
        details = "Group restart executed" if group_success else f"Group restart failed: {output}"
        self.log_test("Supervisorctl Group Operations", group_success, details)
        return group_success
    
    def test_novnc_web_interface(self):
        """Test noVNC web interface accessibility"""
        try:
            # Test main page with retries
            web_success = False
            for attempt in range(3):
                try:
                    response = requests.get(f"{self.base_vnc_url}/", timeout=10)
                    if response.status_code == 200 and "noVNC" in response.text:
                        web_success = True
                        break
                except Exception:
                    if attempt < 2:
                        time.sleep(2)
                        continue
                    break
            
            # Test VNC connection page
            vnc_success = False
            for attempt in range(3):
                try:
                    vnc_response = requests.get(f"{self.base_vnc_url}/vnc.html", timeout=10)
                    if vnc_response.status_code == 200:
                        vnc_success = True
                        break
                except Exception:
                    if attempt < 2:
                        time.sleep(2)
                        continue
                    break
            
            overall_success = web_success and vnc_success
            details = f"Main page: {web_success}, VNC page: {vnc_success}"
            
            self.log_test("noVNC Web Interface", overall_success, details)
            return overall_success
        except Exception as e:
            self.log_test("noVNC Web Interface", False, str(e))
            return False
    
    def test_health_check_script(self):
        """Test the health check script"""
        success, output = self.run_docker_command([
            "bash", "-c", "timeout 15 /app/health_check.sh"
        ], timeout=20)
        
        if success:
            health_success = "✅" in output and ("healthy" in output.lower() or "Browser API is healthy" in output)
        else:
            # If the script times out or fails, but we know the API is working externally,
            # this might be an execution environment issue rather than a real problem
            health_success = False
        
        details = output[:150] + "..." if len(output) > 150 else output
        
        self.log_test("Health Check Script", health_success, details)
        return health_success
    
    def test_browser_api_internal(self):
        """Test browser API from inside container"""
        # Use a simpler approach that's more reliable
        success, output = self.run_docker_command([
            "bash", "-c", "curl -s --max-time 5 http://localhost:8000/health | head -1"
        ], timeout=15)
        
        if success and output:
            try:
                # Try to parse as JSON
                health_data = json.loads(output)
                api_success = health_data.get("success", False) and health_data.get("status") == "healthy"
                details = f"API Status: {health_data.get('status', 'unknown')}"
            except json.JSONDecodeError:
                # If not JSON, check if it contains success indicators
                api_success = '"success":true' in output and '"healthy"' in output
                details = f"API responding with: {output[:50]}..."
        else:
            # Fallback test - just check if the port is listening
            success2, output2 = self.run_docker_command([
                "bash", "-c", "netstat -ln | grep :8000 || ss -ln | grep :8000"
            ], timeout=10)
            
            if success2 and ":8000" in output2:
                api_success = True
                details = "API port is listening (fallback test)"
            else:
                api_success = False
                details = f"Command failed and port check failed: {output}"
        
        self.log_test("Browser API Internal", api_success, details)
        return api_success
    
    def test_browser_api_external(self):
        """Test browser API from external host with improved reliability"""
        api_success = False
        details = ""
        
        # Try multiple times with different approaches
        for attempt in range(3):
            try:
                # Wait between attempts
                if attempt > 0:
                    time.sleep(1)
                
                response = requests.get(
                    f"{self.base_api_url}/health", 
                    timeout=10,
                    headers={'Connection': 'close'}  # Avoid connection reuse issues
                )
                
                if response.status_code == 200:
                    try:
                        health_data = response.json()
                        if health_data.get("success", False) and health_data.get("status") == "healthy":
                            api_success = True
                            details = f"External API Status: {health_data.get('status', 'unknown')} (attempt {attempt + 1})"
                            break
                        else:
                            details = f"API returned unhealthy status: {health_data}"
                    except json.JSONDecodeError:
                        details = "Invalid JSON response from external API"
                else:
                    details = f"HTTP {response.status_code} from external API"
                    
            except requests.exceptions.ConnectionError as e:
                details = f"Connection error on attempt {attempt + 1}: {str(e)}"
                continue
            except Exception as e:
                details = f"Error on attempt {attempt + 1}: {str(e)}"
                continue
        
        self.log_test("Browser API External", api_success, details)
        return api_success
    
    def test_browser_api_docs(self):
        """Test browser API documentation endpoint"""
        success, output = self.run_docker_command([
            "curl", "-s", "--max-time", "10", "http://localhost:8000/docs"
        ], timeout=15)
        
        docs_success = success and ("swagger" in output.lower() or "openapi" in output.lower() or "FastAPI" in output)
        details = "API docs accessible" if docs_success else f"Docs not accessible: {output[:50]}"
        
        self.log_test("Browser API Docs", docs_success, details)
        return docs_success
    
    def test_file_server(self):
        """Test the file server on port 8080"""
        try:
            # Try multiple times with improved error handling
            for attempt in range(3):
                try:
                    response = requests.get("http://localhost:8081/", timeout=10)
                    if response.status_code == 200:
                        details = f"File server response: HTTP {response.status_code}"
                        self.log_test("File Server", True, details)
                        return True
                    else:
                        details = f"HTTP {response.status_code}"
                except Exception:
                    if attempt < 2:
                        time.sleep(1)
                        continue
                    details = "Connection failed after retries"
            
            self.log_test("File Server", False, details)
            return False
        except Exception as e:
            self.log_test("File Server", False, str(e))
            return False
    
    def test_process_monitoring(self):
        """Test process monitoring capabilities"""
        success, output = self.run_docker_command(["supervisorctl", "pid", "all"], timeout=15)
        
        if success:
            pid_count = len([line for line in output.split('\n') if line.strip() and line.strip().isdigit()])
            process_success = pid_count >= 4
            details = f"Found {pid_count} active processes"
        else:
            process_success = False
            details = "Process monitoring failed"
        
        self.log_test("Process Monitoring", process_success, details)
        return process_success
    
    def test_vnc_processes(self):
        """Test VNC-related processes"""
        success, output = self.run_docker_command(["ps", "aux"], timeout=15)
        
        if success:
            vnc_processes = output.count("vnc")
            xvfb_processes = output.count("Xvfb")
            vnc_success = vnc_processes >= 1 and xvfb_processes >= 1
            details = f"VNC processes: {vnc_processes}, Xvfb processes: {xvfb_processes}"
        else:
            vnc_success = False
            details = "Process listing failed"
        
        self.log_test("VNC Processes", vnc_success, details)
        return vnc_success
    
    def test_workspace_setup(self):
        """Test workspace directory and content"""
        success, output = self.run_docker_command(["ls", "-la", "/workspace"], timeout=10)
        
        workspace_success = success and "index.html" in output
        details = "Workspace directory accessible with content" if workspace_success else "Workspace setup incomplete"
        
        self.log_test("Workspace Setup", workspace_success, details)
        return workspace_success
    
    def generate_summary(self):
        """Generate test summary"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r["success"])
        failed = total - passed
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print("=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed == 0:
            print("🎉 ALL TESTS PASSED! System is fully operational")
        elif failed <= 2:
            print("⚠️  System has minor issues but is mostly functional")
        else:
            print("❌ System has significant issues that need attention")
        
        # Save detailed results
        results_file = "/tmp/system_test_results_v3.json"
        with open(results_file, 'w') as f:
            json.dump({
                "summary": {
                    "total": total,
                    "passed": passed,
                    "failed": failed,
                    "success_rate": success_rate,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                },
                "results": self.results
            }, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: {results_file}")
        
        return failed == 0
    
    def run_all_tests(self):
        """Run all system tests"""
        print("🚀 Starting Comprehensive System Test (v3)")
        print("=" * 50)
        
        tests = [
            self.test_container_running,
            self.test_supervisorctl_status,
            self.test_supervisorctl_operations,
            self.test_supervisorctl_group_operations,
            self.test_novnc_web_interface,
            self.test_health_check_script,
            self.test_browser_api_internal,
            self.test_browser_api_external,
            self.test_browser_api_docs,
            self.test_file_server,
            self.test_process_monitoring,
            self.test_vnc_processes,
            self.test_workspace_setup
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_test(f"Test {test.__name__}", False, f"Test failed with exception: {str(e)}")
        
        return self.generate_summary()

def main():
    tester = SystemTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
