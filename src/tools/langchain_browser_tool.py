import httpx
import asyncio
from typing import Dict, Any, Optional, List, Type
from functools import wraps

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from src.utils.logger import logger
from src.tools.utilities.human_intervention import CaptchaInput, LoginInput


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
                # Retry logic to wait for API to start up
                max_retries = 30
                retry_delay = 2
                api_health_url = f"{self.api_base_url}/health"
                
                for attempt in range(max_retries):
                    try:
                        async with httpx.AsyncClient(timeout=10.0) as client:
                            response = await client.get(api_health_url)
                            
                            # Check for successful response
                            if response.status_code == 200:
                                logger.info(f"Browser tool set up successfully with API URL: {self.api_base_url}")
                                return {"success": True, "message": "Setup complete", "api_url": self.api_base_url}
                            
                            # Check if we're getting the "waiting for process" page
                            if "Waiting for process" in response.text:
                                logger.info(f"API not ready yet (attempt {attempt + 1}/{max_retries}), waiting {retry_delay}s...")
                                await asyncio.sleep(retry_delay)
                                continue
                            
                            # Other error response
                            logger.warning(f"Health check failed with status {response.status_code}: {response.text[:200]}")
                            await asyncio.sleep(retry_delay)
                            
                    except Exception as e:
                        logger.warning(f"Health check attempt {attempt + 1}/{max_retries} failed: {str(e)}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(retry_delay)
                        else:
                            raise
                
                # If we get here, all retries failed
                raise Exception(f"Browser API health check failed after {max_retries} attempts")
            else:
                return {"success": False, "error": "No API URL provided"}
        
        except Exception as e:
            logger.error(f"Failed to set up browser tool: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _execute_browser_action(self, endpoint: str, data: Any = None, method: str = "POST") -> Dict[str, Any]:
        """Execute a browser action by calling the FastAPI endpoint.
        
        Args:
            endpoint (str): API endpoint path (without /automation/ prefix)
            data (Any, optional): Request data. Defaults to None.
            method (str, optional): HTTP method. Defaults to "POST".
            
        Returns:
            Dict[str, Any]: Response from the API
        """
        if not self.api_base_url:
            return {"success": False, "error": "API base URL not set. Call setup() first."}
        
        # Add /automation/ prefix to match the actual API endpoints
        url = f"{self.api_base_url}/automation/{endpoint}"
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


# Enhanced Input Schemas for new API endpoints
class NavigateToInput(BaseModel):
    url: str = Field(description="The URL to navigate to")

class SearchGoogleInput(BaseModel):
    query: str = Field(description="The search query")

class NoParamsInput(BaseModel):
    pass

class WaitInput(BaseModel):
    seconds: int = Field(description="Number of seconds to wait")

class ClickElementInput(BaseModel):
    index: int = Field(description="Index of the element to click")

class InputTextInput(BaseModel):
    index: int = Field(description="Index of the element to input text into")
    text: str = Field(description="Text to input")

class SendKeysInput(BaseModel):
    keys: str = Field(description="Keys to send")

class SwitchTabInput(BaseModel):
    tab_index: int = Field(description="Index of the tab to switch to")

class OpenTabInput(BaseModel):
    url: str = Field(description="URL to open in new tab")

class CloseTabInput(BaseModel):
    tab_index: int = Field(description="Index of the tab to close")

class ExtractContentInput(BaseModel):
    goal: str = Field(description="Goal for content extraction")

class ScrollDownInput(BaseModel):
    amount: Optional[int] = Field(default=None, description="Amount to scroll down")

class ScrollUpInput(BaseModel):
    amount: Optional[int] = Field(default=None, description="Amount to scroll up")

class ScrollToTextInput(BaseModel):
    text: str = Field(description="Text to scroll to")

class GetDropdownOptionsInput(BaseModel):
    index: int = Field(description="Index of the dropdown element")

class SelectDropdownOptionInput(BaseModel):
    index: int = Field(description="Index of the dropdown element")
    option_text: str = Field(description="Option text to select")

class ClickCoordinatesInput(BaseModel):
    x: int = Field(description="X coordinate")
    y: int = Field(description="Y coordinate")

class DragDropInput(BaseModel):
    source_x: int = Field(description="Source X coordinate")
    source_y: int = Field(description="Source Y coordinate")
    target_x: int = Field(description="Target X coordinate")
    target_y: int = Field(description="Target Y coordinate")

class PDFOptionsInput(BaseModel):
    format: Optional[str] = Field(default="A4", description="PDF format")
    printBackground: Optional[bool] = Field(default=True, description="Print background")
    displayHeaderFooter: Optional[bool] = Field(default=False, description="Display header/footer")
    headerTemplate: Optional[str] = Field(default=None, description="Header template")
    footerTemplate: Optional[str] = Field(default=None, description="Footer template")

class CookieInput(BaseModel):
    name: str = Field(description="Cookie name")
    value: str = Field(description="Cookie value")
    domain: Optional[str] = Field(default=None, description="Cookie domain")
    path: Optional[str] = Field(default="/", description="Cookie path")

class FrameInput(BaseModel):
    frame_selector: Dict[str, Any] = Field(description="CSS selector for the frame")

class NetworkConditionsInput(BaseModel):
    offline: Optional[bool] = Field(default=False, description="Simulate offline")
    downloadThroughput: Optional[int] = Field(default=None, description="Download throughput")
    uploadThroughput: Optional[int] = Field(default=None, description="Upload throughput")
# Human Intervention Input Schemas
class InterventionRequestInput(BaseModel):
    intervention_type: str = Field(description="Type of intervention needed")
    message: str = Field(description="Message describing the intervention")
    instructions: Optional[str] = Field(default=None, description="Instructions for the human")
    timeout_seconds: Optional[int] = Field(default=300, description="Timeout in seconds")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")
    take_screenshot: Optional[bool] = Field(default=False, description="Take screenshot")
    auto_detect: Optional[bool] = Field(default=False, description="Auto-detect intervention need")

class InterventionCompleteInput(BaseModel):
    intervention_id: str = Field(description="ID of the intervention to complete")
    user_message: Optional[str] = Field(default=None, description="Message from user")
    success: Optional[bool] = Field(default=True, description="Whether intervention was successful")

class InterventionCancelInput(BaseModel):
    intervention_id: str = Field(description="ID of the intervention to cancel")
    reason: Optional[str] = Field(default=None, description="Reason for cancellation")

class InterventionStatusInput(BaseModel):
    intervention_id: Optional[str] = Field(default=None, description="ID of the intervention to check. If not provided, checks the latest active intervention")

class AutoDetectInput(BaseModel):
    check_captcha: Optional[bool] = Field(default=True, description="Check for CAPTCHA")
    check_login: Optional[bool] = Field(default=True, description="Check for login forms")
    check_security: Optional[bool] = Field(default=True, description="Check for security challenges")
    check_anti_bot: Optional[bool] = Field(default=True, description="Check for anti-bot measures")
    check_cookies: Optional[bool] = Field(default=True, description="Check for cookie consent")


# Browser navigation tools
class NavigateToTool(BrowserToolBase):
    name: str = "browser_navigate_to"
    description: str = "Navigate to a specific URL"
    args_schema: Optional[Type[BaseModel]] = NavigateToInput
    
    @BrowserToolBase.requires_setup
    def _run(self, url: str) -> str:
        logger.info(f"Navigating to URL: {url}")
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("navigate_to", {"url": url}))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("navigate_to", {"url": url}))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("navigate_to", {"url": url}))
        except Exception as e:
            result = {"success": False, "error": f"Error in navigate_to: {str(e)}"}
        
        # Return string for better LangChain compatibility
        if result.get("success"):
            return f"Successfully navigated to {url}"
        else:
            return f"Failed to navigate to {url}: {result.get('error', 'Unknown error')}"


