#!/usr/bin/env python3
"""
Live Sandbox Demo
Creates a Daytona sandbox and shows the live browser URLs for manual testing.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


import asyncio
import os
import sys
import webbrowser
from datetime import datetime

# Add the src directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools.utilities.sandbox_manager import SandboxManager
from src.utils.logger import logger


class LiveSandboxDemo:
    """Live sandbox demonstration with manual browser access"""
    
    def __init__(self):
        self.sandbox_manager = SandboxManager()
        self.sandbox_id = None
        self.urls = {}
        
    def create_sandbox(self):
        """Create a Daytona sandbox and extract URLs"""
        logger.info("🚀 Creating live Daytona sandbox for manual testing...")
        
        try:
            result = self.sandbox_manager.create_sandbox()
            (
                self.sandbox_id,
                cdp_url,
                vnc_url,
                novnc_url,
                api_url,
                web_url,
                browser_api_url
            ) = result
            
            self.urls = {
                'sandbox_id': self.sandbox_id,
                'cdp': cdp_url,
                'vnc': vnc_url,
                'novnc': novnc_url,
                'api': api_url,
                'web': web_url,
                'browser_api': browser_api_url,
                'vnc_password': os.getenv("VNC_PASSWORD", "vncpassword")
            }
            
            logger.info(f"✅ Sandbox created: {self.sandbox_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create sandbox: {e}")
            return False
    
    def print_access_info(self):
        """Print comprehensive access information"""
        print("\n" + "="*80)
        print("🎯 LIVE HUMAN INTERVENTION SANDBOX - READY!")
        print("="*80)
        print(f"📱 Sandbox ID: {self.urls['sandbox_id']}")
        print(f"🔑 VNC Password: {self.urls['vnc_password']}")
        print("\n📋 ACCESS URLS:")
        print("-" * 50)
        print(f"🌐 Browser (NoVNC):     {self.urls['novnc']}")
        print(f"🔧 VNC Direct:          {self.urls['vnc']}")
        print(f"📡 API Endpoints:       {self.urls['api']}/docs")
        print(f"🖥️  Web Interface:       {self.urls['web']}")
        print(f"🤖 Browser API:         {self.urls['browser_api']}")
        print(f"🔗 Chrome DevTools:     {self.urls['cdp']}")
        
        print("\n📋 MANUAL TESTING STEPS:")
        print("-" * 50)
        print("1. Open the NoVNC browser URL above")
        print("2. Enter VNC password when prompted")
        print("3. You'll see a Ubuntu desktop with Chrome browser")
        print("4. Navigate to websites that might have:")
        print("   • CAPTCHAs (try Google searches)")
        print("   • Cookie consent dialogs")
        print("   • Login requirements")
        print("   • Anti-bot protection")
        print("5. Test the intervention endpoints:")
        print(f"   • Visit {self.urls['api']}/docs for API testing")
        print("   • Use the Browser API for automation")
        
        print("\n🔍 WHAT TO LOOK FOR:")
        print("-" * 50)
        print("• Chrome browser should be running")
        print("• Browser should respond to manual navigation")
        print("• VNC interface should be smooth and responsive")
        print("• API endpoints should return valid responses")
        print("• Human intervention hooks are in place")
        
        print("\n⚠️  IMPORTANT NOTES:")
        print("-" * 50)
        print("• Keep this script running to maintain the sandbox")
        print("• Press Ctrl+C to cleanup and delete the sandbox")
        print("• Browser API may take 30-60 seconds to fully start")
        print("• VNC password is case-sensitive")
        
        print("="*80)
        print("🚀 Ready for live testing! Check the URLs above.")
        print("="*80)
    
    def open_browser_urls(self):
        """Open key URLs in the default browser"""
        important_urls = [
            ("Human Intervention Browser (NoVNC)", self.urls['novnc']),
            ("API Documentation", f"{self.urls['api']}/docs"),
        ]
        
        logger.info("🌐 Opening key URLs in your default browser...")
        for name, url in important_urls:
            try:
                webbrowser.open(url)
                logger.info(f"✅ Opened: {name}")
            except Exception as e:
                logger.warning(f"⚠️ Could not auto-open {name}: {e}")
                logger.info(f"   Please manually visit: {url}")
    
    def wait_for_interrupt(self):
        """Wait for user interrupt while keeping sandbox alive"""
        try:
            print("\n⏳ Sandbox is live and ready for testing...")
            print("   Press Ctrl+C when done to cleanup and exit.")
            
            # Keep the process alive
            while True:
                import time
                time.sleep(10)
                print(f"   Sandbox {self.sandbox_id} is still running... (Press Ctrl+C to stop)")
                
        except KeyboardInterrupt:
            print("\n🛑 User requested shutdown...")
            return
    
    def cleanup(self):
        """Clean up the sandbox"""
        if self.sandbox_id:
            logger.info(f"🧹 Cleaning up sandbox: {self.sandbox_id}")
            try:
                self.sandbox_manager.delete_sandbox(self.sandbox_id)
                logger.info("✅ Sandbox cleanup completed")
            except Exception as e:
                logger.error(f"❌ Cleanup failed: {e}")


def main():
    """Main demo execution"""
    demo = LiveSandboxDemo()
    
    try:
        # Create sandbox
        if not demo.create_sandbox():
            logger.error("❌ Failed to create sandbox, exiting...")
            return
        
        # Show access information
        demo.print_access_info()
        
        # Open URLs in browser
        demo.open_browser_urls()
        
        # Wait for user to finish testing
        demo.wait_for_interrupt()
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Demo interrupted by user")
    except Exception as e:
        logger.error(f"\n❌ Demo failed: {e}")
    finally:
        # Always cleanup
        demo.cleanup()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
