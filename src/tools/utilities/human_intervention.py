from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import asyncio
import logging
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

class HumanInterventionBase:
    """Base class for human intervention tools."""
    
    def __init__(self):
        self.logger = logger or logging.getLogger(__name__)
    
    async def wait_for_input(self, reason: str, instructions: Optional[str] = None, 
                           timeout_seconds: int = 300) -> Dict[str, Any]:
        """Wait for human input with optional timeout."""
        self.logger.info("\n" + "="*50)
        self.logger.info("🤖 Requesting Human Assistance")
        self.logger.info(f"Reason: {reason}")
        if instructions:
            self.logger.info(f"Instructions: {instructions}")
        self.logger.info("="*50)
        
        try:
            response = asyncio.create_task(self._get_user_input())
            result = await asyncio.wait_for(response, timeout=timeout_seconds)
            self.logger.info("✅ Human intervention completed")
            return {"success": True, "message": "Human intervention completed", "result": result}
        except asyncio.TimeoutError:
            self.logger.error(f"❌ Human intervention timed out after {timeout_seconds} seconds")
            return {"success": False, "error": "Timeout waiting for human input"}
        except Exception as e:
            self.logger.error(f"❌ Error during human intervention: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _get_user_input(self) -> str:
        """Get input from the user."""
        # This runs in an executor to not block the event loop
        user_input = await asyncio.get_event_loop().run_in_executor(
            None, lambda: input("🧑‍💻 Press ENTER when done, or type a message: ")
        )
        return user_input or "Task completed"

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