class SearchGoogleTool(BrowserToolBase):
    name: str = "browser_search_google"
    description: str = "Search Google with the provided query"
    args_schema: Optional[Type[BaseModel]] = SearchGoogleInput
    
    @BrowserToolBase.requires_setup
    def _run(self, query: str) -> str:
        logger.info(f"Searching Google for: {query}")
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("search_google", {"query": query}))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("search_google", {"query": query}))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("search_google", {"query": query}))
        except Exception as e:
            result = {"success": False, "error": f"Error in search_google: {str(e)}"}
        
        # Return string for better LangChain compatibility
        if result.get("success"):
            return f"Successfully searched Google for '{query}'. Page loaded and search results are displayed."
        else:
            return f"Failed to search Google for '{query}': {result.get('error', 'Unknown error')}"


class GoBackTool(BrowserToolBase):
    name: str = "browser_go_back"
    description: str = "Navigate back in browser history"
    
    @BrowserToolBase.requires_setup
    def _run(self) -> Dict[str, Any]:
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("go_back", {}))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("go_back", {}))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("go_back", {}))
        except Exception as e:
            result = {"success": False, "error": f"Error in go_back: {str(e)}"}
        
        return result


class WaitTool(BrowserToolBase):
    name: str = "browser_wait"
    description: str = "Wait for page to load (waits for network idle)"
    args_schema: Optional[Type[BaseModel]] = NoParamsInput
    
    @BrowserToolBase.requires_setup
    def _run(self) -> str:
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("wait", {}))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("wait", {}))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("wait", {}))
        except Exception as e:
            result = {"success": False, "error": f"Error in wait: {str(e)}"}
        
        # Return string for better LangChain compatibility
        if result.get("success"):
            return "Page has finished loading and network is idle."
        else:
            return f"Failed to wait for page: {result.get('error', 'Unknown error')}"


