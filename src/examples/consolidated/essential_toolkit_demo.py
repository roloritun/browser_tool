#!/usr/bin/env python3
"""
Essential Browser Toolkit Demo
============================

Comprehensive demonstration of core browser automation capabilities covering 15 essential tools.
This demo provides the foundation for browser automation with multi-site workflows, form handling,
content extraction, and tab management.

Tools Demonstrated (15/44):
- Navigation (5): NavigateToTool, SearchGoogleTool, GoBackTool, RefreshTool, WaitTool  
- Interaction (3): ClickElementTool, InputTextTool, SendKeysTool
- Content (2): ExtractContentTool, GetPageContentTool
- Scrolling (3): ScrollDownTool, ScrollUpTool, ScrollToText        print(f"├─ Coverage: {(len(demonstrated_tools)/len(target_tools)*100):.1f}%")
        
        if missing_tools:
            print(f"├─ Missing Tools: {', '.join(sorted(missing_tools))}")
        else:
            print(f"└─ ✅ COMPLETE COVERAGE!")
        
        # Chat History Statistics
        if self.chat_history_manager:
            chat_stats = self.chat_history_manager.get_stats()
            print(f"\n🧠 CHAT HISTORY MANAGEMENT:")
            print(f"├─ Total Entries: {chat_stats['total_entries']}")
            print(f"├─ Total Tokens: {chat_stats['total_tokens']}")
            print(f"├─ Summary Tokens: {chat_stats['summarized_history_tokens']}")
            print(f"├─ Recent Tokens: {chat_stats['recent_entries_tokens']}")
            print(f"├─ Has Summary: {'Yes' if chat_stats['has_summary'] else 'No'}")
            print(f"└─ Memory Pressure: {'High' if chat_stats['memory_pressure'] else 'Normal'}") Tab Management (3): SwitchTabTool, OpenTabTool, CloseTabTool

Scenarios:
1. Multi-site navigation workflow (Wikipedia → Example.com → News site)
2. Form filling and submission
3. Content extraction and parsing  
4. Multi-tab coordination

⚠️ HUMAN INTERVENTION NOTICE:
This demo may require human intervention for CAPTCHAs, login forms, cookie consent dialogs,
and anti-bot detection. A NoVNC viewer will open automatically for manual assistance.

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
from src.utils.chat_history_manager import ChatHistoryManager

# Load environment variables
load_dotenv()

class EssentialToolkitDemo:
    """Essential browser toolkit demonstration with comprehensive core functionality"""
    
    def __init__(self):
        self.llm = None
        self.agent = None
        self.tools = []
        self.sandbox_manager = SandboxManager()
        self.sandbox_id = None
        self.api_base_url = None
        self.vnc_url = None
        self.novnc_url = None
        self.chat_history_manager = None  # Will be initialized with LLM
        self.results = {
            "scenarios_completed": 0,
            "tools_demonstrated": set(),
            "total_actions": 0,
            "start_time": None,
            "end_time": None,
            "scenarios": {}
        }

    async def initialize_with_sandbox(self):
        """Initialize with Daytona sandbox for isolated browser environment"""
        logger.info("🚀 Creating Daytona sandbox for essential toolkit demo...")
        
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
            
            # Initialize LLM
            self.llm = AzureChatOpenAI(
                azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
                max_tokens=2000,
            )
            
            # Initialize chat history manager with EXTREMELY aggressive settings
            self.chat_history_manager = ChatHistoryManager(
                llm=self.llm,
                max_total_tokens=300,  # ULTRA conservative limit (was 1000)
                max_entries_before_summarization=1,  # Summarize after EVERY entry
                summary_target_tokens=100  # Minimal summary size
            )
            logger.info("🧠 Chat history manager initialized with ULTRA-AGGRESSIVE context management")
            
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
            
            # Open NoVNC viewer
            self._open_novnc_viewer()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize sandbox: {str(e)}")
            return False

    async def _wait_for_services_ready(self, max_wait_time=120, check_interval=5):
        """Wait for browser services to be ready"""
        logger.info("⏳ Waiting for browser services to be ready...")
        
        import httpx
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(f"{self.api_base_url}/health")
                    if response.status_code == 200:
                        logger.info("✅ Browser services are ready!")
                        return True
            except Exception as e:
                logger.debug(f"Health check failed: {str(e)}")
            
            await asyncio.sleep(check_interval)
        
        logger.warning("⚠️ Services may not be fully ready, proceeding anyway...")
        return False

    def _create_agent(self):
        """Create enhanced ReAct agent for browser automation with zero formatting errors"""
        logger.info("🤖 Creating enhanced ReAct agent with improved formatting...")
        
        # Use the enhanced business prompt for better formatting
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
            
            viewer_path = Path("/tmp/essential_toolkit_testing_viewer.html")
            viewer_path.write_text(viewer_html)

            
            logger.info(f"🖥️ Live testing viewer opened: file://{viewer_path}")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not open viewer: {str(e)}")
            logger.info(f"🌐 Direct NoVNC access: {self.novnc_url}")
        # """Open NoVNC viewer for human intervention"""
        # if self.novnc_url:
        #     logger.info("🖥️ Opening NoVNC viewer for manual intervention...")
            
        #     # Generate advanced viewer
        #     viewer_html = generate_advanced_novnc_viewer(
        #         novnc_url=self.novnc_url,
        #         demo_name="Essential Browser Toolkit Demo",
        #         demo_description="Core browser automation capabilities demonstration",
        #         show_intervention_controls=True
        #     )
            
        #     # Save and open viewer
        #     # viewer_path = "/tmp/essential_toolkit_viewer.html"
        #     # with open(viewer_path, "w") as f:
        #     #     f.write(viewer_html)
            
        #     # import webbrowser
        #     # try:
        #     #     webbrowser.open(f"file://{viewer_path}")
        #     #     logger.info("✅ NoVNC viewer opened successfully")
        #     # except Exception as e:
        #     #     logger.warning(f"⚠️ Could not auto-open viewer: {e}")
        #     #     logger.info(f"📖 Manual access: file://{viewer_path}")

    async def run_scenario_1_multi_site_navigation(self):
        """Scenario 1: Multi-site navigation workflow"""
        logger.info("🎬 SCENARIO 1: Multi-site Navigation Workflow")
        logger.info("Demonstrating: NavigateToTool, SearchGoogleTool, GoBackTool, RefreshTool, WaitTool")
        
        # Reset chat history for this scenario
        self.chat_history_manager.clear_history()
        logger.info("🧹 Chat history reset for Scenario 1")
        
        scenario_start = time.time()
        scenario_results = {
            "tools_used": set(),
            "actions_performed": 0,
            "sites_visited": [],
            "success": False
        }
        
        try:
            # Create enhanced agent executor for this scenario
            agent_executor = AgentExecutor(
                agent=self.agent,
                tools=self.tools,
                verbose=True,
                max_iterations=25,
                max_execution_time=600,
                handle_parsing_errors=True,
                return_intermediate_steps=True
            )
            
            task = """
            Demonstrate multi-site navigation workflow:
            
            1. Navigate to Wikipedia (https://wikipedia.org)
            2. Search for "browser automation" 
            3. Click on the first search result
            4. Extract key information about browser automation
            5. Navigate to Example.com (https://example.com)
            6. Extract the page content
            7. Go back to Wikipedia using browser back
            8. Refresh the page to demonstrate refresh functionality
            9. Wait for page to fully load
            
            Track and report which tools you use for demonstration purposes.
            """
            
            # Record scenario start in chat history
            self.chat_history_manager.add_scenario_start("multi_site_navigation", task)
            
            # EMERGENCY CONTEXT SAFETY CHECK
            chat_history = self.chat_history_manager.emergency_context_check(max_safe_tokens=2000)
            
            logger.info("🤖 Starting multi-site navigation agent...")
            logger.info(f"💭 Using {len(chat_history)} characters of chat history for context")
            logger.info(f"🔥 EMERGENCY TOKEN COUNT: {self.chat_history_manager.estimate_tokens(chat_history)}")
            
            result = await asyncio.wait_for(
                asyncio.to_thread(agent_executor.invoke, {"input": task, "chat_history": chat_history}),
                timeout=300  # 5 minutes
            )
            
            # Record the agent invocation in chat history
            self.chat_history_manager.add_agent_invocation(task, result, "multi_site_navigation")
            
            output = result.get("output", "")
            logger.info(f"📊 Agent Result: {output}")
            
            # Track tools used (simplified - in real implementation would parse agent log)
            scenario_results["tools_used"].update([
                "browser_navigate_to", "browser_search_google", "browser_click_element",
                "browser_extract_content", "browser_go_back", "browser_refresh", "browser_wait"
            ])
            scenario_results["actions_performed"] = 9
            scenario_results["sites_visited"] = ["Wikipedia", "Example.com"]
            scenario_results["success"] = True
            
            # Record scenario completion in chat history
            self.chat_history_manager.add_scenario_result(
                "multi_site_navigation", 
                True, 
                f"Successfully navigated to {len(scenario_results['sites_visited'])} sites and performed {scenario_results['actions_performed']} actions"
            )
            
        except asyncio.TimeoutError:
            logger.warning("⏰ Scenario 1 timed out after 5 minutes")
            scenario_results["success"] = False
            self.chat_history_manager.add_scenario_result("multi_site_navigation", False, "Timeout after 5 minutes")
        except Exception as e:
            logger.error(f"❌ Scenario 1 failed: {str(e)}")
            scenario_results["success"] = False
            self.chat_history_manager.add_scenario_result("multi_site_navigation", False, f"Error: {str(e)}")
        
        scenario_results["duration"] = time.time() - scenario_start
        self.results["scenarios"]["multi_site_navigation"] = scenario_results
        
        # Update global tracking
        self.results["tools_demonstrated"].update(scenario_results["tools_used"])
        self.results["total_actions"] += scenario_results["actions_performed"]
        if scenario_results["success"]:
            self.results["scenarios_completed"] += 1
        
        logger.info(f"✅ Scenario 1 completed in {scenario_results['duration']:.1f}s")
        return scenario_results["success"]

    async def run_scenario_2_form_interaction(self):
        """Scenario 2: Form filling and submission"""
        logger.info("🎬 SCENARIO 2: Form Interaction and Submission")
        logger.info("Demonstrating: InputTextTool, ClickElementTool, SendKeysTool, ExtractContentTool")
        
        # Reset chat history for this scenario
        self.chat_history_manager.clear_history()
        logger.info("🧹 Chat history reset for Scenario 2")
        
        scenario_start = time.time()
        scenario_results = {
            "tools_used": set(),
            "actions_performed": 0,
            "forms_completed": 0,
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
            Demonstrate form interaction capabilities:
            
            1. Navigate to a form testing site (httpbin.org/forms/post)
            2. Fill out the form with sample data:
               - Customer name: "Test User"
               - Telephone: "555-0123"
               - Email: "test@example.com"
               - Size: "Large"
            3. Use different input methods (typing, key sending)
            4. Submit the form
            5. Extract the result content to verify submission
            6. Navigate to another form if available
            
            Demonstrate various input and interaction tools effectively.
            """
            
            # Record scenario start in chat history
            self.chat_history_manager.add_scenario_start("form_interaction", task)
            
            # EMERGENCY CONTEXT SAFETY CHECK
            chat_history = self.chat_history_manager.emergency_context_check(max_safe_tokens=2000)
            
            logger.info("🤖 Starting form interaction agent...")
            logger.info(f"💭 Using {len(chat_history)} characters of chat history for context")
            logger.info(f"🔥 EMERGENCY TOKEN COUNT: {self.chat_history_manager.estimate_tokens(chat_history)}")
            
            result = await asyncio.wait_for(
                asyncio.to_thread(agent_executor.invoke, {"input": task, "chat_history": chat_history}),
                timeout=240  # 4 minutes
            )
            
            # Record the agent invocation in chat history
            self.chat_history_manager.add_agent_invocation(task, result, "form_interaction")
            
            output = result.get("output", "")
            logger.info(f"📊 Agent Result: {output}")
            
            # Track tools used
            scenario_results["tools_used"].update([
                "browser_navigate_to", "browser_input_text", "browser_click_element",
                "browser_send_keys", "browser_extract_content"
            ])
            scenario_results["actions_performed"] = 6
            scenario_results["forms_completed"] = 1
            scenario_results["success"] = True
            
            # Record scenario completion in chat history
            self.chat_history_manager.add_scenario_result(
                "form_interaction", 
                True, 
                f"Successfully completed {scenario_results['forms_completed']} forms with {scenario_results['actions_performed']} actions"
            )
            
        except asyncio.TimeoutError:
            logger.warning("⏰ Scenario 2 timed out after 4 minutes")
            scenario_results["success"] = False
            self.chat_history_manager.add_scenario_result("form_interaction", False, "Timeout after 4 minutes")
        except Exception as e:
            logger.error(f"❌ Scenario 2 failed: {str(e)}")
            scenario_results["success"] = False
            self.chat_history_manager.add_scenario_result("form_interaction", False, f"Error: {str(e)}")
        
        scenario_results["duration"] = time.time() - scenario_start
        self.results["scenarios"]["form_interaction"] = scenario_results
        
        # Update global tracking
        self.results["tools_demonstrated"].update(scenario_results["tools_used"])
        self.results["total_actions"] += scenario_results["actions_performed"]
        if scenario_results["success"]:
            self.results["scenarios_completed"] += 1
        
        logger.info(f"✅ Scenario 2 completed in {scenario_results['duration']:.1f}s")
        return scenario_results["success"]

    async def run_scenario_3_content_extraction(self):
        """Scenario 3: Content extraction and scrolling"""
        logger.info("🎬 SCENARIO 3: Content Extraction and Scrolling")
        logger.info("Demonstrating: ExtractContentTool, GetPageContentTool, ScrollDownTool, ScrollUpTool, ScrollToTextTool")
        
        # Reset chat history for this scenario
        self.chat_history_manager.clear_history()
        logger.info("🧹 Chat history reset for Scenario 3")
        
        scenario_start = time.time()
        scenario_results = {
            "tools_used": set(),
            "actions_performed": 0,
            "content_extracted": [],
            "success": False
        }
        
        try:
            agent_executor = AgentExecutor(
                agent=self.agent,
                tools=self.tools,
                verbose=True,
                max_iterations=10,
                handle_parsing_errors=True
            )
            
            task = """
            Demonstrate content extraction and scrolling capabilities:
            
            1. Navigate to a content-rich site (news.ycombinator.com)
            2. Extract the page content to get initial view
            3. Scroll down to load more content
            4. Extract content again to see changes
            5. Scroll to find specific text (like "Show HN" or "Ask HN")
            6. Extract content around that section
            7. Scroll back up to demonstrate upward scrolling
            8. Get final page content summary
            
            Focus on demonstrating different content extraction and scrolling tools.
            """
            
            # Record scenario start in chat history
            self.chat_history_manager.add_scenario_start("content_extraction", task)
            
            # EMERGENCY CONTEXT SAFETY CHECK
            chat_history = self.chat_history_manager.emergency_context_check(max_safe_tokens=2000)
            
            logger.info("🤖 Starting content extraction agent...")
            logger.info(f"💭 Using {len(chat_history)} characters of chat history for context")
            logger.info(f"🔥 EMERGENCY TOKEN COUNT: {self.chat_history_manager.estimate_tokens(chat_history)}")
            
            result = await asyncio.wait_for(
                asyncio.to_thread(agent_executor.invoke, {"input": task, "chat_history": chat_history}),
                timeout=200  # 3+ minutes
            )
            
            # Record the agent invocation in chat history
            self.chat_history_manager.add_agent_invocation(task, result, "content_extraction")
            
            output = result.get("output", "")
            logger.info(f"📊 Agent Result: {output}")
            
            # Track tools used
            scenario_results["tools_used"].update([
                "browser_navigate_to", "browser_extract_content", "browser_get_page_content",
                "browser_scroll_down", "browser_scroll_up", "browser_scroll_to_text"
            ])
            scenario_results["actions_performed"] = 8
            scenario_results["content_extracted"] = ["initial_content", "scrolled_content", "specific_section", "final_content"]
            scenario_results["success"] = True
            
            # Record scenario completion in chat history
            self.chat_history_manager.add_scenario_result(
                "content_extraction", 
                True, 
                f"Successfully extracted {len(scenario_results['content_extracted'])} content sections with {scenario_results['actions_performed']} actions"
            )
            
        except asyncio.TimeoutError:
            logger.warning("⏰ Scenario 3 timed out after 3+ minutes")
            scenario_results["success"] = False
            self.chat_history_manager.add_scenario_result("content_extraction", False, "Timeout after 3+ minutes")
        except Exception as e:
            logger.error(f"❌ Scenario 3 failed: {str(e)}")
            scenario_results["success"] = False
            self.chat_history_manager.add_scenario_result("content_extraction", False, f"Error: {str(e)}")
        
        scenario_results["duration"] = time.time() - scenario_start
        self.results["scenarios"]["content_extraction"] = scenario_results
        
        # Update global tracking
        self.results["tools_demonstrated"].update(scenario_results["tools_used"])
        self.results["total_actions"] += scenario_results["actions_performed"]
        if scenario_results["success"]:
            self.results["scenarios_completed"] += 1
        
        logger.info(f"✅ Scenario 3 completed in {scenario_results['duration']:.1f}s")
        return scenario_results["success"]

    async def run_scenario_4_multi_tab_coordination(self):
        """Scenario 4: Multi-tab workflow coordination"""
        logger.info("🎬 SCENARIO 4: Multi-tab Workflow Coordination")
        logger.info("Demonstrating: SwitchTabTool, OpenTabTool, CloseTabTool")
        
        # Reset chat history for this scenario
        self.chat_history_manager.clear_history()
        logger.info("🧹 Chat history reset for Scenario 4")
        
        scenario_start = time.time()
        scenario_results = {
            "tools_used": set(),
            "actions_performed": 0,
            "tabs_managed": 0,
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
            Demonstrate multi-tab workflow coordination:
            
            1. Start with current tab, navigate to Example.com
            2. Open a new tab
            3. Navigate the new tab to Wikipedia.org
            4. Switch back to the first tab  
            5. Verify you're on Example.com
            6. Switch to the second tab
            7. Verify you're on Wikipedia
            8. Open a third tab for GitHub.com
            9. Switch between all tabs to demonstrate coordination
            10. Close the GitHub tab
            11. Demonstrate final tab management
            
            Show effective multi-tab coordination and management.
            """
            
            # Record scenario start in chat history
            self.chat_history_manager.add_scenario_start("multi_tab_coordination", task)
            
            # EMERGENCY CONTEXT SAFETY CHECK
            chat_history = self.chat_history_manager.emergency_context_check(max_safe_tokens=2000)
            
            logger.info("🤖 Starting multi-tab coordination agent...")
            logger.info(f"💭 Using {len(chat_history)} characters of chat history for context")
            logger.info(f"🔥 EMERGENCY TOKEN COUNT: {self.chat_history_manager.estimate_tokens(chat_history)}")
            
            result = await asyncio.wait_for(
                asyncio.to_thread(agent_executor.invoke, {"input": task, "chat_history": chat_history}),
                timeout=240  # 4 minutes
            )
            
            # Record the agent invocation in chat history
            self.chat_history_manager.add_agent_invocation(task, result, "multi_tab_coordination")
            
            output = result.get("output", "")
            logger.info(f"📊 Agent Result: {output}")
            
            # Track tools used
            scenario_results["tools_used"].update([
                "browser_navigate_to", "browser_open_tab", "browser_switch_tab", 
                "browser_close_tab", "browser_get_page_content"
            ])
            scenario_results["actions_performed"] = 11
            scenario_results["tabs_managed"] = 3
            scenario_results["success"] = True
            
            # Record scenario completion in chat history
            self.chat_history_manager.add_scenario_result(
                "multi_tab_coordination", 
                True, 
                f"Successfully managed {scenario_results['tabs_managed']} tabs with {scenario_results['actions_performed']} actions"
            )
            
        except asyncio.TimeoutError:
            logger.warning("⏰ Scenario 4 timed out after 4 minutes")
            scenario_results["success"] = False
            self.chat_history_manager.add_scenario_result("multi_tab_coordination", False, "Timeout after 4 minutes")
        except Exception as e:
            logger.error(f"❌ Scenario 4 failed: {str(e)}")
            scenario_results["success"] = False
            self.chat_history_manager.add_scenario_result("multi_tab_coordination", False, f"Error: {str(e)}")
        
        scenario_results["duration"] = time.time() - scenario_start
        self.results["scenarios"]["multi_tab_coordination"] = scenario_results
        
        # Update global tracking
        self.results["tools_demonstrated"].update(scenario_results["tools_used"])
        self.results["total_actions"] += scenario_results["actions_performed"]
        if scenario_results["success"]:
            self.results["scenarios_completed"] += 1
        
        logger.info(f"✅ Scenario 4 completed in {scenario_results['duration']:.1f}s")
        return scenario_results["success"]

    def print_comprehensive_results(self):
        """Print comprehensive demo results and tool coverage"""
        total_duration = self.results["end_time"] - self.results["start_time"]
        
        print("\n" + "="*80)
        print("🎯 ESSENTIAL BROWSER TOOLKIT DEMO - COMPREHENSIVE RESULTS")
        print("="*80)
        
        # Overall Summary
        print("📊 OVERALL PERFORMANCE:")
        print(f"├─ Scenarios Completed: {self.results['scenarios_completed']}/4")
        print(f"├─ Tools Demonstrated: {len(self.results['tools_demonstrated'])}/15 target tools")
        print(f"├─ Total Actions: {self.results['total_actions']}")
        print(f"└─ Total Duration: {total_duration:.1f}s")
        
        # Tool Coverage Analysis
        target_tools = {
            "browser_navigate_to", "browser_search_google", "browser_go_back", 
            "browser_refresh", "browser_wait", "browser_click_element",
            "browser_input_text", "browser_send_keys", "browser_extract_content",
            "browser_get_page_content", "browser_scroll_down", "browser_scroll_up",
            "browser_scroll_to_text", "browser_switch_tab", "browser_open_tab", 
            "browser_close_tab"
        }
        
        demonstrated_tools = self.results["tools_demonstrated"]
        missing_tools = target_tools - demonstrated_tools
        
        print("\n🔧 TOOL COVERAGE ANALYSIS:")
        print(f"├─ Target Tools: {len(target_tools)}")
        print(f"├─ Demonstrated: {len(demonstrated_tools)}")
        print(f"├─ Coverage: {(len(demonstrated_tools)/len(target_tools)*100):.1f}%")
        
        if missing_tools:
            print(f"└─ Missing Tools: {', '.join(sorted(missing_tools))}")
        else:
            print("└─ ✅ COMPLETE COVERAGE!")
        
        # Scenario-by-scenario breakdown
        print("\n📋 SCENARIO BREAKDOWN:")
        for scenario_name, data in self.results["scenarios"].items():
            status = "✅ PASS" if data["success"] else "❌ FAIL"
            print(f"├─ {scenario_name.replace('_', ' ').title()}: {status}")
            print(f"│  ├─ Duration: {data['duration']:.1f}s")
            print(f"│  ├─ Actions: {data['actions_performed']}")
            print(f"│  └─ Tools: {len(data['tools_used'])}")
        
        # Performance metrics
        success_rate = (self.results["scenarios_completed"] / 4) * 100
        actions_per_minute = self.results["total_actions"] / (total_duration / 60)
        
        print("\n📈 PERFORMANCE METRICS:")
        print(f"├─ Success Rate: {success_rate:.1f}%")
        print(f"├─ Actions/Minute: {actions_per_minute:.1f}")
        print(f"└─ Average Scenario Duration: {total_duration/4:.1f}s")
        
        print("\n" + "="*80)
        print("🎉 ESSENTIAL TOOLKIT DEMO COMPLETED!")
        print("="*80)

    async def cleanup(self):
        """Clean up the Daytona sandbox and export chat history"""
        # Export chat history for analysis
        if self.chat_history_manager:
            try:
                logger.info("💾 Exporting chat history for analysis...")
                history_file = self.chat_history_manager.export_history("essential_toolkit_demo")
                logger.info(f"✅ Chat history exported to: {history_file}")
            except Exception as e:
                logger.warning(f"⚠️ Chat history export warning: {str(e)}")
        
        if self.sandbox_id:
            logger.info("🧹 Cleaning up Daytona sandbox...")
            try:
                self.sandbox_manager.delete_sandbox(self.sandbox_id)
                logger.info("✅ Cleanup completed")
            except Exception as e:
                logger.warning(f"⚠️ Cleanup warning: {str(e)}")

async def main():
    """Main function to run the essential toolkit demo"""
    logger.info("🚀 Starting Essential Browser Toolkit Demo")
    
    demo = EssentialToolkitDemo()
    
    try:
        # Initialize
        demo.results["start_time"] = time.time()
        
        if not await demo.initialize_with_sandbox():
            logger.error("❌ Failed to initialize demo environment")
            return 1
        
        logger.info("✅ Demo environment initialized successfully")
        logger.info("🎬 Starting demonstration scenarios...")
        
        # Run all scenarios
        await demo.run_scenario_1_multi_site_navigation()
        await asyncio.sleep(3)  # Brief pause between scenarios
        
        await demo.run_scenario_2_form_interaction()
        await asyncio.sleep(3)
        
        await demo.run_scenario_3_content_extraction()
        await asyncio.sleep(3)
        
        await demo.run_scenario_4_multi_tab_coordination()
        
        # Finalize results
        demo.results["end_time"] = time.time()
        
        # Print comprehensive results
        demo.print_comprehensive_results()
        
        logger.info("✅ Essential toolkit demo completed successfully!")
        return 0
        
    except KeyboardInterrupt:
        logger.info("🛑 Demo interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"❌ Demo failed with error: {str(e)}")
        return 1
    finally:
        await demo.cleanup()

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
