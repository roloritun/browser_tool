#!/usr/bin/env python3
"""
Improved browser agent implementation with fixed intervention tool calling.
This version addresses the core issues identified in the debug testing.
"""

import asyncio
import sys
import time
import warnings
from typing import List
import webbrowser
import os
import sys
from pathlib import Path
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_core.language_models import BaseChatModel
from langchain_openai import AzureChatOpenAI
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv

from src.tools.utilities.browser_tools_init import initialize_browser_tools
from src.tools.utilities.sandbox_manager import SandboxManager
from src.utils.logger import logger

# Load environment variables from .env file
load_dotenv()

# Suppress LangChain deprecation warnings to reduce noise
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langchain")


def create_improved_browser_agent(tools: List[Tool], llm: BaseChatModel) -> AgentExecutor:
    """Create an improved LangChain agent with enhanced intervention capabilities.
    
    Args:
        tools (List[Tool]): List of browser tools
        llm (BaseChatModel): Language model for the agent
        
    Returns:
        AgentExecutor: Agent executor that properly uses intervention tools
    """
    
    # Enhanced prompt template with clear intervention guidelines
    prompt_template = """You are an intelligent browser automation assistant with human intervention capabilities.

AVAILABLE TOOLS:
{tools}

TOOL NAMES: {tool_names}

🆘 HUMAN INTERVENTION RULES - FOLLOW THESE STRICTLY:
1. CAPTCHA Detection: If you see ANY CAPTCHA, image verification, "I'm not a robot", reCAPTCHA, or hCaptcha → Use browser_solve_captcha
2. Login Requirements: If you encounter login forms, password fields, or authentication → Use browser_handle_login
3. Security Challenges: If you see security verification, anti-bot measures, or access blocks → Use browser_request_human_help
4. Unknown Scenarios: If you're unsure or stuck → Use browser_request_human_help
5. Auto-Detection: Use browser_auto_detect_intervention to check if current page needs intervention

🔧 TOOL CALLING FORMAT - USE EXACTLY THIS FORMAT:
Thought: I need to [explain what you're thinking]
Action: [exact tool name]
Action Input: [for single parameter: "value" | for multiple parameters: {{"param1": "value1", "param2": "value2"}}]
Observation: [result will appear here]

EXAMPLES OF CORRECT INTERVENTION USAGE:

Example 1 - CAPTCHA detected:
Thought: I can see a CAPTCHA challenge on this page that requires human verification.
Action: browser_solve_captcha
Action Input: {{"reason": "CAPTCHA detected on page", "instructions": "Please solve the image verification"}}
Observation: [result]

Example 2 - Login form found:
Thought: There's a login form that requires credentials to be entered.
Action: browser_handle_login
Action Input: {{"reason": "Login required", "field_type": "login", "instructions": "Please enter username and password"}}
Observation: [result]

Example 3 - General help needed:
Thought: I need human assistance to complete this complex task.
Action: browser_request_human_help
Action Input: {{"reason": "Complex task requiring human guidance", "instructions": "Please help complete the form"}}
Observation: [result]

⚠️ CRITICAL REQUIREMENTS:
- ALWAYS check page content after navigation for intervention needs
- DO NOT try to solve CAPTCHAs yourself - always use browser_solve_captcha
- DO NOT guess login credentials - always use browser_handle_login
- Use browser_wait after navigation to ensure page loads
- Extract page content to understand what's on the page
- When in doubt, ask for human help

USER REQUEST: {input}

Think step-by-step and use the exact format above:

{agent_scratchpad}"""

    prompt = PromptTemplate.from_template(prompt_template)
    
    # Create memory for conversation context
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=False,
        input_key="input"
        # Removed output_key to avoid deprecation warnings in newer LangChain versions
    )
    
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors="Check your output format. Use: Thought: [reasoning], Action: [exact tool name], Action Input: [valid input]",
        max_iterations=8,
        early_stopping_method="force",
        max_execution_time=600  # 10 minutes
    )
    
    return agent_executor


