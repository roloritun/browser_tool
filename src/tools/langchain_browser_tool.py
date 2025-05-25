import json
import httpx
import asyncio
from typing import Dict, Any, Optional, List, Union, Type
from functools import wraps

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from src.utils.logger import logger
from src.tools.utilities.human_intervention import HumanInterventionInput, CaptchaInput, LoginInput


class BrowserToolBase(BaseTool):
    """Base class for browser automation tools using FastAPI backend."""
    
    name: str
    description: str
    api_base_url: Optional[str] = None
    sandbox_id: Optional[str] = None
    
    class Config:
        """Configuration for this pydantic object."""
        arbitrary_types_allowed = True
    
    @staticmethod
    def requires_setup(func):
        """Decorator to ensure API base URL is set before making requests."""
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self.api_base_url:
                return {
                    "success": False,
                    "error": "Browser tool not initialized. Call setup() first."
                }
            return func(self, *args, **kwargs)
        return wrapper
    
    async def setup(self, api_url: Optional[str] = None, sandbox_id: Optional[str] = None):
        """Set up the tool with API URL.
        
        Args:
            api_url (Optional[str]): The base URL for the browser automation API
            sandbox_id (Optional[str]): The ID of the sandbox running the browser
            
        Returns:
            Dict[str, Any]: Setup result status
        """
        # If API URL is already set, just return
        if self.api_base_url and not api_url:
            logger.info("Browser tool already set up.")
            return {"success": True, "message": "Already set up"}
        
        # Update API URL if provided
        if api_url:
            self.api_base_url = api_url
            
        # Update sandbox ID if provided
        if sandbox_id:
            self.sandbox_id = sandbox_id
            
        try:
            # Test connection with health check
            if self.api_base_url:
                async with httpx.AsyncClient() as client:
                    # Check browser API health on port 8002
                    api_health_url = f"{self.api_base_url}/api"
                    response = await client.get(api_health_url)
                    if response.status_code != 200:
                        raise Exception(f"Browser API health check failed: {response.text}")
                
                logger.info(f"Browser tool set up successfully with API URL: {self.api_base_url}")
                return {"success": True, "message": "Setup complete", "api_url": self.api_base_url}
            else:
                return {"success": False, "error": "No API URL provided"}
        
        except Exception as e:
            logger.error(f"Failed to set up browser tool: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _execute_browser_action(self, endpoint: str, data: Any = None, method: str = "POST") -> Dict[str, Any]:
        """Execute a browser action by calling the FastAPI endpoint.
        
        Args:
            endpoint (str): API endpoint path
            data (Any, optional): Request data. Defaults to None.
            method (str, optional): HTTP method. Defaults to "POST".
            
        Returns:
            Dict[str, Any]: Response from the API
        """
        if not self.api_base_url:
            return {"success": False, "error": "API base URL not set. Call setup() first."}
        
        url = f"{self.api_base_url}/api/automation/{endpoint}"
        logger.debug(f"Calling {method} {url} with data: {data}")
        
        try:
            async with httpx.AsyncClient() as client:
                if method == "POST":
                    response = await client.post(url, json=data)
                elif method == "GET":
                    response = await client.get(url)
                else:
                    return {"success": False, "error": f"Unsupported HTTP method: {method}"}
                
                if response.status_code >= 400:
                    error_message = f"API request failed with status {response.status_code}: {response.text}"
                    logger.error(error_message)
                    return {"success": False, "error": error_message}
                
                result = response.json() if response.headers.get("content-type") == "application/json" else response.text
                return {"success": True, "data": result}
                
        except Exception as e:
            error_message = f"Error executing browser action: {str(e)}"
            logger.error(error_message)
            return {"success": False, "error": error_message}


# Define input schemas for different browser actions
class NavigateUrlInput(BaseModel):
    url: str = Field(..., description="The URL to navigate to")

class SearchGoogleInput(BaseModel):
    query: str = Field(..., description="The search query to use")

class ClickElementInput(BaseModel):
    index: int = Field(..., description="The index of the element to click")

class InputTextInput(BaseModel):
    index: int = Field(..., description="The index of the element to input text into")
    text: str = Field(..., description="The text to input")

class SendKeysInput(BaseModel):
    keys: str = Field(..., description="The keys to send (e.g., 'Enter', 'Escape', 'Control+a')")

class SwitchTabInput(BaseModel):
    page_id: int = Field(..., description="The ID of the tab to switch to")

class OpenTabInput(BaseModel):
    url: str = Field(..., description="The URL to open in the new tab")

class CloseTabInput(BaseModel):
    page_id: int = Field(..., description="The ID of the tab to close")

class ExtractContentInput(BaseModel):
    goal: str = Field(..., description="The extraction goal (e.g., 'extract all links', 'find product information')")

class ScrollInput(BaseModel):
    amount: Optional[int] = Field(None, description="Pixel amount to scroll (if not specified, scrolls one page)")

class ScrollToTextInput(BaseModel):
    text: str = Field(..., description="The text to scroll to")

class GetDropdownOptionsInput(BaseModel):
    index: int = Field(..., description="The index of the dropdown element")

class SelectDropdownOptionInput(BaseModel):
    index: int = Field(..., description="The index of the dropdown element")
    option_text: str = Field(..., description="The text of the option to select")

class ClickCoordinatesInput(BaseModel):
    x: int = Field(..., description="The X coordinate to click")
    y: int = Field(..., description="The Y coordinate to click")

class DragDropInput(BaseModel):
    element_source: Optional[str] = Field(None, description="The source element selector")
    element_target: Optional[str] = Field(None, description="The target element selector") 
    coord_source_x: Optional[int] = Field(None, description="The source X coordinate")
    coord_source_y: Optional[int] = Field(None, description="The source Y coordinate")
    coord_target_x: Optional[int] = Field(None, description="The target X coordinate")
    coord_target_y: Optional[int] = Field(None, description="The target Y coordinate")
    steps: Optional[int] = Field(10, description="Number of steps for the drag operation")
    delay_ms: Optional[int] = Field(5, description="Delay between steps in milliseconds")


# Browser navigation tools
class NavigateToTool(BrowserToolBase):
    name: str = "browser_navigate_to"
    description: str = "Navigate to a specific URL"
    args_schema: Optional[Type[BaseModel]] = NavigateUrlInput
    
    @BrowserToolBase.requires_setup
    def _run(self, url: str) -> Dict[str, Any]:
        logger.info(f"Navigating to URL: {url}")
        result = asyncio.run(self._execute_browser_action("navigate_to", {"url": url}))
        return result


class SearchGoogleTool(BrowserToolBase):
    name: str = "browser_search_google"
    description: str = "Search Google with the provided query"
    args_schema: Optional[Type[BaseModel]] = SearchGoogleInput
    
    @BrowserToolBase.requires_setup
    def _run(self, query: str) -> Dict[str, Any]:
        result = asyncio.run(self._execute_browser_action("search_google", {"query": query}))
        return result


class GoBackTool(BrowserToolBase):
    name: str = "browser_go_back"
    description: str = "Navigate back in browser history"
    
    @BrowserToolBase.requires_setup
    def _run(self) -> Dict[str, Any]:
        result = asyncio.run(self._execute_browser_action("go_back", {}))
        return result


class WaitTool(BrowserToolBase):
    name: str = "browser_wait"
    description: str = "Wait for a specified number of seconds"
    
    @BrowserToolBase.requires_setup
    def _run(self, seconds: int = 3) -> Dict[str, Any]:
        result = asyncio.run(self._execute_browser_action("wait", seconds))
        return result


# Interaction tools
class ClickElementTool(BrowserToolBase):
    name: str = "browser_click_element"
    description: str = "Click on an element by index"
    args_schema: Optional[Type[BaseModel]] = ClickElementInput
    
    @BrowserToolBase.requires_setup
    def _run(self, index: int) -> Dict[str, Any]:
        result = asyncio.run(self._execute_browser_action("click_element", {"index": index}))
        return result


class InputTextTool(BrowserToolBase):
    name: str = "browser_input_text"
    description: str = "Input text into an element"
    args_schema: Optional[Type[BaseModel]] = InputTextInput
    
    @BrowserToolBase.requires_setup
    def _run(self, index: int, text: str) -> Dict[str, Any]:
        result = asyncio.run(self._execute_browser_action("input_text", {"index": index, "text": text}))
        return result


class SendKeysTool(BrowserToolBase):
    name: str = "browser_send_keys"
    description: str = "Send keyboard keys such as Enter, Escape, or keyboard shortcuts"
    args_schema: Optional[Type[BaseModel]] = SendKeysInput
    
    @BrowserToolBase.requires_setup
    def _run(self, keys: str) -> Dict[str, Any]:
        result = asyncio.run(self._execute_browser_action("send_keys", {"keys": keys}))
        return result


# Tab management tools
class SwitchTabTool(BrowserToolBase):
    name: str = "browser_switch_tab"
    description: str = "Switch to a different browser tab"
    args_schema: Optional[Type[BaseModel]] = SwitchTabInput
    
    @BrowserToolBase.requires_setup
    def _run(self, page_id: int) -> Dict[str, Any]:
        result = asyncio.run(self._execute_browser_action("switch_tab", {"page_id": page_id}))
        return result


class OpenTabTool(BrowserToolBase):
    name: str = "browser_open_tab"
    description: str = "Open a new browser tab with the specified URL"
    args_schema: Optional[Type[BaseModel]] = OpenTabInput
    
    @BrowserToolBase.requires_setup
    def _run(self, url: str) -> Dict[str, Any]:
        result = asyncio.run(self._execute_browser_action("open_tab", {"url": url}))
        return result


class CloseTabTool(BrowserToolBase):
    name: str = "browser_close_tab"
    description: str = "Close a browser tab"
    args_schema: Optional[Type[BaseModel]] = CloseTabInput
    
    @BrowserToolBase.requires_setup
    def _run(self, page_id: int) -> Dict[str, Any]:
        result = asyncio.run(self._execute_browser_action("close_tab", {"page_id": page_id}))
        return result


# Content extraction tool
class ExtractContentTool(BrowserToolBase):
    name: str = "browser_extract_content"
    description: str = "Extract content from the current page based on the provided goal"
    args_schema: Optional[Type[BaseModel]] = ExtractContentInput
    
    @BrowserToolBase.requires_setup
    def _run(self, goal: str) -> Dict[str, Any]:
        result = asyncio.run(self._execute_browser_action("extract_content", goal))
        return result


# Scrolling tools
class ScrollDownTool(BrowserToolBase):
    name: str = "browser_scroll_down"
    description: str = "Scroll down the page"
    args_schema: Optional[Type[BaseModel]] = ScrollInput
    
    @BrowserToolBase.requires_setup
    def _run(self, amount: Optional[int] = None) -> Dict[str, Any]:
        data = {"amount": amount} if amount is not None else {}
        result = asyncio.run(self._execute_browser_action("scroll_down", data))
        return result


class ScrollUpTool(BrowserToolBase):
    name: str = "browser_scroll_up"
    description: str = "Scroll up the page"
    args_schema: Optional[Type[BaseModel]] = ScrollInput
    
    @BrowserToolBase.requires_setup
    def _run(self, amount: Optional[int] = None) -> Dict[str, Any]:
        result = asyncio.run(self._execute_browser_action("scroll_up", {"amount": amount} if amount else {}))
        return result


class ScrollToTextTool(BrowserToolBase):
    name: str = "browser_scroll_to_text"
    description: str = "Scroll to specific text on the page"
    args_schema: Optional[Type[BaseModel]] = ScrollToTextInput
    
    @BrowserToolBase.requires_setup
    def _run(self, text: str) -> Dict[str, Any]:
        result = asyncio.run(self._execute_browser_action("scroll_to_text", text))
        return result


# Dropdown tools
class GetDropdownOptionsTool(BrowserToolBase):
    name: str = "browser_get_dropdown_options"
    description: str = "Get all options from a dropdown element"
    args_schema: Optional[Type[BaseModel]] = GetDropdownOptionsInput
    
    @BrowserToolBase.requires_setup
    def _run(self, index: int) -> Dict[str, Any]:
        result = asyncio.run(self._execute_browser_action("get_dropdown_options", index))
        return result


class SelectDropdownOptionTool(BrowserToolBase):
    name: str = "browser_select_dropdown_option"
    description: str = "Select an option from a dropdown by text"
    args_schema: Optional[Type[BaseModel]] = SelectDropdownOptionInput
    
    @BrowserToolBase.requires_setup
    def _run(self, index: int, option_text: str) -> Dict[str, Any]:
        result = asyncio.run(self._execute_browser_action("select_dropdown_option", 
                                                         {"index": index, "option_text": option_text}))
        return result


# Advanced interaction tools
class ClickCoordinatesTool(BrowserToolBase):
    name: str = "browser_click_coordinates"
    description: str = "Click at specific X,Y coordinates on the page"
    args_schema: Optional[Type[BaseModel]] = ClickCoordinatesInput
    
    @BrowserToolBase.requires_setup
    def _run(self, x: int, y: int) -> Dict[str, Any]:
        result = asyncio.run(self._execute_browser_action("click_coordinates", {"x": x, "y": y}))
        return result


class DragDropTool(BrowserToolBase):
    name: str = "browser_drag_drop"
    description: str = "Perform drag and drop operation between elements or coordinates"
    args_schema: Optional[Type[BaseModel]] = DragDropInput
    
    @BrowserToolBase.requires_setup
    def _run(self, 
             element_source: Optional[str] = None, 
             element_target: Optional[str] = None,
             coord_source_x: Optional[int] = None,
             coord_source_y: Optional[int] = None,
             coord_target_x: Optional[int] = None,
             coord_target_y: Optional[int] = None,
             steps: int = 10,
             delay_ms: int = 5) -> Dict[str, Any]:
        
        data = {
            "element_source": element_source,
            "element_target": element_target,
            "coord_source_x": coord_source_x,
            "coord_source_y": coord_source_y,
            "coord_target_x": coord_target_x,
            "coord_target_y": coord_target_y,
            "steps": steps,
            "delay_ms": delay_ms
        }
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}
        
        result = asyncio.run(self._execute_browser_action("drag_drop", data))
        return result


