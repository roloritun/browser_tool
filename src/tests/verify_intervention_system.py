#!/usr/bin/env python3
"""
Human Intervention System - Quick Verification
This script verifies that all components are working correctly.
"""

import os
import sys
import asyncio
import json
from datetime import datetime

# Add the src directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.logger import logger


class SystemVerification:
    """Verify human intervention system components"""
    
    def __init__(self):
        self.results = {}
        
    def verify_environment_variables(self):
        """Verify required environment variables"""
        logger.info("🔍 Verifying environment variables...")
        
        required_vars = [
            "DAYTONA_API_KEY",
            "DAYTONA_API_URL", 
            "AZURE_OPENAI_API_KEY",
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_DEPLOYMENT_NAME",
            "VNC_PASSWORD"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
            self.results['env_vars'] = {"success": False, "missing": missing_vars}
            return False
        else:
            logger.info("✅ All required environment variables found")
            self.results['env_vars'] = {"success": True, "missing": []}
            return True
    
    def verify_docker_api_files(self):
        """Verify Docker API files exist and are complete"""
        logger.info("🔍 Verifying Docker API files...")
        
        required_files = [
            "docker/browser_api/models/intervention_models.py",
            "docker/browser_api/actions/human_intervention.py",
            "docker/browser_api/main.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), file_path)
            if not os.path.exists(full_path):
                missing_files.append(file_path)
        
        if missing_files:
            logger.error(f"❌ Missing Docker API files: {', '.join(missing_files)}")
            self.results['docker_files'] = {"success": False, "missing": missing_files}
            return False
        else:
            logger.info("✅ All Docker API files found")
            self.results['docker_files'] = {"success": True, "missing": []}
            return True
    
    def verify_langchain_tools(self):
        """Verify Langchain tool files exist"""
        logger.info("🔍 Verifying Langchain tool files...")
        
        required_files = [
            "src/tools/enhanced_browser_tools.py",
            "src/tools/utilities/human_intervention.py",
            "src/tools/langchain_browser_tool.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), file_path)
            if not os.path.exists(full_path):
                missing_files.append(file_path)
        
        if missing_files:
            logger.error(f"❌ Missing Langchain tool files: {', '.join(missing_files)}")
            self.results['langchain_files'] = {"success": False, "missing": missing_files}
            return False
        else:
            logger.info("✅ All Langchain tool files found")
            self.results['langchain_files'] = {"success": True, "missing": []}
            return True
    
    def verify_imports(self):
        """Verify that all imports work correctly"""
        logger.info("🔍 Verifying imports...")
        
        try:
            # Test Daytona SDK
            from daytona_sdk import Daytona, DaytonaConfig, CreateSandboxParams
            logger.info("✅ Daytona SDK imports work")
            
            # Test Langchain imports
            from langchain_openai import AzureChatOpenAI
            from langchain.tools import BaseTool
            logger.info("✅ Langchain imports work")
            
            # Test local imports
            from src.tools.utilities.sandbox_manager import SandboxManager
            logger.info("✅ Sandbox manager imports work")
            
            # Test intervention models (if Docker API is available)
            try:
                sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docker"))
                from browser_api.models.intervention_models import InterventionType, InterventionStatus
                logger.info("✅ Intervention models import work")
            except ImportError as e:
                logger.warning(f"⚠️ Intervention models not importable (expected in Docker): {e}")
            
            self.results['imports'] = {"success": True, "error": None}
            return True
            
        except ImportError as e:
            logger.error(f"❌ Import error: {e}")
            self.results['imports'] = {"success": False, "error": str(e)}
            return False
    
    async def verify_sandbox_connection(self):
        """Verify connection to Daytona (without creating sandbox)"""
        logger.info("🔍 Verifying Daytona connection...")
        
        try:
            from src.tools.utilities.sandbox_manager import SandboxManager
            sandbox_manager = SandboxManager()
            logger.info("✅ Daytona client initialized successfully")
            self.results['daytona_connection'] = {"success": True, "error": None}
            return True
            
        except SystemExit:
            logger.error("❌ Daytona connection failed (missing API key or invalid credentials)")
            self.results['daytona_connection'] = {"success": False, "error": "Missing or invalid credentials"}
            return False
        except Exception as e:
            logger.error(f"❌ Daytona connection error: {e}")
            self.results['daytona_connection'] = {"success": False, "error": str(e)}
            return False
    
    def verify_documentation_exists(self):
        """Verify documentation files exist"""
        logger.info("🔍 Verifying documentation files...")
        
        doc_files = [
            "HUMAN_INTERVENTION_README.md",
            "HUMAN_INTERVENTION_COMPLETE_GUIDE.md"
        ]
        
        missing_docs = []
        for doc_file in doc_files:
            full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), doc_file)
            if not os.path.exists(full_path):
                missing_docs.append(doc_file)
        
        if missing_docs:
            logger.warning(f"⚠️ Missing documentation files: {', '.join(missing_docs)}")
            self.results['documentation'] = {"success": False, "missing": missing_docs}
            return False
        else:
            logger.info("✅ Documentation files found")
            self.results['documentation'] = {"success": True, "missing": []}
            return True
    
    async def run_all_verifications(self):
        """Run all verification checks"""
        logger.info("🚀 Starting Human Intervention System Verification")
        logger.info("=" * 60)
        
        checks = [
            ("Environment Variables", self.verify_environment_variables),
            ("Docker API Files", self.verify_docker_api_files),
            ("Langchain Tool Files", self.verify_langchain_tools),
            ("Python Imports", self.verify_imports),
            ("Daytona Connection", self.verify_sandbox_connection),
            ("Documentation", self.verify_documentation_exists)
        ]
        
        all_passed = True
        
        for check_name, check_func in checks:
            logger.info(f"\n🔍 Running: {check_name}")
            try:
                if asyncio.iscoroutinefunction(check_func):
                    result = await check_func()
                else:
                    result = check_func()
                
                if not result:
                    all_passed = False
                    
            except Exception as e:
                logger.error(f"❌ {check_name} check failed: {e}")
                all_passed = False
        
        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("🎯 VERIFICATION SUMMARY")
        logger.info("=" * 60)
        
        for check_name, result in self.results.items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            logger.info(f"{status} {check_name.replace('_', ' ').title()}")
            
            if not result["success"]:
                if "missing" in result and result["missing"]:
                    logger.info(f"     Missing: {', '.join(result['missing'])}")
                if "error" in result and result["error"]:
                    logger.info(f"     Error: {result['error']}")
        
        logger.info("=" * 60)
        
        if all_passed:
            logger.info("🎉 ALL CHECKS PASSED! Human intervention system is ready!")
            logger.info("🚀 You can now run: python src/complete_intervention_demo.py")
        else:
            logger.error("❌ Some checks failed. Please fix the issues above before proceeding.")
        
        logger.info("=" * 60)
        
        return all_passed


async def main():
    """Main verification execution"""
    verifier = SystemVerification()
    
    try:
        result = await verifier.run_all_verifications()
        
        if result:
            print("\n🎯 Next Steps:")
            print("1. Run the complete demo: python src/complete_intervention_demo.py")
            print("2. Or run individual tests: python src/test_intervention_integration.py")
            print("3. Check documentation: HUMAN_INTERVENTION_COMPLETE_GUIDE.md")
        else:
            print("\n🔧 Please fix the failed checks and run verification again.")
            
    except KeyboardInterrupt:
        logger.info("\n🛑 Verification interrupted by user")
    except Exception as e:
        logger.error(f"\n❌ Verification failed: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Verification stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal verification error: {e}")
