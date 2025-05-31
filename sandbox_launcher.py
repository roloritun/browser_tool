#!/usr/bin/env python3
"""
Standalone Daytona sandbox launcher.
This script creates a new sandbox with the browser API and prints the API URL.
You can use this URL to connect to the browser API from other scripts.
"""

import os
import sys
import argparse
from dotenv import load_dotenv
from src.tools.utilities.sandbox_manager import SandboxManager
from src.utils.logger import logger

# Load environment variables from .env file
load_dotenv()


def launch_sandbox(keep_running: bool = True) -> None:
    """Launch a new Daytona sandbox with the browser API.
    
    Args:
        keep_running (bool): Whether to keep the script running to keep the sandbox alive
    """
    try:
        logger.info("Creating Daytona sandbox with browser API...")
        sandbox_manager = SandboxManager()
        sandbox_id, cdp_url, vnc_url, novnc_url, api_url, web_url, x_url = sandbox_manager.create_sandbox()
        
        logger.info("=" * 80)
        logger.info("Sandbox created successfully!")
        logger.info(f"Sandbox ID: {sandbox_id}")
        logger.info(f"Browser API URL: {api_url}")
        logger.info(f"Browser VNC URL: {vnc_url}")
        logger.info(f"Browser NoVNC URL: {novnc_url}")
        logger.info("=" * 80)
        logger.info("Copy these values to use in your browser automation scripts.")
        logger.info("Add the API URL to your .env file as BROWSER_API_URL.")
        
        if keep_running:
            logger.info("Keeping script running to maintain sandbox...")
            logger.info("Press Ctrl+C to stop and delete the sandbox.")
            try:
                # Keep the script running to keep the sandbox alive
                while True:
                    input("Press Enter to show info again, or Ctrl+C to exit...")
                    logger.info("=" * 80)
                    logger.info(f"Sandbox ID: {sandbox_id}")
                    logger.info(f"Browser API URL: {api_url}")
                    logger.info("=" * 80)
            except KeyboardInterrupt:
                logger.info("Exiting...")
        
    except Exception as e:
        logger.error(f"Error creating sandbox: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Launch a Daytona sandbox with browser API")
    parser.add_argument(
        "--no-wait", 
        action="store_true", 
        help="Don't keep the script running after launching the sandbox"
    )
    args = parser.parse_args()
    
    launch_sandbox(keep_running=not args.no_wait)