# Interaction tools
class ClickElementTool(BrowserToolBase):
    name: str = "browser_click_element"
    description: str = "Click on an element by index"
    args_schema: Optional[Type[BaseModel]] = ClickElementInput
    
    @BrowserToolBase.requires_setup
    def _run(self, index: int) -> Dict[str, Any]:
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("click_element", {"index": index}))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("click_element", {"index": index}))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("click_element", {"index": index}))
        except Exception as e:
            result = {"success": False, "error": f"Error in click_element: {str(e)}"}
        
        return result


class InputTextTool(BrowserToolBase):
    name: str = "browser_input_text"
    description: str = "Input text into an element by index. Requires JSON input with 'index' (int) and 'text' (str). Example: {\"index\": 0, \"text\": \"Hello World\"}"
    args_schema: Optional[Type[BaseModel]] = InputTextInput
    
    @BrowserToolBase.requires_setup
    def _run(self, index: int, text: str) -> Dict[str, Any]:
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("input_text", {"index": index, "text": text}))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("input_text", {"index": index, "text": text}))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("input_text", {"index": index, "text": text}))
        except Exception as e:
            result = {"success": False, "error": f"Error in input_text: {str(e)}"}
        
        return result


class SendKeysTool(BrowserToolBase):
    name: str = "browser_send_keys"
    description: str = "Send keyboard keys such as Enter, Escape, or keyboard shortcuts"
    args_schema: Optional[Type[BaseModel]] = SendKeysInput
    
    @BrowserToolBase.requires_setup
    def _run(self, keys: str) -> Dict[str, Any]:
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("send_keys", {"keys": keys}))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("send_keys", {"keys": keys}))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("send_keys", {"keys": keys}))
        except Exception as e:
            result = {"success": False, "error": f"Error in send_keys: {str(e)}"}
        
        return result


# Tab management tools
class SwitchTabTool(BrowserToolBase):
    name: str = "browser_switch_tab"
    description: str = "Switch to a different browser tab"
    args_schema: Optional[Type[BaseModel]] = SwitchTabInput
    
    @BrowserToolBase.requires_setup
    def _run(self, tab_index: int) -> Dict[str, Any]:
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("switch_tab", {"tab_index": tab_index}))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("switch_tab", {"tab_index": tab_index}))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("switch_tab", {"tab_index": tab_index}))
        except Exception as e:
            result = {"success": False, "error": f"Error in switch_tab: {str(e)}"}
        
        return result


class OpenTabTool(BrowserToolBase):
    name: str = "browser_open_tab"
    description: str = "Open a new browser tab with the specified URL"
    args_schema: Optional[Type[BaseModel]] = OpenTabInput
    
    @BrowserToolBase.requires_setup
    def _run(self, url: str) -> Dict[str, Any]:
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("open_tab", {"url": url}))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("open_tab", {"url": url}))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("open_tab", {"url": url}))
        except Exception as e:
            result = {"success": False, "error": f"Error in open_tab: {str(e)}"}
        
        return result


class CloseTabTool(BrowserToolBase):
    name: str = "browser_close_tab"
    description: str = "Close a browser tab"
    args_schema: Optional[Type[BaseModel]] = CloseTabInput
    
    @BrowserToolBase.requires_setup
    def _run(self, tab_index: int) -> Dict[str, Any]:
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("close_tab", {"tab_index": tab_index}))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("close_tab", {"tab_index": tab_index}))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("close_tab", {"tab_index": tab_index}))
        except Exception as e:
            result = {"success": False, "error": f"Error in close_tab: {str(e)}"}
        
        return result


# Content extraction tool
class ExtractContentTool(BrowserToolBase):
    name: str = "browser_extract_content"
    description: str = "Extract content from the current page based on the provided goal"
    args_schema: Optional[Type[BaseModel]] = ExtractContentInput
    
    @BrowserToolBase.requires_setup
    def _run(self, goal: str) -> Dict[str, Any]:
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("extract_content", {"goal": goal}))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("extract_content", {"goal": goal}))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("extract_content", {"goal": goal}))
        except Exception as e:
            result = {"success": False, "error": f"Error in extract_content: {str(e)}"}
        
        return result


# Scrolling tools
class ScrollDownTool(BrowserToolBase):
    name: str = "browser_scroll_down"
    description: str = "Scroll down the page"
    args_schema: Optional[Type[BaseModel]] = ScrollDownInput
    
    @BrowserToolBase.requires_setup
    def _run(self, amount: Optional[int] = None) -> Dict[str, Any]:
        data = {"amount": amount} if amount is not None else {}
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("scroll_down", data))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("scroll_down", data))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("scroll_down", data))
        except Exception as e:
            result = {"success": False, "error": f"Error in scroll_down: {str(e)}"}
        
        return result


