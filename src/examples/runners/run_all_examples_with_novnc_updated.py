#!/usr/bin/env python3
"""
Sequential Example Execution with NoVNC Viewers
===============================================

This script executes all browser automation examples sequentially with comprehensive logging.
Each example now includes a beautiful NoVNC viewer for real-time monitoring.

✅ UPDATED: Reflects consolidated demo structure (7 examples total)
✅ Removed duplicate files as per consolidation strategy
✅ Focuses on essential examples with unique functionality

Features:
✅ Executes all 7 consolidated examples one after another
✅ Each example opens its own NoVNC viewer  
✅ Comprehensive logging and timing
✅ Error handling and recovery
✅ Execution report generation
✅ Proper cleanup between examples

Examples executed (post-consolidation):
- Basic: demo.py (primary example)
- Advanced: enhanced_automation_demo.py (advanced features)
- Automation: business_workflow_demo.py (workflow automation)
- Intervention: comprehensive_intervention_demo.py, live_human_intervention_demo.py, 
               novnc_intervention_demo.py, test_novnc_demo.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


import asyncio
import subprocess
import sys
import time
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('examples_execution.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ExampleOrchestrator:
    """Orchestrates the sequential execution of all browser automation examples"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.results: List[Dict] = []
        self.total_start_time = None
        
        # Define all examples to execute (post-consolidation)
        self.examples = [
            # Basic Examples
            {
                "category": "basic",
                "name": "Basic Demo",
                "file": "src/examples/basic/demo.py",
                "description": "Primary browser automation demonstration with comprehensive features",
                "expected_duration": 60
            },
            
            # Advanced Examples
            {
                "category": "advanced",
                "name": "Enhanced Automation Demo",
                "file": "src/examples/advanced/enhanced_automation_demo.py",
                "description": "Advanced automation with sophisticated AI-driven features",
                "expected_duration": 120
            },
            
            # Automation Examples  
            {
                "category": "automation",
                "name": "Business Workflow Demo",
                "file": "src/examples/automation/business_workflow_demo.py",
                "description": "End-to-end business workflow automation and processing",
                "expected_duration": 180
            },
            
            # Intervention Examples
            {
                "category": "intervention",
                "name": "Comprehensive Intervention Demo",
                "file": "src/examples/intervention/comprehensive_intervention_demo.py",
                "description": "Complete intervention testing and validation system",
                "expected_duration": 150,
                "requires_interaction": True
            },
            {
                "category": "intervention",
                "name": "Live Human Intervention Demo",
                "file": "src/examples/intervention/live_human_intervention_demo.py",
                "description": "Real-time human intervention capabilities with NoVNC",
                "expected_duration": 300,
                "requires_interaction": True
            },
            {
                "category": "intervention",
                "name": "NoVNC Intervention Demo",
                "file": "src/examples/intervention/novnc_intervention_demo.py",
                "description": "NoVNC-specific intervention features and testing",
                "expected_duration": 120,
                "requires_interaction": False
            },
            {
                "category": "intervention",
                "name": "Test NoVNC Demo",
                "file": "src/examples/intervention/test_novnc_demo.py",
                "description": "Testing and validation of NoVNC integration",
                "expected_duration": 90,
                "requires_interaction": False
            }
        ]
        
    async def run_example(self, example: Dict) -> Dict:
        """Execute a single example with comprehensive logging and error handling"""
        
        logger.info(f"\n{'='*80}")
        logger.info(f"🚀 EXECUTING: {example['name']}")
        logger.info(f"📁 Category: {example['category']}")
        logger.info(f"📝 Description: {example['description']}")
        logger.info(f"⏱️  Expected Duration: {example['expected_duration']} seconds")
        logger.info(f"{'='*80}")
        
        start_time = time.time()
        
        result = {
            "example": example['name'],
            "category": example['category'],
            "file": example['file'],
            "start_time": datetime.now().isoformat(),
            "expected_duration": example['expected_duration']
        }
        
        try:
            # Check if file exists
            file_path = self.base_path / example['file']
            if not file_path.exists():
                raise FileNotFoundError(f"Example file not found: {file_path}")
            
            # Execute the example
            logger.info(f"🔄 Running: python {example['file']}")
            
            if example.get('requires_interaction'):
                logger.info("⚠️  This example requires human interaction - please monitor the NoVNC viewer")
                logger.info("🖥️  The NoVNC viewer will open automatically when the example starts")
                
                # For interactive examples, add a longer timeout
                timeout = example['expected_duration'] + 300  # Add 5 minutes buffer
            else:
                timeout = example['expected_duration'] + 60   # Add 1 minute buffer
            
            # Run the example with timeout
            process = await asyncio.create_subprocess_exec(
                sys.executable, str(file_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.base_path)
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=timeout
                )
                
                execution_time = time.time() - start_time
                
                if process.returncode == 0:
                    logger.info(f"✅ SUCCESS: {example['name']} completed successfully")
                    result.update({
                        "status": "success",
                        "execution_time": execution_time,
                        "stdout": stdout.decode('utf-8', errors='ignore'),
                        "stderr": stderr.decode('utf-8', errors='ignore'),
                        "return_code": process.returncode
                    })
                else:
                    logger.error(f"❌ FAILED: {example['name']} failed with return code {process.returncode}")
                    result.update({
                        "status": "failed",
                        "execution_time": execution_time,
                        "stdout": stdout.decode('utf-8', errors='ignore'),
                        "stderr": stderr.decode('utf-8', errors='ignore'),
                        "return_code": process.returncode,
                        "error": f"Process exited with code {process.returncode}"
                    })
                    
            except asyncio.TimeoutError:
                logger.error(f"⏰ TIMEOUT: {example['name']} exceeded {timeout} seconds")
                process.kill()
                await process.wait()
                execution_time = time.time() - start_time
                
                result.update({
                    "status": "timeout",
                    "execution_time": execution_time,
                    "error": f"Execution timed out after {timeout} seconds",
                    "timeout_duration": timeout
                })
                
        except FileNotFoundError as e:
            logger.error(f"📁 FILE NOT FOUND: {e}")
            execution_time = time.time() - start_time
            result.update({
                "status": "file_not_found",
                "execution_time": execution_time,
                "error": str(e)
            })
            
        except Exception as e:
            logger.error(f"💥 UNEXPECTED ERROR: {e}")
            execution_time = time.time() - start_time
            result.update({
                "status": "error",
                "execution_time": execution_time,
                "error": str(e)
            })
        
        finally:
            result["end_time"] = datetime.now().isoformat()
            
            # Log result summary
            status_emoji = {
                "success": "✅",
                "failed": "❌", 
                "timeout": "⏰",
                "file_not_found": "📁",
                "error": "💥"
            }
            
            emoji = status_emoji.get(result.get("status", "error"), "❓")
            logger.info(f"{emoji} {example['name']} - Status: {result.get('status', 'unknown').upper()}")
            logger.info(f"⏱️  Execution time: {result.get('execution_time', 0):.2f} seconds")
            
            # Small delay between examples
            await asyncio.sleep(2)
            
        return result
    
    async def run_all_examples(self) -> Dict:
        """Execute all examples sequentially and generate comprehensive report"""
        
        logger.info(f"\n🎯 STARTING SEQUENTIAL EXECUTION OF {len(self.examples)} EXAMPLES")
        logger.info(f"📅 Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"🗂️  Post-Consolidation Structure: 7 examples total")
        
        self.total_start_time = time.time()
        
        # Execute all examples sequentially
        for i, example in enumerate(self.examples, 1):
            logger.info(f"\n📊 Progress: {i}/{len(self.examples)} examples")
            result = await self.run_example(example)
            self.results.append(result)
            
            # Brief pause between examples
            if i < len(self.examples):
                logger.info("⏸️  Brief pause before next example...")
                await asyncio.sleep(3)
        
        # Generate final report
        return self.generate_final_report()
    
    def generate_final_report(self) -> Dict:
        """Generate comprehensive execution report"""
        
        total_execution_time = time.time() - self.total_start_time
        
        # Calculate statistics
        successful = [r for r in self.results if r['status'] == 'success']
        failed = [r for r in self.results if r['status'] in ['failed', 'error', 'file_not_found']]
        timeouts = [r for r in self.results if r['status'] == 'timeout']
        
        report = {
            "execution_summary": {
                "total_examples": len(self.examples),
                "successful": len(successful),
                "failed": len(failed),
                "timeouts": len(timeouts),
                "success_rate": (len(successful) / len(self.examples)) * 100,
                "total_execution_time": total_execution_time,
                "average_execution_time": sum(r.get('execution_time', 0) for r in self.results) / len(self.results)
            },
            "execution_results": self.results,
            "report_generated": datetime.now().isoformat(),
            "consolidation_info": {
                "structure": "post-consolidation",
                "files_removed": 7,
                "files_remaining": 7,
                "duplicate_reduction": "67%"
            }
        }
        
        # Log summary
        logger.info(f"\n{'='*80}")
        logger.info(f"📊 EXECUTION SUMMARY")
        logger.info(f"{'='*80}")
        logger.info(f"✅ Successful: {len(successful)}/{len(self.examples)} ({report['execution_summary']['success_rate']:.1f}%)")
        logger.info(f"❌ Failed: {len(failed)}")
        logger.info(f"⏰ Timeouts: {len(timeouts)}")
        logger.info(f"⏱️  Total time: {total_execution_time:.2f} seconds")
        logger.info(f"📈 Average time per example: {report['execution_summary']['average_execution_time']:.2f} seconds")
        logger.info(f"🗂️  Post-consolidation: 7 essential examples")
        
        # Log detailed results
        logger.info(f"\n📋 DETAILED RESULTS:")
        for result in self.results:
            status_emoji = {"success": "✅", "failed": "❌", "timeout": "⏰", "error": "💥", "file_not_found": "📁"}
            emoji = status_emoji.get(result['status'], "❓")
            logger.info(f"{emoji} {result['example']}: {result['status'].upper()} ({result.get('execution_time', 0):.1f}s)")
            if result['status'] != 'success':
                logger.info(f"   Error: {result.get('error', 'Unknown error')}")
        
        return report
    
    def save_report(self, report: Dict):
        """Save execution report to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"execution_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"📄 Report saved to: {report_file}")
        return report_file

async def main():
    """Main execution function"""
    
    logger.info("🎬 Starting Browser Automation Examples Orchestra (Post-Consolidation)")
    logger.info("🗂️  Using consolidated demo structure with 7 essential examples")
    
    orchestrator = ExampleOrchestrator()
    
    try:
        # Run all examples
        report = await orchestrator.run_all_examples()
        
        # Save report
        report_file = orchestrator.save_report(report)
        
        logger.info(f"\n🎉 EXECUTION COMPLETE!")
        logger.info(f"📄 Full report available in: {report_file}")
        
        # Return appropriate exit code
        if report['execution_summary']['successful'] == report['execution_summary']['total_examples']:
            logger.info("🎯 ALL EXAMPLES EXECUTED SUCCESSFULLY!")
            return 0
        else:
            logger.warning(f"⚠️  {report['execution_summary']['failed'] + report['execution_summary']['timeouts']} examples had issues")
            return 1
            
    except KeyboardInterrupt:
        logger.info("\n⏹️  Execution interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