# PDF tools
class SavePdfTool(BrowserToolBase):
    name: str = "browser_save_pdf"
    description: str = "Save the current page as a PDF"
    
    @BrowserToolBase.requires_setup
    def _run(self) -> Dict[str, Any]:
        result = asyncio.run(self._execute_browser_action("save_pdf"))
        return result


class GeneratePdfTool(BrowserToolBase):
    name: str = "browser_generate_pdf"
    description: str = "Generate a PDF of the current page and return as base64 encoded string"
    
    @BrowserToolBase.requires_setup
    def _run(self, options: Dict[str, Any] = None) -> Dict[str, Any]:
        result = asyncio.run(self._execute_browser_action("generate_pdf", options or {}))
        return result


# Cookie and storage tools
class GetCookiesTool(BrowserToolBase):
    name: str = "browser_get_cookies"
    description: str = "Get all cookies for the current page"
    
    @BrowserToolBase.requires_setup
    def _run(self) -> Dict[str, Any]:
        result = asyncio.run(self._execute_browser_action("get_cookies", method="POST"))
        return result


class SetCookieTool(BrowserToolBase):
    name: str = "browser_set_cookie"
    description: str = "Set a cookie for the current page"
    
    @BrowserToolBase.requires_setup
    def _run(self, cookie_data: Dict[str, Any]) -> Dict[str, Any]:
        result = asyncio.run(self._execute_browser_action("set_cookie", cookie_data))
        return result