class ScrollUpTool(BrowserToolBase):
    name: str = "browser_scroll_up"
    description: str = "Scroll up the page"
    args_schema: Optional[Type[BaseModel]] = ScrollUpInput
    
    @BrowserToolBase.requires_setup
    def _run(self, amount: Optional[int] = None) -> Dict[str, Any]:
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("scroll_up", {"amount": amount} if amount else {}))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("scroll_up", {"amount": amount} if amount else {}))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("scroll_up", {"amount": amount} if amount else {}))
        except Exception as e:
            result = {"success": False, "error": f"Error in scroll_up: {str(e)}"}
        
        return result


class ScrollToTextTool(BrowserToolBase):
    name: str = "browser_scroll_to_text"
    description: str = "Scroll to specific text on the page"
    args_schema: Optional[Type[BaseModel]] = ScrollToTextInput
    
    @BrowserToolBase.requires_setup
    def _run(self, text: str) -> Dict[str, Any]:
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("scroll_to_text", {"text": text}))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("scroll_to_text", {"text": text}))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("scroll_to_text", {"text": text}))
        except Exception as e:
            result = {"success": False, "error": f"Error in scroll_to_text: {str(e)}"}
        
        return result


# Dropdown tools
class GetDropdownOptionsTool(BrowserToolBase):
    name: str = "browser_get_dropdown_options"
    description: str = "Get all options from a dropdown element"
    args_schema: Optional[Type[BaseModel]] = GetDropdownOptionsInput
    
    @BrowserToolBase.requires_setup
    def _run(self, index: int) -> Dict[str, Any]:
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("get_dropdown_options", {"index": index}))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("get_dropdown_options", {"index": index}))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("get_dropdown_options", {"index": index}))
        except Exception as e:
            result = {"success": False, "error": f"Error in get_dropdown_options: {str(e)}"}
        
        return result


class SelectDropdownOptionTool(BrowserToolBase):
    name: str = "browser_select_dropdown_option"
    description: str = "Select an option from a dropdown by text. Requires JSON input with 'index' (int) and 'option_text' (str). Example: {\"index\": 0, \"option_text\": \"Option 1\"}"
    args_schema: Optional[Type[BaseModel]] = SelectDropdownOptionInput
    
    @BrowserToolBase.requires_setup
    def _run(self, index: int, option_text: str) -> Dict[str, Any]:
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("select_dropdown_option", 
                                                         {"index": index, "option_text": option_text}))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("select_dropdown_option", 
                                                         {"index": index, "option_text": option_text}))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("select_dropdown_option", 
                                                         {"index": index, "option_text": option_text}))
        except Exception as e:
            result = {"success": False, "error": f"Error in select_dropdown_option: {str(e)}"}
        
        return result


# Advanced interaction tools
class ClickCoordinatesTool(BrowserToolBase):
    name: str = "browser_click_coordinates"
    description: str = "Click at specific X,Y coordinates on the page"
    args_schema: Optional[Type[BaseModel]] = ClickCoordinatesInput
    
    @BrowserToolBase.requires_setup
    def _run(self, x: int, y: int) -> Dict[str, Any]:
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("click_coordinates", {"x": x, "y": y}))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("click_coordinates", {"x": x, "y": y}))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("click_coordinates", {"x": x, "y": y}))
        except Exception as e:
            result = {"success": False, "error": f"Error in click_coordinates: {str(e)}"}
        
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
        
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("drag_drop", data))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("drag_drop", data))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("drag_drop", data))
        except Exception as e:
            result = {"success": False, "error": f"Error in drag_drop: {str(e)}"}
        
        return result


# PDF tools
class SavePdfTool(BrowserToolBase):
    name: str = "browser_save_pdf"
    description: str = "Save the current page as a PDF"
    
    @BrowserToolBase.requires_setup
    def _run(self) -> Dict[str, Any]:
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("save_pdf", {}))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("save_pdf", {}))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("save_pdf", {}))
        except Exception as e:
            result = {"success": False, "error": f"Error in save_pdf: {str(e)}"}
        
        return result


class GeneratePdfTool(BrowserToolBase):
    name: str = "browser_generate_pdf"
    description: str = "Generate a PDF of the current page and return as base64 encoded string"
    
    @BrowserToolBase.requires_setup
    def _run(self, options: Dict[str, Any] = None) -> Dict[str, Any]:
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("generate_pdf", options or {}))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("generate_pdf", options or {}))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("generate_pdf", options or {}))
        except Exception as e:
            result = {"success": False, "error": f"Error in generate_pdf: {str(e)}"}
        
        return result


