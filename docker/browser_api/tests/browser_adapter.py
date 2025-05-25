"""
Test adapter that provides backward compatibility for the tests.
This module patches the BrowserAutomation class to support the old method calls.
"""
from ..core.browser_automation import BrowserAutomation
from ..actions.navigation import NavigationActions
from ..actions.interaction import InteractionActions
from ..actions.tab_management import TabManagementActions
from ..actions.content import ContentActions
from ..actions.scroll import ScrollActions
from ..actions.cookies import CookieStorageActions
from ..actions.dialog import DialogActions
from ..actions.frame import FrameActions
from ..actions.network import NetworkActions
from ..actions.drag_drop import DragDropActions

# Create a patched version of BrowserAutomation with all the old methods
class BrowserAutomationAdapter(BrowserAutomation):
    """Adapter class that provides backward compatibility for the tests"""
    
    async def navigate_to(self, action):
        """Adapter for navigate_to"""
        return await NavigationActions.navigate_to(self, action)
    
    async def search_google(self, action):
        """Adapter for search_google"""
        return await NavigationActions.search_google(self, action)
    
    async def go_back(self, action):
        """Adapter for go_back"""
        return await NavigationActions.go_back(self, action)
    
    async def wait(self, action):
        """Adapter for wait"""
        return await NavigationActions.wait(self, action)
    
    async def click_element(self, action):
        """Adapter for click_element"""
        return await InteractionActions.click_element(self, action)
    
    async def click_coordinates(self, action):
        """Adapter for click_coordinates"""
        return await InteractionActions.click_coordinates(self, action)
    
    async def input_text(self, action):
        """Adapter for input_text"""
        return await InteractionActions.input_text(self, action)
    
    async def send_keys(self, action):
        """Adapter for send_keys"""
        return await InteractionActions.send_keys(self, action)
    
    async def switch_tab(self, action):
        """Adapter for switch_tab"""
        return await TabManagementActions.switch_tab(self, action)
    
    async def open_tab(self, action):
        """Adapter for open_tab"""
        return await TabManagementActions.open_tab(self, action)
    
    async def close_tab(self, action):
        """Adapter for close_tab"""
        return await TabManagementActions.close_tab(self, action)
    
    async def extract_content(self, action):
        """Adapter for extract_content"""
        return await ContentActions.extract_content(self, action)
    
    async def save_pdf(self, action):
        """Adapter for save_pdf"""
        return await ContentActions.save_pdf(self, action)
    
    async def generate_pdf(self, action):
        """Adapter for generate_pdf"""
        return await ContentActions.generate_pdf(self, action)
    
    async def scroll_down(self, action):
        """Adapter for scroll_down"""
        return await ScrollActions.scroll_down(self, action)
    
    async def scroll_up(self, action):
        """Adapter for scroll_up"""
        return await ScrollActions.scroll_up(self, action)
    
    async def scroll_to_text(self, action):
        """Adapter for scroll_to_text"""
        return await ScrollActions.scroll_to_text(self, action)
    
    async def get_cookies(self, action):
        """Adapter for get_cookies"""
        return await CookieStorageActions.get_cookies(self, action)
    
    async def set_cookie(self, action):
        """Adapter for set_cookie"""
        return await CookieStorageActions.set_cookie(self, action)
    
    async def clear_cookies(self, action):
        """Adapter for clear_cookies"""
        return await CookieStorageActions.clear_cookies(self, action)
    
    async def clear_local_storage(self, action):
        """Adapter for clear_local_storage"""
        return await CookieStorageActions.clear_local_storage(self, action)
    
    async def accept_dialog(self, action):
        """Adapter for accept_dialog"""
        return await DialogActions.accept_dialog(self, action)
    
    async def dismiss_dialog(self, action):
        """Adapter for dismiss_dialog"""
        return await DialogActions.dismiss_dialog(self, action)
    
    async def switch_to_frame(self, action):
        """Adapter for switch_to_frame"""
        return await FrameActions.switch_to_frame(self, action)
    
    async def switch_to_main_frame(self, action):
        """Adapter for switch_to_main_frame"""
        return await FrameActions.switch_to_main_frame(self, action)
    
    async def set_network_conditions(self, action):
        """Adapter for set_network_conditions"""
        return await NetworkActions.set_network_conditions(self, action)
    
    async def drag_drop(self, action):
        """Adapter for drag_drop"""
        return await DragDropActions.drag_drop(self, action)
    
    async def get_dropdown_options(self, action):
        """Adapter for get_dropdown_options"""
        return await ContentActions.extract_content(self, action)
    
    async def select_dropdown_option(self, action):
        """Adapter for select_dropdown_option"""
        return await InteractionActions.click_element(self, action)
    
    async def get_current_dom_state(self):
        """Adapter for get_current_dom_state - returns the current DOM state"""
        from ..core.dom_handler import DOMHandler
        page = await self.get_current_page()
        return await DOMHandler.get_dom_state(page)
    
    async def extract_ocr_text_from_screenshot(self, screenshot_base64: str) -> str:
        """Adapter for extract_ocr_text_from_screenshot - extracts text using OCR"""
        from ..utils.screenshot_utils import ScreenshotUtils
        return ScreenshotUtils.extract_text_from_image(screenshot_base64)
        
    async def get_updated_browser_state(self, action_name: str) -> tuple:
        """Adapter for get_updated_browser_state - gets updated browser state after an action"""
        from ..core.dom_handler import DOMHandler
        page = await self.get_current_page()
        return await DOMHandler.get_updated_browser_state(page, action_name)

# Create an instance of the adapter
browser_automation_adapter = BrowserAutomationAdapter()
