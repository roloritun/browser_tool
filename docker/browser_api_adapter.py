"""
Backward compatibility adapter for browser_api.py.
This module provides the same interface as the original browser_api.py file
but delegates to the new modular implementation.
"""
from fastapi import APIRouter

# Import the app from the new modular implementation
from browser_api.main import app as modular_app
from browser_api.core.browser_automation import BrowserAutomation
# Import the adapter for backward compatibility
from browser_api.tests.browser_adapter import browser_automation_adapter
# Import test functions for backward compatibility
from browser_api.tests.test_browser_automation import test_browser_api, test_browser_api_2


# Extract the router from the modular app
browser_router = None
for route in modular_app.routes:
    if isinstance(route, APIRouter):
        browser_router = route
        break

if not browser_router:
    # Find the BrowserAutomation instance
    for app in modular_app.routes:
        if hasattr(app, "router") and isinstance(app.router, APIRouter):
            browser_router = app.router
            break

# Create a new instance of BrowserAutomation for backward compatibility
browser_automation = browser_automation_adapter

# All the routes and functionality are now delegated to the modular implementation
# via the imported app and router

# To maintain backward compatibility with direct imports



#
# Make the adapter router available
router = browser_router

# For compatibility with code that might access BrowserAutomation directly
BrowserAutomation = BrowserAutomation

# Create a new API FastAPI app that's a clone of the modular app for backward compatibility
api_app = modular_app

# Setup router and automation service access for server.py compatibility
automation_service = browser_automation

# For backward compatibility with the original `if __name__ == '__main__'` block
if __name__ == '__main__':
    import uvicorn
    import sys
    import asyncio
    
    # Check command line arguments for test mode
    test_mode_1 = "--test" in sys.argv
    test_mode_2 = "--test2" in sys.argv
    
    if test_mode_1:
        print("Running in test mode 1")
        asyncio.run(test_browser_api())
    elif test_mode_2:
        print("Running in test mode 2 (Chess Page)")
        asyncio.run(test_browser_api_2())
    else:
        import os
        port = int(os.getenv("API_PORT", 8000))
        print(f"Starting API server on port {port}")
        uvicorn.run("browser_api_adapter:api_app", host="0.0.0.0", port=port)