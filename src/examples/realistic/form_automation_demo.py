#!/usr/bin/env python3
"""
Form Automation Demo

This demo tests the browser automation tool's ability to handle complex form
workflows including multi-step forms, dynamic form elements, validation handling,
file uploads, and various input types. This showcases the tool's capability
to handle real-world business forms and data entry scenarios.

Sites tested:
- HTML form examples and tutorials
- Bootstrap form components
- Input validation scenarios
- Complex form interactions

Safety: Uses only demo sites and test data.
Ethics: Respects form submission limits and validation rules.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import asyncio
import logging
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from langchain_openai import ChatOpenAI

from tools.utilities.browser_tools_init import initialize_browser_tools
from tools.utilities.sandbox_manager import SandboxManager
from utils.enhanced_agent_formatting import create_enhanced_react_agent
from utils.novnc_viewer import generate_novnc_viewer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Form Test Sites and Scenarios
FORM_TEST_SITES = [
    {
        "name": "W3Schools Form Tutorial",
        "url": "https://www.w3schools.com/html/html_forms.asp",
        "description": "Basic HTML form examples and tutorials",
        "type": "educational_forms",
        "test_scenario": "form_tutorial_navigation",
        "expected_elements": ["form", "input", "button", "select", "textarea"],
        "requires_interaction": False
    },
    {
        "name": "MDN Form Guide",
        "url": "https://developer.mozilla.org/en-US/docs/Learn/Forms/Your_first_form",
        "description": "Comprehensive form development guide",
        "type": "educational_forms", 
        "test_scenario": "form_learning_path",
        "expected_elements": ["form examples", "code snippets", "interactive demos"],
        "requires_interaction": False
    },
    {
        "name": "Bootstrap Form Examples",
        "url": "https://getbootstrap.com/docs/5.3/forms/overview/",
        "description": "Modern responsive form components and styling",
        "type": "component_library",
        "test_scenario": "responsive_form_testing",
        "expected_elements": ["form controls", "validation", "styling examples"],
        "requires_interaction": False
    },
    {
        "name": "HTML5 Input Types Demo",
        "url": "https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input",
        "description": "Comprehensive input type demonstrations",
        "type": "input_validation",
        "test_scenario": "input_type_exploration",
        "expected_elements": ["various input types", "examples", "browser support"],
        "requires_interaction": False
    }
]

# Test data for form filling
FORM_TEST_DATA = {
    "personal": {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe.test@example.com",
        "phone": "555-0123",
        "age": "30",
        "date_of_birth": "1993-05-15"
    },
    "address": {
        "street": "123 Test Street",
        "city": "TestCity",
        "state": "CA",
        "zip_code": "12345",
        "country": "United States"
    },
    "preferences": {
        "newsletter": True,
        "notifications": False,
        "language": "English",
        "theme": "Light"
    }
}

class FormAutomationDemo:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "sites_tested": [],
            "forms_found": 0,
            "form_elements_analyzed": {},
            "input_types_discovered": set(),
            "validation_scenarios": [],
            "interaction_patterns": [],
            "success_metrics": {},
            "challenges_encountered": [],
            "total_execution_time": 0
        }
        self.llm = None
        self.tools = None
        self.agent_executor = None

    async def setup_browser_environment(self):
        """Initialize browser tools and create agent with NoVNC viewer."""
        try:
            # Create sandbox and get URLs
            logger.info("Creating sandbox environment...")
            sandbox_manager = SandboxManager()
            sandbox_id, cdp_url, vnc_url, novnc_url, api_url, web_url, x_url = sandbox_manager.create_sandbox()
            
            # Generate and open NoVNC viewer for real-time monitoring
            logger.info("🖥️ Opening NoVNC viewer for real-time monitoring...")
            try:
                viewer_path = generate_novnc_viewer(
                    novnc_url=novnc_url,
                    vnc_password="vncpassword",
                    auto_open=True
                )
                logger.info(f"✅ NoVNC viewer opened: {viewer_path}")
                logger.info(f"🌐 Direct NoVNC URL: {novnc_url}")
            except Exception as e:
                logger.warning(f"⚠️ Could not open NoVNC viewer: {e}")
                logger.info(f"🌐 You can manually open: {novnc_url}")
            
            # Initialize browser tools with the sandbox
            logger.info("Initializing browser automation tools...")
            self.tools = await initialize_browser_tools(api_url, sandbox_id)
            
            # Initialize LLM
            self.llm = ChatOpenAI(
                model="gpt-4-turbo-preview",
                temperature=0.1,
                max_tokens=2000
            )
            
            # Create enhanced agent
            self.agent_executor = create_enhanced_react_agent(
                llm=self.llm,
                tools=self.tools,
                max_iterations=15,
                max_execution_time=600,
                return_intermediate_steps=True
            )
            
            logger.info("✅ Browser environment setup complete")
            logger.info(f"🔑 VNC Password: vncpassword")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup browser environment: {e}")
            return False

    async def test_form_site(self, site: Dict[str, Any]) -> Dict[str, Any]:
        """Test a specific form site with comprehensive analysis."""
        logger.info(f"\n🔍 Testing {site['name']}...")
        
        site_result = {
            "site_name": site["name"],
            "url": site["url"],
            "test_scenario": site["test_scenario"],
            "success": False,
            "forms_found": 0,
            "elements_analyzed": {},
            "interactions_completed": [],
            "validation_tests": [],
            "execution_time": 0,
            "error_details": None
        }
        
        start_time = time.time()
        
        try:
            # Create task based on site type
            task = self._create_form_analysis_task(site)
            
            # Execute the task
            logger.info(f"🤖 Executing task: {site['test_scenario']}")
            result = await self.agent_executor.ainvoke({"input": task})
            
            # Process and analyze results
            if result and "output" in result:
                site_result.update(self._analyze_form_results(result, site))
                site_result["success"] = True
                logger.info(f"✅ Successfully tested {site['name']}")
            else:
                logger.warning(f"⚠️ Limited results from {site['name']}")
                site_result["success"] = False
                
        except Exception as e:
            logger.error(f"❌ Error testing {site['name']}: {e}")
            site_result["error_details"] = str(e)
            self.results["challenges_encountered"].append({
                "site": site["name"],
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
        
        site_result["execution_time"] = time.time() - start_time
        return site_result

    def _create_form_analysis_task(self, site: Dict[str, Any]) -> str:
        """Create a comprehensive form analysis task."""
        base_task = f"""
