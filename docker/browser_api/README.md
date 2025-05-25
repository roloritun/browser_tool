# Browser API Module

This module provides a modular implementation of browser automation functionality using Playwright.

## Structure

The module is organized as follows:

- **actions/**: Browser action implementations (navigation, interaction, etc.)
- **core/**: Core functionality like browser automation and DOM handling
- **models/**: Data models for actions, DOM, and results
- **tests/**: Test functions and adapter for backward compatibility
- **utils/**: Utility functions for screenshots, PDFs, etc.

## Usage

### As a module

```python
from browser_api.models.action_models import GoToUrlAction
from browser_api.core.browser_automation import BrowserAutomation

# Initialize the browser automation
browser = BrowserAutomation()
await browser.startup()

# Perform browser actions
action = GoToUrlAction(url="https://example.com")
result = await browser.navigate_to(action)

# Clean up
await browser.shutdown()
```

### As an API server

```bash
# Run the FastAPI server
python -m browser_api.main
```

Then make requests to the API endpoints:

```bash
curl -X POST "http://localhost:8000/automation/navigate_to" -H "Content-Type: application/json" -d '{"url": "https://example.com"}'
```

## Tests

See the [tests/README.md](tests/README.md) for information on running tests.

## Backward Compatibility

The module provides backward compatibility with the old monolithic implementation via `browser_api_adapter.py`. This allows existing code to continue working while migrating to the new modular structure.

```python
# Old imports still work for backward compatibility
from browser_api import BrowserAutomation
```
