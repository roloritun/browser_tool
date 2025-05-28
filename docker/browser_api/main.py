"""
Main entry point for the browser API.
This module integrates all the functionality into a single FastAPI application.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI

from browser_api.core.browser_automation import BrowserAutomation
from browser_api.actions.navigation import NavigationActions
from browser_api.actions.interaction import InteractionActions
from browser_api.actions.tab_management import TabManagementActions
from browser_api.actions.content import ContentActions
from browser_api.actions.scroll import ScrollActions
from browser_api.actions.cookies import CookieStorageActions
from browser_api.actions.dialog import DialogActions
from browser_api.actions.frame import FrameActions
from browser_api.actions.network import NetworkActions
from browser_api.actions.drag_drop import DragDropActions
from browser_api.actions.human_intervention import HumanInterventionActions
from browser_api.models.action_models import (
    GoToUrlAction,
    SearchGoogleAction,
    ClickElementAction,
    ClickCoordinatesAction,
    InputTextAction,
    SendKeysAction,
    SwitchTabAction,
    OpenTabAction,
    CloseTabAction,
    ScrollAction,
    NoParamsAction,
    DragDropAction,
    SwitchToFrameAction,
    SetNetworkConditionsAction,
    ScrollToTextAction,
    SetCookieAction,
    WaitAction,
    ExtractContentAction,
    PDFOptionsAction,
    GetDropdownOptionsAction,
    SelectDropdownOptionAction
)
from browser_api.models.intervention_models import (
    InterventionRequestAction,
    InterventionCompleteAction,
    InterventionCancelAction,
    InterventionStatusAction,
    AutoDetectAction
)

# Global browser automation instance
browser_automation = BrowserAutomation()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    # Startup
    await browser_automation.startup()
    yield
    # Shutdown
    await browser_automation.shutdown()

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="Browser Automation API",
        lifespan=lifespan
    )
    
    # Add health check endpoint for Daytona monitoring
    @app.get("/health")
    async def health_check():
        """Health check endpoint for monitoring and deployment"""
        return {
            "success": True,
            "message": "Browser automation API is healthy",
            "status": "healthy",
            "service": "browser_automation_api",
            "version": "2.0.0-modular"
        }
    
    # Register routes for navigation
    @app.post("/automation/navigate_to", tags=["browser"])
    async def navigate_to(action: GoToUrlAction):
        return await NavigationActions.navigate_to(browser_automation, action)
    
    @app.post("/automation/search_google", tags=["browser"])
    async def search_google(action: SearchGoogleAction):
        return await NavigationActions.search_google(browser_automation, action)
    
    @app.post("/automation/go_back", tags=["browser"])
    async def go_back(action: NoParamsAction):
        return await NavigationActions.go_back(browser_automation, action)
    
    @app.post("/automation/go_forward", tags=["browser"])
    async def go_forward(action: NoParamsAction):
        return await NavigationActions.go_forward(browser_automation, action)
    
    @app.post("/automation/refresh", tags=["browser"])
    async def refresh(action: NoParamsAction):
        return await NavigationActions.refresh(browser_automation, action)
    
    @app.post("/automation/wait", tags=["browser"])
    async def wait_action(action: WaitAction):
        return await NavigationActions.wait(browser_automation, action)
    
    # Register routes for element interaction
    @app.post("/automation/click_element", tags=["browser"])
    async def click_element(action: ClickElementAction):
        return await InteractionActions.click_element(browser_automation, action)
    
    @app.post("/automation/click_coordinates", tags=["browser"])
    async def click_coordinates(action: ClickCoordinatesAction):
        return await InteractionActions.click_coordinates(browser_automation, action)
    
    @app.post("/automation/input_text", tags=["browser"])
    async def input_text(action: InputTextAction):
        return await InteractionActions.input_text(browser_automation, action)
    
    @app.post("/automation/send_keys", tags=["browser"])
    async def send_keys(action: SendKeysAction):
        return await InteractionActions.send_keys(browser_automation, action)
    
    # Register routes for tab management
    @app.post("/automation/switch_tab", tags=["browser"])
    async def switch_tab(action: SwitchTabAction):
        return await TabManagementActions.switch_tab(browser_automation, action)
    
    @app.post("/automation/open_tab", tags=["browser"])
    async def open_tab(action: OpenTabAction):
        return await TabManagementActions.open_tab(browser_automation, action)
    
    @app.post("/automation/open_new_tab", tags=["browser"])
    async def open_new_tab(action: OpenTabAction):
        return await TabManagementActions.open_tab(browser_automation, action)
    
    @app.post("/automation/close_tab", tags=["browser"])
    async def close_tab(action: CloseTabAction):
        return await TabManagementActions.close_tab(browser_automation, action)
    
    # Register routes for content actions
    @app.post("/automation/extract_content", tags=["browser"])
    async def extract_content(action: ExtractContentAction):
        return await ContentActions.extract_content(browser_automation, action)
    
    @app.post("/automation/save_pdf", tags=["browser"])
    async def save_pdf(action: PDFOptionsAction):
        return await ContentActions.save_pdf(browser_automation, action)
    
    @app.post("/automation/generate_pdf", tags=["browser"])
    async def generate_pdf(action: PDFOptionsAction):
        return await ContentActions.generate_pdf(browser_automation, action)
    
    @app.post("/automation/get_page_content", tags=["browser"])
    async def get_page_content(action: ExtractContentAction):
        return await ContentActions.extract_content(browser_automation, action)
    
    @app.post("/automation/take_screenshot", tags=["browser"])
    async def take_screenshot(action: NoParamsAction):
        return await ContentActions.take_screenshot(browser_automation, action)
    
    @app.post("/automation/get_page_pdf", tags=["browser"])
    async def get_page_pdf(action: PDFOptionsAction):
        return await ContentActions.generate_pdf(browser_automation, action)
    
    # Register routes for scroll actions
    @app.post("/automation/scroll_down", tags=["browser"])
    async def scroll_down(action: ScrollAction):
        return await ScrollActions.scroll_down(browser_automation, action)
    
    @app.post("/automation/scroll_up", tags=["browser"])
    async def scroll_up(action: ScrollAction):
        return await ScrollActions.scroll_up(browser_automation, action)
    
    @app.post("/automation/scroll_to_text", tags=["browser"])
    async def scroll_to_text(action: ScrollToTextAction):
        return await ScrollActions.scroll_to_text(browser_automation, action)
    
    @app.post("/automation/scroll_to_top", tags=["browser"])
    async def scroll_to_top(action: NoParamsAction):
        return await ScrollActions.scroll_to_top(browser_automation, action)
    
    @app.post("/automation/scroll_to_bottom", tags=["browser"])
    async def scroll_to_bottom(action: NoParamsAction):
        return await ScrollActions.scroll_to_bottom(browser_automation, action)
    
    # Register routes for cookie and storage management
    @app.post("/automation/get_cookies", tags=["browser"])
    async def get_cookies(action: NoParamsAction):
        return await CookieStorageActions.get_cookies(browser_automation, action)
    
    @app.post("/automation/set_cookie", tags=["browser"])
    async def set_cookie(action: SetCookieAction):
        return await CookieStorageActions.set_cookie(browser_automation, action)
    
    @app.post("/automation/clear_cookies", tags=["browser"])
    async def clear_cookies(action: NoParamsAction):
        return await CookieStorageActions.clear_cookies(browser_automation, action)
    
    @app.post("/automation/clear_local_storage", tags=["browser"])
    async def clear_local_storage(action: NoParamsAction):
        return await CookieStorageActions.clear_local_storage(browser_automation, action)
    
    # Register routes for dialog handling
    @app.post("/automation/accept_dialog", tags=["browser"])
    async def accept_dialog(action: NoParamsAction):
        return await DialogActions.accept_dialog(browser_automation, action)
    
    @app.post("/automation/dismiss_dialog", tags=["browser"])
    async def dismiss_dialog(action: NoParamsAction):
        return await DialogActions.dismiss_dialog(browser_automation, action)
    
    # Register routes for frame handling
    @app.post("/automation/switch_to_frame", tags=["browser"])
    async def switch_to_frame(action: SwitchToFrameAction):
        return await FrameActions.switch_to_frame(browser_automation, action)
    
    @app.post("/automation/switch_to_main_frame", tags=["browser"])
    async def switch_to_main_frame(action: NoParamsAction):
        return await FrameActions.switch_to_main_frame(browser_automation, action)
    
    # Register routes for network conditions
    @app.post("/automation/set_network_conditions", tags=["browser"])
    async def set_network_conditions(action: SetNetworkConditionsAction):
        return await NetworkActions.set_network_conditions(browser_automation, action)
    
    # Register routes for drag and drop
    @app.post("/automation/drag_drop", tags=["browser"])
    async def drag_drop(action: DragDropAction):
        return await DragDropActions.drag_drop(browser_automation, action)
    
    @app.post("/automation/drag_and_drop", tags=["browser"])
    async def drag_and_drop(action: DragDropAction):
        return await DragDropActions.drag_drop(browser_automation, action)
    
    # Additional placeholder routes for future implementation
    @app.post("/automation/get_dropdown_options", tags=["browser"])
    async def get_dropdown_options(action: GetDropdownOptionsAction):
        return await ContentActions.extract_content(browser_automation, action)
    
    @app.post("/automation/select_dropdown_option", tags=["browser"])
    async def select_dropdown_option(action: SelectDropdownOptionAction):
        return await InteractionActions.click_element(browser_automation, action)
    
    # Register routes for human intervention
    @app.post("/automation/request_intervention", tags=["human_intervention"])
    async def request_intervention(action: InterventionRequestAction):
        return await HumanInterventionActions.request_intervention(browser_automation, action)
    
    @app.post("/automation/complete_intervention", tags=["human_intervention"])
    async def complete_intervention(action: InterventionCompleteAction):
        return await HumanInterventionActions.complete_intervention(browser_automation, action)
    
    @app.post("/automation/cancel_intervention", tags=["human_intervention"])
    async def cancel_intervention(action: InterventionCancelAction):
        return await HumanInterventionActions.cancel_intervention(browser_automation, action)
    
    @app.post("/automation/intervention_status", tags=["human_intervention"])
    async def intervention_status(action: InterventionStatusAction):
        return await HumanInterventionActions.get_intervention_status(browser_automation, action)
    
    @app.post("/automation/auto_detect_intervention", tags=["human_intervention"])
    async def auto_detect_intervention(action: AutoDetectAction):
        return await HumanInterventionActions.auto_detect_intervention_needed(browser_automation, action)
    
    return app

app = create_app()

# Allow access to the browser automation instance for testing
automation_service = BrowserAutomation()

# Initialize the automation service on first import
async def initialize_automation():
    """Initialize the automation service"""
    await automation_service.startup()

# Cleanup the automation service
async def cleanup_automation():
    """Clean up the automation service"""
    await automation_service.shutdown()

if __name__ == '__main__':
    import uvicorn
    import sys
    from browser_api.tests.test_browser_automation import test_browser_api, test_browser_api_2
    import asyncio
    
    # Check command line arguments for test mode
    test_mode_1 = "--test" in sys.argv or "--test1" in sys.argv
    test_mode_2 = "--test2" in sys.argv
    test_all = "--all" in sys.argv
    
    if test_mode_1:
        print("Running in test mode 1")
        asyncio.run(test_browser_api())
    elif test_mode_2:
        print("Running in test mode 2 (Chess Page)")
        asyncio.run(test_browser_api_2())
    elif test_all:
        print("Running all tests")
        async def run_all():
            await test_browser_api()
            await test_browser_api_2()
        asyncio.run(run_all())
    else:
        import os
        port = int(os.getenv("API_PORT", 8000))
        print(f"Starting API server on port {port}")
        uvicorn.run("browser_api.main:app", host="0.0.0.0", port=port)
