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
        # Create a wrapper function that handles the config parameter
        # Use default parameter to capture the tool in closure properly
        def create_tool_wrapper(tool=browser_tool):
            def wrapper(input_str="", *args, config=None, **kwargs):
                import json
                
                # Check if tool has args_schema and if it's NoParamsInput
                if hasattr(tool, 'args_schema') and tool.args_schema is not None:
                    from src.tools.langchain_browser_tool import NoParamsInput
                    if tool.args_schema == NoParamsInput:
                        # Tool doesn't need parameters, call without arguments
                        return tool._run()
                    else:
                        # Tool expects parameters, handle different input formats
                        if kwargs:
                            # Use kwargs directly if provided
                            return tool._run(**kwargs)
                        elif input_str and input_str.strip():
                            # Try to parse input_str as JSON first for multi-parameter tools
                            try:
                                params = json.loads(input_str)
                                if isinstance(params, dict):
                                    return tool._run(**params)
                                else:
                                    # Single parameter tools
                                    schema_fields = list(tool.args_schema.__fields__.keys())
                                    if len(schema_fields) == 1:
                                        return tool._run(**{schema_fields[0]: params})
                                    else:
                                        return tool._run(input_str)
                            except (json.JSONDecodeError, TypeError):
                                # Not JSON, try to handle as simple parameter
                                schema_fields = list(tool.args_schema.__fields__.keys())
                                if len(schema_fields) == 1:
                                    # Single parameter tool
                                    return tool._run(**{schema_fields[0]: input_str})
                                else:
                                    # Multi-parameter tool, can't parse as single string
                                    return {"success": False, "error": f"Tool {tool.name} requires multiple parameters. Please provide JSON input with keys: {schema_fields}"}
                        else:
                            return tool._run()
                else:
                    # No args_schema, call without arguments
                    return tool._run()
            wrapper.__name__ = f"{tool.name}_wrapper"
            return wrapper

        tools.append(
            Tool(
                name=browser_tool.name,
                description=browser_tool.description,
                func=create_tool_wrapper()
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
