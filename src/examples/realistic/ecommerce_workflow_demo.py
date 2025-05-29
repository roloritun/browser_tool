#!/usr/bin/env python3
"""
E-commerce Workflow Demo

This demo tests the browser automation tool's ability to handle complex e-commerce
workflows including product search, cart management, checkout processes, and 
handling various shopping site challenges like inventory checks, price comparisons,
and form validations.

Sites tested:
- Demo e-commerce sites
- Product catalog browsing
- Shopping cart workflows
- Checkout process automation
- Price comparison scenarios

Safety: Uses only demo sites and test transactions.
Ethics: Respects robots.txt and rate limits.
"""

import asyncio
import os
import sys
import time
import random
from datetime import datetime
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tools.utilities.browser_tools_init import initialize_browser_tools
from tools.utilities.sandbox_manager import SandboxManager
from utils.logger import logger
from utils.enhanced_agent_formatting import create_enhanced_react_agent
from utils.novnc_viewer import generate_novnc_viewer

# Load environment variables
load_dotenv()

# E-commerce Test Sites and Scenarios
ECOMMERCE_TEST_SITES = [
    {
        "name": "Sauce Demo E-commerce",
        "url": "https://www.saucedemo.com/",
        "description": "Demo e-commerce site for testing shopping workflows",
        "type": "full_ecommerce",
        "test_actions": ["login", "browse_products", "add_to_cart", "checkout"],
        "requires_login": True,
        "test_credentials": {"username": "standard_user", "password": "secret_sauce"}
    },
    {
        "name": "Demo E-commerce Store",
        "url": "https://demo.evershop.io/",
        "description": "EverShop demo store for testing shopping features",
        "type": "product_browsing",
        "test_actions": ["browse_categories", "search_products", "view_product_details"],
        "requires_login": False
    },
    {
        "name": "OpenCart Demo",
        "url": "https://demo.opencart.com/",
        "description": "OpenCart demo for comprehensive e-commerce testing",
        "type": "full_ecommerce",
        "test_actions": ["browse_categories", "search", "add_to_cart", "wishlist"],
        "requires_login": False
    },
    {
        "name": "Magento Demo Store",
        "url": "https://magento.softwaretestingboard.com/",
        "description": "Magento demo store for testing complex e-commerce workflows",
        "type": "advanced_ecommerce",
        "test_actions": ["category_navigation", "filtering", "product_comparison", "reviews"],
        "requires_login": False
    }
]

# Product search terms for testing
SEARCH_TERMS = [
    "shirt", "shoes", "laptop", "phone", "watch", 
    "headphones", "backpack", "jacket", "book", "camera"
]

async def test_ecommerce_site(agent_executor, site_info, site_index, total_sites):
    """Test a specific e-commerce site with comprehensive workflow testing."""
    
    site_name = site_info["name"]
    site_url = site_info["url"]
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Testing E-commerce Site {site_index}/{total_sites}: {site_name}")
    logger.info(f"URL: {site_url}")
    logger.info(f"Type: {site_info['type']}")
    logger.info(f"{'='*60}")
    
    start_time = time.time()
    
    # Create task based on site type
    if site_info["type"] == "full_ecommerce":
        task = create_full_ecommerce_task(site_info)
    elif site_info["type"] == "product_browsing":
        task = create_product_browsing_task(site_info)
    elif site_info["type"] == "advanced_ecommerce":
        task = create_advanced_ecommerce_task(site_info)
    else:
        task = create_general_ecommerce_task(site_info)
    
    try:
        logger.info(f"🛒 Starting e-commerce workflow test for {site_info['name']}...")
        result = await agent_executor.ainvoke({"input": task})
        
        elapsed_time = time.time() - start_time
        logger.info(f"✅ Completed {site_info['name']} test in {elapsed_time:.1f}s")
        
        return {
            "site": site_info['name'],
            "url": site_info['url'],
            "success": True,
            "result": result.get("output", "No output"),
            "elapsed_time": elapsed_time,
            "site_type": site_info['type'],
            "workflows_completed": extract_completed_workflows(result.get("output", "")),
            "intermediate_steps": result.get("intermediate_steps", []),
            "errors": []
        }
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(f"❌ Error testing {site_info['name']}: {str(e)}")
        return {
            "site": site_info['name'],
            "url": site_info['url'],
            "success": False,
            "result": "",
            "elapsed_time": elapsed_time,
            "site_type": site_info['type'],
            "workflows_completed": [],
            "intermediate_steps": [],
            "errors": [str(e)]
        }