class ClearCookiesTool(BrowserToolBase):
    name: str = "browser_clear_cookies"
    description: str = "Clear all cookies for the current page"
    
    @BrowserToolBase.requires_setup
    def _run(self) -> Dict[str, Any]:
        result = asyncio.run(self._execute_browser_action("clear_cookies", {}))
        return result


class ClearLocalStorageTool(BrowserToolBase):
    name: str = "browser_clear_local_storage"
    description: str = "Clear local storage for the current page"
    
    @BrowserToolBase.requires_setup
    def _run(self) -> Dict[str, Any]:
        result = asyncio.run(self._execute_browser_action("clear_local_storage", {}))
        return result


# Dialog handling tools
class AcceptDialogTool(BrowserToolBase):
    name: str = "browser_accept_dialog"
    description: str = "Set up handler to accept any dialog (alert, confirm, prompt) that appears"
    
    @BrowserToolBase.requires_setup
    def _run(self) -> Dict[str, Any]:
        result = asyncio.run(self._execute_browser_action("accept_dialog", {}))
        return result


class DismissDialogTool(BrowserToolBase):
    name: str = "browser_dismiss_dialog"
    description: str = "Set up handler to dismiss any dialog (alert, confirm, prompt) that appears"
    
    @BrowserToolBase.requires_setup
    def _run(self) -> Dict[str, Any]:
        result = asyncio.run(self._execute_browser_action("dismiss_dialog", {}))
        return result


