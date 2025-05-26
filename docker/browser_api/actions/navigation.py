"""
Navigation-related actions for browser automation.
This module provides functionality for navigating in the browser.
"""
import traceback

from fastapi import Body
from browser_api.models.action_models import GoToUrlAction, SearchGoogleAction, NoParamsAction
from browser_api.core.dom_handler import DOMHandler

class NavigationActions:
    """Navigation-related browser actions"""
    
    @staticmethod
    async def navigate_to(browser_instance, action: GoToUrlAction = Body(...)):
        """Navigate to a specific URL"""
        try:
            url = action.url
            page = await browser_instance.get_current_page()
            
            print(f"Navigating to URL: {url}")
            
            try:
                # More robust navigation with increased timeout
                response = await page.goto(url, timeout=60000, wait_until="domcontentloaded")
                if not response:
                    print(f"Navigation to {url} didn't return a response object")
                elif response.status >= 400:
                    print(f"Navigation to {url} returned status {response.status}")
                    
                # Explicitly wait for network to be idle for better stability
                try:
                    await page.wait_for_load_state("networkidle", timeout=10000)
                except Exception as idle_error:
                    print(f"Network idle timeout: {idle_error}")
                    # Continue anyway, as the page might be usable
                
                print(f"Successfully navigated to {url}")
                success = True
                message = f"Navigated to {url}"
                error = ""
            except Exception as nav_error:
                print(f"Error during navigation to {url}: {nav_error}")
                traceback.print_exc()
                success = False
                message = f"Failed to navigate to {url}"
                error = str(nav_error)
                
                # Try to recover by waiting a bit
                try:
                    await page.wait_for_timeout(2000)
                except Exception:
                    pass
            
            # Get updated state after action
            dom_state, screenshot, elements, metadata = await DOMHandler.get_updated_browser_state(page, "navigate_to")
            
            return browser_instance.build_action_result(
                success,
                message,
                dom_state,
                screenshot,
                elements,
                metadata,
                error=error
            )
        except Exception as e:
            print(f"Unexpected error in navigate_to: {e}")
            traceback.print_exc()
            return browser_instance.build_action_result(
                False,
                str(e),
                None,
                "",
                "",
                {},
                error=str(e)
            )
    
    @staticmethod
    async def search_google(browser_instance, action: SearchGoogleAction = Body(...)):
        """Search Google for a query"""
        try:
            query = action.query
            page = await browser_instance.get_current_page()
            
            # First, navigate to Google
            try:
                await page.goto("https://www.google.com", timeout=30000, wait_until="domcontentloaded")
                
                # Wait for the search input to be available
                await page.wait_for_selector('input[name="q"]', timeout=5000)
                
                # Type the search query
                await page.fill('input[name="q"]', query)
                
                # Submit the search
                await page.press('input[name="q"]', "Enter")
                
                # Wait for the search results to load
                await page.wait_for_load_state("networkidle", timeout=10000)
                
                success = True
                message = f"Searched Google for '{query}'"
                error = ""
            except Exception as search_error:
                print(f"Error during Google search for '{query}': {search_error}")
                traceback.print_exc()
                success = False
                message = f"Failed to search Google for '{query}'"
                error = str(search_error)
            
            # Get updated state after action
            dom_state, screenshot, elements, metadata = await DOMHandler.get_updated_browser_state(page, "search_google")
            
            return browser_instance.build_action_result(
                success,
                message,
                dom_state,
                screenshot,
                elements,
                metadata,
                error=error
            )
        except Exception as e:
            print(f"Unexpected error in search_google: {e}")
            traceback.print_exc()
            return browser_instance.build_action_result(
                False,
                str(e),
                None,
                "",
                "",
                {},
                error=str(e)
            )
    
    @staticmethod
    async def go_back(browser_instance, _: NoParamsAction = Body(...)):
        """Navigate back to the previous page"""
        try:
            page = await browser_instance.get_current_page()
            
            try:
                # Go back to previous page
                await page.go_back(timeout=30000, wait_until="domcontentloaded")
                
                # Wait for network to be idle
                try:
                    await page.wait_for_load_state("networkidle", timeout=5000)
                except Exception as idle_error:
                    print(f"Network idle timeout: {idle_error}")
                
                success = True
                message = "Navigated back to previous page"
                error = ""
            except Exception as back_error:
                print(f"Error going back: {back_error}")
                traceback.print_exc()
                success = False
                message = "Failed to navigate back"
                error = str(back_error)
            
            # Get updated state after action
            dom_state, screenshot, elements, metadata = await DOMHandler.get_updated_browser_state(page, "go_back")
            
            return browser_instance.build_action_result(
                success,
                message,
                dom_state,
                screenshot,
                elements,
                metadata,
                error=error
            )
        except Exception as e:
            print(f"Unexpected error in go_back: {e}")
            traceback.print_exc()
            return browser_instance.build_action_result(
                False,
                str(e),
                None,
                "",
                "",
                {},
                error=str(e)
            )
    
    @staticmethod
    async def wait(browser_instance, _: NoParamsAction = Body(...)):
        """Wait for a short time to allow content to load"""
        try:
            page = await browser_instance.get_current_page()
            
            try:
                # Wait for network to be idle
                await page.wait_for_load_state("networkidle", timeout=5000)
                
                success = True
                message = "Waited for page to load"
                error = ""
            except Exception as wait_error:
                print(f"Error waiting for page to load: {wait_error}")
                traceback.print_exc()
                success = False
                message = "Failed to wait for page to load"
                error = str(wait_error)
            
            # Get updated state after action
            dom_state, screenshot, elements, metadata = await DOMHandler.get_updated_browser_state(page, "wait")
            
            return browser_instance.build_action_result(
                success,
                message,
                dom_state,
                screenshot,
                elements,
                metadata,
                error=error
            )
        except Exception as e:
            print(f"Unexpected error in wait: {e}")
            traceback.print_exc()
            return browser_instance.build_action_result(
                False,
                str(e),
                None,
                "",
                "",
                {},
                error=str(e)
            )
    
    @staticmethod
    async def go_forward(browser_instance, action: NoParamsAction = Body(...)):
        """Go forward in browser history"""
        try:
            page = await browser_instance.get_current_page()
            
            try:
                await page.go_forward()
                print("Successfully went forward in browser history")
                success = True
                message = "Navigated forward to next page"
                error = ""
            except Exception as forward_error:
                print(f"Error going forward: {forward_error}")
                success = False
                message = "Failed to go forward"
                error = str(forward_error)
            
            # Get updated state after action
            dom_state, screenshot, elements, metadata = await DOMHandler.get_updated_browser_state(page, "go_forward")
            
            return browser_instance.build_action_result(
                success,
                message,
                dom_state,
                screenshot,
                elements,
                metadata,
                error=error
            )
        except Exception as e:
            print(f"Unexpected error in go_forward: {e}")
            traceback.print_exc()
            return browser_instance.build_action_result(
                False,
                str(e),
                None,
                "",
                "",
                {},
                error=str(e)
            )

    @staticmethod
    async def refresh(browser_instance, action: NoParamsAction = Body(...)):
        """Refresh the current page"""
        try:
            page = await browser_instance.get_current_page()
            
            try:
                await page.reload(wait_until="domcontentloaded", timeout=30000)
                print("Successfully refreshed the page")
                success = True
                message = "Page refreshed successfully"
                error = ""
            except Exception as refresh_error:
                print(f"Error refreshing page: {refresh_error}")
                success = False
                message = "Failed to refresh page"
                error = str(refresh_error)
            
            # Get updated state after action
            dom_state, screenshot, elements, metadata = await DOMHandler.get_updated_browser_state(page, "refresh")
            
            return browser_instance.build_action_result(
                success,
                message,
                dom_state,
                screenshot,
                elements,
                metadata,
                error=error
            )
        except Exception as e:
            print(f"Unexpected error in refresh: {e}")
            traceback.print_exc()
            return browser_instance.build_action_result(
                False,
                str(e),
                None,
                "",
                "",
                {},
                error=str(e)
            )
