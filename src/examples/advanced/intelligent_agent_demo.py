#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
Fixed agent implementation that properly calls human intervention tools.
This script addresses the core issues with tool calling format and scenario recognition.
"""

import asyncio
import os
import dotenv
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction, AgentFinish
from src.tools.utilities.browser_tools_init import initialize_browser_tools
from src.tools.utilities.sandbox_manager import SandboxManager
from src.utils.logger import logger
from src.utils.novnc_viewer import generate_novnc_viewer

# Load environment variables
dotenv.load_dotenv()

class InterventionTrackingCallback(BaseCallbackHandler):
    """Enhanced callback to track and fix tool calling issues."""
    
    def __init__(self):
        self.tool_calls = []
        self.intervention_calls = []
        self.parsing_errors = []
        
    def on_agent_action(self, action: AgentAction, **kwargs) -> None:
        self.tool_calls.append({
            "tool": action.tool,
            "input": action.tool_input,
            "log": action.log
        })
        
        # Track intervention tool calls
        if any(keyword in action.tool.lower() for keyword in ["intervention", "human", "captcha", "login"]):
            self.intervention_calls.append(action)
            logger.info(f"🆘 INTERVENTION TOOL CALLED: {action.tool}")
            logger.info(f"📝 Tool Input: {action.tool_input}")
        
        logger.info(f"🤖 AGENT ACTION: {action.tool}")
        logger.info(f"📝 Tool Input: {action.tool_input}")
        
    def on_agent_finish(self, finish: AgentFinish, **kwargs) -> None:
        logger.info("✅ AGENT FINISHED")
        logger.info(f"📊 Total tool calls: {len(self.tool_calls)}")
        logger.info(f"🆘 Intervention calls: {len(self.intervention_calls)}")
        
    def on_tool_start(self, serialized, input_str: str, **kwargs) -> None:
        tool_name = serialized.get("name", "Unknown")
        logger.info(f"🔧 TOOL START: {tool_name} with input: {input_str}")
        
    def on_tool_end(self, output: str, **kwargs) -> None:
        logger.info(f"🔧 TOOL END: {output[:200]}...")
        
    def on_tool_error(self, error, **kwargs) -> None:
        logger.error(f"❌ TOOL ERROR: {error}")
        self.parsing_errors.append(str(error))


def create_improved_agent_prompt():
    """Create an improved prompt that clearly guides intervention tool usage."""
    return PromptTemplate.from_template("""
You are an intelligent browser automation agent with robust human intervention capabilities.

AVAILABLE TOOLS:
{tools}

TOOL NAMES: {tool_names}

CRITICAL INTERVENTION RULES:
🆘 ALWAYS use intervention tools when you encounter ANY of these scenarios:
1. CAPTCHA detection (any image verification, "I'm not a robot", reCAPTCHA, hCaptcha)
2. Login forms requiring credentials (username/password fields)
3. Security challenges or verification steps
4. Anti-bot measures or access blocked messages
5. 2FA/OTP requirements
6. Any page that says "human verification required"

INTERVENTION TOOLS TO USE:
- browser_request_human_help: For general help requests
- browser_solve_captcha: Specifically for CAPTCHA challenges
- browser_handle_login: For login forms and authentication
- browser_request_intervention: For complex scenarios
- browser_auto_detect_intervention: To automatically detect intervention needs

STRICT FORMAT REQUIREMENTS:
You MUST use this exact ReAct format for ALL tool calls:

Thought: [Your reasoning about what to do next]
Action: [EXACT tool name from the list]
Action Input: [Valid JSON or simple string input]
Observation: [Tool result will appear here]

EXAMPLE INTERVENTION USAGE:
Thought: I can see a CAPTCHA challenge on this page that requires human verification.
Action: browser_solve_captcha
Action Input: {{"reason": "CAPTCHA detected on login page", "instructions": "Please solve the image verification challenge", "timeout_seconds": 600}}
Observation: [Human intervention result]

IMPORTANT GUIDELINES:
✅ DO use intervention tools immediately when encountering challenges
✅ DO use exact tool names from the available tools list
✅ DO format inputs as valid JSON for multi-parameter tools
✅ DO wait for intervention to complete before continuing
✅ DO use longer timeouts (600+ seconds) for human intervention
❌ DO NOT try to solve CAPTCHAs yourself
❌ DO NOT skip intervention when clearly needed
❌ DO NOT use markdown formatting in tool calls
❌ DO NOT guess login credentials

PREVIOUS CONVERSATION:
{chat_history}

USER REQUEST: {input}

Begin your response with a Thought, then use the exact format above:

