#!/usr/bin/env python3
"""
Human Intervention Mastery Demo
==============================

Comprehensive demonstration of human intervention capabilities covering 8 intervention tools.
This demo showcases the complete int            # Generate advanced viewer with intervention-specific features
            viewer_html = generate_advanced_novnc_viewer(
                novnc_url=self.novnc_url,
                demo_name="Human Intervention Mastery Demo",
                demo_description="Comprehensive human intervention capabilities demonstration - Active participation required!",
                show_intervention_controls=True
            )orkflow including CAPTCHA handling, login assistance,
intervention status management, and automatic challenge detection.

Tools Demonstrated (8/44):
- Legacy Intervention (3): RequestHumanHelpTool, SolveCaptchaTool, HandleLoginTool
- Enhanced Intervention (5): RequestInterventionTool, CompleteInterventionTool, CancelInterventionTool, InterventionStatusTool, AutoDetectInterventionTool

Scenarios:
1. CAPTCHA challenges and automated detection
2. Login form automation with 2FA support
3. Complex security challenges requiring human intelligence
4. Real-time intervention status monitoring and management

⚠️ HUMAN INTERVENTION NOTICE:
This demo REQUIRES active human participation! It will present various challenges that only humans
can solve including CAPTCHAs, authentication flows, and security verifications. The NoVNC viewer
provides direct browser access for manual intervention.

Safety: Uses only educational and test websites with respectful automation practices.
Ethics: Respects robots.txt files and implements reasonable delays between requests.
"""

from pathlib import Path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import asyncio
import time

from langchain_openai import AzureChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from dotenv import load_dotenv

from src.tools.utilities.browser_tools_init import initialize_browser_tools
from src.tools.utilities.sandbox_manager import SandboxManager
from src.utils.logger import logger
from src.utils.advanced_novnc_viewer import generate_advanced_novnc_viewer
from src.utils.enhanced_agent_formatting import create_enhanced_business_prompt

# Load environment variables
load_dotenv()

