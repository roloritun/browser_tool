#!/usr/bin/env python3
"""
Sequential Demo Runner with Error Monitoring
===========================================

This script runs all browser automation demos one after another and monitors for errors.
It provides comprehensive logging, error tracking, and detailed reporting.
"""

import asyncio
import subprocess
import sys
import time
import json
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class DemoResult:
    """Result of running a single demo"""
    name: str
    path: str
    start_time: float
    end_time: Optional[float] = None
    exit_code: Optional[int] = None
    success: bool = False
    error_message: Optional[str] = None
    stdout: str = ""
    stderr: str = ""
    duration: float = 0.0

@dataclass 
class DemoRunner:
    """Manages sequential execution of all demos with error monitoring"""
    
    results: List[DemoResult] = field(default_factory=list)
    total_start_time: float = 0.0
    total_end_time: float = 0.0
    
    def __post_init__(self):
        self.total_start_time = time.time()
    
    async def run_demo(self, demo_name: str, demo_path: str, timeout: int = 600) -> DemoResult:
        """Run a single demo and capture results"""
        logger.info(f"🎬 Starting demo: {demo_name}")
        logger.info(f"📁 Path: {demo_path}")
        
        result = DemoResult(
            name=demo_name,
            path=demo_path,
            start_time=time.time()
        )
        
        try:
            # Run the demo
            process = await asyncio.create_subprocess_exec(
                sys.executable, demo_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=Path(demo_path).parent
            )
            
            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=timeout
                )
                
                result.stdout = stdout.decode('utf-8', errors='ignore')
                result.stderr = stderr.decode('utf-8', errors='ignore')
                result.exit_code = process.returncode
                result.success = process.returncode == 0
                
            except asyncio.TimeoutError:
                logger.warning(f"⏰ Demo {demo_name} timed out after {timeout} seconds")
                process.kill()
                result.error_message = f"Timeout after {timeout} seconds"
                result.exit_code = -1
                result.success = False
                
        except Exception as e:
            logger.error(f"❌ Failed to run demo {demo_name}: {str(e)}")
            result.error_message = str(e)
            result.exit_code = -2
            result.success = False
        
        result.end_time = time.time()
        result.duration = result.end_time - result.start_time
        
        # Log result
        if result.success:
            logger.info(f"✅ Demo {demo_name} completed successfully in {result.duration:.1f}s")
        else:
            logger.error(f"❌ Demo {demo_name} failed with exit code {result.exit_code}")
            if result.error_message:
                logger.error(f"   Error: {result.error_message}")
            if result.stderr:
                logger.error(f"   Stderr: {result.stderr[:500]}...")
        
        return result
    
    async def run_all_demos(self) -> Dict[str, Any]:
        """Run all demos sequentially"""
        logger.info("🚀 Starting Sequential Demo Execution")
        logger.info("="*80)
        
        # Define all available demos
        demos = [
            ("Essential Toolkit Demo", "src/examples/consolidated/essential_toolkit_demo.py"),
            ("Business Automation Demo", "src/examples/consolidated/business_automation_demo.py"),
            ("Modern Web Demo", "src/examples/consolidated/modern_web_demo.py"),
            ("Social Content Demo", "src/examples/consolidated/social_content_demo.py"),
            ("Advanced Interaction Demo", "src/examples/consolidated/advanced_interaction_demo.py"),
            ("Intervention Mastery Demo", "src/examples/consolidated/intervention_mastery_demo.py"),
            ("Production System Demo", "src/examples/consolidated/production_system_demo.py"),
            ("Live Testing Demo", "src/examples/consolidated/live_testing_demo.py"),
        ]
        
        # Additional standalone demos
        standalone_demos = [
            ("Optimized Agent Demo", "optimized_agent_demo.py"),
            ("Fixed Agent Demo", "fixed_agent_demo.py"),
            ("Comprehensive Fix Demo", "comprehensive_fix_demo.py"),
        ]
        
        # Check which demos actually exist
        available_demos = []
        for name, path in demos + standalone_demos:
            full_path = Path(path)
            if full_path.exists():
                available_demos.append((name, str(full_path.absolute())))
            else:
                logger.warning(f"⚠️ Demo not found: {path}")
        
        logger.info(f"📊 Found {len(available_demos)} available demos")
        
        # Run each demo
        for i, (demo_name, demo_path) in enumerate(available_demos, 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"Demo {i}/{len(available_demos)}: {demo_name}")
            logger.info(f"{'='*60}")
            
            result = await self.run_demo(demo_name, demo_path)
            self.results.append(result)
            
            # Brief pause between demos
            if i < len(available_demos):
                logger.info("⏸️ Pausing 10 seconds before next demo...")
                await asyncio.sleep(10)
        
        self.total_end_time = time.time()
        
        # Generate comprehensive report
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive execution report"""
        total_duration = self.total_end_time - self.total_start_time
        successful_demos = [r for r in self.results if r.success]
        failed_demos = [r for r in self.results if not r.success]
        
        report = {
            "execution_summary": {
                "total_demos": len(self.results),
                "successful": len(successful_demos),
                "failed": len(failed_demos),
                "success_rate": len(successful_demos) / len(self.results) * 100 if self.results else 0,
                "total_duration": total_duration,
                "start_time": datetime.fromtimestamp(self.total_start_time).isoformat(),
                "end_time": datetime.fromtimestamp(self.total_end_time).isoformat()
            },
            "demo_results": []
        }
        
        # Add individual demo results
        for result in self.results:
            demo_report = {
                "name": result.name,
                "path": result.path,
                "success": result.success,
                "duration": result.duration,
                "exit_code": result.exit_code,
                "start_time": datetime.fromtimestamp(result.start_time).isoformat(),
            }
            
            if result.end_time:
                demo_report["end_time"] = datetime.fromtimestamp(result.end_time).isoformat()
            
            if result.error_message:
                demo_report["error"] = result.error_message
            
            if result.stderr:
                demo_report["stderr_excerpt"] = result.stderr[:1000]
            
            report["demo_results"].append(demo_report)
        
        return report
    
    def print_summary(self, report: Dict[str, Any]):
        """Print execution summary"""
        print("\n" + "="*80)
        print("🏁 DEMO EXECUTION SUMMARY")
        print("="*80)
        
        summary = report["execution_summary"]
        print(f"📊 Total Demos: {summary['total_demos']}")
        print(f"✅ Successful: {summary['successful']}")
        print(f"❌ Failed: {summary['failed']}")
        print(f"📈 Success Rate: {summary['success_rate']:.1f}%")
        print(f"⏱️ Total Duration: {summary['total_duration']:.1f} seconds")
        
        print(f"\n🎯 INDIVIDUAL DEMO RESULTS:")
        print("-" * 80)
        
        for demo in report["demo_results"]:
            status = "✅" if demo["success"] else "❌"
            print(f"{status} {demo['name']:<40} {demo['duration']:>6.1f}s  Exit: {demo.get('exit_code', 'N/A')}")
            
            if not demo["success"] and demo.get("error"):
                print(f"   💡 Error: {demo['error']}")
        
        print("\n" + "="*80)
        
        if summary["failed"] > 0:
            print("🔍 FAILED DEMOS ANALYSIS:")
            print("-" * 40)
            
            failed_demos = [d for d in report["demo_results"] if not d["success"]]
            for demo in failed_demos:
                print(f"\n❌ {demo['name']}:")
                print(f"   📁 Path: {demo['path']}")
                print(f"   🔢 Exit Code: {demo.get('exit_code', 'Unknown')}")
                if demo.get("error"):
                    print(f"   ⚠️ Error: {demo['error']}")
                if demo.get("stderr_excerpt"):
                    print(f"   📝 Stderr: {demo['stderr_excerpt'][:200]}...")
        
        print("="*80)

async def main():
    """Main execution function"""
    logger.info("🎪 Sequential Demo Runner Starting")
    
    runner = DemoRunner()
    
    try:
        report = await runner.run_all_demos()
        
        # Print summary
        runner.print_summary(report)
        
        # Save detailed report
        report_file = f"demo_execution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Detailed report saved to: {report_file}")
        
        # Return appropriate exit code
        if report["execution_summary"]["failed"] == 0:
            logger.info("🎉 All demos completed successfully!")
            return 0
        else:
            logger.warning(f"⚠️ {report['execution_summary']['failed']} demos failed")
            return 1
            
    except KeyboardInterrupt:
        logger.info("🛑 Demo execution interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"❌ Demo runner failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