{agent_scratchpad}""")


async def test_fixed_agent():
    """Test the fixed agent implementation."""
    
    logger.info("🚀 Testing Fixed Agent Implementation...")
    
    # Create Daytona sandbox
    logger.info("📦 Creating Daytona sandbox...")
    sandbox_manager = SandboxManager()
    (sandbox_id, cdp_url, vnc_url, 
     novnc_url, api_base_url, web_url, browser_api_url) = sandbox_manager.create_sandbox()
    
    # Generate and open NoVNC viewer for visual monitoring
    logger.info("🖥️ Opening NoVNC viewer for visual monitoring...")
    try:
        viewer_path = generate_novnc_viewer(
            novnc_url=novnc_url,
            vnc_password=os.getenv('VNC_PASSWORD', 'vncpassword'),
            auto_open=True
        )
        logger.info(f"✅ NoVNC viewer opened at: {viewer_path}")
    except Exception as e:
        logger.warning(f"⚠️ Failed to open NoVNC viewer: {e}")
        logger.info(f"🌐 You can manually open: {novnc_url}")
    
    # Wait for services to start
    logger.info("⏳ Waiting for browser services to initialize...")
    await asyncio.sleep(45)
    
    # Initialize Azure OpenAI with better settings for tool calling
    llm = AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"), 
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        temperature=0.0,  # Very deterministic for better tool calling
        max_tokens=2000,  # More tokens for complex reasoning
        model_kwargs={
            "top_p": 0.1,  # Focus on most likely tokens
        }
    )
    
    # Initialize browser tools
    tools = await initialize_browser_tools(api_base_url, sandbox_id)
    
    # Log available tools with focus on intervention tools
    logger.info("📋 Available Tools:")
    intervention_tools = []
    for tool in tools:
        if any(keyword in tool.name.lower() for keyword in ["intervention", "human", "captcha", "login"]):
            intervention_tools.append(tool)
            logger.info(f"  🆘 {tool.name}: {tool.description}")
        else:
            logger.info(f"  - {tool.name}: {tool.description}")
    
    logger.info(f"🆘 Found {len(intervention_tools)} intervention tools")
    
    # Create improved prompt
    prompt = create_improved_agent_prompt()
    
    # Initialize memory
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=False,
        input_key="input"
        # Removed output_key to avoid deprecation warnings in newer LangChain versions
    )
    
    # Create the agent with improved settings
    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )
    
    # Create agent executor with enhanced error handling
    callback_handler = InterventionTrackingCallback()
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        return_intermediate_steps=True,
        callbacks=[callback_handler],
        handle_parsing_errors="Check your output format. You must use: Thought: [reasoning], Action: [exact tool name], Action Input: [valid input]",
        max_iterations=6,
        max_execution_time=300,
        early_stopping_method="force"
    )
    
    logger.info(f"🌐 Human intervention available at: {novnc_url}")
    logger.info(f"🔑 VNC Password: {os.getenv('VNC_PASSWORD', 'vncpassword')}")
    logger.info("📝 INTERVENTION ACCESS INSTRUCTIONS:")
    logger.info("   1. Open the VNC URL above in a browser")
    logger.info("   2. Enter the VNC password when prompted")
    logger.info("   3. You'll see the browser with intervention overlay")
    logger.info("   4. Follow the instructions in the overlay")
    logger.info("   5. Click 'Complete' when done")
    logger.info("⏰ TIMEOUT: Interventions will timeout after 10 minutes")
    
    # Test scenarios designed to trigger intervention
    test_scenarios = [
        {
            "name": "Direct CAPTCHA Test",
            "task": """
Navigate to a website that commonly shows CAPTCHAs .

CRITICAL: After loading any page, you MUST:
1. Check the page content for CAPTCHA indicators
2. If you see ANY signs of CAPTCHA (image verification, "I'm not a robot", reCAPTCHA), immediately use browser_solve_captcha
3. Do NOT attempt to solve it yourself

Start by navigating to Google.com and performing a search.
"""
        },
        {
            "name": "Auto-Detection Test", 
            "task": """
First, navigate to any webpage, then immediately use the browser_auto_detect_intervention tool 
to check if the current page requires human intervention. 

The auto-detection tool should help identify if there are any intervention needs on the current page.
"""
        },
        {
            "name": "Explicit Intervention Request",
            "task": """
This is a direct test of the intervention system. Please immediately use the browser_request_human_help tool 
with the following parameters:
- reason: "Testing intervention system functionality"
- instructions: "This is a test to verify the agent correctly calls intervention tools. Please wait for human interaction through the VNC interface."
- timeout_seconds: 600