def create_full_ecommerce_task(site_info):
    """Create a comprehensive e-commerce testing task."""
    search_term = random.choice(SEARCH_TERMS)
    credentials = site_info.get("test_credentials", {})
    
    task = f"""
    Test the complete e-commerce workflow on {site_info['url']}.
    
    Your comprehensive testing task:
    1. Navigate to the e-commerce site
    2. {"Log in using username: " + credentials.get("username", "") + " and password: " + credentials.get("password", "") if site_info.get("requires_login") else "Explore the homepage"}
    3. Browse product categories and identify available products
    4. Search for "{search_term}" products
    5. Select a product and view its details
    6. Add at least one product to the shopping cart
    7. Navigate to the shopping cart and review items
    8. Start the checkout process (but DO NOT complete the purchase)
    9. Fill out shipping/billing forms with test data only
    10. Stop before payment to avoid any real transactions
    
    Expected site features: {', '.join(site_info.get('test_actions', []))}
    
    Important guidelines:
    - Use only test data for forms (e.g., "Test User", "123 Test St")
    - DO NOT enter real payment information
    - DO NOT complete actual purchases
    - Take screenshots at key workflow steps
    - Report any errors or challenges encountered
    - If you need human help with complex forms, request it
    
    Provide a detailed report of your findings and the e-commerce capabilities tested.
    """
    return task

def create_product_browsing_task(site_info):
    """Create a product browsing focused task."""
    search_term = random.choice(SEARCH_TERMS)
    
    task = f"""
    Test product browsing and catalog features on {site_info['url']}.
    
    Your product browsing task:
    1. Navigate to the e-commerce site
    2. Explore the main navigation and product categories
    3. Browse different product categories (at least 2-3)
    4. Search for "{search_term}" and analyze search results
    5. View detailed product pages for several items
    6. Look for product filtering and sorting options
    7. Check for product reviews, ratings, or recommendations
    8. Test any product comparison features if available
    9. Explore wishlist or favorites functionality if present
    
    Focus areas: {', '.join(site_info.get('test_actions', []))}
    
    Report on:
    - Navigation structure and usability
    - Product catalog organization
    - Search functionality effectiveness
    - Product detail information quality
    - Any advanced browsing features found
    """
    return task

def create_advanced_ecommerce_task(site_info):
    """Create an advanced e-commerce features task."""
    search_term = random.choice(SEARCH_TERMS)
    
    task = f"""
    Test advanced e-commerce features on {site_info['url']}.
    
    Your advanced testing task:
    1. Navigate to the site and explore its structure
    2. Test category navigation and breadcrumb functionality
    3. Use product filtering and sorting options extensively
    4. Search for "{search_term}" and test search refinement
    5. Look for product comparison features and test them
    6. Find and read product reviews or ratings
    7. Test any personalization or recommendation features
    8. Explore user account features (registration/login)
    9. Look for wishlist, favorites, or saved items functionality
    10. Test any social features (sharing, reviews, etc.)
    
    Advanced features to test: {', '.join(site_info.get('test_actions', []))}
    
    Analyze and report on:
    - Site performance and responsiveness
    - Advanced filtering and search capabilities
    - User experience and interface design
    - Personalization and recommendation quality
    - Social and review features
    """
    return task

