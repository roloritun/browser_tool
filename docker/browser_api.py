"""
DEPRECATED: This module is now replaced by the modular browser_api package.
This file is kept for backward compatibility and redirects to browser_api_adapter.py.

Please update your imports to use the new modular structure:
- from browser_api.models.action_models import *  # For action models
- from browser_api.models.dom_models import *     # For DOM models
- from browser_api.models.result_models import *  # For result models
- from browser_api.main import app                # For the FastAPI application
"""
import warnings

warnings.warn(
    "The monolithic browser_api.py is deprecated. Please use the modular browser_api package instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything from the adapter for backward compatibility
from browser_api_adapter import *

if __name__ == '__main__':
    import sys
    import os
    
    # Forward all arguments to the adapter
    cmd = f"python {os.path.join(os.path.dirname(__file__), 'browser_api_adapter.py')} {' '.join(sys.argv[1:])}"
    os.system(cmd)