Important: Use exactly this JSON format for the Action Input:
{{"reason": "Testing intervention system functionality", "instructions": "This is a test to verify the agent correctly calls intervention tools. Please wait for human interaction through the VNC interface.", "timeout_seconds": 600}}
"""
        }
    ]
    
    results = {}
    
    for i, scenario in enumerate(test_scenarios, 1):
        logger.info(f"\n{'='*80}")
        logger.info(f"🧪 TEST SCENARIO {i}: {scenario['name']}")
        logger.info(f"{'='*80}")
        
        # Reset callback state
        callback_handler.tool_calls = []
        callback_handler.intervention_calls = []
        callback_handler.parsing_errors = []
        
        try:
            logger.info(f"📋 Task: {scenario['task']}")
            
            # Execute the task
            result = agent_executor.invoke({"input": scenario['task']})
            
            # Add debug information about the intervention
            logger.info(f"🔍 DEBUG: Agent result: {result}")
            
            # Check if any interventions were actually created
            if callback_handler.intervention_calls:
                logger.info("📋 INTERVENTION DETAILS:")
                for call in callback_handler.intervention_calls:
                    logger.info(f"  Tool: {call.tool}")
                    logger.info(f"  Input: {call.tool_input}")
                    logger.info(f"  Log excerpt: {call.log[:200]}...")
            
            # Analyze results
            intervention_called = len(callback_handler.intervention_calls) > 0
            parsing_errors = len(callback_handler.parsing_errors) > 0
            
            logger.info("✅ Scenario completed")
            logger.info(f"🆘 Intervention called: {intervention_called}")
            logger.info(f"❌ Parsing errors: {parsing_errors}")
            logger.info(f"🔧 Total tool calls: {len(callback_handler.tool_calls)}")
            
            if callback_handler.intervention_calls:
                logger.info("🆘 Intervention tools used:")
                for call in callback_handler.intervention_calls:
                    logger.info(f"  - {call.tool}: {call.tool_input}")
            
            if callback_handler.parsing_errors:
                logger.error("❌ Parsing errors encountered:")
                for error in callback_handler.parsing_errors:
                    logger.error(f"  - {error}")
            
            results[scenario['name']] = {
                "success": True,
                "intervention_called": intervention_called,
                "parsing_errors": parsing_errors,
                "tool_calls": callback_handler.tool_calls,
                "intervention_calls": callback_handler.intervention_calls
            }
            
        except Exception as e:
            logger.error(f"❌ Scenario failed: {e}")
            results[scenario['name']] = {
                "success": False,
                "error": str(e),
                "intervention_called": False,
                "parsing_errors": True
            }
        
        # Brief pause between scenarios
        await asyncio.sleep(3)
    
    # Final analysis
    logger.info(f"\n{'='*80}")
    logger.info("📊 FINAL ANALYSIS - FIXED AGENT PERFORMANCE")
    logger.info(f"{'='*80}")
    
    total_scenarios = len(test_scenarios)
    successful_scenarios = sum(1 for r in results.values() if r["success"])
    intervention_scenarios = sum(1 for r in results.values() if r.get("intervention_called", False))
    error_scenarios = sum(1 for r in results.values() if r.get("parsing_errors", False))
    
    logger.info(f"📈 Total Scenarios: {total_scenarios}")
    logger.info(f"✅ Successful Scenarios: {successful_scenarios}")
    logger.info(f"🆘 Scenarios with Intervention: {intervention_scenarios}")
    logger.info(f"❌ Scenarios with Parsing Errors: {error_scenarios}")
    
    improvement_percentage = (intervention_scenarios / total_scenarios) * 100
    logger.info(f"📊 Intervention Success Rate: {improvement_percentage:.1f}%")
    
    for name, result in results.items():
        status = "✅" if result["success"] else "❌"
        intervention = "🆘" if result.get("intervention_called", False) else "🤖"
        errors = "❌" if result.get("parsing_errors", False) else "✅"
        logger.info(f"{status} {intervention} {errors} {name}")
        
        if result.get("intervention_calls"):
            for call in result["intervention_calls"]:
                logger.info(f"    └─ Used: {call.tool}")
    
    # Performance comparison
    if intervention_scenarios > 1:  # Previous runs showed 1/3 success
        logger.info("\n🎉 IMPROVEMENT ACHIEVED!")
        logger.info("Previous success rate: ~33% (1/3)")
        logger.info(f"Current success rate: {improvement_percentage:.1f}% ({intervention_scenarios}/{total_scenarios})")
    else:
        logger.warning(f"⚠️ Still need improvements. Success rate: {improvement_percentage:.1f}%")
    
    # Cleanup
    logger.info("🧹 Cleaning up resources...")
    sandbox_manager.delete_sandbox(sandbox_id)
    logger.info("✅ Cleanup completed")
    
    return results


async def main():
    """Main function to run the fixed agent test."""
    try:
        results = await test_fixed_agent()
        
        # Determine success
        intervention_count = sum(1 for r in results.values() if r.get("intervention_called", False))
        success_rate = (intervention_count / len(results)) * 100
        
        if success_rate >= 80:  # 80% or higher success rate
            logger.info(f"🎉 SUCCESS: Fixed agent achieved {success_rate:.1f}% intervention success rate!")
            return 0
        elif success_rate >= 50:  # Some improvement
            logger.warning(f"⚠️ PARTIAL SUCCESS: {success_rate:.1f}% success rate - needs more improvement")
            return 0
        else:
            logger.error(f"❌ STILL ISSUES: Only {success_rate:.1f}% success rate")
            return 1
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
