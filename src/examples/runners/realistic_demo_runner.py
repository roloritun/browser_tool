#!/usr/bin/env python3
"""
Realistic Demo Runner

This script provides a comprehensive interface to run all realistic browser automation
demos. It demonstrates the full capabilities of the browser automation tool through
diverse, real-world scenarios that go far beyond basic Google searches.

Available demo suites:
- Two-Factor Authentication Demo
- E-commerce Workflow Demo  
- Form Automation Demo
- JavaScript SPA Demo
- Multi-Tab Workflow Demo
- Social Media Demo

Features:
- Interactive demo selection
- Parallel execution options
- Comprehensive reporting
- NoVNC monitoring integration
- Results aggregation and analysis
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import asyncio
import logging
import time
import json
import os
from datetime import datetime
from typing import Dict, List, Any

from tools.utilities.sandbox_manager import SandboxManager
from utils.novnc_viewer import generate_novnc_viewer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Available realistic demos
REALISTIC_DEMOS = {
    "2fa": {
        "name": "Two-Factor Authentication Demo",
        "module": "two_factor_auth_demo_fixed",
        "description": "Tests 2FA workflows, SMS verification, TOTP, WebAuthn, and hardware keys",
        "estimated_time": "15-20 minutes",
        "complexity": "high",
        "human_interaction": True
    },
    "ecommerce": {
        "name": "E-commerce Workflow Demo", 
        "module": "ecommerce_workflow_demo_fixed",
        "description": "Tests shopping workflows, cart management, checkout processes across multiple sites",
        "estimated_time": "10-15 minutes",
        "complexity": "medium",
        "human_interaction": False
    },
    "forms": {
        "name": "Form Automation Demo",
        "module": "form_automation_demo_fixed", 
        "description": "Tests complex form interactions, validation, input types, and form workflows",
        "estimated_time": "8-12 minutes",
        "complexity": "medium",
        "human_interaction": False
    },
    "spa": {
        "name": "JavaScript SPA Demo",
        "module": "javascript_spa_demo_fixed",
        "description": "Tests React, Vue, Angular applications with dynamic content and state management",
        "estimated_time": "12-18 minutes", 
        "complexity": "high",
        "human_interaction": True
    },
    "multitab": {
        "name": "Multi-Tab Workflow Demo",
        "module": "multi_tab_workflow_demo",
        "description": "Tests complex multi-tab coordination, research workflows, and tab management",
        "estimated_time": "15-25 minutes",
        "complexity": "high", 
        "human_interaction": False
    },
    "social": {
        "name": "Social Media Demo",
        "module": "social_media_demo",
        "description": "Tests ethical social platform exploration, content discovery, and navigation",
        "estimated_time": "10-15 minutes",
        "complexity": "medium",
        "human_interaction": False
    }
}

class RealisticDemoRunner:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "demos_executed": [],
            "total_execution_time": 0,
            "overall_success_rate": 0,
            "summary_metrics": {},
            "aggregated_insights": {},
            "recommendations": []
        }

    def display_demo_menu(self):
        """Display interactive demo selection menu."""
        print("\n" + "=" * 80)
        print("🚀 REALISTIC BROWSER AUTOMATION DEMO SUITE")
        print("=" * 80)
        print("Choose from comprehensive real-world automation scenarios:")
        print()
        
        for key, demo in REALISTIC_DEMOS.items():
            complexity_icon = {"low": "🟢", "medium": "🟡", "high": "🔴"}[demo["complexity"]]
            interaction_icon = "👤" if demo["human_interaction"] else "🤖"
            
            print(f"{key:>8}) {demo['name']}")
            print(f"          {demo['description']}")
            print(f"          {complexity_icon} {demo['complexity'].title()} | ⏱️ {demo['estimated_time']} | {interaction_icon}")
            print()
        
        print("   all) Run All Demos (Full Suite)")
        print(" quick) Quick Demo Selection (2FA + E-commerce + Forms)")
        print("  exit) Exit Demo Runner")
        print("\n" + "=" * 80)

    async def get_user_selection(self) -> List[str]:
        """Get user's demo selection."""
        while True:
            try:
                selection = input("\nEnter demo selection (comma-separated for multiple): ").strip().lower()
                
                if selection == "exit":
                    return []
                elif selection == "all":
                    return list(REALISTIC_DEMOS.keys())
                elif selection == "quick":
                    return ["2fa", "ecommerce", "forms"]
                else:
                    # Parse individual selections
                    selected = [s.strip() for s in selection.split(",")]
                    invalid = [s for s in selected if s not in REALISTIC_DEMOS]
                    
                    if invalid:
                        print(f"❌ Invalid selections: {', '.join(invalid)}")
                        print("Please choose from available demo keys.")
                        continue
                    
                    return selected
                    
            except KeyboardInterrupt:
                print("\n👋 Demo runner interrupted by user")
                return []
            except Exception as e:
                print(f"❌ Error processing selection: {e}")
                continue

    async def run_demo(self, demo_key: str) -> Dict[str, Any]:
        """Run a specific demo and return results."""
        demo_info = REALISTIC_DEMOS[demo_key]
        
        logger.info(f"\n🎬 Starting {demo_info['name']}")
        logger.info(f"📝 Description: {demo_info['description']}")
        logger.info(f"⏱️ Estimated Time: {demo_info['estimated_time']}")
        logger.info(f"🎯 Complexity: {demo_info['complexity'].title()}")
        
        if demo_info['human_interaction']:
            logger.info("👤 This demo may require human intervention - NoVNC viewer recommended")
        
        demo_result = {
            "demo_key": demo_key,
            "demo_name": demo_info["name"],
            "start_time": time.time(),
            "success": False,
            "execution_time": 0,
            "results": None,
            "error": None
        }
        
        try:
            # Import and run the demo module dynamically
            module_name = demo_info['module']
            module_path = f"examples.realistic.{module_name}"
            module = __import__(module_path, fromlist=["main"])
            
            # Run the demo
            results = await module.main()
            
            demo_result.update({
                "success": True,
                "results": results,
                "execution_time": time.time() - demo_result["start_time"]
            })
            
            logger.info(f"✅ {demo_info['name']} completed successfully")
            
        except Exception as e:
            demo_result.update({
                "success": False,
                "error": str(e),
                "execution_time": time.time() - demo_result["start_time"]
            })
            logger.error(f"❌ {demo_info['name']} failed: {e}")
        
        return demo_result

    async def run_selected_demos(self, selected_demos: List[str]):
        """Run all selected demos."""
        logger.info(f"\n🚀 Running {len(selected_demos)} selected demos")
        
        suite_start_time = time.time()
        
        for i, demo_key in enumerate(selected_demos, 1):
            logger.info(f"\n📋 Demo {i}/{len(selected_demos)}: {REALISTIC_DEMOS[demo_key]['name']}")
            
            # Run the demo
            demo_result = await self.run_demo(demo_key)
            self.results["demos_executed"].append(demo_result)
            
            # Brief pause between demos
            if i < len(selected_demos):
                logger.info("⏸️ Pausing 30 seconds between demos...")
                await asyncio.sleep(30)
        
        # Calculate suite metrics
        self.results["total_execution_time"] = time.time() - suite_start_time
        self._calculate_suite_metrics()
        
        logger.info("\n" + "=" * 80)
        logger.info("📊 DEMO SUITE EXECUTION COMPLETED")
        self._print_suite_summary()

    def _calculate_suite_metrics(self):
        """Calculate comprehensive suite metrics."""
        total_demos = len(self.results["demos_executed"])
        successful_demos = len([d for d in self.results["demos_executed"] if d["success"]])
        
        self.results["overall_success_rate"] = (successful_demos / total_demos * 100) if total_demos > 0 else 0
        
        self.results["summary_metrics"] = {
            "total_demos_attempted": total_demos,
            "successful_demos": successful_demos,
            "failed_demos": total_demos - successful_demos,
            "success_rate": self.results["overall_success_rate"],
            "total_execution_time": self.results["total_execution_time"],
            "average_demo_time": sum(d["execution_time"] for d in self.results["demos_executed"]) / total_demos if total_demos > 0 else 0,
            "complexity_distribution": self._get_complexity_distribution(),
            "interaction_requirements": self._get_interaction_requirements()
        }
        
        # Generate insights and recommendations
        self._generate_insights()

    def _get_complexity_distribution(self) -> Dict[str, int]:
        """Get distribution of demo complexities."""
        distribution = {"low": 0, "medium": 0, "high": 0}
        for demo_result in self.results["demos_executed"]:
            demo_key = demo_result["demo_key"]
            complexity = REALISTIC_DEMOS[demo_key]["complexity"]
            distribution[complexity] += 1
        return distribution

    def _get_interaction_requirements(self) -> Dict[str, int]:
        """Get distribution of interaction requirements."""
        requirements = {"automated": 0, "human_interaction": 0}
        for demo_result in self.results["demos_executed"]:
            demo_key = demo_result["demo_key"]
            if REALISTIC_DEMOS[demo_key]["human_interaction"]:
                requirements["human_interaction"] += 1
            else:
                requirements["automated"] += 1
        return requirements

    def _generate_insights(self):
        """Generate insights and recommendations based on results."""
        successful_demos = [d for d in self.results["demos_executed"] if d["success"]]
        failed_demos = [d for d in self.results["demos_executed"] if not d["success"]]
        
        self.results["aggregated_insights"] = {
            "automation_capabilities": self._analyze_capabilities(successful_demos),
            "challenge_patterns": self._analyze_challenges(failed_demos),
            "performance_characteristics": self._analyze_performance(),
            "feature_coverage": self._analyze_feature_coverage()
        }
        
        # Generate recommendations
        recommendations = []
        
        if self.results["overall_success_rate"] >= 80:
            recommendations.append("Excellent automation coverage - tool handles diverse scenarios well")
        elif self.results["overall_success_rate"] >= 60:
            recommendations.append("Good automation capability with room for improvement in complex scenarios")
        else:
            recommendations.append("Automation challenges identified - focus on error handling and edge cases")
        
        high_complexity_success = len([d for d in successful_demos if REALISTIC_DEMOS[d["demo_key"]]["complexity"] == "high"])
        if high_complexity_success > 0:
            recommendations.append("Successfully handles high-complexity workflows including 2FA and SPA interactions")
        
        human_interaction_success = len([d for d in successful_demos if REALISTIC_DEMOS[d["demo_key"]]["human_interaction"]])
        if human_interaction_success > 0:
            recommendations.append("Demonstrates effective human-in-the-loop automation capabilities")
        
        self.results["recommendations"] = recommendations

    def _analyze_capabilities(self, successful_demos: List[Dict]) -> List[str]:
        """Analyze demonstrated automation capabilities."""
        capabilities = []
        
        demo_types = set(REALISTIC_DEMOS[d["demo_key"]]["module"].split("_")[0] for d in successful_demos)
        
        if "two" in demo_types:
            capabilities.append("Multi-factor authentication handling")
        if "ecommerce" in demo_types:
            capabilities.append("E-commerce workflow automation")
        if "form" in demo_types:
            capabilities.append("Complex form interaction and validation")
        if "javascript" in demo_types:
            capabilities.append("Modern SPA and dynamic content handling")
        if "multi" in demo_types:
            capabilities.append("Multi-tab workflow coordination")
        if "social" in demo_types:
            capabilities.append("Social platform navigation and content discovery")
        
        return capabilities

    def _analyze_challenges(self, failed_demos: List[Dict]) -> List[str]:
        """Analyze common challenge patterns."""
        if not failed_demos:
            return ["No significant challenges encountered"]
        
        patterns = []
        
        # Analyze error patterns
        errors = [d.get("error", "") for d in failed_demos if d.get("error")]
        
        if any("timeout" in error.lower() for error in errors):
            patterns.append("Timeout-related challenges in complex interactions")
        if any("element" in error.lower() for error in errors):
            patterns.append("Element location challenges in dynamic content")
        if any("network" in error.lower() for error in errors):
            patterns.append("Network connectivity or site accessibility issues")
        
        return patterns or ["Unspecified technical challenges"]

    def _analyze_performance(self) -> Dict[str, Any]:
        """Analyze performance characteristics."""
        execution_times = [d["execution_time"] for d in self.results["demos_executed"] if d["success"]]
        
        if not execution_times:
            return {"status": "insufficient_data"}
        
        return {
            "average_execution_time": sum(execution_times) / len(execution_times),
            "fastest_demo": min(execution_times),
            "slowest_demo": max(execution_times),
            "total_suite_time": self.results["total_execution_time"],
            "performance_rating": "excellent" if sum(execution_times) / len(execution_times) < 600 else "good"
        }

    def _analyze_feature_coverage(self) -> Dict[str, bool]:
        """Analyze feature coverage across demos."""
        successful_demo_keys = [d["demo_key"] for d in self.results["demos_executed"] if d["success"]]
        
        return {
            "authentication_flows": "2fa" in successful_demo_keys,
            "ecommerce_workflows": "ecommerce" in successful_demo_keys,
            "form_automation": "forms" in successful_demo_keys,
            "spa_interactions": "spa" in successful_demo_keys,
            "multi_tab_coordination": "multitab" in successful_demo_keys,
            "social_content_discovery": "social" in successful_demo_keys
        }

    def _print_suite_summary(self):
        """Print comprehensive suite summary."""
        print("=" * 80)
        print("📊 COMPREHENSIVE DEMO SUITE SUMMARY")
        print("=" * 80)
        
        metrics = self.results["summary_metrics"]
        
        print(f"🎯 Overall Success Rate: {metrics['success_rate']:.1f}%")
        print(f"✅ Successful Demos: {metrics['successful_demos']}/{metrics['total_demos_attempted']}")
        print(f"⏱️ Total Execution Time: {metrics['total_execution_time']:.1f}s ({metrics['total_execution_time']/60:.1f} minutes)")
        print(f"📈 Average Demo Time: {metrics['average_demo_time']:.1f}s")
        
        print("\n📊 COMPLEXITY DISTRIBUTION:")
        for complexity, count in metrics['complexity_distribution'].items():
            print(f"├─ {complexity.title()}: {count} demos")
        
        print("\n🤖 INTERACTION REQUIREMENTS:")
        for req_type, count in metrics['interaction_requirements'].items():
            print(f"├─ {req_type.replace('_', ' ').title()}: {count} demos")
        
        print("\n📈 DEMO-BY-DEMO RESULTS:")
        for i, demo in enumerate(self.results["demos_executed"], 1):
            status = "✅" if demo["success"] else "❌"
            time_taken = demo["execution_time"]
            complexity = REALISTIC_DEMOS[demo["demo_key"]]["complexity"]
            print(f"{status} {i}. {demo['demo_name']} ({complexity}): {time_taken:.1f}s")
        
        if self.results["aggregated_insights"]["automation_capabilities"]:
            print("\n💡 AUTOMATION CAPABILITIES DEMONSTRATED:")
            for capability in self.results["aggregated_insights"]["automation_capabilities"]:
                print(f"├─ {capability}")
        
        if self.results["aggregated_insights"]["challenge_patterns"]:
            print("\n⚠️ CHALLENGE PATTERNS IDENTIFIED:")
            for pattern in self.results["aggregated_insights"]["challenge_patterns"]:
                print(f"├─ {pattern}")
        
        if self.results["recommendations"]:
            print("\n🎯 RECOMMENDATIONS:")
            for recommendation in self.results["recommendations"]:
                print(f"├─ {recommendation}")
        
        performance = self.results["aggregated_insights"]["performance_characteristics"]
        if performance.get("status") != "insufficient_data":
            print("\n⚡ PERFORMANCE ANALYSIS:")
            print(f"├─ Performance Rating: {performance['performance_rating'].title()}")
            print(f"├─ Average Demo Time: {performance['average_execution_time']:.1f}s")
            print(f"├─ Fastest Demo: {performance['fastest_demo']:.1f}s")
            print(f"└─ Slowest Demo: {performance['slowest_demo']:.1f}s")
        
        print("\n" + "=" * 80)

    async def save_results(self):
        """Save comprehensive results to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"realistic_demo_suite_results_{timestamp}.json"
        
        try:
            with open(results_file, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            
            logger.info(f"📄 Comprehensive results saved to: {results_file}")
            return results_file
            
        except Exception as e:
            logger.error(f"❌ Failed to save results: {e}")
            return None

async def main():
    """Main execution function."""
    try:
        # Create demo runner
        runner = RealisticDemoRunner()
        
        # Display welcome and demo information
        print("\n🎬 Welcome to Realistic Demo Suite")
        print("📝 Comprehensive browser automation testing suite featuring real-world scenarios")
        print("   including 2FA, e-commerce, forms, SPAs, multi-tab workflows, and social media.")
        
        # Create sandbox for monitoring
        sandbox_manager = SandboxManager()
        sandbox_id, cdp_url, vnc_url, novnc_url, api_url, web_url, x_url = sandbox_manager.create_sandbox()
        
        # Start NoVNC viewer for monitoring
        try:
            viewer_path = generate_novnc_viewer(
                novnc_url=novnc_url,
                vnc_password=os.getenv('VNC_PASSWORD', 'vncpassword'),
                auto_open=True
            )
            if viewer_path:
                print(f"\n🖥️ NoVNC Viewer Available: {novnc_url}")
                print("👀 Monitor browser automation in real-time!")
        except Exception as e:
            print(f"⚠️ Could not start NoVNC viewer: {e}")
            print("💡 Demo will continue without viewer")
        
        # Display menu and get selection
        runner.display_demo_menu()
        selected_demos = await runner.get_user_selection()
        
        if not selected_demos:
            print("👋 No demos selected. Exiting...")
            return
        
        print(f"\n🎯 Selected Demos: {', '.join(selected_demos)}")
        
        # Confirm execution
        total_time = sum(
            int(REALISTIC_DEMOS[demo]["estimated_time"].split("-")[1].split()[0]) 
            for demo in selected_demos
        )
        
        print(f"⏱️ Estimated Total Time: ~{total_time} minutes")
        
        confirmation = input("\nProceed with demo execution? (y/N): ").strip().lower()
        if confirmation != 'y':
            print("👋 Demo execution cancelled.")
            return
        
        # Run selected demos
        await runner.run_selected_demos(selected_demos)
        
        # Save results
        results_file = await runner.save_results()
        
        print("\n🎉 Demo suite execution completed!")
        if results_file:
            print(f"📄 Detailed results available in: {results_file}")
        
        return runner.results
        
    except KeyboardInterrupt:
        print("\n👋 Demo suite interrupted by user")
    except Exception as e:
        logger.error(f"❌ Demo suite execution failed: {e}")
        raise
    finally:
        # Cleanup
        try:
            sandbox_manager = SandboxManager()
            await sandbox_manager.cleanup()
        except Exception as e:
            logger.error(f"⚠️ Cleanup error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
