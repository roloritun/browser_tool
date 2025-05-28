"""
Enhanced Langchain browser tools with seamless human intervention capabilities.
These tools automatically detect and handle scenarios requiring human assistance.
Updated to use the latest browser automation API with comprehensive endpoint support.
"""
import asyncio
from enum import Enum
from typing import Dict, Any, Optional, Type
from pydantic import BaseModel, Field

from src.tools.langchain_browser_tool import BrowserToolBase
from src.tools.utilities.human_intervention import EnhancedHumanInterventionBase
from src.utils.logger import logger

class InterventionType(str, Enum):
    """Types of human intervention scenarios matching API specification"""
    CAPTCHA_REQUIRED = "captcha"
    LOGIN_REQUIRED = "login_required"
    TWO_FACTOR_AUTH = "two_factor_auth"
    SECURITY_CHECK = "security_check"
    COOKIES_CONSENT = "cookies_consent"
    ANTI_BOT_PROTECTION = "anti_bot_protection"
    COMPLEX_DATA_ENTRY = "complex_data_entry"
    UNKNOWN_BLOCKAGE = "unknown_blockage"
    MANUAL_VERIFICATION = "manual_verification"
    AGE_VERIFICATION = "age_verification"
    CUSTOM = "custom"

class InterventionAwareBrowserTool(BrowserToolBase):
    """Base class for browser tools with automatic human intervention support"""
    
    auto_intervention_enabled: bool = True
    intervention_timeout: int = 300
    intervention_helper: Optional[Any] = None
    browser_url: Optional[str] = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize intervention helper after parent initialization
        if not hasattr(self, 'intervention_helper') or self.intervention_helper is None:
            self.intervention_helper = EnhancedHumanInterventionBase(getattr(self, 'api_base_url', None))
    
    async def _execute_browser_action(self, endpoint: str, data: Any = None, method: str = "POST") -> Dict[str, Any]:
        """Execute a browser action by calling the FastAPI endpoint with /automation/ prefix.
        
        Args:
            endpoint (str): API endpoint path (without /automation/ prefix)
            data (Any, optional): Request data. Defaults to None.
            method (str, optional): HTTP method. Defaults to "POST".
            
        Returns:
            Dict[str, Any]: Response from the API
        """
        if not self.api_base_url:
            return {"success": False, "error": "API base URL not set. Call setup() first."}
        
        # Add /automation/ prefix to endpoint
        full_endpoint = f"automation/{endpoint}"
        url = f"{self.api_base_url}/{full_endpoint}"
        logger.debug(f"Calling {method} {url} with data: {data}")
        
        try:
            import httpx
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
    
    def _run(self, *args, **kwargs) -> str:
        """Synchronous version - runs async method in event loop with parameter mapping"""
        import asyncio
        import concurrent.futures
        
        # Apply parameter mapping before calling _arun
        mapped_kwargs = self._map_parameters(kwargs)
        
        try:
            # Try to get existing event loop
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is already running, create a new one in a thread
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, self._arun(*args, **mapped_kwargs))
                        return future.result()
                else:
                    return loop.run_until_complete(self._arun(*args, **mapped_kwargs))
            except RuntimeError:
                # No event loop running, create a new one
                return asyncio.run(self._arun(*args, **mapped_kwargs))
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _map_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Map common agent parameter names to API schema parameter names"""
        if not isinstance(params, dict):
            return params
        
        # API Schema-based parameter mapping based on OpenAPI spec
        # This maps common agent parameter names to the exact API schema expectations
        api_parameter_mappings = {
            # Navigation and search tools
            'url': 'url',  # GoToUrlAction
            'query': 'query',  # SearchGoogleAction
            
            # Element interaction tools  
            'element_index': 'index',  # ClickElementAction, InputTextAction, etc.
            'element': 'index',  # When agent uses descriptive element names
            'text': 'text',  # InputTextAction
            
            # Wait and timing
            'time': 'seconds',  # For wait actions, though API uses WaitAction with no params
            'seconds': 'seconds',
            
            # Coordinates
            'x': 'x',  # ClickCoordinatesAction  
            'y': 'y',  # ClickCoordinatesAction
            
            # Dropdown operations
            'option': 'option_text',  # SelectDropdownOptionAction expects 'option_text'
            'option_text': 'option_text',
            
            # Tab operations
            'tab_index': 'page_id',  # SwitchTabAction, CloseTabAction
            'page_id': 'page_id',
            
            # Content extraction
            'goal': 'goal',  # ExtractContentAction
            
            # Scroll operations
            'amount': 'amount',  # ScrollAction
            
            # Keys
            'keys': 'keys',  # SendKeysAction
            
            # Human intervention
            'intervention_type': 'intervention_type',  # InterventionRequestAction
            'message': 'message',
            'instructions': 'instructions',
            'timeout_seconds': 'timeout_seconds',
            'intervention_id': 'intervention_id',
        }
        
        mapped_params = {}
        
        # Handle special cases based on tool name patterns
        if 'input_text' in self.name.lower():
            # InputTextAction schema: {text: str, index?: int, selector?: str}
            for key, value in params.items():
                if key in ['element_index', 'element']:
                    mapped_params['index'] = 0 if isinstance(value, str) else value
                elif key == 'text':
                    mapped_params['text'] = value
                else:
                    mapped_params[key] = value
        
        elif 'click' in self.name.lower() and 'element' in self.name.lower():
            # ClickElementAction schema: {index?: int, selector?: str}  
            for key, value in params.items():
                if key in ['element_index', 'element']:
                    mapped_params['index'] = 0 if isinstance(value, str) else value
                else:
                    mapped_params[key] = value
                    
        elif 'wait' in self.name.lower():
            # WaitAction schema: {} (no parameters in API spec)
            # Convert any time-related parameters to empty dict since API expects no params
            mapped_params = {}
            
        elif 'navigate' in self.name.lower():
            # GoToUrlAction schema: {url: str}
            for key, value in params.items():
                if key == 'url':
                    mapped_params['url'] = value
                else:
                    mapped_params[key] = value
                    
        elif 'search' in self.name.lower():
            # SearchGoogleAction schema: {query: str}
            for key, value in params.items():
                if key == 'query':
                    mapped_params['query'] = value
                else:
                    mapped_params[key] = value
                    
        elif 'dropdown' in self.name.lower() and 'select' in self.name.lower():
            # SelectDropdownOptionAction schema: {index: int, option_text: str}
            for key, value in params.items():
                if key in ['element_index', 'element']:
                    mapped_params['index'] = 0 if isinstance(value, str) else value
                elif key in ['option', 'text']:
                    mapped_params['option_text'] = value
                else:
                    mapped_params[key] = value
                    
        elif 'intervention' in self.name.lower():
            # InterventionRequestAction schema varies, map common fields
            for key, value in params.items():
                mapped_key = api_parameter_mappings.get(key, key)
                mapped_params[mapped_key] = value
                
        else:
            # Default mapping for other tools
            for key, value in params.items():
                mapped_key = api_parameter_mappings.get(key, key)
                mapped_params[mapped_key] = value
        
        # Convert common element descriptions to index 0
        if 'index' in mapped_params and isinstance(mapped_params['index'], str):
            element_descriptions = [
                'search bar', 'search box', 'search field', 'search input',
                'input field', 'text input', 'input box', 'text field',
                'button', 'submit button', 'search button',
                'element', 'first element', 'main element'
            ]
            desc_lower = mapped_params['index'].lower()
            if any(desc in desc_lower for desc in element_descriptions):
                mapped_params['index'] = 0
        
        return mapped_params
    
    async def setup(self, api_url: Optional[str] = None, sandbox_id: Optional[str] = None):
        """Set up the tool with API URL and intervention capabilities"""
        result = await super().setup(api_url, sandbox_id)
        if result.get("success") and self.api_base_url:
            self.intervention_helper.set_api_url(self.api_base_url)
        return result
    
    async def _auto_detect_intervention_needed(self) -> Dict[str, Any]:
        """Use the new auto-detect API endpoint to check if intervention is needed"""
        try:
            data = {
                "check_captcha": True,
                "check_login": True,
                "check_security": True,
                "check_anti_bot": True,
                "check_cookies": True
            }
            return await self._execute_browser_action("auto_detect_intervention", data)
        except Exception as e:
            logger.error(f"Auto-detection failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _request_intervention(self, intervention_type: InterventionType, 
                                  message: str, instructions: Optional[str] = None,
                                  context: Optional[Dict[str, Any]] = None,
                                  auto_detect: bool = False) -> Dict[str, Any]:
        """Request human intervention using the new API endpoint"""
        try:
            data = {
                "intervention_type": intervention_type.value,
                "message": message,
                "instructions": instructions,
                "timeout_seconds": self.intervention_timeout,
                "context": context or {},
                "take_screenshot": True,
                "auto_detect": auto_detect
            }
            return await self._execute_browser_action("request_intervention", data)
        except Exception as e:
            logger.error(f"Intervention request failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _check_intervention_status(self, intervention_id: str) -> Dict[str, Any]:
        """Check the status of an intervention request"""
        try:
            data = {"intervention_id": intervention_id}
            return await self._execute_browser_action("intervention_status", data)
        except Exception as e:
            logger.error(f"Status check failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _complete_intervention(self, intervention_id: str, 
                                   user_message: Optional[str] = None,
                                   success: bool = True) -> Dict[str, Any]:
        """Mark an intervention as complete"""
        try:
            data = {
                "intervention_id": intervention_id,
                "user_message": user_message,
                "success": success
            }
            return await self._execute_browser_action("complete_intervention", data)
        except Exception as e:
            logger.error(f"Intervention completion failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _cancel_intervention(self, intervention_id: str, 
                                 reason: Optional[str] = None) -> Dict[str, Any]:
        """Cancel an intervention request"""
        try:
            data = {
                "intervention_id": intervention_id,
                "reason": reason
            }
            return await self._execute_browser_action("cancel_intervention", data)
        except Exception as e:
            logger.error(f"Intervention cancellation failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _execute_with_intervention_support(self, endpoint: str, data: Any = None, 
                                               method: str = "POST", 
                                               retry_on_intervention: bool = True) -> Dict[str, Any]:
        """Execute browser action with automatic intervention detection and handling"""
        
        # First, check if intervention is needed before the action
        if self.auto_intervention_enabled:
            detection_result = await self._auto_detect_intervention_needed()
            if detection_result.get("intervention_needed"):
                logger.info("🔍 Intervention needed detected before action")
                # Handle detected intervention
                await self._handle_detected_intervention(detection_result)
        
        # Execute the main action
        result = await self._execute_browser_action(endpoint, data, method)
        
        # If action failed and we should retry with intervention detection
        if not result.get("success") and retry_on_intervention:
            error_message = result.get("error", "").lower()
            
            # Check for common error patterns that might indicate intervention is needed
            intervention_indicators = [
                "captcha", "blocked", "verification", "security", "bot", 
                "access denied", "forbidden", "rate limit", "please complete"
            ]
            
            if any(indicator in error_message for indicator in intervention_indicators):
                logger.info("🔍 Potential intervention scenario detected from error")
                detection_result = await self._auto_detect_intervention_needed()
                
                if detection_result.get("intervention_needed"):
                    await self._handle_detected_intervention(detection_result)
                    # Retry the action after intervention
                    result = await self._execute_browser_action(endpoint, data, method)
                else:
                    logger.warning(f"No intervention detected but action failed: {result.get('error')}")
        
        return result
    
    async def _handle_detected_intervention(self, detection_result: Dict[str, Any]) -> Dict[str, Any]:
        """Handle intervention based on detection results"""
        intervention_types = detection_result.get("detected_types", [])
        
        if not intervention_types:
            logger.warning("No specific intervention types detected")
            return {"success": False, "error": "No intervention types detected"}
        
        # Map detected types to our enum
        type_mapping = {
            "captcha": InterventionType.CAPTCHA,
            "login_required": InterventionType.LOGIN_REQUIRED,
            "security_check": InterventionType.SECURITY_CHECK,
            "anti_bot_protection": InterventionType.ANTI_BOT_PROTECTION,
            "cookies_consent": InterventionType.COOKIES_CONSENT,
            "two_factor_auth": InterventionType.TWO_FACTOR_AUTH,
            "age_verification": InterventionType.AGE_VERIFICATION
        }
        
        # Use the first detected type or CUSTOM if unknown
        primary_type = intervention_types[0]
        intervention_type = type_mapping.get(primary_type, InterventionType.CUSTOM)
        
        # Create appropriate message and instructions
        messages = {
            InterventionType.CAPTCHA: "CAPTCHA verification required",
            InterventionType.LOGIN_REQUIRED: "Login required to continue",
            InterventionType.SECURITY_CHECK: "Security verification needed",
            InterventionType.ANTI_BOT_PROTECTION: "Anti-bot protection detected",
            InterventionType.COOKIES_CONSENT: "Cookie consent required"
        }
        
        message = messages.get(intervention_type, f"Human intervention needed: {primary_type}")
        instructions = f"Please complete the {primary_type} requirement and click continue"
        
        # Request intervention
        intervention_result = await self._request_intervention(
            intervention_type=intervention_type,
            message=message,
            instructions=instructions,
            context=detection_result,
            auto_detect=True
        )
        
        if intervention_result.get("success"):
            intervention_id = intervention_result.get("intervention_id")
            if intervention_id:
                # Wait for intervention completion
                await self._wait_for_intervention_completion(intervention_id)
        
        return intervention_result
    
    async def _wait_for_intervention_completion(self, intervention_id: str, 
                                              check_interval: int = 5) -> Dict[str, Any]:
        """Wait for intervention to be completed"""
        max_checks = self.intervention_timeout // check_interval
        
        for _ in range(max_checks):
            status_result = await self._check_intervention_status(intervention_id)
            
            if status_result.get("success"):
                status = status_result.get("status")
                if status in ["completed", "cancelled"]:
                    logger.info(f"Intervention {intervention_id} {status}")
                    return status_result
            
            await asyncio.sleep(check_interval)
        
        # Timeout reached
        logger.warning(f"Intervention {intervention_id} timed out")
        await self._cancel_intervention(intervention_id, "Timeout reached")
        return {"success": False, "error": "Intervention timeout"}


# Enhanced Browser Navigation Tools

class SmartNavigationTool(InterventionAwareBrowserTool):
    """Enhanced navigation tool with automatic intervention handling"""
    
    name: str = "smart_navigate_to"
    description: str = """Navigate to a URL with automatic handling of CAPTCHAs, cookie consent, 
    login requirements, and other common barriers. Uses the latest browser automation API."""
    
    class NavigateInput(BaseModel):
        url: str = Field(..., description="URL to navigate to")
    
    args_schema: Type[BaseModel] = NavigateInput
    
    async def _arun(self, url: str) -> str:
        """Navigate to URL with intervention support"""
        try:
            data = {"url": url}
            result = await self._execute_with_intervention_support("navigate_to", data)
            
            if result.get("success"):
                return f"Successfully navigated to {url}"
            else:
                return f"Navigation failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error navigating to {url}: {str(e)}"


class SmartSearchTool(InterventionAwareBrowserTool):
    """Google search tool with intervention support"""
    
    name: str = "smart_search_google"
    description: str = """Search Google with automatic handling of security checks and CAPTCHAs"""
    
    class SearchInput(BaseModel):
        query: str = Field(..., description="Search query")
    
    args_schema: Type[BaseModel] = SearchInput
    
    async def _arun(self, query: str) -> str:
        """Search Google with intervention support"""
        try:
            data = {"query": query}
            result = await self._execute_with_intervention_support("search_google", data)
            
            if result.get("success"):
                return f"Successfully searched for: {query}"
            else:
                return f"Search failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error searching for {query}: {str(e)}"


class SmartGoBackTool(InterventionAwareBrowserTool):
    """Enhanced go back tool with intervention support"""
    
    name: str = "smart_go_back"
    description: str = """Go back in browser history with automatic intervention handling"""
    
    async def _arun(self) -> str:
        """Go back with intervention support"""
        try:
            result = await self._execute_with_intervention_support("go_back", {})
            
            if result.get("success"):
                return "Successfully went back in browser history"
            else:
                return f"Go back failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error going back: {str(e)}"


class SmartGoForwardTool(InterventionAwareBrowserTool):
    """Enhanced go forward tool with intervention support"""
    
    name: str = "smart_go_forward"
    description: str = """Go forward in browser history with automatic intervention handling"""
    
    async def _arun(self) -> str:
        """Go forward with intervention support"""
        try:
            result = await self._execute_with_intervention_support("go_forward", {})
            
            if result.get("success"):
                return "Successfully went forward in browser history"
            else:
                return f"Go forward failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error going forward: {str(e)}"


class SmartRefreshTool(InterventionAwareBrowserTool):
    """Enhanced refresh tool with intervention support"""
    
    name: str = "smart_refresh"
    description: str = """Refresh the current page with automatic intervention handling"""
    
    async def _arun(self) -> str:
        """Refresh with intervention support"""
        try:
            result = await self._execute_with_intervention_support("refresh", {})
            
            if result.get("success"):
                return "Successfully refreshed the page"
            else:
                return f"Refresh failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error refreshing page: {str(e)}"


class SmartWaitTool(InterventionAwareBrowserTool):
    """Enhanced wait tool with intervention support"""
    
    name: str = "smart_wait"
    description: str = """Wait for a specified time with automatic intervention detection"""
    
    class WaitInput(BaseModel):
        seconds: int = Field(3, description="Number of seconds to wait")
    
    args_schema: Type[BaseModel] = WaitInput
    
    async def _arun(self, seconds: int = 3) -> str:
        """Wait with intervention support"""
        try:
            data = {"seconds": seconds}
            result = await self._execute_with_intervention_support("wait", data)
            
            if result.get("success"):
                return f"Successfully waited for {seconds} seconds"
            else:
                return f"Wait failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error waiting: {str(e)}"


# Enhanced Element Interaction Tools

class SmartClickElementTool(InterventionAwareBrowserTool):
    """Enhanced click element tool with intervention support"""
    
    name: str = "smart_click_element"
    description: str = """Click an element by index with automatic intervention handling 
    for any security checks or verifications that may appear"""
    
    class ClickElementInput(BaseModel):
        click_params: str = Field(default="{}", description="JSON string with click parameters containing 'index' field")
    
    args_schema: Type[BaseModel] = ClickElementInput
    
    def _run(self, click_params: str = "{}") -> str:
        """Synchronous version - runs async method in event loop"""
        import asyncio
        import concurrent.futures
        import json
        
        try:
            # Parse JSON string to get index
            params = json.loads(click_params)
            index = params.get('index') or params.get('element_index', 0)
            
            # Try to get existing event loop
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is already running, create a new one in a thread
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, self._arun(index))
                        return future.result()
                else:
                    return loop.run_until_complete(self._arun(index))
            except RuntimeError:
                # No event loop running, create a new one
                return asyncio.run(self._arun(index))
        except (json.JSONDecodeError, KeyError) as e:
            return f"Error parsing click parameters: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def _arun(self, index: int) -> str:
        """Click element with intervention support"""
        try:
            data = {"index": index}
            result = await self._execute_with_intervention_support("click_element", data)
            
            if result.get("success"):
                return f"Successfully clicked element at index: {index}"
            else:
                return f"Click failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error clicking element {index}: {str(e)}"


class SmartInputTextTool(InterventionAwareBrowserTool):
    """Enhanced text input tool with intervention support"""
    
    name: str = "smart_input_text"
    description: str = """Input text into an element with automatic handling of verification steps"""
    
    class InputTextInput(BaseModel):
        index: int = Field(..., description="Index of the element to input text into")
        text: str = Field(..., description="Text to input")
    
    args_schema: Type[BaseModel] = InputTextInput
    
    async def _arun(self, index: int, text: str) -> str:
        """Input text with intervention support"""
        try:
            data = {"index": index, "text": text}
            result = await self._execute_with_intervention_support("input_text", data)
            
            if result.get("success"):
                return f"Successfully input text into element at index: {index}"
            else:
                return f"Text input failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error inputting text into element {index}: {str(e)}"


class SmartSendKeysTool(InterventionAwareBrowserTool):
    """Enhanced send keys tool with intervention support"""
    
    name: str = "smart_send_keys"
    description: str = """Send keyboard keys with automatic intervention handling"""
    
    class SendKeysInput(BaseModel):
        keys: str = Field(..., description="Keys to send (e.g., 'Enter', 'Tab', 'Escape')")
    
    args_schema: Type[BaseModel] = SendKeysInput
    
    async def _arun(self, keys: str) -> str:
        """Send keys with intervention support"""
        try:
            data = {"keys": keys}
            result = await self._execute_with_intervention_support("send_keys", data)
            
            if result.get("success"):
                return f"Successfully sent keys: {keys}"
            else:
                return f"Send keys failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error sending keys {keys}: {str(e)}"


class SmartClickCoordinatesTool(InterventionAwareBrowserTool):
    """Enhanced click coordinates tool with intervention support"""
    
    name: str = "smart_click_coordinates"
    description: str = """Click at specific coordinates with automatic intervention handling"""
    
    class ClickCoordinatesInput(BaseModel):
        x: int = Field(..., description="X coordinate")
        y: int = Field(..., description="Y coordinate")
    
    args_schema: Type[BaseModel] = ClickCoordinatesInput
    
    async def _arun(self, x: int, y: int) -> str:
        """Click coordinates with intervention support"""
        try:
            data = {"x": x, "y": y}
            result = await self._execute_with_intervention_support("click_coordinates", data)
            
            if result.get("success"):
                return f"Successfully clicked at coordinates ({x}, {y})"
            else:
                return f"Click failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error clicking at ({x}, {y}): {str(e)}"


class SmartDragDropTool(InterventionAwareBrowserTool):
    """Enhanced drag and drop tool with intervention support"""
    
    name: str = "smart_drag_drop"
    description: str = """Drag and drop elements with automatic intervention handling"""
    
    class DragDropInput(BaseModel):
        from_index: int = Field(..., description="Index of source element")
        to_index: int = Field(..., description="Index of target element")
    
    args_schema: Type[BaseModel] = DragDropInput
    
    async def _arun(self, from_index: int, to_index: int) -> str:
        """Drag and drop with intervention support"""
        try:
            data = {"from_index": from_index, "to_index": to_index}
            result = await self._execute_with_intervention_support("drag_drop", data)
            
            if result.get("success"):
                return f"Successfully dragged element {from_index} to {to_index}"
            else:
                return f"Drag drop failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error dragging element {from_index} to {to_index}: {str(e)}"


# Enhanced Tab Management Tools

class SmartSwitchTabTool(InterventionAwareBrowserTool):
    """Enhanced switch tab tool with intervention support"""
    
    name: str = "smart_switch_tab"
    description: str = """Switch to a different browser tab with automatic intervention handling"""
    
    class SwitchTabInput(BaseModel):
        page_id: int = Field(..., description="ID of the page/tab to switch to")
    
    args_schema: Type[BaseModel] = SwitchTabInput
    
    async def _arun(self, page_id: int) -> str:
        """Switch tab with intervention support"""
        try:
            data = {"page_id": page_id}
            result = await self._execute_with_intervention_support("switch_tab", data)
            
            if result.get("success"):
                return f"Successfully switched to tab {page_id}"
            else:
                return f"Switch tab failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error switching to tab {page_id}: {str(e)}"


class SmartOpenTabTool(InterventionAwareBrowserTool):
    """Enhanced open tab tool with intervention support"""
    
    name: str = "smart_open_tab"
    description: str = """Open a new browser tab with automatic intervention handling"""
    
    class OpenTabInput(BaseModel):
        url: str = Field(..., description="URL to open in the new tab")
    
    args_schema: Type[BaseModel] = OpenTabInput
    
    async def _arun(self, url: str) -> str:
        """Open tab with intervention support"""
        try:
            data = {"url": url}
            result = await self._execute_with_intervention_support("open_tab", data)
            
            if result.get("success"):
                return f"Successfully opened new tab with URL: {url}"
            else:
                return f"Open tab failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error opening tab with URL {url}: {str(e)}"


class SmartCloseTabTool(InterventionAwareBrowserTool):
    """Enhanced close tab tool with intervention support"""
    
    name: str = "smart_close_tab"
    description: str = """Close a browser tab with automatic intervention handling"""
    
    class CloseTabInput(BaseModel):
        page_id: int = Field(..., description="ID of the page/tab to close")
    
    args_schema: Type[BaseModel] = CloseTabInput
    
    async def _arun(self, page_id: int) -> str:
        """Close tab with intervention support"""
        try:
            data = {"page_id": page_id}
            result = await self._execute_with_intervention_support("close_tab", data)
            
            if result.get("success"):
                return f"Successfully closed tab {page_id}"
            else:
                return f"Close tab failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error closing tab {page_id}: {str(e)}"


# Enhanced Content and Scrolling Tools


class SmartFormFillerTool(InterventionAwareBrowserTool):
    """Form filling tool with intervention support for complex fields"""
    
    name: str = "smart_fill_form"
    description: str = """Fill form fields with automatic handling of complex scenarios like 
    two-factor authentication, CAPTCHA verification, and field validation errors."""
    
    class FormInput(BaseModel):
        # Support multiple input formats for LangChain compatibility
        selector: Optional[str] = Field(None, description="CSS selector for the form field")
        value: Optional[str] = Field(None, description="Value to enter in the field")
        field_type: str = Field("text", description="Type of field (text, password, email, etc.)")
        wait_for_validation: bool = Field(True, description="Wait for field validation")
        
        # Support LangChain agent format
        form_data: Optional[Dict[str, Any]] = Field(None, description="Form data as key-value pairs")
        submit: Optional[bool] = Field(False, description="Whether to submit the form after filling")
        
        class Config:
            extra = "ignore"  # Ignore extra fields
    
    args_schema: Type[BaseModel] = FormInput
    
    def _run(self, *args, **kwargs) -> str:
        """Synchronous version - runs async method in event loop"""
        import asyncio
        import concurrent.futures
        import json
        
        # Handle LangChain calling pattern with positional arguments
        if args and len(args) == 1:
            # LangChain passed a single argument (likely JSON string)
            arg = args[0]
            if isinstance(arg, str):
                try:
                    parsed_data = json.loads(arg)
                    if isinstance(parsed_data, dict):
                        kwargs = parsed_data
                except json.JSONDecodeError:
                    # Not JSON, treat as kwargs
                    pass
            elif isinstance(arg, dict):
                kwargs = arg
        
        # Handle LangChain passing JSON strings as single argument in kwargs
        if len(kwargs) == 1:
            key, value = next(iter(kwargs.items()))
            if isinstance(value, str):
                try:
                    # Try to parse as JSON
                    parsed_data = json.loads(value)
                    if isinstance(parsed_data, dict):
                        kwargs = parsed_data
                except json.JSONDecodeError:
                    # Not JSON, use original kwargs
                    pass
        
        # Convert parameters to kwargs for internal handling
        processed_kwargs = {
            'selector': kwargs.get('selector'),
            'value': kwargs.get('value'), 
            'field_type': kwargs.get('field_type', 'text'),
            'wait_for_validation': kwargs.get('wait_for_validation', True),
            'form_data': kwargs.get('form_data'),
            'submit': kwargs.get('submit', False)
        }
        
        try:
            # Try to get existing event loop
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is already running, create a new one in a thread
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, self._arun_with_kwargs(**processed_kwargs))
                        return future.result()
                else:
                    return loop.run_until_complete(self._arun_with_kwargs(**processed_kwargs))
            except RuntimeError:
                # No event loop running, create a new one
                return asyncio.run(self._arun_with_kwargs(**processed_kwargs))
        except Exception as e:
            return f"Error filling form: {str(e)}"
    
    async def _arun_with_kwargs(self, **kwargs) -> str:
        """Handle both input formats"""
        # Check if using LangChain agent format with form_data
        if 'form_data' in kwargs and kwargs['form_data']:
            form_data = kwargs['form_data']
            submit_form = kwargs.get('submit', False)
            
            # Handle Google search specifically
            if 'q' in form_data:
                # Google search
                data = {"query": form_data['q']}
                result = await self._execute_with_intervention_support("search_google", data)
            else:
                # Generic form filling - try to fill each field
                results = []
                for field_name, field_value in form_data.items():
                    # Try to input text into the field
                    field_data = {"text": str(field_value), "index": 0}
                    field_result = await self._execute_with_intervention_support("input_text", field_data)
                    results.append(f"{field_name}: {field_result.get('success', False)}")
                
                result = {"success": True, "data": {"filled_fields": results}}
            
            if result.get("success"):
                action = "searched" if 'q' in form_data else "filled form"
                if submit_form:
                    action += " and submitted"
                return f"Successfully {action} with data: {form_data}"
            else:
                return f"Failed to fill form: {result.get('error', 'Unknown error')}"
        else:
            # Use original format
            selector = kwargs.get('selector')
            value = kwargs.get('value')
            field_type = kwargs.get('field_type', 'text')
            wait_for_validation = kwargs.get('wait_for_validation', True)
            
            if not selector or not value:
                return "Error: selector and value are required"
                
            return await self._arun(selector, value, field_type, wait_for_validation)
    
    async def _arun(self, selector: str, value: str, field_type: str = "text", 
                   wait_for_validation: bool = True) -> str:
        """Fill form field with intervention support"""
        try:
            # Special handling for sensitive fields
            if field_type.lower() in ["password", "2fa", "otp", "verification"]:
                # Check if manual intervention might be needed
                intervention_result = await self._request_intervention(
                    intervention_type=InterventionType.COMPLEX_DATA_ENTRY,
                    message=f"Please verify and fill the {field_type} field",
                    instructions=f"Fill the field with selector '{selector}' with the appropriate {field_type}",
                )
                
                if not intervention_result.get("success"):
                    return f"Failed to handle {field_type} field: {intervention_result.get('error')}"
                
                # Wait for completion if intervention was requested
                if intervention_result.get("intervention_id"):
                    await self._wait_for_intervention_completion(intervention_result["intervention_id"])
                
                return f"Successfully handled {field_type} field with human assistance"
            else:
                # Regular field handling
                data = {"selector": selector, "text": value, "index": 0}
                result = await self._execute_with_intervention_support("input_text", data)
                
                if result.get("success"):
                    return f"Successfully filled {field_type} field: {selector}"
                else:
                    return f"Failed to fill field: {result.get('error', 'Unknown error')}"
                    
        except Exception as e:
            return f"Error filling form field {selector}: {str(e)}"


# Enhanced Content Extraction Tools

class SmartExtractContentTool(InterventionAwareBrowserTool):
    """Extract page content with intervention support"""
    
    name: str = "smart_extract_content"
    description: str = """Extract content from the current page, handling any access restrictions"""
    
    class ExtractContentInput(BaseModel):
        goal: str = Field(..., description="Specific extraction goal or type")
    
    args_schema: Type[BaseModel] = ExtractContentInput
    
    async def _arun(self, goal: str) -> str:
        """Extract content with intervention support"""
        try:
            result = await self._execute_with_intervention_support("extract_content", {"goal": goal})
            
            if result.get("success"):
                content = result.get("content", "")
                return f"Successfully extracted content:\n{content}"
            else:
                return f"Content extraction failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error extracting content: {str(e)}"


class SmartGetPageContentTool(InterventionAwareBrowserTool):
    """Enhanced get page content tool with intervention support"""
    
    name: str = "smart_get_page_content"
    description: str = """Get page content with automatic intervention handling"""
    
    async def _arun(self) -> str:
        """Get page content with intervention support"""
        try:
            result = await self._execute_with_intervention_support("get_page_content", {})
            
            if result.get("success"):
                content = result.get("content", "")
                return f"Successfully retrieved page content:\n{content}"
            else:
                return f"Get page content failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error getting page content: {str(e)}"


class SmartScrollDownTool(InterventionAwareBrowserTool):
    """Enhanced scroll down tool with intervention support"""
    
    name: str = "smart_scroll_down"
    description: str = """Scroll down the page with automatic intervention handling"""
    
    class ScrollDownInput(BaseModel):
        amount: Optional[int] = Field(None, description="Amount to scroll down (pixels)")
    
    args_schema: Type[BaseModel] = ScrollDownInput
    
    async def _arun(self, amount: Optional[int] = None) -> str:
        """Scroll down with intervention support"""
        try:
            data = {"amount": amount} if amount is not None else {}
            result = await self._execute_with_intervention_support("scroll_down", data)
            
            if result.get("success"):
                return "Successfully scrolled down"
            else:
                return f"Scroll down failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error scrolling down: {str(e)}"


class SmartScrollUpTool(InterventionAwareBrowserTool):
    """Enhanced scroll up tool with intervention support"""
    
    name: str = "smart_scroll_up"
    description: str = """Scroll up the page with automatic intervention handling"""
    
    class ScrollUpInput(BaseModel):
        amount: Optional[int] = Field(None, description="Amount to scroll up (pixels)")
    
    args_schema: Type[BaseModel] = ScrollUpInput
    
    async def _arun(self, amount: Optional[int] = None) -> str:
        """Scroll up with intervention support"""
        try:
            data = {"amount": amount} if amount is not None else {}
            result = await self._execute_with_intervention_support("scroll_up", data)
            
            if result.get("success"):
                return "Successfully scrolled up"
            else:
                return f"Scroll up failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error scrolling up: {str(e)}"


class SmartScrollToTextTool(InterventionAwareBrowserTool):
    """Enhanced scroll to text tool with intervention support"""
    
    name: str = "smart_scroll_to_text"
    description: str = """Scroll to specific text with automatic intervention handling"""
    
    class ScrollToTextInput(BaseModel):
        text: str = Field(..., description="Text to scroll to")
    
    args_schema: Type[BaseModel] = ScrollToTextInput
    
    async def _arun(self, text: str) -> str:
        """Scroll to text with intervention support"""
        try:
            result = await self._execute_with_intervention_support("scroll_to_text", text)
            
            if result.get("success"):
                return f"Successfully scrolled to text: {text}"
            else:
                return f"Scroll to text failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error scrolling to text '{text}': {str(e)}"


class SmartScrollToTopTool(InterventionAwareBrowserTool):
    """Enhanced scroll to top tool with intervention support"""
    
    name: str = "smart_scroll_to_top"
    description: str = """Scroll to top of page with automatic intervention handling"""
    
    async def _arun(self) -> str:
        """Scroll to top with intervention support"""
        try:
            result = await self._execute_with_intervention_support("scroll_to_top", {})
            
            if result.get("success"):
                return "Successfully scrolled to top of page"
            else:
                return f"Scroll to top failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error scrolling to top: {str(e)}"


class SmartScrollToBottomTool(InterventionAwareBrowserTool):
    """Enhanced scroll to bottom tool with intervention support"""
    
    name: str = "smart_scroll_to_bottom"
    description: str = """Scroll to bottom of page with automatic intervention handling"""
    
    async def _arun(self) -> str:
        """Scroll to bottom with intervention support"""
        try:
            result = await self._execute_with_intervention_support("scroll_to_bottom", {})
            
            if result.get("success"):
                return "Successfully scrolled to bottom of page"
            else:
                return f"Scroll to bottom failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error scrolling to bottom: {str(e)}"


# Enhanced Form Interaction Tools

class SmartGetDropdownOptionsTool(InterventionAwareBrowserTool):
    """Enhanced get dropdown options tool with intervention support"""
    
    name: str = "smart_get_dropdown_options"
    description: str = """Get dropdown options with automatic intervention handling"""
    
    class GetDropdownOptionsInput(BaseModel):
        index: int = Field(..., description="Index of the dropdown element")
    
    args_schema: Type[BaseModel] = GetDropdownOptionsInput
    
    async def _arun(self, index: int) -> str:
        """Get dropdown options with intervention support"""
        try:
            result = await self._execute_with_intervention_support("get_dropdown_options", index)
            
            if result.get("success"):
                options = result.get("options", [])
                return f"Successfully retrieved dropdown options: {options}"
            else:
                return f"Get dropdown options failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error getting dropdown options for element {index}: {str(e)}"


class SmartSelectDropdownOptionTool(InterventionAwareBrowserTool):
    """Enhanced select dropdown option tool with intervention support"""
    
    name: str = "smart_select_dropdown_option"
    description: str = """Select dropdown option with automatic intervention handling"""
    
    class SelectDropdownOptionInput(BaseModel):
        index: int = Field(..., description="Index of the dropdown element")
        option_index: int = Field(..., description="Index of the option to select")
    
    args_schema: Type[BaseModel] = SelectDropdownOptionInput
    
    async def _arun(self, index: int, option_index: int) -> str:
        """Select dropdown option with intervention support"""
        try:
            data = {"index": index, "option_index": option_index}
            result = await self._execute_with_intervention_support("select_dropdown_option", data)
            
            if result.get("success"):
                return f"Successfully selected option {option_index} from dropdown {index}"
            else:
                return f"Select dropdown option failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error selecting option {option_index} from dropdown {index}: {str(e)}"


# Enhanced PDF and Screenshot Tools

class SmartSavePdfTool(InterventionAwareBrowserTool):
    """Enhanced save PDF tool with intervention support"""
    
    name: str = "smart_save_pdf"
    description: str = """Save page as PDF with automatic intervention handling"""
    
    class SavePdfInput(BaseModel):
        filename: str = Field(..., description="Filename for the PDF")
    
    args_schema: Type[BaseModel] = SavePdfInput
    
    async def _arun(self, filename: str) -> str:
        """Save PDF with intervention support"""
        try:
            data = {"filename": filename}
            result = await self._execute_with_intervention_support("save_pdf", data)
            
            if result.get("success"):
                return f"Successfully saved PDF: {filename}"
            else:
                return f"Save PDF failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error saving PDF {filename}: {str(e)}"


class SmartGeneratePdfTool(InterventionAwareBrowserTool):
    """Enhanced generate PDF tool with intervention support"""
    
    name: str = "smart_generate_pdf"
    description: str = """Generate PDF with automatic intervention handling"""
    
    async def _arun(self) -> str:
        """Generate PDF with intervention support"""
        try:
            result = await self._execute_with_intervention_support("generate_pdf", {})
            
            if result.get("success"):
                return "Successfully generated PDF"
            else:
                return f"Generate PDF failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error generating PDF: {str(e)}"


class SmartGetPagePdfTool(InterventionAwareBrowserTool):
    """Enhanced get page PDF tool with intervention support"""
    
    name: str = "smart_get_page_pdf"
    description: str = """Get page as PDF with automatic intervention handling"""
    
    async def _arun(self) -> str:
        """Get page PDF with intervention support"""
        try:
            result = await self._execute_with_intervention_support("get_page_pdf", {})
            
            if result.get("success"):
                return "Successfully retrieved page as PDF"
            else:
                return f"Get page PDF failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error getting page PDF: {str(e)}"


class SmartTakeScreenshotTool(InterventionAwareBrowserTool):
    """Enhanced take screenshot tool with intervention support"""
    
    name: str = "smart_take_screenshot"
    description: str = """Take screenshot with automatic intervention handling"""
    
    async def _arun(self) -> str:
        """Take screenshot with intervention support"""
        try:
            result = await self._execute_with_intervention_support("take_screenshot", {})
            
            if result.get("success"):
                return "Successfully took screenshot"
            else:
                return f"Take screenshot failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error taking screenshot: {str(e)}"


# Enhanced Cookie and Storage Management Tools

class SmartGetCookiesTool(InterventionAwareBrowserTool):
    """Enhanced get cookies tool with intervention support"""
    
    name: str = "smart_get_cookies"
    description: str = """Get cookies with automatic intervention handling"""
    
    async def _arun(self) -> str:
        """Get cookies with intervention support"""
        try:
            result = await self._execute_with_intervention_support("get_cookies", {})
            
            if result.get("success"):
                cookies = result.get("cookies", [])
                return f"Successfully retrieved cookies: {cookies}"
            else:
                return f"Get cookies failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error getting cookies: {str(e)}"


class SmartSetCookieTool(InterventionAwareBrowserTool):
    """Enhanced set cookie tool with intervention support"""
    
    name: str = "smart_set_cookie"
    description: str = """Set cookie with automatic intervention handling"""
    
    class SetCookieInput(BaseModel):
        cookie_data: dict = Field(..., description="Cookie data to set")
    
    args_schema: Type[BaseModel] = SetCookieInput
    
    async def _arun(self, cookie_data: dict) -> str:
        """Set cookie with intervention support"""
        try:
            result = await self._execute_with_intervention_support("set_cookie", cookie_data)
            
            if result.get("success"):
                return "Successfully set cookie"
            else:
                return f"Set cookie failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error setting cookie: {str(e)}"


class SmartClearCookiesTool(InterventionAwareBrowserTool):
    """Enhanced clear cookies tool with intervention support"""
    
    name: str = "smart_clear_cookies"
    description: str = """Clear cookies with automatic intervention handling"""
    
    async def _arun(self) -> str:
        """Clear cookies with intervention support"""
        try:
            result = await self._execute_with_intervention_support("clear_cookies", {})
            
            if result.get("success"):
                return "Successfully cleared cookies"
            else:
                return f"Clear cookies failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error clearing cookies: {str(e)}"


class SmartClearLocalStorageTool(InterventionAwareBrowserTool):
    """Enhanced clear local storage tool with intervention support"""
    
    name: str = "smart_clear_local_storage"
    description: str = """Clear local storage with automatic intervention handling"""
    
    async def _arun(self) -> str:
        """Clear local storage with intervention support"""
        try:
            result = await self._execute_with_intervention_support("clear_local_storage", {})
            
            if result.get("success"):
                return "Successfully cleared local storage"
            else:
                return f"Clear local storage failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error clearing local storage: {str(e)}"


# Enhanced Dialog Handling Tools

class SmartAcceptDialogTool(InterventionAwareBrowserTool):
    """Enhanced accept dialog tool with intervention support"""
    
    name: str = "smart_accept_dialog"
    description: str = """Accept dialog with automatic intervention handling"""
    
    async def _arun(self) -> str:
        """Accept dialog with intervention support"""
        try:
            result = await self._execute_with_intervention_support("accept_dialog", {})
            
            if result.get("success"):
                return "Successfully accepted dialog"
            else:
                return f"Accept dialog failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error accepting dialog: {str(e)}"


class SmartDismissDialogTool(InterventionAwareBrowserTool):
    """Enhanced dismiss dialog tool with intervention support"""
    
    name: str = "smart_dismiss_dialog"
    description: str = """Dismiss dialog with automatic intervention handling"""
    
    async def _arun(self) -> str:
        """Dismiss dialog with intervention support"""
        try:
            result = await self._execute_with_intervention_support("dismiss_dialog", {})
            
            if result.get("success"):
                return "Successfully dismissed dialog"
            else:
                return f"Dismiss dialog failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error dismissing dialog: {str(e)}"


# Enhanced Frame Management Tools

class SmartSwitchToFrameTool(InterventionAwareBrowserTool):
    """Enhanced switch to frame tool with intervention support"""
    
    name: str = "smart_switch_to_frame"
    description: str = """Switch to frame with automatic intervention handling"""
    
    class SwitchToFrameInput(BaseModel):
        frame_index: int = Field(..., description="Index of the frame to switch to")
    
    args_schema: Type[BaseModel] = SwitchToFrameInput
    
    async def _arun(self, frame_index: int) -> str:
        """Switch to frame with intervention support"""
        try:
            data = {"frame_index": frame_index}
            result = await self._execute_with_intervention_support("switch_to_frame", data)
            
            if result.get("success"):
                return f"Successfully switched to frame {frame_index}"
            else:
                return f"Switch to frame failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error switching to frame {frame_index}: {str(e)}"


class SmartSwitchToMainFrameTool(InterventionAwareBrowserTool):
    """Enhanced switch to main frame tool with intervention support"""
    
    name: str = "smart_switch_to_main_frame"
    description: str = """Switch to main frame with automatic intervention handling"""
    
    async def _arun(self) -> str:
        """Switch to main frame with intervention support"""
        try:
            result = await self._execute_with_intervention_support("switch_to_main_frame", {})
            
            if result.get("success"):
                return "Successfully switched to main frame"
            else:
                return f"Switch to main frame failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error switching to main frame: {str(e)}"


# Enhanced Network Tools

class SmartSetNetworkConditionsTool(InterventionAwareBrowserTool):
    """Enhanced set network conditions tool with intervention support"""
    
    name: str = "smart_set_network_conditions"
    description: str = """Set network conditions with automatic intervention handling"""
    
    class SetNetworkConditionsInput(BaseModel):
        conditions: dict = Field(..., description="Network conditions to set")
    
    args_schema: Type[BaseModel] = SetNetworkConditionsInput
    
    async def _arun(self, conditions: dict) -> str:
        """Set network conditions with intervention support"""
        try:
            result = await self._execute_with_intervention_support("set_network_conditions", conditions)
            
            if result.get("success"):
                return "Successfully set network conditions"
            else:
                return f"Set network conditions failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error setting network conditions: {str(e)}"


# Enhanced Human Intervention Tools (New API)

class SmartAutoDetectInterventionTool(InterventionAwareBrowserTool):
    """Enhanced auto-detect intervention tool"""
    
    name: str = "smart_auto_detect_intervention"
    description: str = """Automatically detect if human intervention is needed on the current page"""
    
    class AutoDetectInput(BaseModel):
        # Accept the raw input as LangChain provides it
        auto_detect_params: str = Field(default="{}", description="JSON string with detection parameters")
        
        class Config:
            extra = "ignore"  # Ignore extra fields
    
    args_schema: Type[BaseModel] = AutoDetectInput
    
    def _run(self, auto_detect_params: str = "{}") -> str:
        """Synchronous version - runs async method in event loop"""
        import asyncio
        import concurrent.futures
        import json
        
        # Parse the JSON parameters
        try:
            params = json.loads(auto_detect_params)
        except json.JSONDecodeError:
            params = {}
        
        # Extract parameters with defaults
        check_captcha = params.get('check_captcha', True)
        check_login = params.get('check_login', True) 
        check_security = params.get('check_security', True)
        check_anti_bot = params.get('check_anti_bot', True)
        check_cookies = params.get('check_cookies', True)
        
        try:
            # Try to get existing event loop
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is already running, create a new one in a thread
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, self._arun(
                            check_captcha, check_login, check_security, 
                            check_anti_bot, check_cookies))
                        return future.result()
                else:
                    return loop.run_until_complete(self._arun(
                        check_captcha, check_login, check_security, 
                        check_anti_bot, check_cookies))
            except RuntimeError:
                # No event loop running, create a new one
                return asyncio.run(self._arun(
                    check_captcha, check_login, check_security, 
                    check_anti_bot, check_cookies))
        except Exception as e:
            return f"Error detecting intervention needs: {str(e)}"
    
    async def _arun(self, check_captcha: bool = True, check_login: bool = True,
                   check_security: bool = True, check_anti_bot: bool = True,
                   check_cookies: bool = True) -> str:
        """Auto-detect intervention needs"""
        try:
            data = {
                "check_captcha": check_captcha,
                "check_login": check_login,
                "check_security": check_security,
                "check_anti_bot": check_anti_bot,
                "check_cookies": check_cookies
            }
            result = await self._execute_browser_action("auto_detect_intervention", data)
            
            if result.get("success"):
                if result.get("intervention_needed"):
                    detected_types = result.get("detected_types", [])
                    return f"Intervention needed. Detected: {', '.join(detected_types)}"
                else:
                    return "No intervention needed - page is accessible"
            else:
                return f"Detection failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error detecting intervention needs: {str(e)}"


class SmartRequestInterventionTool(InterventionAwareBrowserTool):
    """Enhanced request intervention tool with LangChain JSON string support"""
    
    name: str = "smart_request_intervention"
    description: str = """Request human intervention with comprehensive support. 
    Pass JSON string with intervention parameters. 
    
    Valid intervention_type values:
    - 'captcha': For CAPTCHA solving
    - 'login_required': When login is needed
    - 'security_check': For security verifications
    - 'complex_data_entry': For complex form filling
    - 'anti_bot_protection': When anti-bot measures detected
    - 'two_factor_auth': For 2FA verification
    - 'cookies_consent': For cookie consent dialogs
    - 'age_verification': For age verification prompts
    - 'custom': For any other manual assistance (most common)
    
    Example: {"intervention_type": "custom", "message": "Need help with page analysis"}"""
    
    class RequestInterventionInput(BaseModel):
        intervention_params: str = Field(default="{}", description="JSON string with intervention parameters. Required: intervention_type (from valid list above), message. Optional: instructions, timeout_seconds, context, take_screenshot, auto_detect")
    
    args_schema: Type[BaseModel] = RequestInterventionInput
    
    def _run(self, intervention_params: str = "{}") -> str:
        """Synchronous version - runs async method in event loop"""
        import asyncio
        import concurrent.futures
        import json
        
        try:
            # Parse JSON string to get parameters
            params = json.loads(intervention_params)
            
            # Try to get existing event loop
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is already running, create a new one in a thread
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, self._arun_with_params(params))
                        return future.result()
                else:
                    return loop.run_until_complete(self._arun_with_params(params))
            except RuntimeError:
                # No event loop running, create a new one
                return asyncio.run(self._arun_with_params(params))
        except (json.JSONDecodeError, KeyError) as e:
            return f"Error parsing intervention parameters: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def _arun_with_params(self, params: dict) -> str:
        """Request intervention with enhanced support"""
        try:
            # Valid intervention types from API schema
            valid_types = [
                'captcha', 'login_required', 'security_check', 'complex_data_entry',
                'anti_bot_protection', 'two_factor_auth', 'cookies_consent', 
                'age_verification', 'custom'
            ]
            
            # Extract parameters from dict with defaults
            intervention_type = params.get('intervention_type', 'custom')
            message = params.get('message') or params.get('reason', 'Human intervention requested')
            instructions = params.get('instructions')
            timeout_seconds = params.get('timeout_seconds', 300)
            context = params.get('context', {})
            take_screenshot = params.get('take_screenshot', True)
            auto_detect = params.get('auto_detect', False)
            
            # Validate intervention type
            if intervention_type not in valid_types:
                return f"Invalid intervention_type '{intervention_type}'. Valid types are: {', '.join(valid_types)}. Use 'custom' for general assistance."
            
            data = {
                "intervention_type": intervention_type,
                "message": message,
                "instructions": instructions,
                "timeout_seconds": timeout_seconds,
                "context": context,
                "take_screenshot": take_screenshot,
                "auto_detect": auto_detect
            }
            result = await self._execute_browser_action("request_intervention", data)
            
            if result.get("success"):
                intervention_id = result.get("intervention_id")
                return f"Successfully requested intervention. ID: {intervention_id}"
            else:
                return f"Request intervention failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error requesting intervention: {str(e)}"


class SmartCompleteInterventionTool(InterventionAwareBrowserTool):
    """Enhanced complete intervention tool"""
    
    name: str = "smart_complete_intervention"
    description: str = """Complete human intervention with enhanced support"""
    
    class CompleteInterventionInput(BaseModel):
        intervention_id: str = Field(..., description="ID of the intervention to complete")
        user_message: Optional[str] = Field(None, description="Message from the user")
        success: bool = Field(True, description="Whether the intervention was successful")
    
    args_schema: Type[BaseModel] = CompleteInterventionInput
    
    async def _arun(self, intervention_id: str, user_message: Optional[str] = None,
                   success: bool = True) -> str:
        """Complete intervention with enhanced support"""
        try:
            data = {
                "intervention_id": intervention_id,
                "user_message": user_message,
                "success": success
            }
            result = await self._execute_browser_action("complete_intervention", data)
            
            if result.get("success"):
                return f"Successfully completed intervention {intervention_id}"
            else:
                return f"Complete intervention failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error completing intervention: {str(e)}"


class SmartCancelInterventionTool(InterventionAwareBrowserTool):
    """Enhanced cancel intervention tool"""
    
    name: str = "smart_cancel_intervention"
    description: str = """Cancel human intervention with enhanced support"""
    
    class CancelInterventionInput(BaseModel):
        intervention_id: str = Field(..., description="ID of the intervention to cancel")
        reason: Optional[str] = Field(None, description="Reason for cancellation")
    
    args_schema: Type[BaseModel] = CancelInterventionInput
    
    async def _arun(self, intervention_id: str, reason: Optional[str] = None) -> str:
        """Cancel intervention with enhanced support"""
        try:
            data = {
                "intervention_id": intervention_id,
                "reason": reason
            }
            result = await self._execute_browser_action("cancel_intervention", data)
            
            if result.get("success"):
                return f"Successfully cancelled intervention {intervention_id}"
            else:
                return f"Cancel intervention failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error cancelling intervention: {str(e)}"


class SmartInterventionStatusTool(InterventionAwareBrowserTool):
    """Enhanced intervention status tool"""
    
    name: str = "smart_intervention_status"
    description: str = """Check intervention status with enhanced support"""
    
    class InterventionStatusInput(BaseModel):
        intervention_id: str = Field(..., description="ID of the intervention to check")
    
    args_schema: Type[BaseModel] = InterventionStatusInput
    
    async def _arun(self, intervention_id: str) -> str:
        """Check intervention status with enhanced support"""
        try:
            data = {"intervention_id": intervention_id}
            result = await self._execute_browser_action("intervention_status", data)
            
            if result.get("success"):
                status = result.get("status", "unknown")
                return f"Intervention {intervention_id} status: {status}"
            else:
                return f"Status check failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error checking intervention status: {str(e)}"


class SmartRequestHumanHelpTool(InterventionAwareBrowserTool):
    """Enhanced request human help tool (legacy support)"""
    
    name: str = "smart_request_human_help"
    description: str = """Request human help with legacy support"""
    
    class RequestHumanHelpInput(BaseModel):
        message: str = Field(..., description="Message describing the help needed")
        timeout_seconds: int = Field(300, description="Timeout for the help request")
    
    args_schema: Type[BaseModel] = RequestHumanHelpInput
    
    async def _arun(self, message: str, timeout_seconds: int = 300) -> str:
        """Request human help with enhanced support"""
        try:
            data = {
                "message": message,
                "timeout_seconds": timeout_seconds
            }
            result = await self._execute_browser_action("request_human_help", data)
            
            if result.get("success"):
                return f"Successfully requested human help: {message}"
            else:
                return f"Request human help failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error requesting human help: {str(e)}"


class SmartSolveCaptchaTool(InterventionAwareBrowserTool):
    """Enhanced solve CAPTCHA tool"""
    
    name: str = "smart_solve_captcha"
    description: str = """Solve CAPTCHA with enhanced intervention support"""
    
    class SolveCaptchaInput(BaseModel):
        captcha_type: Optional[str] = Field(None, description="Type of CAPTCHA if known")
        instructions: Optional[str] = Field(None, description="Specific instructions for solving")
        timeout_seconds: int = Field(600, description="Timeout for CAPTCHA solving")
    
    args_schema: Type[BaseModel] = SolveCaptchaInput
    
    async def _arun(self, captcha_type: Optional[str] = None, instructions: Optional[str] = None,
                   timeout_seconds: int = 600) -> str:
        """Solve CAPTCHA with enhanced support"""
        try:
            data = {
                "captcha_type": captcha_type,
                "instructions": instructions,
                "timeout_seconds": timeout_seconds
            }
            result = await self._execute_browser_action("solve_captcha", data)
            
            if result.get("success"):
                return "Successfully solved CAPTCHA"
            else:
                return f"CAPTCHA solving failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error solving CAPTCHA: {str(e)}"


class SmartHandleLoginTool(InterventionAwareBrowserTool):
    """Enhanced handle login tool"""
    
    name: str = "smart_handle_login"
    description: str = """Handle login with enhanced intervention support"""
    
    class HandleLoginInput(BaseModel):
        username: Optional[str] = Field(None, description="Username if available")
        password: Optional[str] = Field(None, description="Password if available")
        instructions: Optional[str] = Field(None, description="Specific login instructions")
        timeout_seconds: int = Field(300, description="Timeout for login handling")
    
    args_schema: Type[BaseModel] = HandleLoginInput
    
    async def _arun(self, username: Optional[str] = None, password: Optional[str] = None,
                   instructions: Optional[str] = None, timeout_seconds: int = 300) -> str:
        """Handle login with enhanced support"""
        try:
            data = {
                "username": username,
                "password": password,
                "instructions": instructions,
                "timeout_seconds": timeout_seconds
            }
            result = await self._execute_browser_action("handle_login", data)
            
            if result.get("success"):
                return "Successfully handled login"
            else:
                return f"Login handling failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Error handling login: {str(e)}"


# ========== ENHANCED TOOL INSTANCES ==========

def get_enhanced_browser_tools():
    """Get all enhanced browser tools with intervention support"""
    return [
        # Enhanced Navigation Tools
        SmartNavigationTool(),
        SmartSearchTool(),
        SmartGoBackTool(),
        SmartGoForwardTool(),
        SmartRefreshTool(),
        SmartWaitTool(),
        
        # Enhanced Interaction Tools
        SmartClickElementTool(),
        SmartInputTextTool(),
        SmartSendKeysTool(),
        SmartClickCoordinatesTool(),
        SmartDragDropTool(),
        
        # Enhanced Tab Management
        SmartSwitchTabTool(),
        SmartOpenTabTool(),
        SmartCloseTabTool(),
        
        # Enhanced Content and Scrolling
        SmartExtractContentTool(),
        SmartGetPageContentTool(),
        SmartScrollDownTool(),
        SmartScrollUpTool(),
        SmartScrollToTextTool(),
        SmartScrollToTopTool(),
        SmartScrollToBottomTool(),
        
        # Enhanced Form Interaction
        SmartGetDropdownOptionsTool(),
        SmartSelectDropdownOptionTool(),
        
        # Enhanced Form Filling
        SmartFormFillerTool(),
        
        # Enhanced PDF and Screenshot Tools
        SmartSavePdfTool(),
        SmartGeneratePdfTool(),
        SmartGetPagePdfTool(),
        SmartTakeScreenshotTool(),
        
        # Enhanced Cookie and Storage Management
        SmartGetCookiesTool(),
        SmartSetCookieTool(),
        SmartClearCookiesTool(),
        SmartClearLocalStorageTool(),
        
        # Enhanced Dialog Handling
        SmartAcceptDialogTool(),
        SmartDismissDialogTool(),
        
        # Enhanced Frame Management
        SmartSwitchToFrameTool(),
        SmartSwitchToMainFrameTool(),
        
        # Enhanced Network Tools
        SmartSetNetworkConditionsTool(),
        
        # Enhanced Human Intervention Tools (New API)
        SmartAutoDetectInterventionTool(),
        SmartRequestInterventionTool(),
        SmartCompleteInterventionTool(),
        SmartCancelInterventionTool(),
        SmartInterventionStatusTool(),
        
        # Enhanced Legacy Intervention Tools (for backward compatibility)
        SmartRequestHumanHelpTool(),
        SmartSolveCaptchaTool(),
        SmartHandleLoginTool(),
    ]
