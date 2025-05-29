#!/usr/bin/env python3
"""
Realistic Demo Validation Test

This script performs quick validation tests on all realistic demos to ensure
they can initialize properly without running the full demonstrations.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import asyncio
import logging
from datetime import datetime

from tools.utilities.browser_tools_init import initialize_browser_tools

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Demo modules to test
DEMO_MODULES = [
    "two_factor_auth_demo_fixed",
    "ecommerce_workflow_demo_fixed", 
    "form_automation_demo_fixed",
    "javascript_spa_demo_fixed",
    "multi_tab_workflow_demo",
    "social_media_demo"
]

class DemoValidationTest:
    def __init__(self):
        self.results = {}
        
    async def test_demo_initialization(self, module_name: str) -> dict:
        """Test if a demo can initialize properly."""
        logger.info(f"\n🔍 Testing {module_name}")
        
        result = {
            "module": module_name,
            "import_success": False,
            "class_instantiation": False,
            "initialization_method": False,
            "main_function": False,
            "error": None
        }
        
        try:
            # Test import
            module_path = f"examples.realistic.{module_name}"
            module = __import__(module_path, fromlist=["main"])
            result["import_success"] = True
            logger.info(f"✅ {module_name}: Import successful")
            
            # Test main function exists
            if hasattr(module, 'main'):
                result["main_function"] = True
                logger.info(f"✅ {module_name}: Main function found")
            else:
                logger.warning(f"⚠️ {module_name}: No main function found")
            
            # Try to find and instantiate the demo class
            class_names = [
                "TwoFactorAuthDemo",
                "EcommerceWorkflowDemo", 
                "FormAutomationDemo",
                "JavaScriptSPADemo",
                "MultiTabWorkflowDemo",
                "SocialMediaDemo"
            ]
            
            demo_class = None
            for class_name in class_names:
                if hasattr(module, class_name):
                    demo_class = getattr(module, class_name)
                    result["class_instantiation"] = True
                    logger.info(f"✅ {module_name}: Demo class {class_name} found")
                    break
            
            if demo_class:
                # Try to instantiate (without initializing)
                demo_instance = demo_class()
                
                # Check for initialize method
                if hasattr(demo_instance, 'initialize'):
                    result["initialization_method"] = True
                    logger.info(f"✅ {module_name}: Initialize method found")
            
            logger.info(f"✅ {module_name}: Validation completed successfully")
            
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"❌ {module_name}: Validation failed - {e}")
        
        return result
    
    async def run_all_validations(self):
        """Run validation tests on all demo modules."""
        logger.info("\n🚀 Starting Realistic Demo Validation Tests")
        logger.info(f"📋 Testing {len(DEMO_MODULES)} demo modules")
        
        start_time = datetime.now()
        
        for i, module_name in enumerate(DEMO_MODULES, 1):
            logger.info(f"\n📋 Test {i}/{len(DEMO_MODULES)}")
            result = await self.test_demo_initialization(module_name)
            self.results[module_name] = result
            
            # Brief pause between tests
            await asyncio.sleep(1)
        
        end_time = datetime.now()
        
        # Generate summary
        self.print_validation_summary(start_time, end_time)
        
        return self.results
    
    def print_validation_summary(self, start_time, end_time):
        """Print comprehensive validation summary."""
        print(f"\n{'='*80}")
        print("📊 REALISTIC DEMO VALIDATION SUMMARY")
        print(f"{'='*80}")
        
        execution_time = (end_time - start_time).total_seconds()
        print(f"⏱️ Total Validation Time: {execution_time:.1f}s")
        print(f"📋 Modules Tested: {len(DEMO_MODULES)}")
        
        # Count successes and failures
        successful_imports = len([r for r in self.results.values() if r["import_success"]])
        successful_main_functions = len([r for r in self.results.values() if r["main_function"]])
        successful_classes = len([r for r in self.results.values() if r["class_instantiation"]])
        successful_init_methods = len([r for r in self.results.values() if r["initialization_method"]])
        
        print(f"\n📈 VALIDATION RESULTS:")
        print(f"✅ Successful Imports: {successful_imports}/{len(DEMO_MODULES)}")
        print(f"✅ Main Functions Found: {successful_main_functions}/{len(DEMO_MODULES)}")
        print(f"✅ Demo Classes Found: {successful_classes}/{len(DEMO_MODULES)}")
        print(f"✅ Initialize Methods Found: {successful_init_methods}/{len(DEMO_MODULES)}")
        
        print(f"\n📋 DETAILED RESULTS:")
        for module_name, result in self.results.items():
            status = "✅" if result["import_success"] and result["main_function"] else "❌"
            print(f"{status} {module_name}")
            
            if result["error"]:
                print(f"    ❌ Error: {result['error']}")
            else:
                features = []
                if result["import_success"]: features.append("Import")
                if result["main_function"]: features.append("Main")
                if result["class_instantiation"]: features.append("Class")
                if result["initialization_method"]: features.append("Init")
                print(f"    ✅ Features: {', '.join(features)}")
        
        # Overall assessment
        overall_success_rate = (successful_imports / len(DEMO_MODULES)) * 100
        
        print(f"\n🎯 OVERALL ASSESSMENT:")
        if overall_success_rate >= 90:
            print(f"🎉 Excellent! {overall_success_rate:.1f}% of demos validated successfully")
            print("✅ Realistic demo suite is ready for execution")
        elif overall_success_rate >= 75:
            print(f"🟡 Good progress: {overall_success_rate:.1f}% of demos validated")
            print("⚠️ Some issues may need attention before full execution")
        else:
            print(f"🔴 Issues detected: Only {overall_success_rate:.1f}% of demos validated")
            print("❌ Significant fixes needed before demo execution")
        
        print(f"\n💡 NEXT STEPS:")
        if overall_success_rate >= 90:
            print("├─ Run individual demos for full testing")
            print("├─ Execute realistic_demo_runner.py for comprehensive suite")
            print("└─ Monitor demos with NoVNC viewer for real-time observation")
        else:
            failed_modules = [name for name, result in self.results.items() if not result["import_success"]]
            if failed_modules:
                print(f"├─ Fix import issues in: {', '.join(failed_modules[:3])}")
            print("├─ Address reported errors and missing components")
            print("└─ Re-run validation after fixes")
        
        print(f"\n{'='*80}")

async def main():
    """Main validation function."""
    try:
        validator = DemoValidationTest()
        results = await validator.run_all_validations()
        
        print(f"\n🎉 Realistic Demo Validation completed!")
        
        # Return success status for automation
        successful_imports = len([r for r in results.values() if r["import_success"]])
        success_rate = (successful_imports / len(DEMO_MODULES)) * 100
        
        return success_rate >= 75  # Consider 75%+ as acceptable
        
    except KeyboardInterrupt:
        print("\n👋 Validation interrupted by user")
        return False
    except Exception as e:
        logger.error(f"❌ Validation execution failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(main())
