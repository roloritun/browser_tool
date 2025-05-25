#!/usr/bin/env python3
"""
Test script for browser automation tools.
"""

import asyncio
import json
import time
import sys
from dotenv import load_dotenv

from src.tools.langchain_browser_tool import BrowserToolkit
from src.utils.logger import logger

# Load environment variables
load_dotenv()


async def test_browser_tools():
    """Test browser tools functionality."""
    start_time = time.time()
    logger.info("Starting browser tools test...")
    
    # Create sandbox and get API URL
    from src.tools.utilities.sandbox_manager import SandboxManager
    sandbox_manager = SandboxManager()
    sandbox_id, cdp_url, _, _, api_url, _, _ = sandbox_manager.create_sandbox()
    
    # Initialize toolkit with API URL from sandbox
    toolkit = BrowserToolkit(api_url=api_url, sandbox_id=sandbox_id)
    setup_result = await toolkit.setup()
    
    if not setup_result["success"]:
        logger.error(f"Failed to set up browser tools: {setup_result.get('error', 'Unknown error')}")
        return 1
    
    logger.info(f"Browser tools initialized successfully. API URL: {toolkit.tools[0].api_base_url}")
    
    # Test navigation
    navigate_tool = toolkit.get_tool("browser_navigate_to")
    if not navigate_tool:
        logger.error("Navigate tool not found")
        return 1
    
    logger.info("Testing navigation to example.com...")
    result = await navigate_tool._execute_browser_action("navigate_to", {"url": "https://example.com"})
    logger.info(f"Navigation result: {json.dumps(result, indent=2)}")
    
    # Wait a moment for page to load
    await asyncio.sleep(2)
    
    # Test content extraction
    extract_tool = toolkit.get_tool("browser_extract_content")
    if not extract_tool:
        logger.error("Extract content tool not found")
        return 1
    
    logger.info("Testing content extraction...")
    result = await extract_tool._execute_browser_action("extract_content", "Extract all text from the page")
    logger.info(f"Extraction result: {json.dumps(result, indent=2)}")
    
    elapsed_time = time.time() - start_time
    logger.info(f"Tests completed in {elapsed_time:.2f} seconds")
    return 0


def main():
    """Main function."""
    try:
        exit_code = asyncio.run(test_browser_tools())
        return exit_code
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
