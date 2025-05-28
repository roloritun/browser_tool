"""
Enhanced Browser Automation with Daytona Integration
==================================================

This demo showcases enhanced browser automation using LangChain agents with
Daytona sandboxes for isolated browser environments and human intervention capabilities.

Features demonstrated:
• LangChain AgentExecutor with enhanced browser tools
• Daytona sandbox creation and management  
• Automatic CAPTCHA detection and human intervention
• Real-world automation scenarios
• VNC access for human assistance when needed
"""
import asyncio
import os
import time
import aiohttp
from dotenv import load_dotenv

from langchain_openai import AzureChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

from src.tools.enhanced_browser_tools import (
    SmartNavigationTool, SmartFormFillerTool, SmartClickElementTool,
    SmartRequestInterventionTool, SmartAutoDetectInterventionTool
)
from src.tools.utilities.sandbox_manager import SandboxManager
from src.utils.logger import logger
from src.utils.novnc_viewer import generate_novnc_viewer

# Load environment variables
load_dotenv()

class EnhancedBrowserAutomation:
    """Enhanced browser automation with Daytona integration and human intervention"""
    
    def __init__(self):
        self.llm = None
        self.agent = None
        self.tools = []
        self.sandbox_manager = SandboxManager()
        self.sandbox_id = None
        self.api_base_url = None
        self.vnc_url = None
        self.novnc_url = None
        
    async def initialize_with_sandbox(self):
        """Initialize with Daytona sandbox for isolated browser environment"""
        logger.info("🚀 Initializing Enhanced Browser Automation with Daytona...")
        
        # Create Daytona sandbox
        logger.info("📦 Creating Daytona sandbox...")
        (self.sandbox_id, cdp_url, self.vnc_url, 
         self.novnc_url, self.api_base_url, web_url, browser_api_url) = self.sandbox_manager.create_sandbox()
        
        # Generate and open NoVNC viewer for visual monitoring
        logger.info("🖥️ Opening NoVNC viewer for visual monitoring...")
        try:
            viewer_path = generate_novnc_viewer(
                novnc_url=self.novnc_url,
                vnc_password=os.getenv('VNC_PASSWORD', 'vncpassword'),
                auto_open=True
            )
            logger.info(f"✅ NoVNC viewer opened at: {viewer_path}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to open NoVNC viewer: {e}")
            logger.info(f"🌐 You can manually open: {self.novnc_url}")
        
        # Wait for services to start with health check
        logger.info("⏳ Waiting for browser services to initialize...")
        await self._wait_for_services_ready()
        
        # Initialize Azure OpenAI
        self.llm = AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            temperature=0.1
        )
        
        # Set up enhanced tools with automatic intervention
        self.tools = [
            SmartNavigationTool(auto_intervention_enabled=True, intervention_timeout=300),
            SmartFormFillerTool(auto_intervention_enabled=True, intervention_timeout=300),
            SmartClickElementTool(auto_intervention_enabled=True, intervention_timeout=300),
            SmartRequestInterventionTool(auto_intervention_enabled=True, intervention_timeout=300),
            SmartAutoDetectInterventionTool(auto_intervention_enabled=True, intervention_timeout=300)
        ]
        
        # Setup all tools with the sandbox API
        for tool in self.tools:
            await tool.setup(self.api_base_url, self.sandbox_id)
        
        # Initialize agent with memory
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Create enhanced agent prompt with proper ReAct format
        prompt = PromptTemplate.from_template("""
You are an enhanced browser automation assistant with human intervention capabilities.

AVAILABLE TOOLS:
{tools}

TOOL NAMES: {tool_names}

Your mission is to automate complex web tasks while seamlessly requesting human help when needed.

CAPABILITIES:
- Navigate websites intelligently
- Fill forms with appropriate data  
- Click elements and interact with pages
- Extract content and information
- Wait for page elements to load
- Handle CAPTCHAs by requesting human assistance
- Manage login requirements with human help
- Deal with anti-bot protection through intervention

INTERVENTION PROTOCOL:
When encountering challenges requiring human intelligence:
1. The tools will automatically detect intervention needs
2. Human receives VNC access to the browser environment  
3. They can solve CAPTCHAs, enter credentials, handle security checks
4. Automation resumes seamlessly after human assistance

IMPORTANT: You MUST follow this exact format for tool usage:

Thought: [Your reasoning about what to do next]
Action: [Tool name from the TOOL NAMES list above]
Action Input: [Valid JSON input for the tool]
Observation: [Result from the tool will appear here]

EXAMPLES:
Thought: I need to navigate to Google to start a search.
Action: smart_navigate_to
Action Input: {{"url": "https://google.com"}}
Observation: Successfully navigated to https://google.com

Thought: I need to fill in a search form with a query.
Action: smart_fill_form
Action Input: {{"form_params": "{{\"form_data\": {{\"q\": \"browser automation\"}}, \"submit\": true}}"}}
Observation: Form filled and submitted successfully

Thought: I need to click on an element, like a search button.
Action: smart_click_element
Action Input: {{"click_params": "{{\"index\": 0}}"}}
Observation: Element clicked successfully

Thought: I need to request human help for a CAPTCHA.
Action: smart_request_intervention
Action Input: {{"intervention_params": "{{\"intervention_type\": \"captcha\", \"reason\": \"Google CAPTCHA detected\", \"instructions\": \"Please solve the CAPTCHA to continue\"}}"}}
Observation: Human intervention requested for CAPTCHA assistance

PREVIOUS CONVERSATION:
{chat_history}

HUMAN REQUEST: {input}

{agent_scratchpad}
""")

        # Create the agent
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create agent executor
        self.agent = AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=memory,
            verbose=True,
            return_intermediate_steps=True,
            handle_parsing_errors=True,
            max_iterations=10,
            max_execution_time=1200  # 20 minutes
        )
        
        logger.info("✅ Enhanced browser automation initialized with human intervention support")
        logger.info(f"🌐 Human intervention available at: {self.novnc_url}")
        logger.info(f"🔑 VNC Password: {os.getenv('VNC_PASSWORD', 'vncpassword')}")
        
    async def _wait_for_services_ready(self, max_wait_time=120, check_interval=5):
        """Wait for browser services to be ready with health checks instead of blind wait"""
        start_time = time.time()
        services_ready = False
        
        while not services_ready and (time.time() - start_time) < max_wait_time:
            try:
                # Check if the browser API is responding
                async with aiohttp.ClientSession() as session:
                    health_url = f"{self.api_base_url}/automation/health"
                    async with session.get(health_url, timeout=5) as response:
                        if response.status == 200:
                            logger.info("✅ Browser API is ready!")
                            services_ready = True
                            break
            except Exception:
                # Services not ready yet, continue waiting
                elapsed = time.time() - start_time
                logger.info(f"⏳ Waiting for services... ({elapsed:.1f}s elapsed)")
                
            if not services_ready:
                await asyncio.sleep(check_interval)
        
        if not services_ready:
            logger.warning(f"⚠️ Services may not be fully ready after {max_wait_time}s, proceeding anyway...")
        
        # Additional brief wait for service stabilization
        await asyncio.sleep(5)

    async def run_google_search_example(self):
        """Example: Google search with automatic intervention handling"""
        logger.info("🔍 Starting Google search example with intervention support...")
        
        try:
            # This will automatically handle cookie consent, CAPTCHAs, anti-bot protection
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.agent.invoke({
                    "input": "Navigate to Google and search for 'AI browser automation'. "
                            "Handle any CAPTCHAs, cookie consent dialogs, or security checks automatically. "
                            "Extract the first 3 search results including titles and links."
                })
            )
            
            logger.info(f"✅ Google search completed: {result['output']}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Google search failed: {e}")
            return None
    
    async def run_complex_form_example(self):
        """Example: Complex form filling with intervention support"""
        logger.info("📝 Starting complex form example with intervention support...")
        
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.agent.invoke({
                    "input": "Navigate to a contact form or registration page (try typeform.com). "
                            "Fill out the form with realistic data like name: 'John Smith', "
                            "email: 'john@example.com', message: 'Testing automation'. "
                            "If you encounter CAPTCHAs, verification steps, or login requirements, "
                            "use the human intervention capabilities. Complete the form submission."
                })
            )
            
            logger.info(f"✅ Form filling completed: {result['output']}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Form filling failed: {e}")
            return None
    
    async def run_ecommerce_example(self):
        """Example: E-commerce automation with intervention for payment/verification"""
        logger.info("🛒 Starting e-commerce automation example...")
        
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.agent.invoke({
                    "input": "Navigate to an e-commerce site like Amazon. "
                            "Search for 'wireless headphones', find a well-reviewed product, "
                            "and add it to cart. Proceed to checkout but STOP before payment. "
                            "Handle any login prompts, CAPTCHAs, or verification steps "
                            "by requesting human intervention. Provide a summary of the selected product."
                })
            )
            
            logger.info(f"✅ E-commerce automation completed: {result['output']}")
            return result
            
        except Exception as e:
            logger.error(f"❌ E-commerce automation failed: {e}")
            return None
    
    async def run_news_research_example(self):
        """Example: News research with content extraction"""
        logger.info("📰 Starting news research example...")
        
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.agent.invoke({
                    "input": "Navigate to a major news website like BBC or CNN. "
                            "Find the top 3 news stories and extract their headlines and summaries. "
                            "Handle any cookie consent dialogs automatically. "
                            "If there are subscription prompts or anti-bot measures, "
                            "handle them appropriately or request human intervention."
                })
            )
            
            logger.info(f"✅ News research completed: {result['output']}")
            return result
            
        except Exception as e:
            logger.error(f"❌ News research failed: {e}")
            return None
    
    async def cleanup(self):
        """Clean up the Daytona sandbox"""
        if self.sandbox_id:
            logger.info("🧹 Cleaning up Daytona sandbox...")
            self.sandbox_manager.delete_sandbox(self.sandbox_id)
            logger.info("✅ Cleanup completed")

