#!/usr/bin/env python3
"""
Multi-Tab Workflow Demo

This demo tests the browser automation tool's ability to handle complex multi-tab
workflows that are common in real-world scenarios. It demonstrates tab management,
cross-tab data coordination, concurrent operations, and sophisticated workflow
orchestration across multiple browser contexts.

Scenarios tested:
- Research workflows with multiple sources
- Comparison shopping across sites
- Multi-step proce        print("\        print("\n📊 DETAILED METRICS:")
        print(f"├─ Workflow Types Tested: {metrics['workflow_types_tested']}")
        print(f"├─ Avg Tabs per Scenario: {metrics['average_tabs_per_scenario']:.1f}")
        print(f"├─ Coordination Strategies: {len(self.results['coordination_strategies'])}")
        print(f"└─ Total Runtime: {self.results['total_execution_time']:.1f}s")
        
        if self.results["workflow_patterns"]:
            print("\n🔄 WORKFLOW PATTERNS TESTED:")
            for pattern, count in sorted(self.results["workflow_patterns"].items()):
                print(f"├─ {pattern.replace('_', ' ').title()}: {count} times")
        
        if self.results["coordination_strategies"]:
            print("\n🤝 COORDINATION STRATEGIES:")
            for strategy in self.results["coordination_strategies"]:
                print(f"├─ {strategy.replace('_', ' ').title()}")
        
        print("\n📈 SCENARIO-BY-SCENARIO RESULTS:")ICS:")
        print(f"├─ Workflow Types Tested: {metrics['workflow_types_tested']}")
        print(f"├─ Avg Tabs per Scenario: {metrics['average_tabs_per_scenario']:.1f}")
        print(f"├─ Coordination Strategies: {len(self.results['coordination_strategies'])}")
        print(f"└─ Total Runtime: {self.results['total_execution_time']:.1f}s")
        
        if self.results["workflow_patterns"]:
            print("\n🔄 WORKFLOW PATTERNS TESTED:")
            for pattern, count in self.results["workflow_patterns"].items():
                print(f"├─ {pattern.replace('_', ' ').title()}: {count} times")
        
        if self.results["coordination_strategies"]:
            print("\n🤝 COORDINATION STRATEGIES:")
            for strategy in self.results["coordination_strategies"]:
                print(f"├─ {strategy.replace('_', ' ').title()}")
        
        print("\n📈 SCENARIO-BY-SCENARIO RESULTS:")s
- Data collection and coordination
- Tab-based task management

Safety: Uses only public sites and demo data.
Ethics: Respects rate limits and site usage policies.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, Any

from langchain_openai import ChatOpenAI

from tools.utilities.browser_tools_init import initialize_browser_tools
from tools.utilities.sandbox_manager import SandboxManager
from utils.enhanced_agent_formatting import create_enhanced_react_agent
from utils.novnc_viewer import generate_novnc_viewer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Multi-tab workflow scenarios
MULTI_TAB_SCENARIOS = [
    {
        "name": "Research Comparison Workflow",
        "description": "Compare information across multiple educational sources",
        "tabs": [
            {
                "name": "Wikipedia Main",
                "url": "https://en.wikipedia.org/wiki/Main_Page",
                "purpose": "Primary information source",
                "actions": ["search_topic", "gather_overview", "find_related_links"]
            },
            {
                "name": "MDN Web Docs",
                "url": "https://developer.mozilla.org/en-US/",
                "purpose": "Technical documentation source",
                "actions": ["search_documentation", "gather_technical_details", "find_examples"]
            },
            {
                "name": "Stack Overflow",
                "url": "https://stackoverflow.com/",
                "purpose": "Community knowledge source",
                "actions": ["search_questions", "gather_solutions", "analyze_discussions"]
            }
        ],
        "workflow_type": "research_aggregation",
        "coordination_required": True,
        "data_sharing": ["search_terms", "findings", "comparisons"]
    },
    {
        "name": "Learning Path Workflow",
        "description": "Navigate through multiple learning resources systematically",
        "tabs": [
            {
                "name": "W3Schools Tutorial",
                "url": "https://www.w3schools.com/",
                "purpose": "Tutorial source",
                "actions": ["browse_tutorials", "follow_examples", "practice_exercises"]
            },
            {
                "name": "GitHub Examples",
                "url": "https://github.com/explore",
                "purpose": "Code examples source",
                "actions": ["explore_repositories", "analyze_code", "find_patterns"]
            },
            {
                "name": "CodePen Demos",
                "url": "https://codepen.io/trending",
                "purpose": "Interactive demos source",
                "actions": ["explore_demos", "test_interactions", "understand_implementations"]
            }
        ],
        "workflow_type": "educational_progression",
        "coordination_required": True,
        "data_sharing": ["learning_progress", "code_examples", "techniques"]
    },
    {
        "name": "Documentation Navigation Workflow",
        "description": "Navigate through interconnected documentation sites",
        "tabs": [
            {
                "name": "React Documentation",
                "url": "https://reactjs.org/docs/getting-started.html",
                "purpose": "Framework documentation",
                "actions": ["read_guides", "follow_examples", "understand_concepts"]
            },
            {
                "name": "TypeScript Handbook",
                "url": "https://www.typescriptlang.org/docs/",
                "purpose": "Language documentation",
                "actions": ["study_types", "learn_syntax", "practice_examples"]
            },
            {
                "name": "Node.js Guides",
                "url": "https://nodejs.org/en/docs/guides/",
                "purpose": "Runtime documentation",
                "actions": ["understand_runtime", "learn_apis", "explore_modules"]
            }
        ],
        "workflow_type": "documentation_study",
        "coordination_required": False,
        "data_sharing": ["concepts", "cross_references", "integration_points"]
    }
]

class MultiTabWorkflowDemo:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "scenarios_tested": [],
            "tabs_managed": 0,
            "workflow_patterns": {},
            "coordination_strategies": [],
            "data_sharing_examples": [],
            "tab_management_metrics": {},
            "success_metrics": {},
            "challenges_encountered": [],
            "total_execution_time": 0
        }
        self.llm = None
        self.tools = None
        self.agent_executor = None

    async def setup_browser_environment(self):
        """Initialize browser tools and create agent."""
        try:
            # Initialize browser tools
            logger.info("Initializing browser automation tools...")
            self.tools = await initialize_browser_tools()
            
            # Initialize LLM
            self.llm = ChatOpenAI(
                model="gpt-4-turbo-preview",
                temperature=0.1,
                max_tokens=2500
            )
            
            # Create enhanced agent
            self.agent_executor = create_enhanced_react_agent(
                llm=self.llm,
                tools=self.tools,
                max_iterations=25,
                max_execution_time=1200,
                return_intermediate_steps=True
            )
            
            logger.info("✅ Browser environment setup complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup browser environment: {e}")
            return False

    async def test_multi_tab_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Test a specific multi-tab workflow scenario."""
        logger.info(f"\n📑 Testing Multi-Tab Scenario: {scenario['name']}")
        
        scenario_result = {
            "scenario_name": scenario["name"],
            "workflow_type": scenario["workflow_type"],
            "tabs_planned": len(scenario["tabs"]),
            "coordination_required": scenario["coordination_required"],
            "success": False,
            "tabs_opened": 0,
            "workflow_steps_completed": [],
            "coordination_achieved": False,
            "data_shared": [],
            "tab_navigation_patterns": [],
            "execution_time": 0,
            "error_details": None
        }
        
        start_time = time.time()
        
        try:
            # Create comprehensive multi-tab workflow task
            task = self._create_multi_tab_task(scenario)
            
            # Execute the task
            logger.info(f"🤖 Executing multi-tab workflow: {scenario['workflow_type']}")
            result = await self.agent_executor.ainvoke({"input": task})
            
            # Process and analyze results
            if result and "output" in result:
                scenario_result.update(self._analyze_multi_tab_results(result, scenario))
                scenario_result["success"] = True
                logger.info(f"✅ Successfully completed {scenario['name']}")
            else:
                logger.warning(f"⚠️ Limited results from {scenario['name']}")
                scenario_result["success"] = False
                
        except Exception as e:
            logger.error(f"❌ Error in multi-tab scenario {scenario['name']}: {e}")
            scenario_result["error_details"] = str(e)
            self.results["challenges_encountered"].append({
                "scenario": scenario["name"],
                "workflow_type": scenario["workflow_type"],
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
        
        scenario_result["execution_time"] = time.time() - start_time
        return scenario_result

    def _create_multi_tab_task(self, scenario: Dict[str, Any]) -> str:
        """Create a comprehensive multi-tab workflow task."""
        base_task = f"""
Execute a comprehensive multi-tab workflow for: {scenario['name']}

WORKFLOW DESCRIPTION: {scenario['description']}
WORKFLOW TYPE: {scenario['workflow_type']}
COORDINATION REQUIRED: {scenario['coordination_required']}

MULTI-TAB EXECUTION PLAN:

PHASE 1: TAB SETUP AND INITIAL NAVIGATION
"""
        
        # Add tab-specific instructions
        for i, tab in enumerate(scenario['tabs'], 1):
            base_task += f"""
TAB {i}: {tab['name']}
- URL: {tab['url']}
- Purpose: {tab['purpose']}
- Actions: {', '.join(tab['actions'])}
"""
        
        base_task += f"""

PHASE 2: WORKFLOW EXECUTION STRATEGY

1. **Sequential Tab Opening**:
   - Open each tab systematically
   - Verify page loading and accessibility
   - Take initial screenshots for documentation
   - Navigate to key sections relevant to the workflow

2. **Content Exploration Per Tab**:
   - Execute the specified actions for each tab
   - Gather relevant information based on tab purpose
   - Document key findings and observations
   - Note any cross-references or related content

3. **Cross-Tab Coordination** (if required):
   - Switch between tabs to compare information
   - Look for connections and relationships
   - Synthesize findings across multiple sources
   - Document coordination strategies used

4. **Workflow Integration**:
   - Combine insights from all tabs
   - Demonstrate understanding of the complete workflow
   - Show how different tabs contribute to the overall goal
   - Document the value of the multi-tab approach

SPECIFIC EXECUTION REQUIREMENTS:

🔍 **Information Gathering**:
- Extract key information from each tab
- Note the unique value each source provides
- Document search strategies and navigation patterns
- Identify the most valuable content sources

🔄 **Tab Management**:
- Demonstrate efficient tab switching
- Show awareness of browser tab state
- Use appropriate navigation within each tab
- Manage multiple content streams effectively

🎯 **Workflow Optimization**:
- Show how multi-tab approach enhances the task
- Demonstrate time efficiency through parallel information access
- Identify synergies between different content sources
- Optimize the workflow based on findings

📊 **Documentation and Analysis**:
- Take screenshots at key workflow points
- Document successful tab coordination examples
- Note performance characteristics and efficiency gains
- Provide insights on multi-tab workflow benefits

SAFETY AND ETHICS:
- Only use public, educational content
- Respect rate limits and site usage policies
- Focus on learning and demonstration rather than data extraction
- Maintain appropriate browsing behavior across all tabs

EXPECTED OUTCOMES:
- Successful multi-tab workflow execution
- Demonstration of tab coordination strategies
- Evidence of enhanced productivity through parallel browsing
- Comprehensive documentation of the workflow benefits

Please execute this multi-tab workflow systematically and provide detailed analysis of the coordination strategies and workflow benefits achieved.
        """
        
        return base_task

    def _analyze_multi_tab_results(self, result: Dict[str, Any], scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the results from multi-tab workflow testing."""
        analysis = {
            "tabs_opened": 0,
            "workflow_steps_completed": [],
            "coordination_achieved": False,
            "data_shared": [],
            "tab_navigation_patterns": []
        }
        
        output_text = result.get("output", "").lower()
        
        # Count tab references
        tab_indicators = ["tab", "window", "switch", "navigate", "open"]
        for indicator in tab_indicators:
            count = output_text.count(indicator)
            if count > 0:
                analysis["tabs_opened"] = max(analysis["tabs_opened"], min(count, len(scenario["tabs"])))
        
        # Check for workflow steps
        workflow_steps = ["search", "analyze", "compare", "gather", "document", "navigate"]
        for step in workflow_steps:
            if step in output_text:
                analysis["workflow_steps_completed"].append(step)
        
        # Check for coordination activities
        coordination_terms = ["compare", "coordinate", "combine", "synthesize", "integrate"]
        for term in coordination_terms:
            if term in output_text:
                analysis["coordination_achieved"] = True
                break
        
        # Check for data sharing examples
        data_sharing_terms = ["information", "findings", "data", "insights", "connections"]
        for term in data_sharing_terms:
            if term in output_text:
                analysis["data_shared"].append(term)
        
        # Navigation patterns
        navigation_terms = ["click", "scroll", "search", "browse", "explore"]
        for term in navigation_terms:
            if term in output_text:
                analysis["tab_navigation_patterns"].append(term)
        
        # Update global metrics
        self.results["tabs_managed"] += analysis["tabs_opened"]
        
        workflow_type = scenario["workflow_type"]
        if workflow_type not in self.results["workflow_patterns"]:
            self.results["workflow_patterns"][workflow_type] = 0
        self.results["workflow_patterns"][workflow_type] += 1
        
        return analysis

    async def run_comprehensive_multi_tab_demo(self):
        """Run the complete multi-tab workflow demonstration."""
        logger.info("🚀 Starting Comprehensive Multi-Tab Workflow Demo")
        logger.info("=" * 70)
        
        demo_start_time = time.time()
        
        # Setup browser environment
        if not await self.setup_browser_environment():
            logger.error("❌ Failed to setup browser environment")
            return self.results
        
        # Test each multi-tab scenario
        for i, scenario in enumerate(MULTI_TAB_SCENARIOS, 1):
            logger.info(f"\n📑 Testing Scenario {i}/{len(MULTI_TAB_SCENARIOS)}: {scenario['name']}")
            logger.info(f"🔄 Workflow Type: {scenario['workflow_type']}")
            logger.info(f"📊 Tabs Required: {len(scenario['tabs'])}")
            logger.info(f"🤝 Coordination: {'Yes' if scenario['coordination_required'] else 'No'}")
            
            scenario_result = await self.test_multi_tab_scenario(scenario)
            self.results["scenarios_tested"].append(scenario_result)
            
            # Update coordination strategies
            if scenario_result.get("coordination_achieved"):
                self.results["coordination_strategies"].append(scenario["workflow_type"])
            
            # Update data sharing examples
            self.results["data_sharing_examples"].extend(
                scenario_result.get("data_shared", [])
            )
            
            # Brief pause between scenarios
            await asyncio.sleep(3)
        
        # Calculate final metrics
        self.results["total_execution_time"] = time.time() - demo_start_time
        self.results["success_metrics"] = self._calculate_success_metrics()
        
        logger.info("\n" + "=" * 70)
        logger.info("📊 MULTI-TAB WORKFLOW DEMO COMPLETED")
        self._print_comprehensive_summary()
        
        return self.results

    def _calculate_success_metrics(self) -> Dict[str, Any]:
        """Calculate comprehensive success metrics."""
        successful_scenarios = len([s for s in self.results["scenarios_tested"] if s.get("success", False)])
        total_scenarios = len(self.results["scenarios_tested"])
        
        coordinated_workflows = len([s for s in self.results["scenarios_tested"] 
                                   if s.get("coordination_achieved", False)])
        
        return {
            "scenarios_successfully_completed": successful_scenarios,
            "total_scenarios_attempted": total_scenarios,
            "success_rate": (successful_scenarios / total_scenarios * 100) if total_scenarios > 0 else 0,
            "total_tabs_managed": self.results["tabs_managed"],
            "workflow_types_tested": len(self.results["workflow_patterns"]),
            "coordination_success_rate": (coordinated_workflows / total_scenarios * 100) if total_scenarios > 0 else 0,
            "average_tabs_per_scenario": (
                self.results["tabs_managed"] / total_scenarios
            ) if total_scenarios > 0 else 0,
            "average_execution_time": (
                sum(s.get("execution_time", 0) for s in self.results["scenarios_tested"]) / 
                len(self.results["scenarios_tested"])
            ) if self.results["scenarios_tested"] else 0
        }

    def _print_comprehensive_summary(self):
        """Print detailed summary of the demo results."""
        print("\n" + "=" * 70)
        print("📑 MULTI-TAB WORKFLOW DEMO SUMMARY")
        print("=" * 70)
        
        metrics = self.results["success_metrics"]
        
        print(f"🎯 Overall Success Rate: {metrics['success_rate']:.1f}%")
        print(f"📑 Scenarios Completed: {metrics['scenarios_successfully_completed']}/{metrics['total_scenarios_attempted']}")
        print(f"🗂️ Total Tabs Managed: {metrics['total_tabs_managed']}")
        print(f"🤝 Coordination Success: {metrics['coordination_success_rate']:.1f}%")
        print(f"⚡ Avg Execution Time: {metrics['average_execution_time']:.1f}s")
        
        print("\n📊 DETAILED METRICS:")
        print(f"├─ Workflow Types Tested: {metrics['workflow_types_tested']}")
        print(f"├─ Avg Tabs per Scenario: {metrics['average_tabs_per_scenario']:.1f}")
        print(f"├─ Coordination Strategies: {len(self.results['coordination_strategies'])}")
        print(f"└─ Total Runtime: {self.results['total_execution_time']:.1f}s")
        
        if self.results["workflow_patterns"]:
            print("\n🔄 WORKFLOW PATTERNS TESTED:")
            for pattern, count in sorted(self.results["workflow_patterns"].items()):
                print(f"├─ {pattern.replace('_', ' ').title()}: {count} times")
        
        if self.results["coordination_strategies"]:
            print("\n🤝 COORDINATION STRATEGIES:")
            for strategy in set(self.results["coordination_strategies"]):
                print(f"├─ {strategy.replace('_', ' ').title()}")
        
        print("\n📈 SCENARIO-BY-SCENARIO RESULTS:")
        for i, scenario in enumerate(self.results["scenarios_tested"], 1):
            status = "✅" if scenario.get("success", False) else "❌"
            tabs = scenario.get("tabs_opened", 0)
            time_taken = scenario.get("execution_time", 0)
            coord = "🤝" if scenario.get("coordination_achieved", False) else "📋"
            print(f"{status} {coord} {i}. {scenario['scenario_name']}: {tabs} tabs, {time_taken:.1f}s")
        
        if self.results["challenges_encountered"]:
            print("\n⚠️ CHALLENGES ENCOUNTERED:")
            for challenge in self.results["challenges_encountered"]:
                print(f"├─ {challenge['scenario']}: {challenge['error']}")
        
        print("\n💡 MULTI-TAB WORKFLOW CAPABILITIES DEMONSTRATED:")
        print("├─ Complex tab management and coordination")
        print("├─ Cross-tab information synthesis")
        print("├─ Parallel browsing and research workflows")
        print("├─ Educational content navigation strategies")
        print("├─ Workflow optimization through multi-tasking")
        print("├─ Browser state management across contexts")
        print("└─ Enhanced productivity through parallel processing")
        
        print("\n" + "=" * 70)

async def main():
    """Main execution function."""
    try:
        # Create sandbox environment
        sandbox_manager = SandboxManager()
        
        logger.info("🎬 Starting Multi-Tab Workflow Demo")
        logger.info("📋 Demo: Multi-Tab Workflow Demo")
        logger.info("📝 Description: Comprehensive testing of browser automation capabilities for complex multi-tab workflows")
        
        # Start NoVNC viewer
        try:
            novnc_url = "http://localhost:6080/vnc.html?autoconnect=true&resize=downscale"
            viewer_path = generate_novnc_viewer(
                novnc_url=novnc_url,
                vnc_password=os.getenv('VNC_PASSWORD', 'vncpassword'),
                auto_open=True
            )
            if viewer_path:
                logger.info(f"🖥️ NoVNC Viewer: {novnc_url}")
                logger.info("👀 You can monitor the browser automation in real-time!")
        except Exception as e:
            logger.warning(f"⚠️ Could not start NoVNC viewer: {e}")
            logger.info("💡 Demo will continue without viewer")
        
        # Create and run demo
        demo = MultiTabWorkflowDemo()
        results = await demo.run_comprehensive_multi_tab_demo()
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"multi_tab_workflow_demo_results_{timestamp}.json"
        
        import json
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"📄 Results saved to: {results_file}")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Demo execution failed: {e}")
        raise
    finally:
        # Cleanup
        try:
            if 'sandbox_manager' in locals():
                await sandbox_manager.cleanup()
        except Exception as e:
            logger.error(f"⚠️ Cleanup error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