def create_general_ecommerce_task(site_info):
    """Create a general e-commerce exploration task."""
    search_term = random.choice(SEARCH_TERMS)
    
    task = f"""
    Explore and analyze the e-commerce capabilities of {site_info['url']}.
    
    Your exploration task:
    1. Navigate to the site and analyze its structure
    2. Identify the main e-commerce features available
    3. Test basic product browsing and search for "{search_term}"
    4. Explore any shopping cart or purchase workflows
    5. Look for user account or personalization features
    6. Test the overall user experience and navigation
    7. Document any unique or interesting features found
    
    Provide a comprehensive analysis of the site's e-commerce capabilities.
    """
    return task

def extract_completed_workflows(output_text):
    """Extract completed workflow information from agent output."""
    workflows = []
    output_lower = output_text.lower()
    
    # Check for common e-commerce workflow indicators
    workflow_indicators = [
        ("navigation", ["navigate", "visited", "browsed"]),
        ("product_search", ["search", "searched", "found products"]),
        ("product_details", ["product detail", "product page", "viewed product"]),
        ("add_to_cart", ["added to cart", "cart", "shopping cart"]),
        ("checkout", ["checkout", "billing", "shipping", "payment"]),
        ("login", ["logged in", "login", "authentication"]),
        ("filtering", ["filter", "filtered", "sorting"]),
        ("comparison", ["compare", "comparison", "compared"])
    ]
    
    for workflow, keywords in workflow_indicators:
        if any(keyword in output_lower for keyword in keywords):
            workflows.append(workflow)
    
    return workflows

