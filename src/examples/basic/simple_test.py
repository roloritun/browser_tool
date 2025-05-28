#!/usr/bin/env python3
"""
Simple test version of the demo that just tests sandbox creation and browser tool initialization
without requiring Azure OpenAI setup.
"""
import asyncio
import sys
import time
from pathlib import Path
import os

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.tools.utilities.sandbox_manager import SandboxManager
from src.tools.utilities.browser_tools_init import get_browser_tools
from src.utils.logger import logger


async def test_sandbox_and_tools():
    """Test sandbox creation and browser tools initialization."""
    try:
        logger.info("Starting sandbox and tools test...")
        
        # Create sandbox and get URLs
        logger.info("Creating Daytona sandbox...")
        sandbox_manager = SandboxManager()
        sandbox_id, cdp_url, vnc_url, novnc_url, api_url, web_url, x_url = sandbox_manager.create_sandbox()
        
        logger.info(f"✅ Sandbox created: {sandbox_id}")
        logger.info(f"📺 NoVNC URL: {novnc_url}")
        logger.info(f"🔗 API URL: {api_url}")
        
        # Wait for API to be ready and initialize tools with retry
        logger.info("Waiting for browser API to be ready...")
        max_retries = 30  # 60 seconds total
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                browser_tools = await asyncio.to_thread(lambda: get_browser_tools(api_url=api_url, sandbox_id=sandbox_id))
                logger.info(f"✅ Successfully initialized {len(browser_tools)} browser tools")
                
                # Test that we can access tool names
                tool_names = [tool.name for tool in browser_tools[:5]]  # First 5 tools
                logger.info(f"📋 Sample tools: {tool_names}")
                
                logger.info("🎉 Test completed successfully!")
                logger.info(f"🌐 You can manually access the browser at: {novnc_url}")
                logger.info("🔑 VNC password: vncpassword")
                
                return 0
                
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.info(f"API not ready yet (attempt {attempt + 1}/{max_retries}), waiting {retry_delay}s...")
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error(f"❌ Failed to initialize browser tools after {max_retries} attempts: {str(e)}")
                    return 1
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        return 1


def main():
    """Main function to run the test."""
    start_time = time.time()
    logger.info("🧪 Starting simple sandbox and tools test...")
    
    try:
        exit_code = asyncio.run(test_sandbox_and_tools())
        elapsed_time = time.time() - start_time
        logger.info(f"⏱️ Test completed in {elapsed_time:.2f} seconds")
        return exit_code
    except KeyboardInterrupt:
        logger.info("⚠️ Test interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"💥 Unhandled exception: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