async def main():
    """Main function to run enhanced browser automation examples"""
    
    automation = EnhancedBrowserAutomation()
    
    try:
        # Initialize with Daytona sandbox
        await automation.initialize_with_sandbox()
        
        logger.info("\n" + "="*70)
        logger.info("🎯 ENHANCED BROWSER AUTOMATION WITH DAYTONA")
        logger.info("="*70)
        logger.info("This demo showcases:")
        logger.info("• LangChain AgentExecutor with enhanced browser tools")
        logger.info("• Daytona sandbox isolation for browser automation")
        logger.info("• Automatic CAPTCHA detection and human intervention")
        logger.info("• VNC access for human assistance when needed")
        logger.info("• Real-world automation scenarios")
        logger.info("="*70)
        logger.info(f"🌐 Human Intervention URL: {automation.novnc_url}")
        logger.info(f"🔑 VNC Password: {os.getenv('VNC_PASSWORD', 'vncpassword')}")
        logger.info("="*70)
        
        # Run automation examples
        examples = [
            ("🔍 Google Search with Intervention", automation.run_google_search_example),
            ("📝 Complex Form Filling", automation.run_complex_form_example),
            ("🛒 E-commerce Automation", automation.run_ecommerce_example),
            ("📰 News Research and Extraction", automation.run_news_research_example)
        ]
        
        results = {}
        
        for example_name, example_func in examples:
            logger.info(f"\n🚀 Running: {example_name}")
            logger.info("-" * 50)
            
            try:
                start_time = time.time()
                result = await example_func()
                end_time = time.time()
                
                if result:
                    results[example_name] = {
                        "status": "success",
                        "duration": end_time - start_time,
                        "output": result.get('output', 'Completed successfully')
                    }
                    logger.info(f"✅ {example_name} completed in {end_time - start_time:.1f}s")
                else:
                    results[example_name] = {
                        "status": "failed",
                        "duration": end_time - start_time,
                        "error": "No result returned"
                    }
                    logger.warning(f"⚠️ {example_name} completed with warnings")
                    
            except Exception as e:
                logger.error(f"❌ {example_name} failed: {e}")
                results[example_name] = {
                    "status": "error",
                    "error": str(e),
                    "duration": 0
                }
            
            # Brief pause between examples
            await asyncio.sleep(5)
        
        # Summary
        logger.info("\n" + "="*70)
        logger.info("🎉 ENHANCED AUTOMATION DEMO SUMMARY")
        logger.info("="*70)
        
        successful = sum(1 for r in results.values() if r["status"] == "success")
        total = len(results)
        
        logger.info(f"📊 Success Rate: {successful}/{total} examples completed successfully")
        
        for example_name, result in results.items():
            status_emoji = "✅" if result["status"] == "success" else "❌" if result["status"] == "error" else "⚠️"
            duration = result.get("duration", 0)
            logger.info(f"{status_emoji} {example_name}: {result['status'].upper()} ({duration:.1f}s)")
        
        logger.info("\n🎯 KEY FEATURES DEMONSTRATED:")
        logger.info("• Intelligent LangChain agent with browser automation")
        logger.info("• Seamless human intervention for complex challenges")
        logger.info("• Daytona sandbox isolation and VNC access")
        logger.info("• Real-world website automation scenarios")
        logger.info("• Automatic CAPTCHA and security handling")
        
        logger.info(f"\n🌐 VNC Access URL: {automation.novnc_url}")
        logger.info("🚀 Enhanced browser automation successfully demonstrated!")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize enhanced automation: {e}")
        logger.error("Please ensure Daytona credentials are configured properly")
        
    finally:
        # Always cleanup the sandbox
        await automation.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
