#!/usr/bin/env python3
"""
Main test script for running browser automation tests.
Usage:
    python run_tests.py --test1  # Run first test scenario
    python run_tests.py --test2  # Run chess page test scenario
    python run_tests.py --dom    # Run DOM handler test
    python run_tests.py --all    # Run all tests
"""
import asyncio
import sys
import argparse
from browser_api.tests.test_browser_automation import test_browser_api, test_browser_api_2
from browser_api.tests.test_dom_handler import test_dom_handler

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Run browser automation tests")
    parser.add_argument("--test1", action="store_true", help="Run basic browser automation test")
    parser.add_argument("--test2", action="store_true", help="Run chess page test")
    parser.add_argument("--dom", action="store_true", help="Run DOM handler test")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    return parser.parse_args()

async def run_all_tests():
    """Run all tests sequentially"""
    print("=== Running all tests ===")
    await test_browser_api()
    print("\n\n=== Test 1 completed, starting Test 2 ===\n\n")
    await test_browser_api_2()
    print("\n\n=== Test 2 completed, starting DOM Handler Test ===\n\n")
    await test_dom_handler()

if __name__ == "__main__":
    args = parse_args()
    
    if args.test1:
        asyncio.run(test_browser_api())
    elif args.test2:
        asyncio.run(test_browser_api_2())
    elif args.dom:
        asyncio.run(test_dom_handler())
    elif args.all:
        asyncio.run(run_all_tests())
    else:
        print("Please specify a test to run. Use --help for options.")
        sys.exit(1)
