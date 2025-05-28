import os
import asyncio
from typing import List, Optional
from langchain.agents import Tool
from src.tools.langchain_browser_tool import BrowserToolkit
from src.tools.enhanced_browser_tools import get_enhanced_browser_tools
from src.tools.utilities.sandbox_manager import SandboxManager


async def initialize_browser_tools(api_url: Optional[str] = None, sandbox_id: Optional[str] = None, use_enhanced: bool = True) -> List[Tool]:
    """Initialize and set up browser tools for use with LangChain.
    
    Args:
        api_url (Optional[str]): The base URL for the browser automation API.
                               If not provided, a new sandbox will be created.
        sandbox_id (Optional[str]): The ID of the sandbox running the browser.
        use_enhanced (bool): Whether to use enhanced tools (default: True) or standard tools
    
    Returns:
        List[Tool]: List of LangChain tools for browser automation
    """
    if use_enhanced:
        # Use enhanced tools by default for better intervention support
        return await initialize_enhanced_browser_tools(api_url=api_url, sandbox_id=sandbox_id)
    
    # Fallback to standard tools for backward compatibility
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


def get_browser_tools(api_url: Optional[str] = None, sandbox_id: Optional[str] = None, use_enhanced: bool = True) -> List[Tool]:
    """Get browser tools for use with LangChain (synchronous version).
    
    Args:
        api_url (Optional[str]): The base URL for the browser automation API.
                              If not provided, a new sandbox will be created.
        sandbox_id (Optional[str]): The ID of the sandbox running the browser.
        use_enhanced (bool): Whether to use enhanced tools (default: True) or standard tools
    
    Returns:
        List[Tool]: List of LangChain tools for browser automation
    """
    return asyncio.run(initialize_browser_tools(api_url=api_url, sandbox_id=sandbox_id, use_enhanced=use_enhanced))