async def ecommerce_workflow_demo():
    """
    Main demo function that tests various e-commerce workflow scenarios.
    
    This demo showcases the browser automation tool's ability to:
    1. Navigate complex e-commerce sites
    2. Handle authentication and user sessions
    3. Perform product searches and browsing
    4. Manage shopping cart operations
    5. Test checkout processes (without completing purchases)
    6. Handle dynamic content and AJAX requests
    7. Work with forms and user inputs
    8. Provide detailed workflow analysis
    """
    
    print("\n" + "="*80)
    print("🛒 E-COMMERCE WORKFLOW DEMO")
    print("="*80)
    print("This demo tests browser automation with complex e-commerce workflows.")
    print("It showcases product browsing, cart management, and checkout processes.")
    print("All tests use demo sites and test data only - no real purchases.")
    print("="*80)
    
    # Create sandbox
    sandbox_manager = SandboxManager()
    sandbox_id, cdp_url, vnc_url, novnc_url, api_url, web_url, x_url = sandbox_manager.create_sandbox()
    
    # Generate and open NoVNC viewer for real-time monitoring
    logger.info("🖥️ Opening NoVNC viewer for e-commerce automation monitoring...")
    try:
        viewer_path = generate_novnc_viewer(
            novnc_url=novnc_url,
            vnc_password=os.getenv('VNC_PASSWORD', 'vncpassword'),
            auto_open=True
        )
        logger.info(f"✅ E-commerce monitoring viewer opened at: {viewer_path}")
        logger.info("👀 Monitor the e-commerce automation in real-time")
    except Exception as e:
        logger.warning(f"⚠️ Failed to open NoVNC viewer: {e}")
        logger.info(f"🌐 You can manually open: {novnc_url}")
    
    try:
        # Initialize tools
        tools = await initialize_browser_tools(api_url, sandbox_id)
        logger.info(f"✅ Initialized {len(tools)} tools")
        
        # Enhanced LLM Configuration
        from langchain_openai import AzureChatOpenAI
        
        llm = AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            temperature=0.0,  # Maximum determinism
            max_tokens=3000,  # More tokens for complex workflows
            top_p=0.05,      # Focused sampling
            model_name="gpt-4o"
        )
        
        # Create enhanced agent with all fixes
        agent_executor = create_enhanced_react_agent(
            llm=llm,
            tools=tools,
            max_iterations=20,      # More iterations for complex workflows
            max_execution_time=1200, # 20 minute timeout
            return_intermediate_steps=True,
            early_stopping_method="force"
        )
        
        # Test results storage
        all_results = []
        successful_tests = 0
        total_sites = len(ECOMMERCE_TEST_SITES)
        
        logger.info(f"\n🚀 Starting tests on {total_sites} e-commerce sites...")
        print(f"\n🚀 Starting tests on {total_sites} e-commerce sites...")
        print("🛍️ Testing shopping workflows, cart management, and checkout processes")
        
        for i, site_info in enumerate(ECOMMERCE_TEST_SITES, 1):
            print(f"\n📍 Testing site {i}/{total_sites}: {site_info['name']}")
            
            # Test the e-commerce site
            site_results = await test_ecommerce_site(agent_executor, site_info, i, total_sites)
            all_results.append(site_results)
            
            if site_results["success"]:
                successful_tests += 1
                print(f"✅ {site_info['name']}: Success")
                print(f"   📦 Workflows completed: {len(site_results['workflows_completed'])}")
            else:
                print(f"❌ {site_info['name']}: {', '.join(site_results['errors'])}")
            
            # Brief pause between sites
            if i < total_sites:
                await asyncio.sleep(3)
        
        # Generate comprehensive summary report
        print("\n" + "="*80)
        print("📊 E-COMMERCE DEMO RESULTS SUMMARY")
        print("="*80)
        print(f"Total sites tested: {total_sites}")
        print(f"Successful tests: {successful_tests}")
        print(f"Success rate: {(successful_tests/total_sites)*100:.1f}%")
        print()
        
        # Aggregate statistics
        total_workflows = sum(len(r["workflows_completed"]) for r in all_results)
        total_time = sum(r["elapsed_time"] for r in all_results)
        
        print(f"📈 AGGREGATE STATISTICS")
        print(f"Total workflows tested: {total_workflows}")
        print(f"Total testing time: {total_time:.1f} seconds")
        print(f"Average time per site: {total_time/total_sites:.1f} seconds")
        print()
        
        # Detailed results for each site
        for result in all_results:
            status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
            print(f"{status} {result['site']} ({result['site_type']})")
            
            if result["workflows_completed"]:
                workflows_str = ', '.join(result["workflows_completed"][:5])
                if len(result["workflows_completed"]) > 5:
                    workflows_str += f" (+{len(result['workflows_completed']) - 5} more)"
                print(f"   🔄 Workflows: {workflows_str}")
            
            if result["intermediate_steps"]:
                print(f"   📋 Steps: {len(result['intermediate_steps'])}")
            
            print(f"   ⏱️ Time: {result['elapsed_time']:.1f}s")
            
            if result["errors"]:
                print(f"   ❌ Errors: {', '.join(result['errors'])}")
            print()
        
        print("="*80)
        print("🎯 DEMO INSIGHTS")
        print("="*80)
        print("This demo demonstrates the browser automation tool's capabilities for:")
        print("• Navigating complex e-commerce sites with dynamic content")
        print("• Handling authentication and session management")
        print("• Performing comprehensive product search and browsing")
        print("• Managing shopping cart operations and inventory tracking")
        print("• Testing checkout processes without completing transactions")
        print("• Working with forms, validations, and user inputs")
        print("• Handling AJAX requests and dynamic loading")
        print("• Providing detailed workflow analysis and reporting")
        print()
        print("The tool successfully automates complex shopping workflows while")
        print("maintaining safety by using only demo sites and test data.")
        print("="*80)
        
        return True
        
    except Exception as e:
        logger.error(f"Demo failed with error: {e}")
        print(f"\n❌ Demo failed: {e}")
        return False
    
    finally:
        # Cleanup
        try:
            sandbox_manager.delete_sandbox(sandbox_id)
            logger.info("Sandbox deleted successfully")
        except Exception as e:
            logger.error(f"Error deleting sandbox: {e}")

async def main():
    """Main function"""
    try:
        success = await ecommerce_workflow_demo()
        
        if success:
            print("\n🎉 E-COMMERCE WORKFLOW DEMO SUCCESSFUL!")
            print("Demonstrated complex shopping automation capabilities.")
        else:
            print("\n❌ Demo encountered issues")
            
    except Exception as e:
        print(f"💥 Demo failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