# Cookie and storage tools
class GetCookiesTool(BrowserToolBase):
    name: str = "browser_get_cookies"
    description: str = "Get all cookies for the current page"
    
    @BrowserToolBase.requires_setup
    def _run(self) -> Dict[str, Any]:
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("get_cookies", method="POST"))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("get_cookies", method="POST"))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("get_cookies", method="POST"))
        except Exception as e:
            result = {"success": False, "error": f"Error in get_cookies: {str(e)}"}
        
        return result


class SetCookieTool(BrowserToolBase):
    name: str = "browser_set_cookie"
    description: str = "Set a cookie for the current page"
    
    @BrowserToolBase.requires_setup
    def _run(self, cookie_data: Dict[str, Any]) -> Dict[str, Any]:
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("set_cookie", cookie_data))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("set_cookie", cookie_data))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("set_cookie", cookie_data))
        except Exception as e:
            result = {"success": False, "error": f"Error in set_cookie: {str(e)}"}
        
        return result


class ClearCookiesTool(BrowserToolBase):
    name: str = "browser_clear_cookies"
    description: str = "Clear all cookies for the current page"
    
    @BrowserToolBase.requires_setup
    def _run(self) -> Dict[str, Any]:
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("clear_cookies", {}))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("clear_cookies", {}))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("clear_cookies", {}))
        except Exception as e:
            result = {"success": False, "error": f"Error in clear_cookies: {str(e)}"}
        
        return result


class ClearLocalStorageTool(BrowserToolBase):
    name: str = "browser_clear_local_storage"
    description: str = "Clear local storage for the current page"
    
    @BrowserToolBase.requires_setup
    def _run(self) -> Dict[str, Any]:
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("clear_local_storage", {}))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("clear_local_storage", {}))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("clear_local_storage", {}))
        except Exception as e:
            result = {"success": False, "error": f"Error in clear_local_storage: {str(e)}"}
        
        return result


# Dialog handling tools
class AcceptDialogTool(BrowserToolBase):
    name: str = "browser_accept_dialog"
    description: str = "Set up handler to accept any dialog (alert, confirm, prompt) that appears"
    
    @BrowserToolBase.requires_setup
    def _run(self) -> Dict[str, Any]:
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("accept_dialog", {}))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("accept_dialog", {}))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("accept_dialog", {}))
        except Exception as e:
            result = {"success": False, "error": f"Error in accept_dialog: {str(e)}"}
        
        return result


class DismissDialogTool(BrowserToolBase):
    name: str = "browser_dismiss_dialog"
    description: str = "Set up handler to dismiss any dialog (alert, confirm, prompt) that appears"
    
    @BrowserToolBase.requires_setup
    def _run(self) -> Dict[str, Any]:
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("dismiss_dialog", {}))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("dismiss_dialog", {}))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("dismiss_dialog", {}))
        except Exception as e:
            result = {"success": False, "error": f"Error in dismiss_dialog: {str(e)}"}
        
        return result


# Frame handling tools
class SwitchToFrameTool(BrowserToolBase):
    name: str = "browser_switch_to_frame"
    description: str = "Switch to a specific iframe on the page"
    args_schema: Optional[Type[BaseModel]] = FrameInput
    
    @BrowserToolBase.requires_setup
    def _run(self, frame_selector: Dict[str, Any]) -> Dict[str, Any]:
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("switch_to_frame", frame_selector))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("switch_to_frame", frame_selector))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("switch_to_frame", frame_selector))
        except Exception as e:
            result = {"success": False, "error": f"Error in switch_to_frame: {str(e)}"}
        
        return result


class SwitchToMainFrameTool(BrowserToolBase):
    name: str = "browser_switch_to_main_frame"
    description: str = "Switch back to the main frame (top-level document)"
    
    @BrowserToolBase.requires_setup
    def _run(self) -> Dict[str, Any]:
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("switch_to_main_frame", {}))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("switch_to_main_frame", {}))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("switch_to_main_frame", {}))
        except Exception as e:
            result = {"success": False, "error": f"Error in switch_to_main_frame: {str(e)}"}
        
        return result


# Network conditions tool
class SetNetworkConditionsTool(BrowserToolBase):
    name: str = "browser_set_network_conditions"
    description: str = "Set network conditions for the current page"
    args_schema: Optional[Type[BaseModel]] = NetworkConditionsInput
    
    @BrowserToolBase.requires_setup
    def _run(self, network_data: Dict[str, Any]) -> Dict[str, Any]:
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("set_network_conditions", network_data))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("set_network_conditions", network_data))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("set_network_conditions", network_data))
        except Exception as e:
            result = {"success": False, "error": f"Error in set_network_conditions: {str(e)}"}
        
        return result


# Human Intervention Tools
class RequestHumanHelpInput(BaseModel):
    reason: str = Field(description="Reason for requesting human help")
    instructions: Optional[str] = Field(default=None, description="Instructions for the human")
    timeout_seconds: Optional[int] = Field(default=300, description="Timeout in seconds")