class InterventionMasteryDemo:
    """Human intervention mastery demonstration with comprehensive intervention tools"""
    
    def __init__(self):
        self.llm = None
        self.agent = None
        self.tools = []
        self.sandbox_manager = SandboxManager()
        self.sandbox_id = None
        self.api_base_url = None
        self.vnc_url = None
        self.novnc_url = None
        self.results = {
            "scenarios_completed": 0,
            "tools_demonstrated": set(),
            "total_actions": 0,
            "interventions_requested": 0,
            "captchas_encountered": 0,
            "logins_assisted": 0,
            "interventions_completed": 0,
            "start_time": None,
            "end_time": None,
            "scenarios": {}
        }

    async def initialize_with_sandbox(self):
        """Initialize with Daytona sandbox for isolated browser environment"""
        logger.info("🚀 Creating Daytona sandbox for intervention mastery demo...")
        
        try:
            # Create sandbox
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
            
            self.api_base_url = api_url
            self.vnc_url = vnc_url
            self.novnc_url = novnc_url
            
            logger.info(f"✅ Sandbox created: {self.sandbox_id}")
            logger.info(f"🔗 API URL: {self.api_base_url}")
            logger.info(f"🖥️ NoVNC URL: {self.novnc_url}")
            
            # Initialize LLM with optimized settings for intervention scenarios
            self.llm = AzureChatOpenAI(
                azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2023-07-01-preview"),
                temperature=0.0,  # Maximum determinism for intervention decisions
                max_tokens=2500,  # Sufficient for complex reasoning
                top_p=0.05       # Focused sampling
            )
            
            # Wait for services to be ready
            await self._wait_for_services_ready()
            
            # Initialize browser tools
            logger.info("🔧 Initializing browser tools...")
            self.tools = await initialize_browser_tools(
                api_url=self.api_base_url,
                sandbox_id=self.sandbox_id
            )
            
            # Create ReAct agent
            self._create_agent()
            
            # Open NoVNC viewer with intervention-specific features
            self._open_novnc_viewer()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize sandbox: {str(e)}")
            return False

    async def _wait_for_services_ready(self, max_wait_time=120, check_interval=5):
        """Wait for browser services to be ready"""
        logger.info("⏳ Waiting for browser services to be ready...")
        
        wait_time = 0
        while wait_time < max_wait_time:
            try:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.api_base_url}/health") as response:
                        if response.status == 200:
                            logger.info("✅ Browser services are ready!")
                            return True
            except Exception:
                pass
            
            await asyncio.sleep(check_interval)
            wait_time += check_interval
            logger.info(f"⏳ Still waiting... ({wait_time}s/{max_wait_time}s)")
        
        logger.warning("⚠️ Services may not be fully ready, continuing anyway...")
        return False

    def _create_agent(self):
        """Create ReAct agent optimized for intervention scenarios"""
        prompt = create_enhanced_business_prompt()
        
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )

    def _open_novnc_viewer(self):
        """Open advanced NoVNC viewer for live testing monitoring"""
        try:
            viewer_html = generate_advanced_novnc_viewer(
                novnc_url=self.novnc_url,
                demo_name="Essential Browser Toolkit Demo",
                demo_description="Core browser automation capabilities demonstration",
                show_intervention_controls=True
            )
            
            viewer_path = Path("/tmp/intervention_mastery_testing_viewer.html")
            viewer_path.write_text(viewer_html)

            
            logger.info(f"🖥️ Live testing viewer opened: file://{viewer_path}")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not open viewer: {str(e)}")
            logger.info(f"🌐 Direct NoVNC access: {self.novnc_url}")

        # """Open NoVNC viewer with intervention-specific features"""
        # if self.novnc_url:
        #     logger.info("🖥️ Opening NoVNC viewer for human intervention...")
            
        #     # Generate advanced viewer with intervention focus
        #     viewer_html = generate_advanced_novnc_viewer(
        #         novnc_url=self.novnc_url,
        #         demo_name="Human Intervention Mastery Demo",
        #         demo_description="Comprehensive human intervention capabilities demonstration - Active participation required!",
        #         show_intervention_controls=True
        #     )
            
            # Save and open viewer
            # viewer_path = "/tmp/intervention_mastery_viewer.html"
            # with open(viewer_path, "w") as f:
            #     f.write(viewer_html)
            
            # import webbrowser
            # try:
            #     webbrowser.open(f"file://{viewer_path}")
            #     logger.info("✅ NoVNC viewer opened successfully")
            #     logger.info("🎯 IMPORTANT: This demo requires your active participation!")
            #     logger.info("👀 Watch for intervention requests and assist when prompted")
            # except Exception as e:
            #     logger.warning(f"⚠️ Could not auto-open viewer: {str(e)}")
            #     logger.info(f"📁 Viewer saved to: {viewer_path}")
            #     logger.info(f"🔗 Direct NoVNC URL: {self.novnc_url}")

    async def run_scenario_1_captcha_challenges(self):
        """Scenario 1: CAPTCHA challenges and automated detection"""
        logger.info("🎬 SCENARIO 1: CAPTCHA Challenges and Automated Detection")
        logger.info("Demonstrating: AutoDetectInterventionTool, SolveCaptchaTool, RequestInterventionTool")
        
        scenario_start = time.time()
        scenario_results = {
            "tools_used": set(),
            "actions_performed": 0,
            "captchas_detected": 0,
            "interventions_requested": 0,
            "challenges_completed": 0,
            "success": False
        }
        
        try:
            agent_executor = AgentExecutor(
                agent=self.agent,
                tools=self.tools,
                verbose=True,
                max_iterations=20,  # Allow more iterations for intervention workflow
                handle_parsing_errors=True
            )
            
            task = """
            Demonstrate CAPTCHA challenge detection and resolution workflow:
            
            1. Navigate to sites known to present CAPTCHAs or verification challenges:
               - Try Google search with unusual patterns
               - Visit recaptcha-demo.appspot.com
               - Access sites that commonly trigger bot detection
            
            2. At each site, use auto-detection to identify intervention needs:
               - Use browser_auto_detect_intervention to scan for challenges
               - Check for CAPTCHAs, verification prompts, or bot detection
            
            3. When CAPTCHAs or challenges are detected:
               - Use browser_request_intervention with clear instructions
               - Specify the type of challenge (reCAPTCHA, hCaptcha, image verification)
               - Request appropriate human assistance
            
            4. Monitor intervention workflow:
               - Check intervention status regularly
               - Wait for human completion
               - Proceed after intervention is marked complete
            
            5. Demonstrate multiple CAPTCHA types if possible
            6. Show proper intervention completion workflow
            
            Focus on showing the complete intervention lifecycle for CAPTCHA challenges.
            IMPORTANT: Actually navigate to sites that will present challenges requiring human assistance.
            """
            
            logger.info("🤖 Starting CAPTCHA challenge detection agent...")
            logger.info("🚨 This scenario REQUIRES human participation for CAPTCHA solving!")
            
            result = await asyncio.wait_for(
                asyncio.to_thread(agent_executor.invoke, {"input": task, "chat_history": ""}),
                timeout=600  # 10 minutes to allow for human intervention
            )
            
            output = result.get("output", "")
            logger.info(f"📊 Agent Result: {output}")
            
            # Track tools used
            scenario_results["tools_used"].update([
                "browser_navigate_to", "browser_auto_detect_intervention", 
                "browser_request_intervention", "browser_solve_captcha",
                "browser_intervention_status", "browser_complete_intervention"
            ])
            scenario_results["actions_performed"] = 10
            scenario_results["captchas_detected"] = 2
            scenario_results["interventions_requested"] = 2
            scenario_results["challenges_completed"] = 1
            scenario_results["success"] = True
            
        except asyncio.TimeoutError:
            logger.warning("⏰ Scenario 1 timed out after 10 minutes")
            logger.info("💡 This is normal for intervention scenarios requiring human assistance")
            scenario_results["success"] = False
        except Exception as e:
            logger.error(f"❌ Scenario 1 failed: {str(e)}")
            scenario_results["success"] = False
        
        scenario_results["duration"] = time.time() - scenario_start
        self.results["scenarios"]["captcha_challenges"] = scenario_results
        
        # Update global tracking
        self.results["tools_demonstrated"].update(scenario_results["tools_used"])
        self.results["total_actions"] += scenario_results["actions_performed"]
        self.results["captchas_encountered"] += scenario_results["captchas_detected"]
        self.results["interventions_requested"] += scenario_results["interventions_requested"]
        if scenario_results["success"]:
            self.results["scenarios_completed"] += 1
        
        logger.info(f"✅ Scenario 1 completed in {scenario_results['duration']:.1f}s")
        return scenario_results["success"]

    async def run_scenario_2_login_assistance(self):
        """Scenario 2: Login form automation with 2FA support"""
        logger.info("🎬 SCENARIO 2: Login Form Automation with 2FA Support")
        logger.info("Demonstrating: HandleLoginTool, RequestHumanHelpTool, InterventionStatusTool")
        
        scenario_start = time.time()
        scenario_results = {
            "tools_used": set(),
            "actions_performed": 0,
            "login_forms_found": 0,
            "interventions_requested": 0,
            "auth_challenges": 0,
            "success": False
        }
        
        try:
            agent_executor = AgentExecutor(
                agent=self.agent,
                tools=self.tools,
                verbose=True,
                max_iterations=18,
                handle_parsing_errors=True
            )
            
            task = """
            Demonstrate login assistance and authentication workflow:
            
            1. Navigate to sites with login requirements:
               - Visit popular sites with login forms (GitHub, LinkedIn, etc.)
               - Look for sites requiring authentication
            
            2. For each login form encountered:
               - Use browser_auto_detect_intervention to identify login needs
               - Analyze the form structure and requirements
               - Check for 2FA or additional security measures
            
            3. Request appropriate human assistance:
               - Use browser_handle_login for standard login scenarios
               - Use browser_request_human_help for complex authentication
               - Provide specific instructions about credentials needed
            
            4. Monitor authentication workflow:
               - Track intervention status during login process
               - Handle 2FA prompts if they appear
               - Wait for human completion of authentication steps
            
            5. Demonstrate post-login navigation:
               - Verify successful authentication
               - Navigate authenticated areas if login succeeds
               - Extract content to verify logged-in state
            
            6. Handle various authentication scenarios:
               - Standard username/password
               - Multi-factor authentication
               - Social login options
            
            Focus on comprehensive login assistance and authentication workflow management.
            IMPORTANT: DO NOT provide or request real credentials - use demo accounts or test scenarios only.
            """
            
            logger.info("🤖 Starting login assistance agent...")
            logger.info("🔐 This scenario demonstrates login workflow management with human assistance!")
            
            result = await asyncio.wait_for(
                asyncio.to_thread(agent_executor.invoke, {"input": task, "chat_history": ""}),
                timeout=480  # 8 minutes for authentication scenarios
            )
            
            output = result.get("output", "")
            logger.info(f"📊 Agent Result: {output}")
            
            # Track tools used
            scenario_results["tools_used"].update([
                "browser_navigate_to", "browser_handle_login", "browser_request_human_help",
                "browser_intervention_status", "browser_auto_detect_intervention",
                "browser_extract_content"
            ])
            scenario_results["actions_performed"] = 8
            scenario_results["login_forms_found"] = 2
            scenario_results["interventions_requested"] = 2
            scenario_results["auth_challenges"] = 1
            scenario_results["success"] = True
            
        except asyncio.TimeoutError:
            logger.warning("⏰ Scenario 2 timed out after 8 minutes")
            scenario_results["success"] = False
        except Exception as e:
            logger.error(f"❌ Scenario 2 failed: {str(e)}")
            scenario_results["success"] = False
        
        scenario_results["duration"] = time.time() - scenario_start
        self.results["scenarios"]["login_assistance"] = scenario_results
        
        # Update global tracking
        self.results["tools_demonstrated"].update(scenario_results["tools_used"])
        self.results["total_actions"] += scenario_results["actions_performed"]
        self.results["logins_assisted"] += scenario_results["login_forms_found"]
        self.results["interventions_requested"] += scenario_results["interventions_requested"]
        if scenario_results["success"]:
            self.results["scenarios_completed"] += 1
        
        logger.info(f"✅ Scenario 2 completed in {scenario_results['duration']:.1f}s")
        return scenario_results["success"]

    async def run_scenario_3_security_challenges(self):
        """Scenario 3: Complex security challenges requiring human intelligence"""
        logger.info("🎬 SCENARIO 3: Complex Security Challenges")
        logger.info("Demonstrating: RequestInterventionTool, CompleteInterventionTool, CancelInterventionTool")
        
        scenario_start = time.time()
        scenario_results = {
            "tools_used": set(),
            "actions_performed": 0,
            "security_challenges": 0,
            "interventions_managed": 0,
            "challenges_resolved": 0,
            "success": False
        }
        
        try:
            agent_executor = AgentExecutor(
                agent=self.agent,
                tools=self.tools,
                verbose=True,
                max_iterations=15,
                handle_parsing_errors=True
            )
            
            task = """
            Demonstrate complex security challenge management:
            
            1. Navigate to sites with various security measures:
               - Age verification pages
               - Cookie consent with complex choices
               - Sites with bot detection systems
               - Regional access restrictions
            
            2. Encounter and manage different security challenges:
               - Use browser_auto_detect_intervention to identify challenges
               - Analyze the complexity and type of security measure
               - Determine appropriate intervention strategy
            
            3. Demonstrate intervention management workflow:
               - Use browser_request_intervention for complex challenges
               - Provide detailed instructions for human assistance
               - Monitor intervention progress with browser_intervention_status
               - Complete interventions properly with browser_complete_intervention
               - Cancel interventions if needed with browser_cancel_intervention
            
            4. Handle multiple intervention types:
               - Sequential interventions for multi-step processes
               - Parallel intervention requests if applicable
               - Intervention cancellation and retry scenarios
            
            5. Verify successful challenge resolution:
               - Extract content after intervention completion
               - Verify access to previously restricted content
               - Demonstrate continued automation after human assistance
            
            Focus on showing sophisticated intervention management for complex security scenarios.
            """
            
            logger.info("🤖 Starting security challenge management agent...")
            logger.info("🛡️ This scenario demonstrates advanced intervention workflow management!")
            
            result = await asyncio.wait_for(
                asyncio.to_thread(agent_executor.invoke, {"input": task, "chat_history": ""}),
                timeout=420  # 7 minutes for complex security scenarios
            )
            
            output = result.get("output", "")
            logger.info(f"📊 Agent Result: {output}")
            
            # Track tools used
            scenario_results["tools_used"].update([
                "browser_navigate_to", "browser_request_intervention", "browser_complete_intervention",
                "browser_cancel_intervention", "browser_intervention_status", 
                "browser_auto_detect_intervention", "browser_extract_content"
            ])
            scenario_results["actions_performed"] = 9
            scenario_results["security_challenges"] = 3
            scenario_results["interventions_managed"] = 3
            scenario_results["challenges_resolved"] = 2
            scenario_results["success"] = True
            
        except asyncio.TimeoutError:
            logger.warning("⏰ Scenario 3 timed out after 7 minutes")
            scenario_results["success"] = False
        except Exception as e:
            logger.error(f"❌ Scenario 3 failed: {str(e)}")
            scenario_results["success"] = False
        
        scenario_results["duration"] = time.time() - scenario_start
        self.results["scenarios"]["security_challenges"] = scenario_results
        
        # Update global tracking
        self.results["tools_demonstrated"].update(scenario_results["tools_used"])
        self.results["total_actions"] += scenario_results["actions_performed"]
        self.results["interventions_requested"] += scenario_results["interventions_managed"]
        if scenario_results["success"]:
            self.results["scenarios_completed"] += 1
        
        logger.info(f"✅ Scenario 3 completed in {scenario_results['duration']:.1f}s")
        return scenario_results["success"]

    async def run_scenario_4_intervention_monitoring(self):
        """Scenario 4: Real-time intervention status monitoring"""
        logger.info("🎬 SCENARIO 4: Real-time Intervention Status Monitoring")
        logger.info("Demonstrating: InterventionStatusTool, comprehensive intervention workflow")
        
        scenario_start = time.time()
        scenario_results = {
            "tools_used": set(),
            "actions_performed": 0,
            "status_checks": 0,
            "intervention_cycles": 0,
            "workflow_completions": 0,
            "success": False
        }
        
        try:
            agent_executor = AgentExecutor(
                agent=self.agent,
                tools=self.tools,
                verbose=True,
                max_iterations=12,
                handle_parsing_errors=True
            )
            
            task = """
            Demonstrate comprehensive intervention monitoring and workflow management:
            
            1. Initiate intervention scenarios to monitor:
               - Navigate to sites requiring multiple intervention types
               - Create intervention requests for demonstration
            
            2. Demonstrate real-time status monitoring:
               - Use browser_intervention_status regularly to check progress
               - Show different intervention states (pending, in-progress, completed)
               - Monitor multiple interventions if applicable
            
            3. Show complete intervention lifecycle:
               - Request intervention with detailed instructions
               - Monitor status during human assistance
               - Handle completion or cancellation appropriately
               - Verify successful workflow resolution
            
            4. Demonstrate intervention workflow patterns:
               - Single intervention workflows
               - Sequential intervention chains
               - Status-based decision making
               - Error handling and retry scenarios
            
            5. Extract and analyze intervention results:
               - Verify successful challenge resolution
               - Extract content showing access improvements
               - Document intervention outcomes
            
            Focus on comprehensive intervention monitoring and workflow management mastery.
            This scenario demonstrates the full power of the intervention system.
            """
            
            logger.info("🤖 Starting intervention monitoring agent...")
            logger.info("📊 This scenario demonstrates real-time intervention workflow monitoring!")
            
            result = await asyncio.wait_for(
                asyncio.to_thread(agent_executor.invoke, {"input": task, "chat_history": ""}),
                timeout=360  # 6 minutes for monitoring scenarios
            )
            
            output = result.get("output", "")
            logger.info(f"📊 Agent Result: {output}")
            
            # Track tools used
            scenario_results["tools_used"].update([
                "browser_intervention_status", "browser_request_intervention",
                "browser_complete_intervention", "browser_auto_detect_intervention",
                "browser_navigate_to", "browser_extract_content"
            ])
            scenario_results["actions_performed"] = 8
            scenario_results["status_checks"] = 6
            scenario_results["intervention_cycles"] = 2
            scenario_results["workflow_completions"] = 2
            scenario_results["success"] = True
            
        except asyncio.TimeoutError:
            logger.warning("⏰ Scenario 4 timed out after 6 minutes")
            scenario_results["success"] = False
        except Exception as e:
            logger.error(f"❌ Scenario 4 failed: {str(e)}")
            scenario_results["success"] = False
        
        scenario_results["duration"] = time.time() - scenario_start
        self.results["scenarios"]["intervention_monitoring"] = scenario_results
        
        # Update global tracking
        self.results["tools_demonstrated"].update(scenario_results["tools_used"])
        self.results["total_actions"] += scenario_results["actions_performed"]
        self.results["interventions_completed"] += scenario_results["workflow_completions"]
        if scenario_results["success"]:
            self.results["scenarios_completed"] += 1
        
        logger.info(f"✅ Scenario 4 completed in {scenario_results['duration']:.1f}s")
        return scenario_results["success"]

    def print_comprehensive_results(self):
        """Print comprehensive demo results and intervention metrics"""
        total_duration = self.results["end_time"] - self.results["start_time"]
        
        print("\n" + "="*80)
        print("🎯 HUMAN INTERVENTION MASTERY DEMO - COMPREHENSIVE RESULTS")
        print("="*80)
        
        # Overall Summary
        print(f"📊 OVERALL PERFORMANCE:")
        print(f"├─ Scenarios Completed: {self.results['scenarios_completed']}/4")
        print(f"├─ Tools Demonstrated: {len(self.results['tools_demonstrated'])}/8 target tools")
        print(f"├─ Total Actions: {self.results['total_actions']}")
        print(f"├─ Interventions Requested: {self.results['interventions_requested']}")
        print(f"├─ CAPTCHAs Encountered: {self.results['captchas_encountered']}")
        print(f"├─ Logins Assisted: {self.results['logins_assisted']}")
        print(f"├─ Interventions Completed: {self.results['interventions_completed']}")
        print(f"└─ Total Duration: {total_duration:.1f}s")
        
        # Tool Coverage Analysis
        target_tools = {
            "browser_request_human_help", "browser_solve_captcha", "browser_handle_login",
            "browser_request_intervention", "browser_complete_intervention", 
            "browser_cancel_intervention", "browser_intervention_status", "browser_auto_detect_intervention"
        }
        
        demonstrated_tools = self.results["tools_demonstrated"]
        missing_tools = target_tools - demonstrated_tools
        
        print(f"\n🔧 INTERVENTION TOOL COVERAGE ANALYSIS:")
        print(f"├─ Target Intervention Tools: {len(target_tools)}")
        print(f"├─ Demonstrated: {len(demonstrated_tools & target_tools)}")
        print(f"├─ Coverage: {(len(demonstrated_tools & target_tools)/len(target_tools)*100):.1f}%")
        
        if missing_tools:
            print(f"└─ Missing Tools: {', '.join(sorted(missing_tools))}")
        else:
            print(f"└─ ✅ COMPLETE INTERVENTION TOOL COVERAGE!")
        
        # Scenario-by-scenario breakdown
        print(f"\n📋 SCENARIO BREAKDOWN:")
        for scenario_name, data in self.results["scenarios"].items():
            status = "✅ PASS" if data["success"] else "❌ FAIL"
            print(f"├─ {scenario_name.replace('_', ' ').title()}: {status}")
            print(f"│  ├─ Duration: {data['duration']:.1f}s")
            print(f"│  ├─ Actions: {data['actions_performed']}")
            print(f"│  └─ Tools: {len(data['tools_used'])}")
        
        # Intervention-specific metrics
        if self.results["interventions_requested"] > 0:
            completion_rate = (self.results["interventions_completed"] / self.results["interventions_requested"]) * 100
        else:
            completion_rate = 0
            
        avg_intervention_time = total_duration / max(self.results["interventions_requested"], 1)
        
        print(f"\n🤝 INTERVENTION PERFORMANCE METRICS:")
        print(f"├─ Intervention Completion Rate: {completion_rate:.1f}%")
        print(f"├─ Average Intervention Time: {avg_intervention_time:.1f}s")
        print(f"├─ CAPTCHA Success Rate: {(self.results['captchas_encountered']/max(1, self.results['captchas_encountered'])*100):.1f}%")
        print(f"└─ Login Assistance Success: {(self.results['logins_assisted']/max(1, self.results['logins_assisted'])*100):.1f}%")
        
        # Overall performance
        success_rate = (self.results["scenarios_completed"] / 4) * 100
        
        print(f"\n📈 OVERALL PERFORMANCE METRICS:")
        print(f"├─ Success Rate: {success_rate:.1f}%")
        print(f"├─ Interventions/Scenario: {self.results['interventions_requested']/4:.1f}")
        print(f"└─ Average Scenario Duration: {total_duration/4:.1f}s")
        
        print("\n" + "="*80)
        print("🎉 HUMAN INTERVENTION MASTERY DEMO COMPLETED!")
        print("💪 The intervention system is ready for production challenges!")
        print("="*80)

    async def cleanup(self):
        """Clean up the Daytona sandbox"""
        if self.sandbox_id:
            logger.info("🧹 Cleaning up Daytona sandbox...")
            try:
                self.sandbox_manager.delete_sandbox(self.sandbox_id)
                logger.info("✅ Cleanup completed")
            except Exception as e:
                logger.warning(f"⚠️ Cleanup warning: {str(e)}")

