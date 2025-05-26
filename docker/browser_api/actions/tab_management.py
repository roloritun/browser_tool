"""
Tab management actions for browser automation.
This module provides functionality for managing browser tabs.
"""
import traceback

from fastapi import Body
from browser_api.models.action_models import SwitchTabAction, OpenTabAction, CloseTabAction
from browser_api.core.dom_handler import DOMHandler

class TabManagementActions:
    """Tab management browser actions"""
    
    @staticmethod
    async def switch_tab(browser_instance, action: SwitchTabAction = Body(...)):
        """Switch to a different tab by tab index or page ID"""
        try:
            # Use tab_index as primary, fall back to page_id if provided
            page_id = action.tab_index if action.tab_index is not None else action.page_id
            
            if page_id is None:
                return browser_instance.build_action_result(
                    False,
                    "No tab index or page ID provided",
                    None,
                    "",
                    "",
                    {},
                    error="Either tab_index or page_id must be provided"
                )
            
            # Verify the page ID is valid
            if page_id < 0 or page_id >= len(browser_instance.pages):
                return browser_instance.build_action_result(
                    False,
                    f"Invalid tab index: {page_id}",
                    None,
                    "",
                    "",
                    {},
                    error=f"Tab index must be between 0 and {len(browser_instance.pages) - 1}"
                )
            
            # Switch to the specified page
            browser_instance.current_page_index = page_id
            
            # Reset the current frame when switching tabs
            browser_instance.current_frame = None
            
            # Get the current page after switching
            page = await browser_instance.get_current_page()
            
            success = True
            message = f"Switched to tab with ID {page_id}"
            error = ""
            
            # Get updated state after action
            dom_state, screenshot, elements, metadata = await DOMHandler.get_updated_browser_state(page, "switch_tab")
            
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
            print(f"Unexpected error in switch_tab: {e}")
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
    async def open_tab(browser_instance, action: OpenTabAction = Body(...)):
        """Open a new tab with the specified URL"""
        try:
            url = action.url
            
            try:
                # Create a new page
                page = await browser_instance.browser.new_page()
                
                # Navigate to the specified URL
                await page.goto(url, timeout=60000, wait_until="domcontentloaded")
                
                # Wait for network to be idle for better stability
                try:
                    await page.wait_for_load_state("networkidle", timeout=10000)
                except Exception as idle_error:
                    print(f"Network idle timeout: {idle_error}")
                
                # Add the page to the list and switch to it
                browser_instance.pages.append(page)
                browser_instance.current_page_index = len(browser_instance.pages) - 1
                
                # Reset the current frame when opening a new tab
                browser_instance.current_frame = None
                
                success = True
                message = f"Opened new tab with URL: {url}"
                error = ""
            except Exception as open_error:
                print(f"Error opening new tab: {open_error}")
                traceback.print_exc()
                success = False
                message = f"Failed to open new tab with URL: {url}"
                error = str(open_error)
            
            # Get updated state after action
            dom_state, screenshot, elements, metadata = await DOMHandler.get_updated_browser_state(page, "open_tab")
            
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
            print(f"Unexpected error in open_tab: {e}")
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
    async def close_tab(browser_instance, action: CloseTabAction = Body(...)):
        """Close a tab by tab index or page ID"""
        try:
            # Use tab_index as primary, fall back to page_id if provided
            page_id = action.tab_index if action.tab_index is not None else action.page_id
            
            if page_id is None:
                return browser_instance.build_action_result(
                    False,
                    "No tab index or page ID provided",
                    None,
                    "",
                    "",
                    {},
                    error="Either tab_index or page_id must be provided"
                )
            
            # Verify the page ID is valid
            if page_id < 0 or page_id >= len(browser_instance.pages):
                return browser_instance.build_action_result(
                    False,
                    f"Invalid tab index: {page_id}",
                    None,
                    "",
                    "",
                    {},
                    error=f"Tab index must be between 0 and {len(browser_instance.pages) - 1}"
                )
            
            # Make sure we're not closing the last tab
            if len(browser_instance.pages) <= 1:
                return browser_instance.build_action_result(
                    False,
                    "Cannot close the last tab",
                    None,
                    "",
                    "",
                    {},
                    error="At least one tab must remain open"
                )
            
            try:
                # Get the page to close
                page_to_close = browser_instance.pages[page_id]
                
                # Close the page
                await page_to_close.close()
                
                # Remove the page from the list
                browser_instance.pages.pop(page_id)
                
                # Adjust the current page index if necessary
                if browser_instance.current_page_index >= page_id:
                    browser_instance.current_page_index = max(0, browser_instance.current_page_index - 1)
                
                # Reset the current frame when closing a tab
                browser_instance.current_frame = None
                
                success = True
                message = f"Closed tab with ID {page_id}"
                error = ""
            except Exception as close_error:
                print(f"Error closing tab: {close_error}")
                traceback.print_exc()
                success = False
                message = f"Failed to close tab with ID {page_id}"
                error = str(close_error)
            
            # Get updated state after action
            page = await browser_instance.get_current_page()
            dom_state, screenshot, elements, metadata = await DOMHandler.get_updated_browser_state(page, "close_tab")
            
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
            print(f"Unexpected error in close_tab: {e}")
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