# Frame handling tools
class SwitchToFrameTool(BrowserToolBase):
    name: str = "browser_switch_to_frame"
    description: str = "Switch to a specific iframe on the page"
    
    @BrowserToolBase.requires_setup
    def _run(self, frame_data: Dict[str, Any]) -> Dict[str, Any]:
        result = asyncio.run(self._execute_browser_action("switch_to_frame", frame_data))
        return result


class SwitchToMainFrameTool(BrowserToolBase):
    name: str = "browser_switch_to_main_frame"
    description: str = "Switch back to the main frame (top-level document)"
    
    @BrowserToolBase.requires_setup
    def _run(self) -> Dict[str, Any]:
        result = asyncio.run(self._execute_browser_action("switch_to_main_frame", {}))
        return result


# Network conditions tool
class SetNetworkConditionsTool(BrowserToolBase):
    name: str = "browser_set_network_conditions"
    description: str = "Set network conditions for the current page"
    
    @BrowserToolBase.requires_setup
    def _run(self, network_data: Dict[str, Any]) -> Dict[str, Any]:
        result = asyncio.run(self._execute_browser_action("set_network_conditions", network_data))
        return result


# Human Intervention Tools
class RequestHumanHelpTool(BrowserToolBase):
    name: str = "browser_request_human_help"
    description: str = "Request human intervention for complex tasks, captchas, or unknown information"
    args_schema: Optional[Type[BaseModel]] = HumanInterventionInput
    
    @BrowserToolBase.requires_setup
    def _run(self, reason: str, instructions: Optional[str] = None, timeout_seconds: int = 300) -> Dict[str, Any]:
        logger.info(f"Requesting human help: {reason}")
        if instructions:
            logger.info(f"Instructions for human: {instructions}")
        
        # Wait for user input
        try:
            print("\n🤖 -> 🧑‍💻 Human help needed!")
            print(f"Reason: {reason}")
            if instructions:
                print(f"Instructions: {instructions}")
            input("Press Enter when you're done...")
            return {"success": True, "message": "Human intervention completed"}
        except KeyboardInterrupt:
            return {"success": False, "error": "Human intervention cancelled"}

