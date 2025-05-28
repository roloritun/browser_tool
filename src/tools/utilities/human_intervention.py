from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import asyncio
import logging
import httpx
from src.utils.logger import logger

class HumanInterventionInput(BaseModel):
    reason: str = Field(..., description="Reason for requesting human intervention")
    instructions: Optional[str] = Field(None, description="Specific instructions for the human")
    timeout_seconds: Optional[int] = Field(300, description="How long to wait for human input")

class CaptchaInput(HumanInterventionInput):
    screenshot: bool = Field(True, description="Whether to take a screenshot of the CAPTCHA")

class LoginInput(HumanInterventionInput):
    field_type: str = Field(..., description="Type of login field (e.g., 'password', '2fa', 'username')")
    selector: Optional[str] = Field(None, description="CSS selector for the input field")

# Enhanced intervention types for API compatibility
class InterventionType:
    CAPTCHA = "captcha"
    LOGIN_REQUIRED = "login_required"
    SECURITY_CHECK = "security_check"
    COMPLEX_DATA_ENTRY = "complex_data_entry"
    ANTI_BOT_PROTECTION = "anti_bot_protection"
    TWO_FACTOR_AUTH = "two_factor_auth"
    COOKIES_CONSENT = "cookies_consent"
    AGE_VERIFICATION = "age_verification"
    CUSTOM = "custom"

