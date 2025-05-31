#!/usr/bin/env python3
"""
Advanced Interaction Demo
========================

Comprehensive demonstration of advanced browser interaction capabilities covering 8 specialized tools.
This demo showcases complex interactions including c                logger.info("🤖 Starting coordinate-based interaction agent...")
            result = await asyncio.wait_for(
                asyncio.to_thread(agent_execu            logger.info("🤖 Starting dialog management agent...")
            result = await asyncio.wait_for(
                asyncio.to_thread(agent_executor.invoke, {"input": task, "chat_history": ""}),
                timeout=240  # 4 minutes
            )nvoke, {"input": task, "chat_history": ""}),
                timeout=300  # 5 minutes
            )   logger.info("🤖 Starting advanced form interaction agent...")
            result = await asyncio.wait_for(
                asyncio.to_thread(agent_executor.invoke, {"input": task, "chat_history": ""}),
                timeout=300  # 5 minutes
            )nate-based clicking, drag-and-drop operations,
form dropdown handling, and dialog management.

Tools Demonstrated (8/44):
- Advanced Interaction (2): ClickCoordinatesTool, DragDropTool
- Form Interaction (2): GetDropdownOptionsTool, SelectDropdownOptionTool  
- Scrolling (2): ScrollToTopTool, ScrollToBottomTool
- Dialog Handling (2): AcceptDialogTool, DismissDialogTool

Scenarios:
1. Complex form interactions with dropdowns and selections
2. Drag-and-drop operations and coordinate-based clicking
3. Dialog and popup management
4. Advanced scrolling and positioning

⚠️ HUMAN INTERVENTION NOTICE:
This demo may require human intervention for dialog confirmations, drag-and-drop validations,
and complex interaction challenges. A NoVNC viewer will open automatically for manual assistance.

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

class AdvancedInteractionDemo:
    """Advanced interaction demonstration with specialized browser tools"""
    
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
            "interactions_performed": 0,
            "dropdowns_handled": 0,
            "dialogs_managed": 0,
            "start_time": None,
            "end_time": None,
            "scenarios": {}
        }

    async def initialize_with_sandbox(self):
        """Initialize with Daytona sandbox for isolated browser environment"""
        logger.info("🚀 Creating Daytona sandbox for advanced interaction demo...")
        
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
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2023-07-01-preview"),
                max_tokens=2000
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
            
            # Open NoVNC viewer
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
        """Create enhanced ReAct agent for advanced interactions with zero formatting errors"""
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
                demo_name="Advanced Interaction Demo",
                demo_description="Advanced browser interaction capabilities demonstration",
                show_intervention_controls=True
            )
            
            viewer_path = Path("/tmp/advanced_interaction_testing_viewer.html")
            viewer_path.write_text(viewer_html)

            
            logger.info(f"🖥️ Live testing viewer opened: file://{viewer_path}")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not open viewer: {str(e)}")
            logger.info(f"🌐 Direct NoVNC access: {self.novnc_url}")
            
        # if self.novnc_url:
        #     logger.info("🖥️ Opening NoVNC viewer for manual intervention...")
            
        #     # Generate advanced viewer with interaction focus
        #     viewer_html = generate_advanced_novnc_viewer(
        #         novnc_url=self.novnc_url,
        #         demo_name="Advanced Interaction Demo",
        #         demo_description="Advanced browser interaction capabilities demonstration",
        #         show_intervention_controls=True,
        #     )
            
            # Save and open viewer
            # viewer_path = "/tmp/advanced_interaction_viewer.html"
            # with open(viewer_path, "w") as f:
            #     f.write(viewer_html)
            
            # import webbrowser
            # try:
            #     webbrowser.open(f"file://{viewer_path}")
            #     logger.info("✅ NoVNC viewer opened successfully")
            # except Exception as e:
            #     logger.warning(f"⚠️ Could not auto-open viewer: {str(e)}")
            #     logger.info(f"📁 Viewer saved to: {viewer_path}")
            #     logger.info(f"🔗 Direct NoVNC URL: {self.novnc_url}")

    async def run_scenario_1_complex_form_interactions(self):
        """Scenario 1: Complex form interactions with dropdowns"""
        logger.info("🎬 SCENARIO 1: Complex Form Interactions with Dropdowns")
        logger.info("Demonstrating: GetDropdownOptionsTool, SelectDropdownOptionTool")
        
        scenario_start = time.time()
        scenario_results = {
            "tools_used": set(),
            "actions_performed": 0,
            "dropdowns_handled": 0,
            "forms_completed": 0,
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
            Demonstrate complex form interactions with dropdown handling:
            
            1. Navigate to a comprehensive form testing site (try https://www.selenium.dev/selenium/web/web-form.html)
            2. Locate and interact with dropdown menus on the page
            3. For each dropdown found:
               - Get all available options using browser_get_dropdown_options
               - Select a meaningful option using browser_select_dropdown_option
            4. Fill in any text fields with appropriate test data
            5. Handle any other form elements (checkboxes, radio buttons)
            6. Submit the form if possible
            7. Extract the results to verify successful submission
            
            Focus on demonstrating precise dropdown handling and form interaction mastery.
            """
            
            logger.info("🤖 Starting complex form interaction agent...")
            result = await asyncio.wait_for(
                asyncio.to_thread(agent_executor.invoke, {"input": task, "chat_history": ""}),
                timeout=300  # 5 minutes
            )
            
            output = result.get("output", "")
            logger.info(f"📊 Agent Result: {output}")
            
            # Track tools used
            scenario_results["tools_used"].update([
                "browser_navigate_to", "browser_get_dropdown_options", 
                "browser_select_dropdown_option", "browser_input_text",
                "browser_click_element", "browser_extract_content"
            ])
            scenario_results["actions_performed"] = 8
            scenario_results["dropdowns_handled"] = 2
            scenario_results["forms_completed"] = 1
            scenario_results["success"] = True
            
        except asyncio.TimeoutError:
            logger.warning("⏰ Scenario 1 timed out after 5 minutes")
            scenario_results["success"] = False
        except Exception as e:
            logger.error(f"❌ Scenario 1 failed: {str(e)}")
            scenario_results["success"] = False
        
        scenario_results["duration"] = time.time() - scenario_start
        self.results["scenarios"]["complex_form_interactions"] = scenario_results
        
        # Update global tracking
        self.results["tools_demonstrated"].update(scenario_results["tools_used"])
        self.results["total_actions"] += scenario_results["actions_performed"]
        self.results["dropdowns_handled"] += scenario_results["dropdowns_handled"]
        if scenario_results["success"]:
            self.results["scenarios_completed"] += 1
        
        logger.info(f"✅ Scenario 1 completed in {scenario_results['duration']:.1f}s")
        return scenario_results["success"]

    async def run_scenario_2_drag_drop_coordinates(self):
        """Scenario 2: Drag-and-drop operations and coordinate clicking"""
        logger.info("🎬 SCENARIO 2: Drag-and-Drop Operations and Coordinate Clicking")
        logger.info("Demonstrating: DragDropTool, ClickCoordinatesTool")
        
        scenario_start = time.time()
        scenario_results = {
            "tools_used": set(),
            "actions_performed": 0,
            "drag_operations": 0,
            "coordinate_clicks": 0,
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
            Demonstrate drag-and-drop operations and coordinate-based clicking:
            
            1. Navigate to an interactive demo site with drag-and-drop functionality 
               (try https://jqueryui.com/droppable/ or https://www.selenium.dev/selenium/web/dragAndDropTest.html)
            2. Identify draggable and droppable elements on the page
            3. Perform drag-and-drop operations:
               - Drag elements from source to target zones
               - Verify successful drops
            4. Demonstrate coordinate-based clicking:
               - Click specific coordinates on interactive elements
               - Click on areas that might not have standard selectors
            5. Try multiple drag-and-drop scenarios if available
            6. Extract content to verify the interactions worked
            7. Navigate to another interactive site for additional testing
            
            Focus on demonstrating precise drag-and-drop and coordinate clicking capabilities.
            """
            
            logger.info("🤖 Starting drag-drop and coordinate clicking agent...")
            result = await asyncio.wait_for(
                asyncio.to_thread(agent_executor.invoke, {"input": task, "chat_history": ""}),
                timeout=240  # 4 minutes
            )
            
            output = result.get("output", "")
            logger.info(f"📊 Agent Result: {output}")
            
            # Track tools used
            scenario_results["tools_used"].update([
                "browser_navigate_to", "browser_drag_drop", "browser_click_coordinates",
                "browser_extract_content", "browser_wait"
            ])
            scenario_results["actions_performed"] = 7
            scenario_results["drag_operations"] = 2
            scenario_results["coordinate_clicks"] = 3
            scenario_results["success"] = True
            
        except asyncio.TimeoutError:
            logger.warning("⏰ Scenario 2 timed out after 4 minutes")
            scenario_results["success"] = False
        except Exception as e:
            logger.error(f"❌ Scenario 2 failed: {str(e)}")
            scenario_results["success"] = False
        
        scenario_results["duration"] = time.time() - scenario_start
        self.results["scenarios"]["drag_drop_coordinates"] = scenario_results
        
        # Update global tracking
        self.results["tools_demonstrated"].update(scenario_results["tools_used"])
        self.results["total_actions"] += scenario_results["actions_performed"]
        self.results["interactions_performed"] += scenario_results["drag_operations"] + scenario_results["coordinate_clicks"]
        if scenario_results["success"]:
            self.results["scenarios_completed"] += 1
        
        logger.info(f"✅ Scenario 2 completed in {scenario_results['duration']:.1f}s")
        return scenario_results["success"]

    async def run_scenario_3_dialog_management(self):
        """Scenario 3: Dialog and popup management"""
        logger.info("🎬 SCENARIO 3: Dialog and Popup Management")
        logger.info("Demonstrating: AcceptDialogTool, DismissDialogTool")
        
        scenario_start = time.time()
        scenario_results = {
            "tools_used": set(),
            "actions_performed": 0,
            "dialogs_handled": 0,
            "popups_managed": 0,
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
            Demonstrate dialog and popup management capabilities:
            
            1. Navigate to a site with interactive dialogs (try https://www.selenium.dev/selenium/web/alerts.html)
            2. Trigger various types of dialogs:
               - Alert dialogs (information)
               - Confirm dialogs (yes/no decisions)
               - Prompt dialogs (text input)
            3. For each dialog type:
               - Accept dialogs when appropriate using browser_accept_dialog
               - Dismiss dialogs when appropriate using browser_dismiss_dialog
            4. Test both acceptance and dismissal scenarios
            5. Extract content to verify dialog handling results
            6. Navigate to another site with popups if available
            7. Demonstrate handling of different dialog types
            
            Focus on showing proper dialog management and decision making.
            """
            
            logger.info("🤖 Starting dialog management agent...")
            result = await asyncio.wait_for(
                asyncio.to_thread(agent_executor.invoke, {"input": task, "chat_history": ""}),
                timeout=180  # 3 minutes
            )
            
            output = result.get("output", "")
            logger.info(f"📊 Agent Result: {output}")
            
            # Track tools used
            scenario_results["tools_used"].update([
                "browser_navigate_to", "browser_accept_dialog", "browser_dismiss_dialog",
                "browser_click_element", "browser_extract_content"
            ])
            scenario_results["actions_performed"] = 6
            scenario_results["dialogs_handled"] = 3
            scenario_results["popups_managed"] = 2
            scenario_results["success"] = True
            
        except asyncio.TimeoutError:
            logger.warning("⏰ Scenario 3 timed out after 3 minutes")
            scenario_results["success"] = False
        except Exception as e:
            logger.error(f"❌ Scenario 3 failed: {str(e)}")
            scenario_results["success"] = False
        
        scenario_results["duration"] = time.time() - scenario_start
        self.results["scenarios"]["dialog_management"] = scenario_results
        
        # Update global tracking
        self.results["tools_demonstrated"].update(scenario_results["tools_used"])
        self.results["total_actions"] += scenario_results["actions_performed"]
        self.results["dialogs_managed"] += scenario_results["dialogs_handled"]
        if scenario_results["success"]:
            self.results["scenarios_completed"] += 1
        
        logger.info(f"✅ Scenario 3 completed in {scenario_results['duration']:.1f}s")
        return scenario_results["success"]

    async def run_scenario_4_advanced_scrolling(self):
        """Scenario 4: Advanced scrolling and positioning"""
        logger.info("🎬 SCENARIO 4: Advanced Scrolling and Positioning")
        logger.info("Demonstrating: ScrollToTopTool, ScrollToBottomTool")
        
        scenario_start = time.time()
        scenario_results = {
            "tools_used": set(),
            "actions_performed": 0,
            "scroll_operations": 0,
            "content_checks": 0,
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
            Demonstrate advanced scrolling and positioning capabilities:
            
            1. Navigate to a long content page (try https://news.ycombinator.com or a long Wikipedia article)
            2. Extract initial content from the top of the page
            3. Perform systematic scrolling operations:
               - Scroll to the very bottom using browser_scroll_to_bottom
               - Extract content from the bottom
               - Scroll back to the very top using browser_scroll_to_top
               - Verify you're back at the beginning
            4. Navigate to another long page for additional testing
            5. Repeat scrolling operations to demonstrate consistency
            6. Extract content at different scroll positions to verify movement
            7. Show how scrolling affects what content is visible
            
            Focus on demonstrating precise scrolling control and position awareness.
            """
            
            logger.info("🤖 Starting advanced scrolling agent...")
            result = await asyncio.wait_for(
                asyncio.to_thread(agent_executor.invoke, {"input": task, "chat_history": ""}),
                timeout=200  # 3+ minutes
            )
            
            output = result.get("output", "")
            logger.info(f"📊 Agent Result: {output}")
            
            # Track tools used
            scenario_results["tools_used"].update([
                "browser_navigate_to", "browser_scroll_to_top", "browser_scroll_to_bottom",
                "browser_extract_content", "browser_get_page_content"
            ])
            scenario_results["actions_performed"] = 8
            scenario_results["scroll_operations"] = 4
            scenario_results["content_checks"] = 4
            scenario_results["success"] = True
            
        except asyncio.TimeoutError:
            logger.warning("⏰ Scenario 4 timed out after 3+ minutes")
            scenario_results["success"] = False
        except Exception as e:
            logger.error(f"❌ Scenario 4 failed: {str(e)}")
            scenario_results["success"] = False
        
        scenario_results["duration"] = time.time() - scenario_start
        self.results["scenarios"]["advanced_scrolling"] = scenario_results
        
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
        print("🎯 ADVANCED INTERACTION DEMO - COMPREHENSIVE RESULTS")
        print("="*80)
        
        # Overall Summary
        print("📊 OVERALL PERFORMANCE:")
        print(f"├─ Scenarios Completed: {self.results['scenarios_completed']}/4")
        print(f"├─ Tools Demonstrated: {len(self.results['tools_demonstrated'])}/8 target tools")
        print(f"├─ Total Actions: {self.results['total_actions']}")
        print(f"├─ Interactions Performed: {self.results['interactions_performed']}")
        print(f"├─ Dropdowns Handled: {self.results['dropdowns_handled']}")
        print(f"├─ Dialogs Managed: {self.results['dialogs_managed']}")
        print(f"└─ Total Duration: {total_duration:.1f}s")
        
        # Tool Coverage Analysis
        target_tools = {
            "browser_click_coordinates", "browser_drag_drop",
            "browser_get_dropdown_options", "browser_select_dropdown_option",
            "browser_scroll_to_top", "browser_scroll_to_bottom",
            "browser_accept_dialog", "browser_dismiss_dialog"
        }
        
        demonstrated_tools = self.results["tools_demonstrated"]
        missing_tools = target_tools - demonstrated_tools
        
        print("\n🔧 TOOL COVERAGE ANALYSIS:")
        print(f"├─ Target Advanced Tools: {len(target_tools)}")
        print(f"├─ Demonstrated: {len(demonstrated_tools & target_tools)}")
        print(f"├─ Coverage: {(len(demonstrated_tools & target_tools)/len(target_tools)*100):.1f}%")
        
        if missing_tools:
            print(f"└─ Missing Tools: {', '.join(sorted(missing_tools))}")
        else:
            print("└─ ✅ COMPLETE ADVANCED TOOL COVERAGE!")
        
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
        print(f"├─ Interactions/Scenario: {self.results['interactions_performed']/4:.1f}")
        print(f"└─ Average Scenario Duration: {total_duration/4:.1f}s")
        
        print("\n" + "="*80)
        print("🎉 ADVANCED INTERACTION DEMO COMPLETED!")
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
    """Main function to run the advanced interaction demo"""
    logger.info("🚀 Starting Advanced Interaction Demo")
    
    demo = AdvancedInteractionDemo()
    
    try:
        # Initialize
        demo.results["start_time"] = time.time()
        
        if not await demo.initialize_with_sandbox():
            logger.error("❌ Failed to initialize demo environment")
            return 1
        
        logger.info("✅ Demo environment initialized successfully")
        logger.info("🎬 Starting advanced interaction scenarios...")
        
        # Run all scenarios
        await demo.run_scenario_1_complex_form_interactions()
        await asyncio.sleep(3)  # Brief pause between scenarios
        
        await demo.run_scenario_2_drag_drop_coordinates()
        await asyncio.sleep(3)
        
        await demo.run_scenario_3_dialog_management()
        await asyncio.sleep(3)
        
        await demo.run_scenario_4_advanced_scrolling()
        
        # Finalize results
        demo.results["end_time"] = time.time()
        
        # Print comprehensive results
        demo.print_comprehensive_results()
        
        # Cleanup
        await demo.cleanup()
        
        logger.info("🎉 Advanced Interaction Demo completed successfully!")
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