class SolveCaptchaTool(BrowserToolBase):
    name: str = "browser_solve_captcha"
    description: str = "Request human help to solve a CAPTCHA"
    args_schema: Optional[Type[BaseModel]] = CaptchaInput
    
    @BrowserToolBase.requires_setup
    def _run(self, reason: str, instructions: Optional[str] = None, 
             screenshot: bool = True, timeout_seconds: int = 300) -> Dict[str, Any]:
        logger.info("Requesting human help to solve CAPTCHA")
        
        try:
            if screenshot:
                # Take screenshot of the page focusing on the CAPTCHA
                result = asyncio.run(self._execute_browser_action(
                    "take_screenshot", 
                    {"filename": "captcha.png"}
                ))
                if result.get("success"):
                    print("\n📸 Screenshot saved as 'captcha.png'")

            print("\n🤖 -> 🧑‍💻 Human help needed to solve CAPTCHA!")
            print(f"Reason: {reason}")
            if instructions:
                print(f"Instructions: {instructions}")
            input("Press Enter when you've solved the CAPTCHA...")
            return {"success": True, "message": "CAPTCHA solved by human"}
        except KeyboardInterrupt:
            return {"success": False, "error": "CAPTCHA solving cancelled"}

class HandleLoginTool(BrowserToolBase):
    name: str = "browser_handle_login"
    description: str = "Request human help for login, 2FA, or sensitive input"
    args_schema: Optional[Type[BaseModel]] = LoginInput
    
    @BrowserToolBase.requires_setup
    def _run(self, reason: str, field_type: str, selector: Optional[str] = None,
             instructions: Optional[str] = None, timeout_seconds: int = 300) -> Dict[str, Any]:
        logger.info(f"Requesting human help for {field_type} input")
        
        try:
            print(f"\n🤖 -> 🧑‍💻 Human help needed for {field_type}!")
            print(f"Reason: {reason}")
            if instructions:
                print(f"Instructions: {instructions}")
            if selector:
                print(f"Please locate the input field with selector: {selector}")
            input("Press Enter when you've completed the input...")
            return {"success": True, "message": f"{field_type} input completed by human"}
        except KeyboardInterrupt:
            return {"success": False, "error": f"{field_type} input cancelled"}


