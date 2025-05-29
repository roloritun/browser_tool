#!/usr/bin/env python3
"""
Optimized Browser Agent with Enhanced LLM Configuration
======================================================

This version addresses the parsing issues and optimizes the LLM settings
for better performance with browser automation tasks.
"""

import asyncio
import os
import time
from typing import List
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_core.language_models import BaseChatModel
from langchain_openai import AzureChatOpenAI
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv

from src.tools.utilities.browser_tools_init import initialize_browser_tools
from src.tools.utilities.sandbox_manager import SandboxManager
from src.utils.logger import logger

# Load environment variables
load_dotenv()


def create_optimized_browser_agent(tools: List[Tool], llm: BaseChatModel) -> AgentExecutor:
    """Create an optimized LangChain agent with enhanced LLM performance."""
    
    # Highly optimized prompt template for consistent output
    prompt_template = """You are a browser automation expert. Follow this EXACT format for ALL responses:

AVAILABLE TOOLS:
{tools}

TOOL NAMES: {tool_names}

🎯 CRITICAL SUCCESS RULES:
1. ALWAYS end with "Final Answer:" when task is complete
2. Use EXACT tool names from the list above
3. Format tool inputs as valid JSON for multi-parameter tools
4. Use intervention tools for CAPTCHAs, logins, or security challenges

📋 REQUIRED FORMAT (use this EXACTLY):
Thought: [your reasoning about what to do next]
Action: [exact tool name from list]
Action Input: [simple string OR valid JSON object]
Observation: [tool output will appear here]

💡 EXAMPLES:

Simple tool call:
Thought: I need to navigate to Google.com
Action: smart_navigate_to
Action Input: "https://www.google.com"
Observation: [result]

Complex tool call:
Thought: I need to extract specific content from the page
Action: smart_extract_content  
Action Input: {{"goal": "extract first search result title and URL"}}
Observation: [result]

Task completion:
Thought: I have successfully completed the requested task
Final Answer: [clear summary of what was accomplished]

🚨 INTERVENTION EXAMPLES:
Thought: I see a CAPTCHA that needs human verification
Action: smart_solve_captcha
Action Input: {{"reason": "CAPTCHA detected", "instructions": "Please solve the verification challenge"}}
Observation: [result]

USER TASK: {input}

Begin with a Thought about your first step:

{agent_scratchpad}"""

    prompt = PromptTemplate.from_template(prompt_template)
    
    # Create memory
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=False,
        input_key="input"
    )
    
    # Create agent
    agent = create_react_agent(llm, tools, prompt)
    
    # Create optimized agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,  # Better error handling
        max_iterations=12,  # More iterations for complex tasks
        early_stopping_method="force",
        max_execution_time=900,  # 15 minutes
        return_intermediate_steps=True
    )
    
    return agent_executor


async def main_optimized():
    """Main function with optimized LLM settings."""
    logger.info("🚀 Starting OPTIMIZED browser automation demo...")
    
    try:
        # Create sandbox
        sandbox_manager = SandboxManager()
        (sandbox_id, cdp_url, vnc_url, 
         novnc_url, api_base_url, web_url, browser_api_url) = sandbox_manager.create_sandbox()
        
        logger.info(f"🌐 Browser viewer: {novnc_url}")
        logger.info(f"🔑 VNC Password: vncpassword")
        
        # Wait for services
        logger.info("⏳ Waiting for browser API...")
        await asyncio.sleep(30)
        
        # Initialize tools
        tools = await initialize_browser_tools(api_base_url, sandbox_id)
        logger.info(f"✅ Initialized {len(tools)} browser tools")
        
        # Create OPTIMIZED LLM with better settings
        llm = AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            temperature=0.0,  # Maximum determinism for consistent output
            max_tokens=4000,  # More tokens for complex reasoning
            top_p=0.05,  # Very focused sampling
            frequency_penalty=0.0,
            presence_penalty=0.0,
            request_timeout=60,  # Longer timeout
            max_retries=3  # Retry failed requests
        )
        
        # Create optimized agent
        agent_executor = create_optimized_browser_agent(tools, llm)
        
        logger.info("🧪 Testing optimized agent with complex task...")
        
        # Test with a more comprehensive task
        test_task = """
Navigate to Google.com and search for 'browser automation'. 
Extract the title and URL of the first search result.
If you encounter any CAPTCHAs or security challenges, use intervention tools.
Provide a clear summary of what you found.
"""
        
        start_time = time.time()
        result = agent_executor.invoke({"input": test_task})
        duration = time.time() - start_time
        
        logger.info(f"✅ Task completed in {duration:.2f} seconds")
        logger.info(f"🎯 Result: {result.get('output', 'No output')}")
        
        # Analyze the execution
        if result.get('output') and 'Final Answer:' in str(result.get('output', '')):
            logger.info("🎉 SUCCESS: Agent properly completed task with Final Answer")
        else:
            logger.warning("⚠️ PARSING ISSUE: Agent didn't provide proper Final Answer")
        
        # Show intermediate steps
        if result.get('intermediate_steps'):
            logger.info(f"🔍 Executed {len(result['intermediate_steps'])} steps")
            for i, (action, observation) in enumerate(result['intermediate_steps'], 1):
                logger.info(f"  Step {i}: {action.tool} -> {str(observation)[:100]}...")
        
        # Cleanup
        logger.info("🧹 Cleaning up...")
        sandbox_manager.delete_sandbox(sandbox_id)
        
        return 0 if 'Final Answer:' in str(result.get('output', '')) else 1
        
    except Exception as e:
        logger.error(f"❌ Optimized demo failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main_optimized())
    print(f"\n{'='*60}")
    if exit_code == 0:
        print("🎉 OPTIMIZED AGENT: SUCCESS")
        print("✅ Proper output formatting achieved")
        print("✅ Task completion confirmed")
    else:
        print("⚠️ OPTIMIZED AGENT: NEEDS IMPROVEMENT")
        print("❌ Output formatting issues persist")
    print(f"{'='*60}")
    exit(exit_code)
