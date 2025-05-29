#!/usr/bin/env python3
"""
COMPREHENSIVE DEMO VALIDATION SCRIPT
===================================

This script validates all demos across the entire project to identify
import issues, missing dependencies, and structural problems.
"""

import sys
import os
import importlib
import time
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from utils.logger import logger

class DemoValidator:
    """Comprehensive demo validation system"""
    
    def __init__(self):
        self.results = {}
        self.total_demos = 0
        self.successful_demos = 0
        self.failed_demos = 0
        
    def find_all_demo_files(self) -> Dict[str, List[str]]:
        """Find all demo files organized by category"""
        base_path = Path(__file__).parent / "examples"
        demo_files = {
            "basic": [],
            "advanced": [],
            "automation": [],
            "intervention": [],
            "realistic": []
        }
        
        for category in demo_files.keys():
            category_path = base_path / category
            if category_path.exists():
                for file_path in category_path.glob("*.py"):
                    if file_path.name != "__init__.py":
                        demo_files[category].append(str(file_path))
        
        return demo_files
    
    def validate_demo(self, demo_path: str) -> Dict[str, Any]:
        """Validate a single demo file"""
        demo_name = Path(demo_path).stem
        result = {
            "demo_name": demo_name,
            "demo_path": demo_path,
            "import_success": False,
            "main_function": False,
            "demo_class": False,
            "errors": [],
            "warnings": []
        }
        
        try:
            # Convert file path to module path
            rel_path = Path(demo_path).relative_to(Path(__file__).parent)
            module_path = str(rel_path.with_suffix('')).replace(os.sep, '.')
            
            logger.info(f"🔍 Testing {demo_name}")
            
            # Try to import the module
            spec = importlib.util.spec_from_file_location(module_path, demo_path)
            if spec is None or spec.loader is None:
                result["errors"].append("Cannot create module spec")
                return result
                
            module = importlib.util.module_from_spec(spec)
            
            # Execute the module import
            spec.loader.exec_module(module)
            result["import_success"] = True
            logger.info(f"   ✅ Import successful")
            
            # Check for main function
            if hasattr(module, 'main'):
                result["main_function"] = True
                logger.info(f"   ✅ Main function found")
            else:
                result["warnings"].append("No main function found")
                logger.info(f"   ⚠️ No main function found")
            
            # Check for demo classes (look for classes ending in Demo)
            demo_classes = [name for name in dir(module) 
                          if name.endswith('Demo') and isinstance(getattr(module, name), type)]
            
            if demo_classes:
                result["demo_class"] = True
                result["demo_classes"] = demo_classes
                logger.info(f"   ✅ Demo class(es) found: {', '.join(demo_classes)}")
            else:
                result["warnings"].append("No demo class found")
                logger.info(f"   ⚠️ No demo class found")
            
            # Additional validation checks
            if hasattr(module, '__name__') and hasattr(module, '__file__'):
                result["module_structure"] = True
            
            logger.info(f"   ✅ {demo_name}: Validation completed successfully")
            
        except ImportError as e:
            error_msg = f"Import error: {str(e)}"
            result["errors"].append(error_msg)
            logger.error(f"   ❌ {demo_name}: {error_msg}")
            
        except SyntaxError as e:
            error_msg = f"Syntax error: {str(e)}"
            result["errors"].append(error_msg)
            logger.error(f"   ❌ {demo_name}: {error_msg}")
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            result["errors"].append(error_msg)
            logger.error(f"   ❌ {demo_name}: {error_msg}")
            logger.debug(f"   Stack trace: {traceback.format_exc()}")
        
        return result
    
    def validate_all_demos(self) -> Dict[str, Any]:
        """Validate all demos and generate comprehensive report"""
        logger.info("🚀 Starting Comprehensive Demo Validation")
        logger.info("=" * 80)
        
        demo_files = self.find_all_demo_files()
        
        # Count total demos
        for category, files in demo_files.items():
            self.total_demos += len(files)
        
        logger.info(f"📋 Found {self.total_demos} demo files across {len(demo_files)} categories")
        logger.info("")
        
        all_results = {}
        
        for category, files in demo_files.items():
            if not files:
                continue
                
            logger.info(f"📁 CATEGORY: {category.upper()}")
            logger.info("-" * 50)
            
            category_results = []
            category_success = 0
            
            for demo_file in files:
                result = self.validate_demo(demo_file)
                category_results.append(result)
                
                if result["import_success"] and not result["errors"]:
                    category_success += 1
                    self.successful_demos += 1
                else:
                    self.failed_demos += 1
                
                time.sleep(0.2)  # Brief pause between tests
            
            all_results[category] = {
                "results": category_results,
                "total": len(files),
                "successful": category_success,
                "failed": len(files) - category_success
            }
            
            logger.info(f"   📊 Category Summary: {category_success}/{len(files)} successful")
            logger.info("")
        
        # Generate comprehensive report
        return self.generate_final_report(all_results)
    
    def generate_final_report(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final validation report"""
        logger.info("=" * 80)
        logger.info("📊 COMPREHENSIVE DEMO VALIDATION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"⏱️ Total Validation Time: {time.time():.1f}s")
        logger.info(f"📋 Total Demos Tested: {self.total_demos}")
        logger.info("")
        
        logger.info("📈 OVERALL RESULTS:")
        logger.info(f"✅ Successful Demos: {self.successful_demos}/{self.total_demos}")
        logger.info(f"❌ Failed Demos: {self.failed_demos}/{self.total_demos}")
        success_rate = (self.successful_demos / self.total_demos * 100) if self.total_demos > 0 else 0
        logger.info(f"📊 Success Rate: {success_rate:.1f}%")
        logger.info("")
        
        logger.info("📋 CATEGORY BREAKDOWN:")
        for category, data in all_results.items():
            category_rate = (data["successful"] / data["total"] * 100) if data["total"] > 0 else 0
            status = "✅" if category_rate == 100 else "⚠️" if category_rate >= 50 else "❌"
            logger.info(f"   {status} {category.upper()}: {data['successful']}/{data['total']} ({category_rate:.1f}%)")
        
        logger.info("")
        
        # Detailed failure analysis
        logger.info("🔍 DETAILED FAILURE ANALYSIS:")
        logger.info("-" * 50)
        
        common_errors = {}
        failed_demos = []
        
        for category, data in all_results.items():
            for result in data["results"]:
                if result["errors"]:
                    failed_demos.append(f"{category}/{result['demo_name']}")
                    for error in result["errors"]:
                        # Categorize common errors
                        if "Import error" in error:
                            if "browser_tools" in error:
                                common_errors.setdefault("Missing browser_tools import", []).append(result["demo_name"])
                            elif "sys.path" in error or "ModuleNotFoundError" in error:
                                common_errors.setdefault("Path/Module issues", []).append(result["demo_name"])
                            else:
                                common_errors.setdefault("Other import errors", []).append(result["demo_name"])
                        elif "Syntax error" in error:
                            common_errors.setdefault("Syntax errors", []).append(result["demo_name"])
                        else:
                            common_errors.setdefault("Other errors", []).append(result["demo_name"])
        
        for error_type, demos in common_errors.items():
            logger.info(f"   {error_type}: {len(demos)} demos")
            for demo in demos[:3]:  # Show first 3 examples
                logger.info(f"      • {demo}")
            if len(demos) > 3:
                logger.info(f"      ... and {len(demos) - 3} more")
            logger.info("")
        
        # Success stories
        logger.info("🎉 SUCCESSFUL DEMOS:")
        logger.info("-" * 30)
        
        for category, data in all_results.items():
            successful_in_category = [r["demo_name"] for r in data["results"] 
                                    if r["import_success"] and not r["errors"]]
            if successful_in_category:
                logger.info(f"   {category.upper()}:")
                for demo in successful_in_category:
                    logger.info(f"      ✅ {demo}")
                logger.info("")
        
        # Recommendations
        logger.info("💡 RECOMMENDATIONS:")
        logger.info("-" * 20)
        
        if self.failed_demos > 0:
            logger.info("📌 Priority fixes needed:")
            logger.info("   1. Fix sys.path setup in demo files")
            logger.info("   2. Ensure proper browser_tools imports")
            logger.info("   3. Add missing main() functions where needed")
            logger.info("   4. Standardize demo class naming conventions")
            logger.info("")
        
        if success_rate >= 80:
            logger.info("🎯 OVERALL ASSESSMENT:")
            logger.info("🎉 Excellent! Most demos are working correctly")
            logger.info("✅ Project is in good health with minor fixes needed")
        elif success_rate >= 60:
            logger.info("🎯 OVERALL ASSESSMENT:")
            logger.info("⚠️ Good progress with some work remaining")
            logger.info("🔧 Focus on fixing common import and structure issues")
        else:
            logger.info("🎯 OVERALL ASSESSMENT:")
            logger.info("❌ Significant work needed to restore demo functionality")
            logger.info("🚨 Priority: Fix core import and structure issues")
        
        logger.info("")
        logger.info("=" * 80)
        
        return {
            "total_demos": self.total_demos,
            "successful_demos": self.successful_demos,
            "failed_demos": self.failed_demos,
            "success_rate": success_rate,
            "category_results": all_results,
            "common_errors": common_errors,
            "failed_demos_list": failed_demos
        }

def main():
    """Main validation execution"""
    try:
        validator = DemoValidator()
        results = validator.validate_all_demos()
        
        logger.info("🎉 Comprehensive Demo Validation completed!")
        
        # Return exit code based on success rate
        if results["success_rate"] >= 80:
            return 0  # Success
        elif results["success_rate"] >= 50:
            return 1  # Warning
        else:
            return 2  # Critical issues
            
    except KeyboardInterrupt:
        logger.info("\n🛑 Validation stopped by user")
        return 3
    except Exception as e:
        logger.error(f"\n❌ Fatal validation error: {e}")
        return 4

if __name__ == "__main__":
    sys.exit(main())