# Get all tools as a list
def get_browser_tools() -> List[BrowserToolBase]:
    """Return a list of all browser tools."""
    return [
        # Navigation Tools
        NavigateToTool(),
        SearchGoogleTool(),
        GoBackTool(),
        WaitTool(),
        
        # Interaction Tools
        ClickElementTool(),
        InputTextTool(),
        SendKeysTool(),
        
        # Tab Management
        SwitchTabTool(),
        OpenTabTool(),
        CloseTabTool(),
        
        # Content and Scrolling
        ExtractContentTool(),
        ScrollDownTool(),
        ScrollUpTool(),
        ScrollToTextTool(),
        
        # Form Interaction
        GetDropdownOptionsTool(),
        SelectDropdownOptionTool(),
        ClickCoordinatesTool(),
        DragDropTool(),
        
        # Human Intervention Tools
        RequestHumanHelpTool(),
        SolveCaptchaTool(),
        HandleLoginTool(),
        SavePdfTool(),
        GeneratePdfTool(),
        GetCookiesTool(),
        SetCookieTool(),
        ClearCookiesTool(),
        ClearLocalStorageTool(),
        AcceptDialogTool(),
        DismissDialogTool(),
        SwitchToFrameTool(),
        SwitchToMainFrameTool(),
        SetNetworkConditionsTool(),
        RequestHumanHelpTool(),
        SolveCaptchaTool(),
        HandleLoginTool(),
    ]


# Main browser toolkit class that wraps all tools
class BrowserToolkit:
    """A toolkit that provides access to all browser automation tools."""
    
    def __init__(self, api_url: Optional[str] = None, sandbox_id: Optional[str] = None):
        """Initialize the browser toolkit.
        
        Args:
            api_url (Optional[str]): The base URL for the browser automation API
            sandbox_id (Optional[str]): The ID of the sandbox running the browser
        """
        self.tools = get_browser_tools()
        self._is_setup = False
        self.api_url = api_url
        self.sandbox_id = sandbox_id
    
    async def setup(self, api_url: Optional[str] = None, sandbox_id: Optional[str] = None):
        """Set up all tools.
        
        Args:
            api_url (Optional[str]): The base URL for the browser automation API
            sandbox_id (Optional[str]): The ID of the sandbox running the browser
            
        Returns:
            Dict[str, Any]: Setup result status
        """
        if self._is_setup and not api_url:
            return {"success": True, "message": "Already set up"}
        
        # Use provided values or fallback to ones set in constructor
        api_url = api_url or self.api_url
        sandbox_id = sandbox_id or self.sandbox_id
        
        if not api_url:
            return {"success": False, "error": "No API URL provided"}
        
        # Set up the first tool with the provided API URL
        result = await self.tools[0].setup(api_url=api_url, sandbox_id=sandbox_id)
        
        if result["success"]:
            # Share the API base URL and sandbox ID with all tools
            for tool in self.tools[1:]:
                tool.api_base_url = api_url
                tool.sandbox_id = sandbox_id
            
            # Update instance variables
            self.api_url = api_url
            self.sandbox_id = sandbox_id
            self._is_setup = True
        
        return result
    
    def get_tools(self) -> List[BrowserToolBase]:
        """Get all tools in the toolkit."""
        return self.tools
    
    def get_tool(self, name: str) -> Optional[BrowserToolBase]:
        """Get a specific tool by name."""
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None