def generate_and_open_viewer(vnc_url: str, novnc_url: str, vnc_password: str = "secret"):
    """Generate and open an HTML viewer for VNC and noVNC URLs and password."""
    try:
        # Get the template path - navigate to src/tools/templates from examples/basic
        base_path = Path(__file__).parent.parent.parent  # Go up to project root
        template_path = base_path / "tools" / "templates" / "viewer.html"
        output_path = base_path / "tools" / "templates" / "current_viewer.html"

        # Read the template
        with open(template_path, "r") as f:
            template_content = f.read()

        # Replace placeholders
        html_content = (template_content
            .replace("__VNC_URL__", vnc_url)
            .replace("__NOVNC_URL__", novnc_url)
            .replace("__VNC_PASSWORD__", vnc_password))

        # Write the generated HTML
        os.makedirs(output_path.parent, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(html_content)

        # Open in browser
        webbrowser.open(f"file://{output_path}")
        logger.info(f"Opened viewer at: {output_path}")

    except Exception as e:
        logger.error(f"Failed to generate or open viewer: {str(e)}")


async def main_async():
    """Main async function to demonstrate improved browser tools."""
    try:
        logger.info("🚀 Initializing improved browser automation agent...")
        
        # Create sandbox and get URLs
        sandbox_manager = SandboxManager()
        sandbox_id, cdp_url, vnc_url, novnc_url, api_url, web_url, x_url = sandbox_manager.create_sandbox()
        
        # Generate and open the viewer
        generate_and_open_viewer(vnc_url, novnc_url, vnc_password="vncpassword")
        
        # Wait for API to be ready and initialize tools with retry
        logger.info("⏳ Waiting for browser API to be ready...")
        max_retries = 30
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                from src.tools.utilities.browser_tools_init import initialize_browser_tools
                tools = await initialize_browser_tools(api_url, sandbox_id)
                if tools:
                    logger.info(f"✅ Successfully initialized {len(tools)} browser tools")
                    break
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                else:
                    raise Exception(f"Failed to initialize tools after {max_retries} attempts: {e}")
        
        # Log available intervention tools
        intervention_tools = [tool for tool in tools if any(keyword in tool.name.lower() 
                             for keyword in ["intervention", "human", "captcha", "login"])]
        logger.info(f"🆘 Available intervention tools ({len(intervention_tools)}):")
        for tool in intervention_tools:
            logger.info(f"  - {tool.name}: {tool.description}")
        
        # Initialize Azure OpenAI with optimal settings for tool calling
        llm = AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            temperature=0.0,  # Deterministic for better tool calling
            max_tokens=2000,
            top_p=0.1  # Moved from model_kwargs to fix deprecation warning
        )
        
        # Create the improved agent
        agent_executor = create_improved_browser_agent(tools, llm)
        
        logger.info(f"🌐 Browser viewer: {novnc_url}")
        logger.info(f"🔑 VNC Password: vncpassword")
        
        # Example usage with basic demo scenario
        logger.info("Running example browser automation task...")
        result = agent_executor.invoke({
            "input": "Navigate to Google.com and search for 'LangChain'. Extract the first result's title and URL. If you encounter any CAPTCHAs or security challenges, use the appropriate intervention tools."
        })
        
        logger.info(f"Agent execution completed: {result}")
        
        # Interactive mode for manual testing
        logger.info(f"\n🤖 Agent is ready for interactive testing!")
        logger.info(f"🌐 Browser access: {novnc_url}")
        logger.info(f"🔑 VNC Password: vncpassword")
        
    except Exception as e:
        logger.error(f"❌ Error in main: {e}")
        raise


def main():
    """Main function to run the improved demo."""
    start_time = time.time()
    logger.info("Starting improved browser automation demo...")
    
    try:
        exit_code = asyncio.run(main_async())
        elapsed_time = time.time() - start_time
        logger.info(f"Demo completed in {elapsed_time:.2f} seconds")
        return exit_code
    except KeyboardInterrupt:
        logger.info("Demo interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
