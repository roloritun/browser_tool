"""
Core browser automation functionality.
This module provides the main browser automation class that integrates all functionality.
"""
import asyncio
import logging
import os
import traceback
from typing import Dict, List, Tuple, Optional, Any

from fastapi import APIRouter, Body, HTTPException
from playwright.async_api import async_playwright, Browser, Page

from browser_api.models.dom_models import DOMState, DOMElementNode
from browser_api.models.result_models import BrowserActionResult

class BrowserAutomation:
    def __init__(self):
        self.router = APIRouter()
        self.browser: Browser = None
        self.pages: List[Page] = []
        self.current_page_index: int = 0
        self.current_frame = None
        self.logger = logging.getLogger("browser_automation")
        self.include_attributes = ["id", "href", "src", "alt", "aria-label", "placeholder", "name", "role", "title", "value"]
        self.screenshot_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        # Register routes
        self.router.on_startup.append(self.startup)
        self.router.on_shutdown.append(self.shutdown)
        
        # We'll register specific routes in main.py after importing all action modules
        
    async def startup(self):
        """Initialize the browser instance on startup"""
        try:
            print("Starting browser initialization...")
            playwright = await async_playwright().start()
            print("Playwright started, launching browser...")
            
            # Use non-headless mode for VNC visibility with slower timeouts
            launch_options = {
                "headless": False,
                "timeout": 120000,  # Increase timeout to 2 minutes
                "args": [
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--display=:99"  # Ensure browser uses the VNC display
                ]
            }
            
            try:
                self.browser = await playwright.chromium.launch(**launch_options)
                print("Browser launched successfully")
            except Exception as browser_error:
                print(f"Failed to launch browser: {browser_error}")
                # Try with minimal options
                print("Retrying with minimal options...")
                launch_options = {"timeout": 90000}
                self.browser = await playwright.chromium.launch(**launch_options)
                print("Browser launched with minimal options")

            try:
                await self.get_current_page()
                print("Found existing page, using it")
                self.current_page_index = 0
            except Exception as page_error:
                print(f"Error finding existing page, creating new one. ({page_error})")
                page = await self.browser.new_page()
                print("New page created successfully")
                self.pages.append(page)
                self.current_page_index = 0
                # Navigate to about:blank to ensure page is ready
                # await page.goto("google.com", timeout=30000)
                print("Navigated to google.com")
                
                print("Browser initialization completed successfully")
        except Exception as e:
            print(f"Browser startup error: {str(e)}")
            traceback.print_exc()
            raise RuntimeError(f"Browser initialization failed: {str(e)}")
            
    async def shutdown(self):
        """Clean up browser instance on shutdown"""
        if self.browser:
            await self.browser.close()

    async def get_current_page(self) -> Page:
        """Get the current active page"""
        if not self.pages:
            raise HTTPException(status_code=500, detail="No browser pages available")
        return self.pages[self.current_page_index]
        
    async def get_current_context(self):
        """Get the current context (page or frame) for interactions"""
        if self.current_frame:
            return self.current_frame
        return await self.get_current_page()

    async def get_updated_browser_state(self, action_name: str = "action") -> Tuple[DOMState, str, str, Dict[str, Any]]:
        """Get updated browser state after an action
        
        Returns:
            Tuple containing:
            - DOM state
            - Screenshot base64
            - Formatted elements string
            - Metadata dictionary
        """
        # This method should be implemented in dom_handler.py
        # For now, we'll provide a placeholder implementation
        return None, "", "", {}
        
    def build_action_result(self, success: bool, message: str, dom_state: Optional[DOMState],
                        screenshot_base64: str, elements: str, metadata: Dict[str, Any],
                        error: str = "", content: Any = None) -> BrowserActionResult:
        """Build a standardized action result
        
        Args:
            success: Whether the action was successful
            message: Message describing the result
            dom_state: Current DOM state
            screenshot_base64: Base64 encoded screenshot
            elements: Formatted string of interactive elements
            metadata: Additional metadata
            error: Error message if any
            content: Additional content to return
            
        Returns:
            BrowserActionResult object
        """
        # This should also be implemented in a separate module
        # For now, we'll provide a placeholder implementation
        result = BrowserActionResult(
            success=success,
            message=message,
            error=error,
            content=content
        )
        
        if dom_state:
            result.url = dom_state.url
            result.title = dom_state.title
            result.elements = elements
            result.screenshot_base64 = screenshot_base64
            result.pixels_above = dom_state.pixels_above
            result.pixels_below = dom_state.pixels_below
            
            # Add metadata
            if metadata:
                result.element_count = metadata.get("element_count", 0)
                result.interactive_elements = metadata.get("interactive_elements", [])
                result.viewport_width = metadata.get("viewport_width")
                result.viewport_height = metadata.get("viewport_height")
                
        return result
