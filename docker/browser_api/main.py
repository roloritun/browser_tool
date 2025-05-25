"""
Main entry point for the browser API.
This module integrates all the functionality into a single FastAPI application.
"""
from fastapi import FastAPI

from .core.browser_automation import BrowserAutomation
from .actions.navigation import NavigationActions
from .actions.interaction import InteractionActions
from .actions.tab_management import TabManagementActions
from .actions.content import ContentActions
from .actions.scroll import ScrollActions
from .actions.cookies import CookieStorageActions
from .actions.dialog import DialogActions
from .actions.frame import FrameActions
from .actions.network import NetworkActions
from .actions.drag_drop import DragDropActions

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(title="Browser Automation API")
    
    # Add health check endpoint for Daytona monitoring
    @app.get("/health")
    async def health_check():
        """Health check endpoint for monitoring and deployment"""
        return {
            "status": "healthy",
            "service": "browser_automation_api",
            "version": "2.0.0-modular"
        }
    
    # Create the browser automation instance
    browser_automation = BrowserAutomation()
    
    # Register the router with the app
    app.include_router(browser_automation.router, tags=["browser"])
    
    # Register startup and shutdown handlers
    app.on_event("startup")(browser_automation.startup)
    app.on_event("shutdown")(browser_automation.shutdown)
    
    # Register routes for navigation
    browser_automation.router.post("/automation/navigate_to")(
        lambda action: NavigationActions.navigate_to(browser_automation, action)
    )
    browser_automation.router.post("/automation/search_google")(
        lambda action: NavigationActions.search_google(browser_automation, action)
    )
    browser_automation.router.post("/automation/go_back")(
        lambda action: NavigationActions.go_back(browser_automation, action)
    )
    browser_automation.router.post("/automation/wait")(
        lambda action: NavigationActions.wait(browser_automation, action)
    )
    
    # Register routes for element interaction
    browser_automation.router.post("/automation/click_element")(
        lambda action: InteractionActions.click_element(browser_automation, action)
    )
    browser_automation.router.post("/automation/click_coordinates")(
        lambda action: InteractionActions.click_coordinates(browser_automation, action)
    )
    browser_automation.router.post("/automation/input_text")(
        lambda action: InteractionActions.input_text(browser_automation, action)
    )
    browser_automation.router.post("/automation/send_keys")(
        lambda action: InteractionActions.send_keys(browser_automation, action)
    )
    
    # Register routes for tab management
    browser_automation.router.post("/automation/switch_tab")(
        lambda action: TabManagementActions.switch_tab(browser_automation, action)
    )
    browser_automation.router.post("/automation/open_tab")(
        lambda action: TabManagementActions.open_tab(browser_automation, action)
    )
    browser_automation.router.post("/automation/close_tab")(
        lambda action: TabManagementActions.close_tab(browser_automation, action)
    )
    
    # Register routes for content actions
    browser_automation.router.post("/automation/extract_content")(
        lambda action: ContentActions.extract_content(browser_automation, action)
    )
    browser_automation.router.post("/automation/save_pdf")(
        lambda action: ContentActions.save_pdf(browser_automation, action)
    )
    browser_automation.router.post("/automation/generate_pdf")(
        lambda action: ContentActions.generate_pdf(browser_automation, action)
    )
    
    # Register routes for scroll actions
    browser_automation.router.post("/automation/scroll_down")(
        lambda action: ScrollActions.scroll_down(browser_automation, action)
    )
    browser_automation.router.post("/automation/scroll_up")(
        lambda action: ScrollActions.scroll_up(browser_automation, action)
    )
    browser_automation.router.post("/automation/scroll_to_text")(
        lambda action: ScrollActions.scroll_to_text(browser_automation, action)
    )
    
    # Register routes for cookie and storage management
    browser_automation.router.post("/automation/get_cookies")(
        lambda action: CookieStorageActions.get_cookies(browser_automation, action)
    )
    browser_automation.router.post("/automation/set_cookie")(
        lambda action: CookieStorageActions.set_cookie(browser_automation, action)
    )
    browser_automation.router.post("/automation/clear_cookies")(
        lambda action: CookieStorageActions.clear_cookies(browser_automation, action)
    )
    browser_automation.router.post("/automation/clear_local_storage")(
        lambda action: CookieStorageActions.clear_local_storage(browser_automation, action)
    )
    
    # Register routes for dialog handling
    browser_automation.router.post("/automation/accept_dialog")(
        lambda action: DialogActions.accept_dialog(browser_automation, action)
    )
    browser_automation.router.post("/automation/dismiss_dialog")(
        lambda action: DialogActions.dismiss_dialog(browser_automation, action)
    )
    
    # Register routes for frame handling
    browser_automation.router.post("/automation/switch_to_frame")(
        lambda action: FrameActions.switch_to_frame(browser_automation, action)
    )
    browser_automation.router.post("/automation/switch_to_main_frame")(
        lambda action: FrameActions.switch_to_main_frame(browser_automation, action)
    )
    
    # Register routes for network conditions
    browser_automation.router.post("/automation/set_network_conditions")(
        lambda action: NetworkActions.set_network_conditions(browser_automation, action)
    )
    
    # Register routes for drag and drop
    browser_automation.router.post("/automation/drag_drop")(
        lambda action: DragDropActions.drag_drop(browser_automation, action)
    )
    
    # Additional placeholder routes for future implementation
    browser_automation.router.post("/automation/get_dropdown_options")(
        lambda action: ContentActions.extract_content(browser_automation, action)
    )
    browser_automation.router.post("/automation/select_dropdown_option")(
        lambda action: InteractionActions.click_element(browser_automation, action)
    )
    
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
    from .tests.test_browser_automation import test_browser_api, test_browser_api_2
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
