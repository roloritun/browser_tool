#!/usr/bin/env python3
"""
Example of using the browser tools with an existing API URL.
This is useful when you want to reuse an existing browser sandbox
instead of creating a new one each time.
"""

import asyncio
import os
import sys
from typing import List, Dict
from dotenv import load_dotenv
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_core.language_models import BaseChatModel
from langchain_openai import AzureChatOpenAI

from src.tools.utilities.browser_tools_init import get_browser_tools
from src.utils.logger import logger

# Load environment variables from .env file
load_dotenv()


def create_browser_agent(tools: List[Tool], llm: BaseChatModel) -> AgentExecutor:
    """Create a LangChain agent with browser tools.
    
    Args:
        tools (List[Tool]): List of browser tools
        llm (BaseChatModel): Language model for the agent
        
    Returns:
        AgentExecutor: Agent executor that can use browser tools
    """
    prompt_template = """You are a browser automation assistant. You can help users automate web browsing tasks.
You have access to the following tools:

{tools}

Use the tools to help the user accomplish their task.
Always use one tool at a time and wait for the result before using another tool.
If you don't know how to solve a problem with the given tools, just say so.

User: {input}
Agent: """

    prompt = PromptTemplate.from_template(prompt_template)
    
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
    )
    
    return agent_executor


async def run_single_task(api_url: str, task: str) -> Dict:
    """Run a single browser automation task.
    
    Args:
        api_url (str): The base URL for the browser automation API
        task (str): The task to perform
        
    Returns:
        Dict: Result of the task
    """
    # Create LLM
    logger.info("Initializing Azure OpenAI language model...")
    llm = AzureChatOpenAI(
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15"),
        temperature=0.2
    )
    
    # Get browser tools using the provided API URL
    logger.info(f"Initializing browser tools with API URL: {api_url}")
    browser_tools = get_browser_tools(api_url=api_url)
    logger.info(f"Successfully initialized {len(browser_tools)} browser tools")
    
    # Create agent
    agent_executor = create_browser_agent(browser_tools, llm)
    
    # Run the task
    logger.info(f"Running browser automation task: {task}")
    result = await agent_executor.ainvoke({"input": task})
    
    logger.info("Task completed")
    return result


async def main_async():
    """Main async function to demonstrate browser tools with existing API URL."""
    try:
        # Get the API URL from environment variables
        api_url = os.getenv("BROWSER_API_URL")
        
        if not api_url:
            logger.error("BROWSER_API_URL not found in environment variables.")
            logger.error("Please set BROWSER_API_URL in your .env file.")
            return 1
        
        # Example task
        task = "Navigate to example.com, wait 3 seconds, and then extract the main content."
        
        # Run the task
        result = await run_single_task(api_url, task)
        logger.info(f"Agent execution completed: {result}")
        
    except Exception as e:
        logger.error(f"Error in browser automation demo: {str(e)}")
        return 1
    
    return 0


def main():
    """Main function to run the browser automation demo with existing API."""
    logger.info("Starting browser automation demo with existing API URL...")
    
    try:
        exit_code = asyncio.run(main_async())
        logger.info("Demo completed")
        return exit_code
    except KeyboardInterrupt:
        logger.info("Demo interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
