#!/usr/bin/env python3
"""
JavaScript SPA (Single Page Application) Demo

This demo tests the browser automation tool's capabilities with modern JavaScript
Single Page Applications including React, Vue.js, Angular, and vanilla JS applications.

Key testing areas:
- Dynamic content loading and state management
- Client-side routing and navigation
- Modern framework component interactions
- API integration and real-time updates
- Performance characteristics and optimization detection

Safety: Uses only demo sites and test interactions.
Ethics: Respects application performance and API rate limits.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, List, Any

from langchain_openai import ChatOpenAI

from tools.utilities.browser_tools_init import initialize_browser_tools
from tools.utilities.sandbox_manager import SandboxManager
from utils.enhanced_agent_formatting import create_enhanced_react_agent
from utils.novnc_viewer import generate_novnc_viewer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# JavaScript SPA Test Sites and Scenarios
SPA_TEST_SITES = [
    {
        "name": "React TodoMVC",
        "url": "https://todomvc.com/examples/react/build/",
        "framework": "React",
        "features": ["component_state", "virtual_dom", "hooks"],
        "test_type": "todo_app"
    },
    {
        "name": "Vue.js TodoMVC", 
        "url": "https://todomvc.com/examples/vue/",
        "framework": "Vue.js",
        "features": ["reactive_data", "directives", "computed_properties"],
        "test_type": "todo_app"
    },
    {
        "name": "Angular TodoMVC",
        "url": "https://todomvc.com/examples/angular/",
        "framework": "Angular",
        "features": ["typescript", "dependency_injection", "services"],
        "test_type": "todo_app"
    },
    {
        "name": "Vanilla JS TodoMVC",
        "url": "https://todomvc.com/examples/vanilla-es6/",
        "framework": "Vanilla JavaScript",
        "features": ["es6_modules", "custom_elements", "native_apis"],
        "test_type": "todo_app"
    }
]

class JavaScriptSPADemo:
    def __init__(self):
        self.sandbox_manager = None
        self.tools = None
        self.agent_executor = None
        self.llm = None
        
    async def initialize(self):
        """Initialize the demo environment."""
        try:
            # Initialize sandbox and tools
            self.sandbox_manager = SandboxManager()
            await self.sandbox_manager.initialize()
            
            # Initialize browser tools
            self.tools = await initialize_browser_tools()
            
            # Initialize LLM
            self.llm = ChatOpenAI(
                model="gpt-4", 
                temperature=0.1,
                timeout=60.0
            )
            
            # Create agent
            self.agent_executor = create_enhanced_react_agent(
                llm=self.llm,
                tools=self.tools,
                max_iterations=20,
                max_execution_time=900,
                return_intermediate_steps=True
            )
            
            logger.info("✅ JavaScript SPA Demo initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize JavaScript SPA Demo: {e}")
            return False

    async def test_spa_framework(self, site_info: Dict[str, Any]) -> Dict[str, Any]:
        """Test a specific SPA framework."""
        logger.info(f"\n🔍 Testing {site_info['name']} ({site_info['framework']})")
        
        result = {
            "site_name": site_info["name"],
            "framework": site_info["framework"],
            "url": site_info["url"],
            "features_tested": site_info["features"],
            "test_results": {},
            "success": False,
            "error": None,
            "performance_metrics": {},
            "framework_detection": {},
            "interaction_results": []
        }
        
        try:
            # Create comprehensive SPA testing task
            task = f"""
Test the Single Page Application at {site_info['url']} which uses {site_info['framework']}.

Perform these comprehensive tests:

1. FRAMEWORK DETECTION AND ANALYSIS:
   - Navigate to the site and analyze the page structure
   - Detect framework-specific patterns and characteristics
   - Identify key features: {', '.join(site_info['features'])}
   - Look for framework-specific elements and patterns

2. DYNAMIC CONTENT TESTING (if Todo app):
   - Add multiple todo items with different text
   - Toggle todo completion status
   - Filter todos (All, Active, Completed)
   - Clear completed todos
   - Test bulk operations

3. CLIENT-SIDE ROUTING:
   - Test navigation between different views/routes
   - Verify URL changes and browser history
   - Check if page refreshes maintain state

4. COMPONENT INTERACTION:
   - Test interactive elements (buttons, inputs, checkboxes)
   - Verify real-time updates and state changes
   - Check for proper event handling

5. PERFORMANCE ANALYSIS:
   - Measure initial load time and rendering
   - Test responsiveness of interactions
   - Check for smooth animations and transitions

6. MODERN FEATURES:
   - Look for Service Worker registration
   - Check for Progressive Web App features
   - Test offline capabilities if available