class RequestHumanHelpTool(BrowserToolBase):
    name: str = "browser_request_human_help"
    description: str = "Request human intervention for complex tasks, captchas, or unknown information. Requires 'reason' parameter (string). Optional: 'instructions' (string), 'timeout_seconds' (int)"
    args_schema: Optional[Type[BaseModel]] = RequestHumanHelpInput
    
    @BrowserToolBase.requires_setup
    def _run(self, reason: str, instructions: Optional[str] = None, timeout_seconds: int = 300) -> str:
        logger.info(f"Requesting human help: {reason}")
        
        data = {
            "intervention_type": "custom",
            "message": reason,
            "instructions": instructions or "",
            "timeout_seconds": timeout_seconds
        }
        
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("request_intervention", data))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("request_intervention", data))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("request_intervention", data))
        except Exception as e:
            result = {"success": False, "error": f"Error in request_human_help: {str(e)}"}
        
        # Return string for better LangChain compatibility
        if result.get("success"):
            return f"Human intervention requested successfully: {reason}. Instructions: {instructions or 'None'}. Please check the VNC viewer for manual assistance."
        else:
            return f"Failed to request human intervention: {result.get('error', 'Unknown error')}"

class SolveCaptchaTool(BrowserToolBase):
    name: str = "browser_solve_captcha"
    description: str = "Request human help to solve a CAPTCHA"
    args_schema: Optional[Type[BaseModel]] = CaptchaInput
    
    @BrowserToolBase.requires_setup
    def _run(self, reason: str, instructions: Optional[str] = None, 
             screenshot: bool = False, timeout_seconds: int = 300) -> Dict[str, Any]:
        logger.info("Requesting human help to solve CAPTCHA")
        
        data = {
            "intervention_type": "captcha",
            "message": reason,
            "instructions": instructions or "Please solve the CAPTCHA on the page",
            "timeout_seconds": timeout_seconds,
            "take_screenshot": screenshot
        }
        
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("request_intervention", data))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("request_intervention", data))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("request_intervention", data))
        except Exception as e:
            result = {"success": False, "error": f"Error in solve_captcha: {str(e)}"}
        
        return result

class HandleLoginTool(BrowserToolBase):
    name: str = "browser_handle_login"
    description: str = "Request human help for login, 2FA, or sensitive input"
    args_schema: Optional[Type[BaseModel]] = LoginInput
    
    @BrowserToolBase.requires_setup
    def _run(self, reason: str, field_type: str, selector: Optional[str] = None,
             instructions: Optional[str] = None, timeout_seconds: int = 300) -> Dict[str, Any]:
        logger.info(f"Requesting human help for {field_type} input")
        
        login_instructions = f"Please complete {field_type} input"
        if instructions:
            login_instructions += f": {instructions}"
        if selector:
            login_instructions += f" (field selector: {selector})"
        
        # Map field types to intervention types
        intervention_type_map = {
            "login": "login_required",
            "password": "login_required", 
            "2fa": "two_factor_auth",
            "security": "security_check"
        }
        
        intervention_type = intervention_type_map.get(field_type.lower(), "custom")
        
        data = {
            "intervention_type": intervention_type,
            "message": reason,
            "instructions": login_instructions,
            "timeout_seconds": timeout_seconds
        }
        
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("request_intervention", data))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("request_intervention", data))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("request_intervention", data))
        except Exception as e:
            result = {"success": False, "error": f"Error in handle_login: {str(e)}"}
        
        return result


# Enhanced Human Intervention Tools using new API endpoints

class RequestInterventionTool(BrowserToolBase):
    name: str = "browser_request_intervention"
    description: str = "Request human intervention using the new API endpoint"
    args_schema: Optional[Type[BaseModel]] = InterventionRequestInput
    
    @BrowserToolBase.requires_setup
    def _run(self, intervention_type: str, message: str, instructions: Optional[str] = None,
             timeout_seconds: int = 300, context: Optional[Dict[str, Any]] = None,
             take_screenshot: bool = False, auto_detect: bool = False) -> Dict[str, Any]:
        data = {
            "intervention_type": intervention_type,
            "message": message,
            "instructions": instructions,
            "timeout_seconds": timeout_seconds,
            "context": context,
            "take_screenshot": take_screenshot,
            "auto_detect": auto_detect
        }
        
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("request_intervention", data))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("request_intervention", data))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("request_intervention", data))
        except Exception as e:
            result = {"success": False, "error": f"Error in request_intervention: {str(e)}"}
        
        return result