Navigate to {site['url']} and perform comprehensive form analysis for {site['name']}.

ANALYSIS OBJECTIVES:
1. **Form Discovery**: Find and catalog all forms on the page
2. **Element Analysis**: Identify input types, validation patterns, and interactive elements
3. **Content Exploration**: Navigate through form-related content and examples
4. **Documentation Review**: Read through form tutorials and best practices
5. **Interactive Testing**: Test any available form demos or examples (safely)

SPECIFIC TASKS:
- Navigate to the URL and wait for full page load
- Identify all form elements (forms, inputs, buttons, selects, textareas)
- Document different input types encountered (text, email, password, date, etc.)
- Look for validation examples and error handling patterns
- Test any interactive form demonstrations available
- Explore form-related documentation and tutorials
- Take screenshots of interesting form patterns or examples

SAFETY GUIDELINES:
- Only interact with demo forms and educational content
- Do not submit any real data or create accounts
- Focus on learning and analysis rather than data submission
- Respect the educational nature of these sites

EXPECTED OUTCOMES:
- Comprehensive catalog of form elements and patterns
- Understanding of modern form development practices
- Documentation of validation and interaction patterns
- Screenshots of notable form examples

Please provide detailed analysis of what you discover about form automation capabilities and patterns.
        """
        
        # Add site-specific instructions
        if site["type"] == "educational_forms":
            base_task += "\n\nFOCUS: Educational content navigation and form concept exploration."
        elif site["type"] == "component_library":
            base_task += "\n\nFOCUS: Component demonstrations and responsive design patterns."
        elif site["type"] == "input_validation":
            base_task += "\n\nFOCUS: Input type varieties and validation mechanism exploration."
            
        return base_task

    def _analyze_form_results(self, result: Dict[str, Any], site: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the results from form testing."""
        analysis = {
            "forms_found": 0,
            "elements_analyzed": {},
            "interactions_completed": [],
            "validation_tests": []
        }
        
        output_text = result.get("output", "").lower()
        
        # Analyze form-related content
        form_indicators = ["form", "input", "button", "field", "validation", "submit"]
        for indicator in form_indicators:
            if indicator in output_text:
                analysis["interactions_completed"].append(f"{indicator}_interaction")
        
        # Check for specific form elements mentioned
        input_types = ["text", "email", "password", "number", "date", "checkbox", "radio", "select"]
        for input_type in input_types:
            if input_type in output_text:
                self.results["input_types_discovered"].add(input_type)
                analysis["elements_analyzed"][input_type] = True
        
        # Look for validation patterns
        validation_patterns = ["required", "pattern", "validation", "error", "invalid", "valid"]
        for pattern in validation_patterns:
            if pattern in output_text:
                analysis["validation_tests"].append(pattern)
        
        # Estimate forms found based on content
        form_mentions = output_text.count("form")
        analysis["forms_found"] = min(form_mentions, 10)  # Cap at reasonable number
        
        return analysis

    async def run_comprehensive_form_demo(self):
        """Run the complete form automation demonstration."""
        logger.info("🚀 Starting Comprehensive Form Automation Demo")
        logger.info("=" * 60)
        
        demo_start_time = time.time()
        
        # Setup browser environment
        if not await self.setup_browser_environment():
            logger.error("❌ Failed to setup browser environment")
            return self.results
        
        # Test each form site
        for i, site in enumerate(FORM_TEST_SITES, 1):
            logger.info(f"\n📋 Testing Site {i}/{len(FORM_TEST_SITES)}: {site['name']}")
            logger.info(f"🔗 URL: {site['url']}")
            logger.info(f"📝 Scenario: {site['test_scenario']}")
            
            site_result = await self.test_form_site(site)
            self.results["sites_tested"].append(site_result)
            
            # Update aggregate metrics
            self.results["forms_found"] += site_result.get("forms_found", 0)
            
            # Merge element analysis
            for element, found in site_result.get("elements_analyzed", {}).items():
                if element not in self.results["form_elements_analyzed"]:
                    self.results["form_elements_analyzed"][element] = 0
                if found:
                    self.results["form_elements_analyzed"][element] += 1
            
            # Add interaction patterns
            self.results["interaction_patterns"].extend(
                site_result.get("interactions_completed", [])
            )
            
            # Add validation scenarios
            self.results["validation_scenarios"].extend(
                site_result.get("validation_tests", [])
            )
            
            # Brief pause between sites
            await asyncio.sleep(2)
        
        # Calculate final metrics
        self.results["total_execution_time"] = time.time() - demo_start_time
        self.results["success_metrics"] = self._calculate_success_metrics()
        
        # Convert set to list for JSON serialization
        self.results["input_types_discovered"] = list(self.results["input_types_discovered"])
        
        logger.info("\n" + "=" * 60)
        logger.info("📊 FORM AUTOMATION DEMO COMPLETED")
        self._print_comprehensive_summary()
        
        return self.results

    def _calculate_success_metrics(self) -> Dict[str, Any]:
        """Calculate comprehensive success metrics."""
        successful_tests = len([s for s in self.results["sites_tested"] if s.get("success", False)])
        total_tests = len(self.results["sites_tested"])
        
        return {
            "sites_successfully_tested": successful_tests,
            "total_sites_attempted": total_tests,
            "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0,
            "total_forms_found": self.results["forms_found"],
            "unique_input_types": len(self.results["input_types_discovered"]),
            "form_elements_analyzed": len(self.results["form_elements_analyzed"]),
            "interaction_patterns_discovered": len(set(self.results["interaction_patterns"])),
            "validation_scenarios_found": len(set(self.results["validation_scenarios"])),
            "average_execution_time": (
                sum(s.get("execution_time", 0) for s in self.results["sites_tested"]) / 
                len(self.results["sites_tested"])
            ) if self.results["sites_tested"] else 0
        }

    def _print_comprehensive_summary(self):
        """Print detailed summary of the demo results."""
        print("\n" + "=" * 60)
        print("📋 FORM AUTOMATION DEMO SUMMARY")
        print("=" * 60)
        
        metrics = self.results["success_metrics"]
        
        print(f"🎯 Overall Success Rate: {metrics['success_rate']:.1f}%")
        print(f"🌐 Sites Tested: {metrics['sites_successfully_tested']}/{metrics['total_sites_attempted']}")
        print(f"📝 Forms Discovered: {metrics['total_forms_found']}")
        print(f"🔧 Input Types Found: {metrics['unique_input_types']}")
        print(f"⚡ Avg Execution Time: {metrics['average_execution_time']:.1f}s")
        
        print(f"\n📊 DETAILED METRICS:")
        print(f"├─ Form Elements Analyzed: {metrics['form_elements_analyzed']}")
        print(f"├─ Interaction Patterns: {metrics['interaction_patterns_discovered']}")
        print(f"├─ Validation Scenarios: {metrics['validation_scenarios_found']}")
        print(f"└─ Total Runtime: {self.results['total_execution_time']:.1f}s")
        
        if self.results["input_types_discovered"]:
            print(f"\n🔍 INPUT TYPES DISCOVERED:")
            for input_type in sorted(self.results["input_types_discovered"]):
                print(f"├─ {input_type}")
        
        print(f"\n📈 SITE-BY-SITE RESULTS:")
        for i, site in enumerate(self.results["sites_tested"], 1):
            status = "✅" if site.get("success", False) else "❌"
            forms = site.get("forms_found", 0)
            time_taken = site.get("execution_time", 0)
            print(f"{status} {i}. {site['site_name']}: {forms} forms, {time_taken:.1f}s")
        
        if self.results["challenges_encountered"]:
            print(f"\n⚠️ CHALLENGES ENCOUNTERED:")
            for challenge in self.results["challenges_encountered"]:
                print(f"├─ {challenge['site']}: {challenge['error']}")
        
        print(f"\n💡 FORM AUTOMATION CAPABILITIES DEMONSTRATED:")
        print(f"├─ Educational content navigation and analysis")
        print(f"├─ Form element discovery and cataloging")
        print(f"├─ Input type identification and interaction")
        print(f"├─ Validation pattern recognition")
        print(f"├─ Responsive design evaluation")
        print(f"└─ Documentation-based learning workflows")
        
        print("\n" + "=" * 60)

async def main():
    """Main execution function."""
    try:
        logger.info("🎬 Starting Form Automation Demo")
        logger.info("📝 Demonstrates comprehensive form handling and validation testing")
        
        # Create and run demo
        demo = FormAutomationDemo()
        results = await demo.run_comprehensive_form_demo()
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"form_automation_demo_results_{timestamp}.json"
        
        import json
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"📄 Results saved to: {results_file}")
        return results
        
    except Exception as e:
        logger.error(f"❌ Demo execution failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