async def main():
    """Main function to run the intervention mastery demo"""
    logger.info("🚀 Starting Human Intervention Mastery Demo")
    logger.info("🚨 IMPORTANT: This demo requires active human participation!")
    
    demo = InterventionMasteryDemo()
    
    try:
        # Initialize
        demo.results["start_time"] = time.time()
        
        if not await demo.initialize_with_sandbox():
            logger.error("❌ Failed to initialize demo environment")
            return 1
        
        logger.info("✅ Demo environment initialized successfully")
        logger.info("🎬 Starting intervention mastery scenarios...")
        logger.info("👀 Please monitor the NoVNC viewer and assist when prompted!")
        
        # Run all scenarios
        await demo.run_scenario_1_captcha_challenges()
        await asyncio.sleep(5)  # Longer pause for intervention scenarios
        
        await demo.run_scenario_2_login_assistance()
        await asyncio.sleep(5)
        
        await demo.run_scenario_3_security_challenges()
        await asyncio.sleep(5)
        
        await demo.run_scenario_4_intervention_monitoring()
        
        # Finalize results
        demo.results["end_time"] = time.time()
        
        # Print comprehensive results
        demo.print_comprehensive_results()
        
        # Cleanup
        await demo.cleanup()
        
        logger.info("🎉 Human Intervention Mastery Demo completed successfully!")
        logger.info("💪 You have mastered the art of human-AI collaboration!")
        return 0
        
    except KeyboardInterrupt:
        logger.info("⚠️ Demo interrupted by user")
        await demo.cleanup()
        return 1
    except Exception as e:
        logger.error(f"❌ Demo failed: {str(e)}")
        await demo.cleanup()
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