class CompleteInterventionTool(BrowserToolBase):
    name: str = "browser_complete_intervention"
    description: str = "Mark an intervention as completed"
    args_schema: Optional[Type[BaseModel]] = InterventionCompleteInput
    
    @BrowserToolBase.requires_setup
    def _run(self, intervention_id: str, user_message: Optional[str] = None, 
             success: bool = True) -> Dict[str, Any]:
        data = {
            "intervention_id": intervention_id,
            "user_message": user_message,
            "success": success
        }
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("complete_intervention", data))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("complete_intervention", data))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("complete_intervention", data))
        except Exception as e:
            result = {"success": False, "error": f"Error in complete_intervention: {str(e)}"}
        
        return result


class CancelInterventionTool(BrowserToolBase):
    name: str = "browser_cancel_intervention"
    description: str = "Cancel a pending intervention"
    args_schema: Optional[Type[BaseModel]] = InterventionCancelInput
    
    @BrowserToolBase.requires_setup
    def _run(self, intervention_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        data = {
            "intervention_id": intervention_id,
            "reason": reason
        }
        
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("cancel_intervention", data))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("cancel_intervention", data))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("cancel_intervention", data))
        except Exception as e:
            result = {"success": False, "error": f"Error in cancel_intervention: {str(e)}"}
        
        return result


class InterventionStatusTool(BrowserToolBase):
    name: str = "browser_intervention_status"
    description: str = "Check the status of an intervention. If no intervention_id is provided, checks the latest active intervention."
    args_schema: Optional[Type[BaseModel]] = InterventionStatusInput
    
    @BrowserToolBase.requires_setup
    def _run(self, intervention_id: Optional[str] = None) -> Dict[str, Any]:
        data = {"intervention_id": intervention_id} if intervention_id else {}
        
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("intervention_status", data))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("intervention_status", data))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("intervention_status", data))
        except Exception as e:
            result = {"success": False, "error": f"Error in intervention_status: {str(e)}"}
        
        return result


class AutoDetectInterventionTool(BrowserToolBase):
    name: str = "browser_auto_detect_intervention"
    description: str = "Automatically detect if human intervention is needed"
    args_schema: Optional[Type[BaseModel]] = AutoDetectInput
    
    @BrowserToolBase.requires_setup
    def _run(self, check_captcha: bool = True, check_login: bool = True,
             check_security: bool = True, check_anti_bot: bool = True,
             check_cookies: bool = True) -> Dict[str, Any]:
        data = {
            "check_captcha": check_captcha,
            "check_login": check_login,
            "check_security": check_security,
            "check_anti_bot": check_anti_bot,
            "check_cookies": check_cookies
        }
        
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("auto_detect_intervention", data))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("auto_detect_intervention", data))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("auto_detect_intervention", data))
        except Exception as e:
            result = {"success": False, "error": f"Error in auto_detect_intervention: {str(e)}"}
        
        return result


class GetPageContentTool(BrowserToolBase):
    name: str = "browser_get_page_content"
    description: str = "Get the content of the current page including text, links, and interactive elements"
    args_schema: Optional[Type[BaseModel]] = NoParamsInput
    
    @BrowserToolBase.requires_setup
    def _run(self) -> str:
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("get_page_content", {}))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("get_page_content", {}))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("get_page_content", {}))
        except Exception as e:
            result = {"success": False, "error": f"Error in get_page_content: {str(e)}"}
        
        # Return string content for better LangChain compatibility
        if result.get("success"):
            page_data = result.get("data", {})
            if isinstance(page_data, dict):
                content_parts = []
                if "title" in page_data:
                    content_parts.append(f"Page Title: {page_data['title']}")
                if "url" in page_data:
                    content_parts.append(f"Current URL: {page_data['url']}")
                if "content" in page_data:
                    content_parts.append(f"Page Content:\n{page_data['content']}")
                if "elements" in page_data:
                    content_parts.append(f"Interactive Elements:\n{page_data['elements']}")
                return "\n\n".join(content_parts)
            else:
                return str(page_data)
        else:
            return f"Failed to get page content: {result.get('error', 'Unknown error')}"


# Additional navigation tools

class GoForwardTool(BrowserToolBase):
    name: str = "browser_go_forward"
    description: str = "Navigate forward in browser history"
    args_schema: Optional[Type[BaseModel]] = NoParamsInput
    
    @BrowserToolBase.requires_setup
    def _run(self) -> Dict[str, Any]:
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("go_forward", {}))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("go_forward", {}))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("go_forward", {}))
        except Exception as e:
            result = {"success": False, "error": f"Error in go_forward: {str(e)}"}
        
        return result


class RefreshTool(BrowserToolBase):
    name: str = "browser_refresh"
    description: str = "Refresh the current page"
    args_schema: Optional[Type[BaseModel]] = NoParamsInput
    
    @BrowserToolBase.requires_setup
    def _run(self) -> Dict[str, Any]:
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("refresh", {}))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("refresh", {}))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("refresh", {}))
        except Exception as e:
            result = {"success": False, "error": f"Error in refresh: {str(e)}"}
        
        return result


# Additional scrolling tools