async def initialize_enhanced_browser_tools(api_url: Optional[str] = None, sandbox_id: Optional[str] = None) -> List[Tool]:
    """Initialize and set up ENHANCED browser tools for use with LangChain.
    
    Args:
        api_url (Optional[str]): The base URL for the browser automation API.
                               If not provided, a new sandbox will be created.
        sandbox_id (Optional[str]): The ID of the sandbox running the browser.
    
    Returns:
        List[Tool]: List of LangChain tools for enhanced browser automation with intervention support
    """
    # If API URL is not provided, create a new sandbox
    if not api_url:
        sandbox_manager = SandboxManager()
        sandbox_id, cdp_url, _, _, api_url, _, _ = sandbox_manager.create_sandbox()
        # We'll keep the CDP URL as it's needed for browser automation
        if cdp_url:
            os.environ['CHROME_CDP'] = cdp_url
    
    # Get enhanced browser tools
    enhanced_tools = get_enhanced_browser_tools()
    
    # Set API URL and sandbox ID for all enhanced tools
    for tool in enhanced_tools:
        if hasattr(tool, 'api_base_url'):
            tool.api_base_url = api_url
        if hasattr(tool, 'sandbox_id'):
            tool.sandbox_id = sandbox_id
    
    # Convert enhanced tools to LangChain Tool format
    tools = []
    for browser_tool in enhanced_tools:
        # Create a wrapper function that handles the config parameter
        def create_enhanced_tool_wrapper(tool=browser_tool):
            def wrapper(input_str="", *args, config=None, **kwargs):
                import json
                
                def map_parameters_to_api_schema(params_dict, tool_name):
                    """Map parameter names to match exact OpenAPI schema requirements"""
                    if not isinstance(params_dict, dict):
                        return params_dict
                    
                    # Normalize tool name for matching
                    normalized_name = tool_name.lower().replace("smart_", "").replace("browser_", "")
                    
                    # Handle special cases that need parameter restructuring
                    if any(x in normalized_name for x in ["extract_content", "get_page_content"]):
                        # CRITICAL FIX: API expects {"goal": str} object for ExtractContentAction
                        # But implementation uses NoParamsAction - let's try both formats
                        if isinstance(params_dict, str):
                            return {"goal": params_dict}
                        elif "goal" not in params_dict and params_dict:
                            # If no goal specified, use first string value or create default
                            goal_value = next((v for v in params_dict.values() if isinstance(v, str)), "Extract page content")
                            return {"goal": goal_value}
                        elif not params_dict:
                            # Empty dict means use default
                            return {"goal": "Extract page content"}
                        return params_dict
                    
                    elif "wait" in normalized_name:
                        # CRITICAL FIX: WaitAction expects empty object {}
                        return {}
                    
                    elif any(x in normalized_name for x in ["take_screenshot", "go_back", "go_forward", "refresh"]):
                        # NoParamsAction schemas expect empty object
                        return {}
                        
                    elif "search_google" in normalized_name:
                        # Ensure query parameter exists
                        if isinstance(params_dict, str):
                            return {"query": params_dict}
                        elif "query" not in params_dict:
                            query_value = next((v for v in params_dict.values() if isinstance(v, str)), "")
                            return {"query": query_value}
                        return params_dict
                    
                    elif "navigate" in normalized_name:
                        # Ensure url parameter exists  
                        if isinstance(params_dict, str):
                            return {"url": params_dict}
                        elif "url" not in params_dict:
                            url_value = next((v for v in params_dict.values() if isinstance(v, str)), "")
                            return {"url": url_value}
                        return params_dict
                        
                    elif "intervention" in normalized_name and "request" in normalized_name:
                        # Handle intervention requests with proper type mapping
                        mapped = {}
                        for key, value in params_dict.items():
                            if key == "intervention_type" and isinstance(value, str):
                                # Ensure valid intervention type
                                valid_types = ["captcha", "login_required", "security_check", 
                                             "complex_data_entry", "anti_bot_protection", 
                                             "two_factor_auth", "cookies_consent", "age_verification", "custom"]
                                mapped["intervention_type"] = value if value in valid_types else "custom"
                            else:
                                mapped[key] = value
                        return mapped
                    
                    # Handle element interactions with proper parameter mapping
                    elif any(x in normalized_name for x in ['input_text', 'click_element']):
                        mapped_params = {}
                        for key, value in params_dict.items():
                            if key in ['element_index', 'element']:
                                mapped_params['index'] = 0 if isinstance(value, str) else value
                            elif key == 'text':
                                mapped_params['text'] = value
                            elif key == 'selector':
                                mapped_params['selector'] = value
                            else:
                                mapped_params[key] = value
                        return mapped_params
                    
                    # Default: return parameters as-is for other tools
                    return params_dict
                
                def convert_element_descriptions_to_index(params_dict):
                    """Convert string element descriptions to index 0 as fallback"""
                    if not isinstance(params_dict, dict):
                        return params_dict
                        
                    # Convert common element descriptions to index 0
                    element_descriptions = [
                        'search bar', 'search box', 'search field', 'search input',
                        'input field', 'text input', 'input box', 'text field',
                        'button', 'submit button', 'search button',
                        'element', 'first element', 'main element'
                    ]
                    
                    if 'index' in params_dict and isinstance(params_dict['index'], str):
                        desc_lower = params_dict['index'].lower()
                        if any(desc in desc_lower for desc in element_descriptions):
                            params_dict['index'] = 0
                            
                    return params_dict
                
                # Check if tool has args_schema
                if hasattr(tool, 'args_schema') and tool.args_schema is not None:
                    # Use model_fields for Pydantic v2 compatibility, fallback to __fields__ for v1
                    if hasattr(tool.args_schema, 'model_fields'):
                        schema_fields = list(tool.args_schema.model_fields.keys())
                    else:
                        schema_fields = list(tool.args_schema.__fields__.keys())
                    
                    # Tool expects parameters, handle different input formats
                    if kwargs:
                        # Use kwargs directly if provided, but apply parameter mapping
                        mapped_kwargs = map_parameters_to_api_schema(kwargs, tool.name)
                        converted_kwargs = convert_element_descriptions_to_index(mapped_kwargs)
                        return tool._run(**converted_kwargs)
                    elif input_str and input_str.strip():
                        # Try to parse input_str as JSON first for multi-parameter tools
                        try:
                            params = json.loads(input_str)
                            if isinstance(params, dict):
                                # Apply API schema mapping and element description conversion
                                mapped_params = map_parameters_to_api_schema(params, tool.name)
                                converted_params = convert_element_descriptions_to_index(mapped_params)
                                return tool._run(**converted_params)
                            else:
                                # Single parameter tools
                                if len(schema_fields) == 1:
                                    return tool._run(**{schema_fields[0]: params})
                                else:
                                    return tool._run(input_str)
                        except (json.JSONDecodeError, TypeError):
                            # Not JSON, try to handle as simple parameter
                            if len(schema_fields) == 1:
                                # Single parameter tool - use the input_str directly
                                return tool._run(**{schema_fields[0]: input_str})
                            else:
                                # Multi-parameter tool, can't parse as single string
                                return {"success": False, "error": f"Tool {tool.name} requires multiple parameters. Please provide JSON input with keys: {schema_fields}"}
                    else:
                        # Empty input - provide defaults for tools that require parameters
                        if hasattr(tool, 'args_schema') and tool.args_schema:
                            if len(schema_fields) == 1:
                                # Single parameter tool with empty input - use a default value
                                param_name = schema_fields[0]
                                
                                # Provide tool-specific defaults
                                if 'extract_content' in tool.name.lower():
                                    default_value = "Extract page content"
                                elif 'goal' in param_name.lower():
                                    default_value = "Complete the task"
                                elif 'query' in param_name.lower():
                                    default_value = ""
                                elif 'message' in param_name.lower():
                                    default_value = "Task assistance needed"
                                else:
                                    default_value = ""
                                    
                                return tool._run(**{param_name: default_value})
                            else:
                                # Multi-parameter tool with empty input
                                return {"success": False, "error": f"Tool {tool.name} requires parameters. Please provide JSON input with keys: {schema_fields}"}
                        else:
                            # Tool has no parameters, call without arguments
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
                func=create_enhanced_tool_wrapper()
            )
        )
    
    return tools


def get_enhanced_browser_tools_as_langchain(api_url: Optional[str] = None, sandbox_id: Optional[str] = None) -> List[Tool]:
    """Get enhanced browser tools for use with LangChain (synchronous version).
    
    Args:
        api_url (Optional[str]): The base URL for the browser automation API.
        sandbox_id (Optional[str]): The ID of the sandbox running the browser.
    
    Returns:
        List[Tool]: List of enhanced LangChain tools for browser automation with intervention support
    """
    return asyncio.run(initialize_enhanced_browser_tools(api_url=api_url, sandbox_id=sandbox_id))
