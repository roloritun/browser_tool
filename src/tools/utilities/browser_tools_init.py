import os
import asyncio
from typing import List, Optional
from langchain.agents import Tool
from src.tools.langchain_browser_tool import BrowserToolkit
from src.tools.utilities.sandbox_manager import SandboxManager


async def initialize_browser_tools(api_url: Optional[str] = None, sandbox_id: Optional[str] = None) -> List[Tool]:
    """Initialize and set up browser tools for use with LangChain.
    
    Args:
        api_url (Optional[str]): The base URL for the browser automation API.
                               If not provided, a new sandbox will be created.
        sandbox_id (Optional[str]): The ID of the sandbox running the browser.
    
    Returns:
        List[Tool]: List of LangChain tools for browser automation
    """
    # If API URL is not provided, create a new sandbox
    if not api_url:
        sandbox_manager = SandboxManager()
        sandbox_id, cdp_url, _, _, api_url, _, _ = sandbox_manager.create_sandbox()
        # We'll keep the CDP URL as it's needed for browser automation
        if cdp_url:
            os.environ['CHROME_CDP'] = cdp_url
    
    # Initialize toolkit with the API URL
    toolkit = BrowserToolkit(api_url=api_url, sandbox_id=sandbox_id)
    setup_result = await toolkit.setup()
    
    if not setup_result["success"]:
        raise Exception(f"Failed to set up browser tools: {setup_result.get('error', 'Unknown error')}")
    
    # Convert to LangChain Tool format
    tools = []
    for browser_tool in toolkit.get_tools():
        tools.append(
            Tool(
                name=browser_tool.name,
                description=browser_tool.description,
                func=browser_tool._run
            )
        )
    
    return tools


def get_browser_tools(api_url: Optional[str] = None, sandbox_id: Optional[str] = None) -> List[Tool]:
    """Get browser tools for use with LangChain (synchronous version).
    
    Args:
        api_url (Optional[str]): The base URL for the browser automation API.
                              If not provided, a new sandbox will be created.
        sandbox_id (Optional[str]): The ID of the sandbox running the browser.
    
    Returns:
        List[Tool]: List of LangChain tools for browser automation
    """
    return asyncio.run(initialize_browser_tools(api_url=api_url, sandbox_id=sandbox_id))