Provide detailed analysis of:
- Framework-specific patterns detected
- SPA functionality effectiveness
- Performance characteristics
- Any challenges encountered
- Overall user experience quality

Focus on demonstrating the browser automation tool's ability to handle modern JavaScript applications effectively.
"""
            
            # Execute the task
            start_time = time.time()
            agent_result = await self.agent_executor.ainvoke({"input": task})
            execution_time = time.time() - start_time
            
            # Process results
            result.update({
                "success": True,
                "test_results": {
                    "agent_output": agent_result.get("output", ""),
                    "execution_time": execution_time,
                    "steps_taken": len(agent_result.get("intermediate_steps", [])),
                    "final_status": "completed"
                },
                "performance_metrics": {
                    "execution_time": execution_time,
                    "complexity_handled": "high",
                    "framework_features_tested": len(site_info["features"])
                }
            })
            
            logger.info(f"✅ {site_info['name']} testing completed successfully")
            
        except Exception as e:
            result.update({
                "success": False,
                "error": str(e),
                "test_results": {"status": "failed", "error": str(e)}
            })
            logger.error(f"❌ {site_info['name']} testing failed: {e}")
        
        return result

    async def run_comprehensive_spa_tests(self) -> Dict[str, Any]:
        """Run comprehensive SPA testing across all frameworks."""
        logger.info("\n🚀 Starting comprehensive JavaScript SPA testing")
        
        demo_results = {
            "demo_name": "JavaScript SPA Demo",
            "timestamp": datetime.now().isoformat(),
            "sites_tested": [],
            "overall_success": True,
            "summary_metrics": {},
            "framework_analysis": {},
            "recommendations": []
        }
        
        start_time = time.time()
        
        # Test each SPA site
        for i, site_info in enumerate(SPA_TEST_SITES, 1):
            logger.info(f"\n📋 Test {i}/{len(SPA_TEST_SITES)}: {site_info['name']}")
            
            site_result = await self.test_spa_framework(site_info)
            demo_results["sites_tested"].append(site_result)
            
            if not site_result["success"]:
                demo_results["overall_success"] = False
            
            # Brief pause between tests
            if i < len(SPA_TEST_SITES):
                logger.info("⏸️ Pausing between framework tests...")
                await asyncio.sleep(15)
        
        # Calculate comprehensive metrics
        total_time = time.time() - start_time
        successful_tests = len([r for r in demo_results["sites_tested"] if r["success"]])
        
        demo_results["summary_metrics"] = {
            "total_frameworks_tested": len(SPA_TEST_SITES),
            "successful_tests": successful_tests,
            "success_rate": (successful_tests / len(SPA_TEST_SITES)) * 100,
            "total_execution_time": total_time,
            "average_test_time": total_time / len(SPA_TEST_SITES),
            "frameworks_covered": [site["framework"] for site in SPA_TEST_SITES]
        }
        
        # Generate framework analysis
        demo_results["framework_analysis"] = self._analyze_framework_performance(
            demo_results["sites_tested"]
        )
        
        # Generate recommendations
        demo_results["recommendations"] = self._generate_spa_recommendations(
            demo_results["sites_tested"], demo_results["summary_metrics"]
        )
        
        return demo_results

    def _analyze_framework_performance(self, test_results: List[Dict]) -> Dict[str, Any]:
        """Analyze performance across different frameworks."""
        analysis = {
            "framework_comparison": {},
            "feature_coverage": {},
            "performance_insights": [],
            "complexity_handling": {}
        }
        
        for result in test_results:
            if result["success"]:
                framework = result["framework"]
                
                analysis["framework_comparison"][framework] = {
                    "success": result["success"],
                    "execution_time": result["test_results"].get("execution_time", 0),
                    "features_tested": result["features_tested"],
                    "complexity": "high" if "react" in framework.lower() or "angular" in framework.lower() else "medium"
                }
        
        # Identify best performing frameworks
        if analysis["framework_comparison"]:
            fastest_framework = min(
                analysis["framework_comparison"].items(),
                key=lambda x: x[1]["execution_time"]
            )[0]
            analysis["performance_insights"].append(f"Fastest framework testing: {fastest_framework}")
        
        return analysis

    def _generate_spa_recommendations(self, test_results: List[Dict], metrics: Dict) -> List[str]:
        """Generate recommendations based on SPA testing results."""
        recommendations = []
        
        success_rate = metrics["success_rate"]
        
        if success_rate >= 90:
            recommendations.append("Excellent SPA automation coverage - handles modern frameworks effectively")
        elif success_rate >= 75:
            recommendations.append("Good SPA automation with some framework-specific optimizations needed")
        else:
            recommendations.append("SPA automation challenges identified - focus on dynamic content handling")
        
        # Framework-specific recommendations
        successful_frameworks = [r["framework"] for r in test_results if r["success"]]
        
        if "React" in successful_frameworks:
            recommendations.append("Successfully handles React virtual DOM and component state")
        if "Vue.js" in successful_frameworks:
            recommendations.append("Effective Vue.js reactive data and directive handling")
        if "Angular" in successful_frameworks:
            recommendations.append("Demonstrates Angular TypeScript and service integration capability")
        
        if len(successful_frameworks) >= 3:
            recommendations.append("Multi-framework compatibility demonstrated across major SPA technologies")
        
        return recommendations

    async def print_results_summary(self, results: Dict[str, Any]):
        """Print a comprehensive summary of SPA testing results."""
        print(f"\n{'='*80}")
        print("📊 JAVASCRIPT SPA DEMO RESULTS SUMMARY")
        print(f"{'='*80}")
        
        metrics = results["summary_metrics"]
        print(f"🎯 Overall Success Rate: {metrics['success_rate']:.1f}%")
        print(f"✅ Successful Framework Tests: {metrics['successful_tests']}/{metrics['total_frameworks_tested']}")
        print(f"⏱️ Total Execution Time: {metrics['total_execution_time']:.1f}s")
        print(f"📈 Average Test Time: {metrics['average_test_time']:.1f}s per framework")
        
        print("\n📋 FRAMEWORKS TESTED:")
        for framework in metrics["frameworks_covered"]:
            print(f"├─ {framework}")
        
        print("\n📊 DETAILED RESULTS:")
        for i, result in enumerate(results["sites_tested"], 1):
            status = "✅" if result["success"] else "❌"
            exec_time = result["test_results"].get("execution_time", 0)
            print(f"{status} {i}. {result['site_name']} ({result['framework']}): {exec_time:.1f}s")
        
        if results["framework_analysis"]["performance_insights"]:
            print("\n⚡ PERFORMANCE INSIGHTS:")
            for insight in results["framework_analysis"]["performance_insights"]:
                print(f"├─ {insight}")
        
        if results["recommendations"]:
            print("\n💡 RECOMMENDATIONS:")
            for recommendation in results["recommendations"]:
                print(f"├─ {recommendation}")
        
        print(f"\n{'='*80}")

    async def cleanup(self):
        """Clean up demo resources."""
        try:
            if self.sandbox_manager:
                await self.sandbox_manager.cleanup()
            logger.info("✅ JavaScript SPA Demo cleanup completed")
        except Exception as e:
            logger.error(f"⚠️ Cleanup error: {e}")

async def main():
    """Main execution function."""
    demo = JavaScriptSPADemo()
    
    try:
        # Initialize demo first to get sandbox URLs
        if not await demo.initialize():
            print("❌ Failed to initialize JavaScript SPA Demo")
            return None
        
        # Display demo information
        print("\n🎬 Starting JavaScript SPA Demo")
        print("📝 Testing modern Single Page Applications including React, Vue.js, Angular, and vanilla JS.")
        print("Demonstrates handling of dynamic content, client-side routing, and framework-specific patterns.")
        
        # Open NoVNC viewer for monitoring (assuming we have the novnc_url from sandbox)
        try:
            viewer_path = generate_novnc_viewer(
                novnc_url="placeholder_url",  # This would come from sandbox initialization
                vnc_password=os.getenv('VNC_PASSWORD', 'vncpassword'),
                auto_open=True
            )
            print(f"\n🖥️ NoVNC Viewer opened: {viewer_path}")
        except Exception as e:
            print(f"⚠️ Could not open NoVNC viewer: {e}")
        
        print("👀 Monitor SPA testing in real-time!")
        
        print(f"\n🚀 Testing {len(SPA_TEST_SITES)} JavaScript SPA frameworks...")
        
        # Run comprehensive SPA tests
        results = await demo.run_comprehensive_spa_tests()
        
        # Display results
        await demo.print_results_summary(results)
        
        print("\n🎉 JavaScript SPA Demo completed!")
        print(f"📊 Success Rate: {results['summary_metrics']['success_rate']:.1f}%")
        
        return results
        
    except KeyboardInterrupt:
        print("\n👋 JavaScript SPA Demo interrupted by user")
        return None
    except Exception as e:
        logger.error(f"❌ JavaScript SPA Demo execution failed: {e}")
        return None
    finally:
        await demo.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