class ScrollToTopTool(BrowserToolBase):
    name: str = "browser_scroll_to_top"
    description: str = "Scroll to the top of the page"
    args_schema: Optional[Type[BaseModel]] = NoParamsInput
    
    @BrowserToolBase.requires_setup
    def _run(self) -> Dict[str, Any]:
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("scroll_to_top", {}))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("scroll_to_top", {}))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("scroll_to_top", {}))
        except Exception as e:
            result = {"success": False, "error": f"Error in scroll_to_top: {str(e)}"}
        
        return result


class ScrollToBottomTool(BrowserToolBase):
    name: str = "browser_scroll_to_bottom"
    description: str = "Scroll to the bottom of the page"
    args_schema: Optional[Type[BaseModel]] = NoParamsInput
    
    @BrowserToolBase.requires_setup
    def _run(self) -> Dict[str, Any]:
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("scroll_to_bottom", {}))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("scroll_to_bottom", {}))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("scroll_to_bottom", {}))
        except Exception as e:
            result = {"success": False, "error": f"Error in scroll_to_bottom: {str(e)}"}
        
        return result


# Enhanced PDF and screenshot tools

class GetPagePdfTool(BrowserToolBase):
    name: str = "browser_get_page_pdf"
    description: str = "Get the current page as a PDF"
    args_schema: Optional[Type[BaseModel]] = PDFOptionsInput
    
    @BrowserToolBase.requires_setup
    def _run(self, format: Optional[str] = "A4", printBackground: Optional[bool] = True,
             displayHeaderFooter: Optional[bool] = False, headerTemplate: Optional[str] = None,
             footerTemplate: Optional[str] = None) -> Dict[str, Any]:
        data = {
            "format": format,
            "printBackground": printBackground,
            "displayHeaderFooter": displayHeaderFooter,
            "headerTemplate": headerTemplate,
            "footerTemplate": footerTemplate
        }
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("get_page_pdf", data))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("get_page_pdf", data))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("get_page_pdf", data))
        except Exception as e:
            result = {"success": False, "error": f"Error in get_page_pdf: {str(e)}"}
        
        return result


class TakeScreenshotTool(BrowserToolBase):
    name: str = "browser_take_screenshot"
    description: str = "Take a screenshot of the current page"
    args_schema: Optional[Type[BaseModel]] = NoParamsInput
    
    @BrowserToolBase.requires_setup
    def _run(self) -> Dict[str, Any]:
        # Handle event loop properly for LangChain compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_browser_action("take_screenshot", {}))
                    result = future.result()
            else:
                result = loop.run_until_complete(self._execute_browser_action("take_screenshot", {}))
        except RuntimeError:
            # No event loop running, create a new one
            result = asyncio.run(self._execute_browser_action("take_screenshot", {}))
        except Exception as e:
            result = {"success": False, "error": f"Error in take_screenshot: {str(e)}"}
        
        return result


# Get all tools as a list
def get_browser_tools() -> List[BrowserToolBase]:
    """Return a list of all browser tools."""
    return [
        # Navigation Tools
        NavigateToTool(),
        SearchGoogleTool(),
        GoBackTool(),
        GoForwardTool(),
        RefreshTool(),
        WaitTool(),
        
        # Interaction Tools
        ClickElementTool(),
        InputTextTool(),
        SendKeysTool(),
        ClickCoordinatesTool(),
        DragDropTool(),
        
        # Tab Management
        SwitchTabTool(),
        OpenTabTool(),
        CloseTabTool(),
        
        # Content and Scrolling
        ExtractContentTool(),
        GetPageContentTool(),
        ScrollDownTool(),
        ScrollUpTool(),
        ScrollToTextTool(),
        ScrollToTopTool(),
        ScrollToBottomTool(),
        
        # Form Interaction
        GetDropdownOptionsTool(),
        SelectDropdownOptionTool(),
        
        # Human Intervention Tools (Legacy)
        RequestHumanHelpTool(),
        SolveCaptchaTool(),
        HandleLoginTool(),
        
        # Human Intervention Tools (Enhanced)
        RequestInterventionTool(),
        CompleteInterventionTool(),
        CancelInterventionTool(),
        InterventionStatusTool(),
        AutoDetectInterventionTool(),
        
        # PDF and Screenshot Tools
        SavePdfTool(),
        GeneratePdfTool(),
        GetPagePdfTool(),
        TakeScreenshotTool(),
        
        # Cookie and Storage Management
        GetCookiesTool(),
        SetCookieTool(),
        ClearCookiesTool(),
        ClearLocalStorageTool(),
        
        # Dialog Handling
        AcceptDialogTool(),
        DismissDialogTool(),
        
        # Frame Management
        SwitchToFrameTool(),
        SwitchToMainFrameTool(),
        
        # Network Tools
        SetNetworkConditionsTool(),
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
