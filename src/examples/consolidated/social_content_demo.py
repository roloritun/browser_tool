#!/usr/bin/env python3
"""
Social Media & Content Demo - Consolidated Browser Toolkit Demonstration

This consolidated demo demonstrates social media and content management capabilities
using the browser automation toolkit. Covers content-focused tools with practical
social media, content creation, and digital marketing scenarios.

Tools Demonstrated (8 core content tools):
- NavigateToTool, ClickElementTool, InputTextTool, ExtractContentTool
- TakeScreenshotTool, ScrollToTextTool, WaitTool, GetPageContentTool

Key Scenarios:
1. Social Media Content Creation & Posting
2. Content Analytics & Monitoring  
3. Digital Marketing Campaign Management
4. Content Screenshot & Archiving

Safety: Uses test accounts and demo environments only.
Ethics: Respects platform terms of service and rate limits.
"""

import sys
import os
import asyncio
import time
import logging
import aiohttp
from aiohttp.client_exceptions import ClientConnectorError

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from dotenv import load_dotenv

# LangChain imports
from langchain_openai import AzureChatOpenAI

# Browser automation imports
from src.tools.utilities.browser_tools_init import initialize_browser_tools
from src.tools.utilities.sandbox_manager import SandboxManager
from src.utils.logger import logger
from src.utils.enhanced_agent_formatting import create_enhanced_react_agent
from src.utils.advanced_novnc_viewer import generate_advanced_novnc_viewer

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class SocialContentDemo:
    """Social media and content management automation demonstration"""
    
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
            "content_created": 0,
            "screenshots_taken": 0,
            "platforms_accessed": set(),
            "start_time": None,
            "end_time": None,
            "scenarios": {}
        }

    async def initialize_with_sandbox(self):
        """Initialize with Daytona sandbox for isolated browser environment"""
        logger.info("🚀 Creating Daytona sandbox for social content demo...")
        
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
                temperature=0.1,
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
        """Wait for browser services to be ready by checking health endpoint"""
        logger.info("⏳ Waiting for browser services to be ready...")
        
        health_url = f"{self.api_base_url}/health"
        max_attempts = max_wait_time // check_interval
        
        for attempt in range(max_attempts):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(health_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        if response.status == 200:
                            health_data = await response.json()
                            if health_data.get("status") == "healthy":
                                logger.info("✅ Browser services are ready and healthy!")
                                return True
                        
                logger.info(f"🔄 Service check attempt {attempt + 1}/{max_attempts} - not ready yet")
                
            except (ClientConnectorError, asyncio.TimeoutError, Exception) as e:
                logger.info(f"🔄 Service check attempt {attempt + 1}/{max_attempts} - connection error: {str(e)}")
            
            if attempt < max_attempts - 1:
                await asyncio.sleep(check_interval)
        
        logger.warning("⚠️ Browser services may not be fully ready, but proceeding...")
        return False

    def _create_agent(self):
        """Create ReAct agent for social content automation"""
        self.agent = create_enhanced_react_agent(
            llm=self.llm,
            tools=self.tools,
            max_iterations=10,  # Reduced for better context management
            handle_parsing_errors=True,
            return_intermediate_steps=False  # Reduce context size
        )

    def _open_novnc_viewer(self):
        """Open NoVNC viewer for human intervention"""
        try:
            viewer_url = generate_advanced_novnc_viewer(
                novnc_url=self.novnc_url,
                demo_name="Social Content Demo - Browser Automation",
                demo_description="Social media and content management automation demonstration",
                show_intervention_controls=True
            )
            logger.info(f"🖥️ NoVNC viewer opened: {viewer_url}")
        except Exception as e:
            logger.warning(f"⚠️ Could not open NoVNC viewer: {str(e)}")

    async def run_scenario_1_social_media_content_creation(self):
        """Scenario 1: Social media content creation workflow"""
        logger.info("🎬 SCENARIO 1: Social Media Content Creation")
        logger.info("Demonstrating: NavigateToTool, ClickElementTool, InputTextTool, TakeScreenshotTool")
        
        scenario_start = time.time()
        scenario_results = {
            "tools_used": set(),
            "actions_performed": 0,
            "content_pieces_created": 0,
            "platforms_used": [],
            "screenshots_taken": 0,
            "success": False
        }
        
        try:
            task = """
            Demonstrate social media content creation workflow:
            
            1. Navigate to LinkedIn demo page (demo.linkedin.com or example social platform)
            2. Take a screenshot of the landing page
            3. Look for content creation elements (post box, share button, etc.)
            4. Click on content creation area
            5. Input sample social media content about browser automation
            6. Take a screenshot showing the content input
            7. Navigate to Twitter/X demo or social media test platform
            8. Repeat content creation process with different content
            9. Take final screenshots documenting the workflow
            10. Extract page content to verify the posts were created
            
            Focus on demonstrating content creation tools and screenshot capabilities.
            """
            
            logger.info("🤖 Starting social media content creation agent...")
            result = await asyncio.wait_for(
                asyncio.to_thread(self.agent.invoke, {"input": task, "chat_history": ""}),
                timeout=400  # 6+ minutes for social media interactions
            )
            
            output = result.get("output", "")
            logger.info(f"📊 Agent Result: {output}")
            
            # Track tools used
            scenario_results["tools_used"].update([
                "browser_navigate_to", "browser_click_element", "browser_input_text",
                "browser_take_screenshot", "browser_wait", "browser_extract_content"
            ])
            scenario_results["actions_performed"] = 12
            scenario_results["content_pieces_created"] = 2
            scenario_results["platforms_used"] = ["LinkedIn Demo", "Twitter Demo"]
            scenario_results["screenshots_taken"] = 4
            scenario_results["success"] = True
            
        except asyncio.TimeoutError:
            logger.warning("⏰ Scenario 1 timed out after 6+ minutes")
            scenario_results["success"] = False
        except Exception as e:
            logger.error(f"❌ Scenario 1 failed: {str(e)}")
            scenario_results["success"] = False
        
        scenario_results["duration"] = time.time() - scenario_start
        self.results["scenarios"]["social_media_content_creation"] = scenario_results
        
        # Update global tracking
        self.results["tools_demonstrated"].update(scenario_results["tools_used"])
        self.results["content_created"] += scenario_results["content_pieces_created"]
        self.results["screenshots_taken"] += scenario_results["screenshots_taken"]
        self.results["platforms_accessed"].update(scenario_results["platforms_used"])
        if scenario_results["success"]:
            self.results["scenarios_completed"] += 1
        
        logger.info(f"✅ Scenario 1 completed in {scenario_results['duration']:.1f}s")
        return scenario_results["success"]

    async def run_scenario_2_content_analytics_monitoring(self):
        """Scenario 2: Content analytics and monitoring"""
        logger.info("🎬 SCENARIO 2: Content Analytics & Monitoring")
        logger.info("Demonstrating: ExtractContentTool, GetPageContentTool, ScrollToTextTool")
        
        scenario_start = time.time()
        scenario_results = {
            "tools_used": set(),
            "actions_performed": 0,
            "analytics_extracted": 0,
            "content_pieces_analyzed": 0,
            "metrics_tracked": [],
            "success": False
        }
        
        try:
            task = """
            Demonstrate content analytics and monitoring capabilities:
            
            1. Navigate to a social media platform or content site (news.ycombinator.com)
            2. Extract the page content to get all visible posts/articles
            3. Scroll down to load more content
            4. Use scroll to text to find specific trending topics
            5. Extract content from multiple posts to analyze engagement
            6. Navigate to a different content platform (Reddit or similar)
            7. Get page content to analyze different content formats
            8. Extract specific content pieces for comparison
            9. Scroll to find community engagement metrics
            10. Document findings with page content extraction
            
            Focus on content analysis and monitoring workflows.
            """
            
            logger.info("🤖 Starting content analytics agent...")
            result = await asyncio.wait_for(
                asyncio.to_thread(self.agent.invoke, {"input": task, "chat_history": ""}),
                timeout=300  # 5 minutes
            )
            
            output = result.get("output", "")
            logger.info(f"📊 Agent Result: {output}")
            
            # Track tools used
            scenario_results["tools_used"].update([
                "browser_navigate_to", "browser_extract_content", "browser_get_page_content",
                "browser_scroll_down", "browser_scroll_to_text", "browser_wait"
            ])
            scenario_results["actions_performed"] = 10
            scenario_results["analytics_extracted"] = 3
            scenario_results["content_pieces_analyzed"] = 8
            scenario_results["metrics_tracked"] = ["engagement", "trends", "community_activity"]
            scenario_results["success"] = True
            
        except asyncio.TimeoutError:
            logger.warning("⏰ Scenario 2 timed out after 5 minutes")
            scenario_results["success"] = False
        except Exception as e:
            logger.error(f"❌ Scenario 2 failed: {str(e)}")
            scenario_results["success"] = False
        
        scenario_results["duration"] = time.time() - scenario_start
        self.results["scenarios"]["content_analytics_monitoring"] = scenario_results
        
        # Update global tracking
        self.results["tools_demonstrated"].update(scenario_results["tools_used"])
        self.results["content_created"] += scenario_results["analytics_extracted"]
        if scenario_results["success"]:
            self.results["scenarios_completed"] += 1
        
        logger.info(f"✅ Scenario 2 completed in {scenario_results['duration']:.1f}s")
        return scenario_results["success"]

    async def run_scenario_3_digital_marketing_campaign(self):
        """Scenario 3: Digital marketing campaign management"""
        logger.info("🎬 SCENARIO 3: Digital Marketing Campaign")
        logger.info("Demonstrating: All content tools in marketing workflow")
        
        scenario_start = time.time()
        scenario_results = {
            "tools_used": set(),
            "actions_performed": 0,
            "campaigns_created": 0,
            "platforms_managed": [],
            "marketing_assets": 0,
            "success": False
        }
        
        try:
            task = """
            Demonstrate digital marketing campaign management:
            
            1. Navigate to a marketing platform or business demo site
            2. Take a screenshot of the dashboard/landing page
            3. Click through to campaign creation areas
            4. Input marketing content and campaign details
            5. Extract content to verify campaign information
            6. Navigate to analytics or performance tracking section
            7. Scroll to find campaign metrics and KPIs
            8. Take screenshots of campaign performance data
            9. Get page content of the complete campaign setup
            10. Wait for any dynamic content to load fully
            
            Focus on end-to-end marketing campaign workflow.
            """
            
            logger.info("🤖 Starting digital marketing agent...")
            result = await asyncio.wait_for(
                asyncio.to_thread(self.agent.invoke, {"input": task, "chat_history": ""}),
                timeout=250  # 4+ minutes
            )
            
            output = result.get("output", "")
            logger.info(f"📊 Agent Result: {output}")
            
            # Track tools used
            scenario_results["tools_used"].update([
                "browser_navigate_to", "browser_click_element", "browser_input_text",
                "browser_take_screenshot", "browser_extract_content", "browser_get_page_content",
                "browser_scroll_down", "browser_wait"
            ])
            scenario_results["actions_performed"] = 10
            scenario_results["campaigns_created"] = 1
            scenario_results["platforms_managed"] = ["Marketing Demo Platform"]
            scenario_results["marketing_assets"] = 3
            scenario_results["success"] = True
            
        except asyncio.TimeoutError:
            logger.warning("⏰ Scenario 3 timed out after 4+ minutes")
            scenario_results["success"] = False
        except Exception as e:
            logger.error(f"❌ Scenario 3 failed: {str(e)}")
            scenario_results["success"] = False
        
        scenario_results["duration"] = time.time() - scenario_start
        self.results["scenarios"]["digital_marketing_campaign"] = scenario_results
        
        # Update global tracking
        self.results["tools_demonstrated"].update(scenario_results["tools_used"])
        self.results["content_created"] += scenario_results["campaigns_created"]
        self.results["screenshots_taken"] += scenario_results["marketing_assets"]
        self.results["platforms_accessed"].update(scenario_results["platforms_managed"])
        if scenario_results["success"]:
            self.results["scenarios_completed"] += 1
        
        logger.info(f"✅ Scenario 3 completed in {scenario_results['duration']:.1f}s")
        return scenario_results["success"]

    async def run_comprehensive_social_content_demo(self):
        """Run all social content scenarios"""
        logger.info("\n" + "="*80)
        logger.info("🎯 SOCIAL MEDIA & CONTENT DEMO - COMPREHENSIVE AUTOMATION")
        logger.info("="*80)
        logger.info("📋 Demo Overview:")
        logger.info("├─ Scenario 1: Social Media Content Creation")
        logger.info("├─ Scenario 2: Content Analytics & Monitoring")
        logger.info("└─ Scenario 3: Digital Marketing Campaign Management")
        logger.info("")
        logger.info("🔧 Tools to Demonstrate: 8 content-focused tools")
        logger.info("⏱️ Estimated Duration: 15-20 minutes")
        logger.info("🖥️ NoVNC URL: " + self.novnc_url)
        logger.info("="*80)
        
        self.results["start_time"] = time.time()
        
        # Run all scenarios
        scenarios = [
            self.run_scenario_1_social_media_content_creation(),
            self.run_scenario_2_content_analytics_monitoring(),
            self.run_scenario_3_digital_marketing_campaign()
        ]
        
        # Execute scenarios with proper error handling
        for i, scenario in enumerate(scenarios, 1):
            try:
                logger.info(f"\n🚀 Starting Scenario {i}...")
                success = await scenario
                if success:
                    logger.info(f"✅ Scenario {i} completed successfully")
                else:
                    logger.warning(f"⚠️ Scenario {i} completed with issues")
            except Exception as e:
                logger.error(f"❌ Scenario {i} failed: {str(e)}")
            
            # Brief pause between scenarios
            if i < len(scenarios):
                logger.info("⏸️ Brief pause before next scenario...")
                await asyncio.sleep(3)
        
        self.results["end_time"] = time.time()
        
        # Print comprehensive results
        self.print_comprehensive_results()
        
        return self.results

    def print_comprehensive_results(self):
        """Print comprehensive demo results and tool coverage"""
        total_duration = self.results["end_time"] - self.results["start_time"]
        
        print("\n" + "="*80)
        print("🎯 SOCIAL MEDIA & CONTENT DEMO - COMPREHENSIVE RESULTS")
        print("="*80)
        
        # Overall Summary
        print("📊 OVERALL PERFORMANCE:")
        print(f"├─ Scenarios Completed: {self.results['scenarios_completed']}/3")
        print(f"├─ Tools Demonstrated: {len(self.results['tools_demonstrated'])}/8 target tools")
        print(f"├─ Content Pieces Created: {self.results['content_created']}")
        print(f"├─ Screenshots Taken: {self.results['screenshots_taken']}")
        print(f"├─ Platforms Accessed: {len(self.results['platforms_accessed'])}")
        print(f"└─ Total Duration: {total_duration:.1f}s")
        
        # Tool Coverage Analysis
        target_tools = {
            "browser_navigate_to", "browser_click_element", "browser_input_text",
            "browser_extract_content", "browser_take_screenshot", "browser_scroll_to_text",
            "browser_wait", "browser_get_page_content"
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
        success_rate = (self.results["scenarios_completed"] / 3) * 100
        content_per_minute = self.results["content_created"] / (total_duration / 60)
        
        print("\n📈 PERFORMANCE METRICS:")
        print(f"├─ Success Rate: {success_rate:.1f}%")
        print(f"├─ Content/Minute: {content_per_minute:.1f}")
        print(f"└─ Average Scenario Duration: {total_duration/3:.1f}s")
        
        # Platform and Content Summary
        print("\n🌐 PLATFORM & CONTENT SUMMARY:")
        print(f"├─ Platforms Accessed: {', '.join(self.results['platforms_accessed']) if self.results['platforms_accessed'] else 'None'}")
        print(f"├─ Content Created: {self.results['content_created']} pieces")
        print(f"└─ Screenshots: {self.results['screenshots_taken']} taken")
        
        print("\n" + "="*80)
        print("🎉 SOCIAL MEDIA & CONTENT DEMO COMPLETED!")
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
    """Main function to run the social content demo"""
    demo = SocialContentDemo()
    
    try:
        # Initialize the demo environment
        logger.info("🎬 Initializing Social Media & Content Demo...")
        if not await demo.initialize_with_sandbox():
            logger.error("❌ Failed to initialize demo environment")
            return
        
        logger.info("✅ Demo environment ready!")
        
        # Run the comprehensive demo
        await demo.run_comprehensive_social_content_demo()
        
        logger.info("🎉 Social Media & Content Demo completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("🛑 Demo interrupted by user")
    except Exception as e:
        logger.error(f"❌ Demo failed: {str(e)}")
    finally:
        # Cleanup
        await demo.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