class EnhancedHumanInterventionBase:
    """Enhanced base class for human intervention tools with API integration."""
    
    def __init__(self, api_base_url: Optional[str] = None):
        self._logger = logger or logging.getLogger(__name__)
        self.api_base_url = api_base_url
    
    def set_api_url(self, api_url: str):
        """Set the API base URL for browser automation"""
        self.api_base_url = api_url
    
    async def request_intervention_api(self, intervention_type: str, message: str, 
                                     instructions: Optional[str] = None, 
                                     timeout_seconds: int = 300,
                                     context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Request intervention through the browser API"""
        if not self.api_base_url:
            return await self._fallback_intervention(message, instructions, timeout_seconds)
        
        try:
            url = f"{self.api_base_url}/automation/request_intervention"
            payload = {
                "intervention_type": intervention_type,
                "message": message,
                "instructions": instructions,
                "timeout_seconds": timeout_seconds,
                "context": context or {},
                "take_screenshot": True,
                "auto_detect": False
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        intervention_id = result.get("content", {}).get("intervention_id")
                        self._logger.info(f"🚨 Intervention requested successfully: {intervention_id}")
                        
                        # Wait for completion by polling status
                        return await self._wait_for_intervention_completion(intervention_id, timeout_seconds)
                    else:
                        self._logger.error(f"Intervention request failed: {result.get('error')}")
                        return {"success": False, "error": result.get("error")}
                else:
                    self._logger.error(f"API request failed with status {response.status_code}")
                    return await self._fallback_intervention(message, instructions, timeout_seconds)
                    
        except Exception as e:
            self._logger.error(f"Error requesting intervention via API: {e}")
            return await self._fallback_intervention(message, instructions, timeout_seconds)
    
    async def _wait_for_intervention_completion(self, intervention_id: str, timeout_seconds: int) -> Dict[str, Any]:
        """Wait for intervention completion by polling the status endpoint"""
        start_time = asyncio.get_event_loop().time()
        poll_interval = 2  # Poll every 2 seconds
        
        while (asyncio.get_event_loop().time() - start_time) < timeout_seconds:
            try:
                url = f"{self.api_base_url}/automation/intervention_status"
                payload = {"intervention_id": intervention_id}
                
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(url, json=payload)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("success"):
                            content = result.get("content", {})
                            status = content.get("status")
                            
                            if status == "completed":
                                self._logger.info("✅ Human intervention completed successfully")
                                return {"success": True, "message": "Human intervention completed"}
                            elif status == "cancelled":
                                self._logger.info("❌ Human intervention was cancelled")
                                return {"success": False, "error": "Intervention cancelled by user"}
                            elif status == "timeout":
                                self._logger.warning("⏰ Human intervention timed out")
                                return {"success": False, "error": "Intervention timed out"}
                            elif status == "failed":
                                self._logger.error("❌ Human intervention failed")
                                return {"success": False, "error": "Intervention failed"}
                            
                            # Still pending, continue polling
                            time_remaining = content.get("time_remaining", 0)
                            self._logger.info(f"⏳ Waiting for intervention... ({time_remaining}s remaining)")
                        
            except Exception as e:
                self._logger.error(f"Error polling intervention status: {e}")
            
            await asyncio.sleep(poll_interval)
        
        # Timeout reached
        self._logger.error("⏰ Timeout waiting for intervention completion")
        return {"success": False, "error": "Timeout waiting for intervention completion"}
    
    async def auto_detect_and_handle(self) -> Dict[str, Any]:
        """Automatically detect and handle common intervention scenarios"""
        if not self.api_base_url:
            return {"success": False, "error": "API URL not set"}
        
        try:
            url = f"{self.api_base_url}/automation/auto_detect_intervention"
            payload = {
                "check_captcha": True,
                "check_login": True,
                "check_security": True,
                "check_anti_bot": True,
                "check_cookies": True
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        content = result.get("content", {})
                        
                        if content.get("intervention_needed"):
                            detected_types = content.get("detected_types", [])
                            recommendations = content.get("recommendations", [])
                            
                            self._logger.info(f"🔍 Auto-detected intervention needed: {detected_types}")
                            
                            # Request intervention for the first detected type
                            if detected_types and recommendations:
                                intervention_type = detected_types[0]
                                message = recommendations[0]
                                
                                return await self.request_intervention_api(
                                    intervention_type=intervention_type,
                                    message=message,
                                    instructions=f"Auto-detected: {', '.join(detected_types)}"
                                )
                        else:
                            self._logger.info("✅ No intervention needed")
                            return {"success": True, "message": "No intervention needed"}
                    
                    return result
                else:
                    self._logger.error(f"Auto-detection failed with status {response.status_code}")
                    return {"success": False, "error": f"API request failed: {response.status_code}"}
                    
        except Exception as e:
            self._logger.error(f"Error in auto-detection: {e}")
            return {"success": False, "error": str(e)}
    
    async def _fallback_intervention(self, message: str, instructions: Optional[str], timeout_seconds: int) -> Dict[str, Any]:
        """Fallback to console-based intervention when API is not available"""
        self._logger.info("\n" + "="*50)
        self._logger.info("🤖 Requesting Human Assistance (Console Mode)")
        self._logger.info(f"Reason: {message}")
        if instructions:
            self._logger.info(f"Instructions: {instructions}")
        self._logger.info("="*50)
        
        try:
            response = asyncio.create_task(self._get_user_input())
            result = await asyncio.wait_for(response, timeout=timeout_seconds)
            self._logger.info("✅ Human intervention completed")
            return {"success": True, "message": "Human intervention completed", "result": result}
        except asyncio.TimeoutError:
            self._logger.error(f"❌ Human intervention timed out after {timeout_seconds} seconds")
            return {"success": False, "error": "Timeout waiting for human input"}
        except Exception as e:
            self._logger.error(f"❌ Error during human intervention: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _get_user_input(self) -> str:
        """Get input from the user."""
        user_input = await asyncio.get_event_loop().run_in_executor(
            None, lambda: input("🧑‍💻 Press ENTER when done, or type a message: ")
        )
        return user_input or "Task completed"

# Legacy classes for backward compatibility
class HumanInterventionBase(EnhancedHumanInterventionBase):
    """Legacy base class for backward compatibility"""
    
    def __init__(self):
        super().__init__()
        self.logger = logger or logging.getLogger(__name__)
    
    async def wait_for_input(self, reason: str, instructions: Optional[str] = None, 
                           timeout_seconds: int = 300) -> Dict[str, Any]:
        """Legacy method for backward compatibility"""
        return await self._fallback_intervention(reason, instructions, timeout_seconds)
    
    async def request_intervention(self, intervention_type: str, message: str, 
                                 instructions: Optional[str] = None, 
                                 timeout_seconds: int = 300) -> Dict[str, Any]:
        """Request human intervention - alias for request_intervention_api for backward compatibility"""
        return await self.request_intervention_api(
            intervention_type=intervention_type,
            message=message,
            instructions=instructions,
            timeout_seconds=timeout_seconds
        )

class CaptchaHandler(HumanInterventionBase):
    """Handler for CAPTCHA-related human intervention."""
    
    async def handle_captcha(self, reason: str = "CAPTCHA detected", 
                           screenshot: bool = True) -> Dict[str, Any]:
        """Handle CAPTCHA detection and solving."""
        instructions = (
            "Please solve the CAPTCHA in the browser.\n"
            "The NoVNC viewer should be open showing the current page."
        )
        
        if screenshot:
            # TODO: Implement screenshot capture
            pass
            
        return await self.wait_for_input(reason, instructions)

class LoginHandler(HumanInterventionBase):
    """Handler for login-related human intervention."""
    
    async def handle_login(self, field_type: str, reason: Optional[str] = None, 
                         selector: Optional[str] = None) -> Dict[str, Any]:
        """Handle login-related human intervention."""
        type_map = {
            "password": "password",
            "2fa": "two-factor authentication code",
            "username": "username",
            "email": "email address"
        }
        
        field_name = type_map.get(field_type, field_type)
        reason = reason or f"Need human input for {field_name}"
        instructions = f"Please enter the {field_name} in the browser window"
        
        if selector:
            instructions += f"\nField selector: {selector}"
            
        return await self.wait_for_input(reason, instructions)

class GeneralInterventionHandler(HumanInterventionBase):
    """Handler for general human intervention requests."""
    
    async def handle_intervention(self, reason: str, 
                                instructions: Optional[str] = None) -> Dict[str, Any]:
        """Handle general human intervention requests."""
        return await self.wait_for_input(reason, instructions)

# Create singleton instances
captcha_handler = CaptchaHandler()
login_handler = LoginHandler()
general_handler = GeneralInterventionHandler()
