"""
Cookie and storage management actions for browser automation.
This module provides functionality for managing cookies and local storage.
"""
import asyncio
import traceback
from typing import Dict, Any, List, Optional

from fastapi import Body
from ..models.action_models import NoParamsAction
from ..core.dom_handler import DOMHandler

class CookieStorageActions:
    """Cookie and storage management browser actions"""
    
    @staticmethod
    async def get_cookies(browser_instance, _: NoParamsAction = Body(...)):
        """Get all cookies for the current page"""
        try:
            cookies = await CookieStorageActions._get_cookies(browser_instance)
            
            # Get updated state after action
            page = await browser_instance.get_current_page()
            dom_state, screenshot, elements, metadata = await DOMHandler.get_updated_browser_state(page, "get_cookies")
            
            return browser_instance.build_action_result(
                True,
                "Retrieved cookies",
                dom_state,
                screenshot,
                elements,
                metadata,
                error="",
                content=cookies
            )
        except Exception as e:
            print(f"Unexpected error in get_cookies: {e}")
            traceback.print_exc()
            return browser_instance.build_action_result(
                False,
                str(e),
                None,
                "",
                "",
                {},
                error=str(e),
                content=None
            )
            
    @staticmethod
    async def _get_cookies(browser_instance) -> List[Dict[str, Any]]:
        """Get all cookies for the current page - internal implementation"""
        try:
            page = await browser_instance.get_current_page()
            cookies = await page.context.cookies()
            return cookies
        except Exception as e:
            print(f"Error getting cookies: {e}")
            traceback.print_exc()
            return []
            
    @staticmethod
    async def set_cookie(browser_instance, cookie_data: Dict[str, Any] = Body(...)):
        """Set a cookie for the current page"""
        try:
            result = await CookieStorageActions._set_cookie(
                browser_instance,
                name=cookie_data.get("name"),
                value=cookie_data.get("value"),
                domain=cookie_data.get("domain"),
                path=cookie_data.get("path", "/"),
                expires=cookie_data.get("expires"),
                http_only=cookie_data.get("httpOnly", False),
                secure=cookie_data.get("secure", False),
                same_site=cookie_data.get("sameSite")
            )
            
            # Get updated state after action
            page = await browser_instance.get_current_page()
            dom_state, screenshot, elements, metadata = await DOMHandler.get_updated_browser_state(page, "set_cookie")
            
            return browser_instance.build_action_result(
                result,
                "Cookie set successfully" if result else "Failed to set cookie",
                dom_state,
                screenshot,
                elements,
                metadata,
                error="" if result else "Failed to set cookie",
                content=None
            )
        except Exception as e:
            print(f"Unexpected error in set_cookie: {e}")
            traceback.print_exc()
            return browser_instance.build_action_result(
                False,
                str(e),
                None,
                "",
                "",
                {},
                error=str(e),
                content=None
            )
            
    @staticmethod
    async def _set_cookie(browser_instance, name: str, value: str, domain: Optional[str] = None, 
                      path: str = "/", expires: Optional[int] = None, 
                      http_only: bool = False, secure: bool = False, 
                      same_site: Optional[str] = None) -> bool:
        """Set a cookie for the current page - internal implementation"""
        try:
            if not name or not value:
                print("Error setting cookie: name and value are required")
                return False
                
            page = await browser_instance.get_current_page()
            current_url = page.url
            
            # Create the cookie with required parameters
            cookie = {
                "name": name,
                "value": value,
            }
            
            # Must include either url or domain+path (Playwright requirement)
            if domain:
                cookie["domain"] = domain
                cookie["path"] = path
            else:
                # If no domain is provided, set URL which is required by Playwright API
                cookie["url"] = current_url
            
            # Add other optional parameters if provided
            if path and domain:
                cookie["path"] = path
            if expires:
                cookie["expires"] = expires
            if http_only:
                cookie["httpOnly"] = http_only
            if secure:
                cookie["secure"] = secure
            if same_site:
                cookie["sameSite"] = same_site
            
            print(f"Setting cookie with parameters: {cookie}")
            
            # Add the cookie
            await page.context.add_cookies([cookie])
            
            # Verify cookie was set by checking cookies after setting
            await asyncio.sleep(0.5)  # Give it a moment to set
            cookies = await CookieStorageActions._get_cookies(browser_instance)
            
            for c in cookies:
                if c.get("name") == name and c.get("value") == value:
                    print(f"Successfully set cookie: {name}={value}")
                    return True
            
            # If we get here, the cookie wasn't found in verification
            print(f"Warning: Cookie {name} may not have been set correctly")
            
            # Try one more time with a longer wait
            await asyncio.sleep(1)
            cookies = await CookieStorageActions._get_cookies(browser_instance)
            for c in cookies:
                if c.get("name") == name and c.get("value") == value:
                    print(f"Successfully set cookie on second verification: {name}={value}")
                    return True
                    
            print(f"Error: Cookie {name} could not be verified after setting")
            return False
        except Exception as e:
            print(f"Error setting cookie: {e}")
            traceback.print_exc()
            return False
            
    @staticmethod
    async def clear_cookies(browser_instance, _: NoParamsAction = Body(...)):
        """Clear all cookies for the current page"""
        try:
            result = await CookieStorageActions._clear_cookies(browser_instance)
            
            # Get updated state after action
            page = await browser_instance.get_current_page()
            dom_state, screenshot, elements, metadata = await DOMHandler.get_updated_browser_state(page, "clear_cookies")
            
            return browser_instance.build_action_result(
                result,
                "Cookies cleared successfully" if result else "Failed to clear cookies",
                dom_state,
                screenshot,
                elements,
                metadata,
                error="" if result else "Failed to clear cookies",
                content=None
            )
        except Exception as e:
            print(f"Unexpected error in clear_cookies: {e}")
            traceback.print_exc()
            return browser_instance.build_action_result(
                False,
                str(e),
                None,
                "",
                "",
                {},
                error=str(e),
                content=None
            )
    
    @staticmethod
    async def _clear_cookies(browser_instance) -> bool:
        """Clear all cookies for the current page - internal implementation"""
        try:
            page = await browser_instance.get_current_page()
            
            # Get cookies before clearing
            cookies_before = await page.context.cookies()
            
            # Clear all cookies
            await page.context.clear_cookies()
            
            # Verify cookies were cleared
            cookies_after = await page.context.cookies()
            
            if not cookies_after:
                print("Successfully cleared all cookies")
                return True
            
            if len(cookies_after) < len(cookies_before):
                print(f"Partially cleared cookies: {len(cookies_before)} before, {len(cookies_after)} after")
                return True
                
            print("Failed to clear cookies")
            return False
        except Exception as e:
            print(f"Error clearing cookies: {e}")
            traceback.print_exc()
            return False
    
    @staticmethod
    async def clear_local_storage(browser_instance, _: NoParamsAction = Body(...)):
        """Clear local storage for the current page"""
        try:
            page = await browser_instance.get_current_page()
            
            try:
                # Clear local storage using JavaScript
                await page.evaluate("localStorage.clear()")
                
                success = True
                message = "Local storage cleared successfully"
                error = ""
            except Exception as storage_error:
                print(f"Error clearing local storage: {storage_error}")
                traceback.print_exc()
                success = False
                message = "Failed to clear local storage"
                error = str(storage_error)
            
            # Get updated state after action
            dom_state, screenshot, elements, metadata = await DOMHandler.get_updated_browser_state(page, "clear_local_storage")
            
            return browser_instance.build_action_result(
                success,
                message,
                dom_state,
                screenshot,
                elements,
                metadata,
                error=error,
                content=None
            )
        except Exception as e:
            print(f"Unexpected error in clear_local_storage: {e}")
            traceback.print_exc()
            return browser_instance.build_action_result(
                False,
                str(e),
                None,
                "",
                "",
                {},
                error=str(e),
                content=None
            )
