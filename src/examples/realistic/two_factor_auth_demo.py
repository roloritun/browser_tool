#!/usr/bin/env python3
"""
Two-Factor Authentication (2FA) Demo

This demo tests the browser automation tool's ability to handle various 2FA scenarios
including SMS codes, authenticator apps, backup codes, and email verification.
This showcases the human intervention capabilities when automation encounters
security measures that require manual input.

Sites tested:
- Demo 2FA sites for testing various authentication methods
- CAPTCHA sites that often require 2FA
- WebAuthn demo sites

Safety: This demo uses test accounts and demo sites only.
Ethics: Always respect rate limits and terms of service.
"""

import asyncio
import os
import sys
import time
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

# 2FA Test Sites and Scenarios
TWO_FA_TEST_SITES = [
    {
        "name": "Demo 2FA Site",
        "url": "https://demo.twilio.com/two-factor-authentication",
        "description": "Twilio's 2FA demo site for testing SMS verification",
        "type": "sms_demo",
        "intervention_needed": True,
        "test_actions": ["register", "verify_sms"]
    },
    {
        "name": "Auth0 2FA Demo", 
        "url": "https://auth0.com/mfa",
        "description": "Auth0's multi-factor authentication demo",
        "type": "mfa_demo",
        "intervention_needed": True,
        "test_actions": ["explore_mfa_options", "test_totp"]
    },
    {
        "name": "2FA Testing Playground",
        "url": "https://www.protectimus.com/demo/",
        "description": "Protectimus 2FA demo with various authentication methods",
        "type": "multi_method",
        "intervention_needed": True,
        "test_actions": ["test_totp", "test_sms", "test_push"]
    },
    {
        "name": "FIDO2 WebAuthn Demo",
        "url": "https://webauthn.io/",
        "description": "WebAuthn demonstration for passwordless authentication",
        "type": "webauthn",
        "intervention_needed": True,
        "test_actions": ["register_credential", "authenticate"]
    },
    {
        "name": "Yubico WebAuthn Demo",
        "url": "https://demo.yubico.com/webauthn-technical/registration",
        "description": "Yubico's WebAuthn technical demo",
        "type": "hardware_key",
        "intervention_needed": True,
        "test_actions": ["explore_webauthn", "test_registration"]
    }
]

async def test_2fa_site(agent_executor, site_info, site_index, total_sites):
    """Test a specific 2FA site and document the authentication challenges."""
    
    site_name = site_info["name"]
    site_url = site_info["url"]
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Testing 2FA Site {site_index}/{total_sites}: {site_name}")
    logger.info(f"URL: {site_url}")
    logger.info(f"Type: {site_info['type']}")
    logger.info(f"{'='*60}")
    
    start_time = time.time()
    
    # Task for the agent to perform
    task = f"""
    Navigate to {site_url} and analyze the page for 2FA/MFA challenges.
    
    Your task:
    1. Navigate to the URL
    2. Look for any authentication challenges or 2FA setup options
    3. Identify the type of 2FA (SMS, TOTP, WebAuthn, etc.)
    4. If you find a 2FA flow, request human help if needed
    5. Try to complete any authentication forms that require 2FA
    6. Report what you found and whether human intervention was needed
    
    Expected auth type: {site_info['type']}
    
    If you encounter any 2FA or security challenge:
    - Request human help if needed
    - Provide clear instructions on what needs to be done
    - Wait for human completion before proceeding
    
    Be thorough in your analysis and report all security authentication challenges found.
    """
    
    try:
        logger.info(f"🔒 Starting automated analysis of {site_info['name']}...")
        result = await agent_executor.ainvoke({"input": task})
        
        elapsed_time = time.time() - start_time
        logger.info(f"✅ Completed {site_info['name']} analysis in {elapsed_time:.1f}s")
        
        return {
            "site": site_info['name'],
            "url": site_info['url'],
            "success": True,
            "result": result.get("output", "No output"),
            "elapsed_time": elapsed_time,
            "challenge_type": site_info['type'],
            "human_intervention_used": "human help" in result.get("output", "").lower() or "intervention" in result.get("output", "").lower(),
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
            "challenge_type": site_info['type'],
            "human_intervention_used": False,
            "intermediate_steps": [],
            "errors": [str(e)]
        }

async def two_factor_auth_demo():
    """
    Main demo function that tests various 2FA authentication scenarios.
    
    This demo showcases the browser automation tool's ability to:
    1. Navigate to sites with 2FA requirements
    2. Identify different types of authentication challenges
    3. Handle human intervention for security-sensitive operations
    4. Work with various 2FA methods (SMS, TOTP, WebAuthn, etc.)
    5. Provide detailed feedback on authentication flows
    """
    
    print("\n" + "="*80)
    print("🔐 TWO-FACTOR AUTHENTICATION (2FA) DEMO")
    print("="*80)
    print("This demo tests browser automation with various 2FA scenarios.")
    print("It showcases human intervention capabilities for security-sensitive operations.")
    print("All tests use demo sites and test accounts only.")
    print("="*80)
    
    # Create sandbox
    sandbox_manager = SandboxManager()
    sandbox_id, cdp_url, vnc_url, novnc_url, api_url, web_url, x_url = sandbox_manager.create_sandbox()
    
    # Open NoVNC viewer for real-time monitoring and intervention
    try:
        viewer_path = generate_novnc_viewer(
            novnc_url=novnc_url,
            vnc_password=os.getenv('VNC_PASSWORD', 'vncpassword'),
            auto_open=True
        )
        logger.info(f"🖥️ NoVNC Viewer opened: {viewer_path}")
    except Exception as e:
        logger.error(f"Failed to open NoVNC viewer: {e}")
        logger.info(f"🌐 You can manually open: {novnc_url}")
    
    logger.info("👀 Monitor the browser automation in real-time")
    logger.info("🤝 Be ready to help with 2FA when requested")
    
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
            max_tokens=2500,  # Sufficient for complex reasoning
            top_p=0.05,      # Focused sampling
            model_name="gpt-4o"
        )
        
        # Create enhanced agent with all fixes
        agent_executor = create_enhanced_react_agent(
            llm=llm,
            tools=tools,
            max_iterations=15,      # Increased for complex tasks
            max_execution_time=900, # 15 minute timeout
            return_intermediate_steps=True,
            early_stopping_method="force"
        )
        
        # Test results storage
        all_results = []
        successful_tests = 0
        total_sites = len(TWO_FA_TEST_SITES)
        
        logger.info(f"\n🚀 Starting tests on {total_sites} 2FA sites...")
        print(f"\n🚀 Starting tests on {total_sites} 2FA sites...")
        print("💡 NoVNC viewer should be available for manual intervention")
        print("🔗 Human intervention may be required for authentication steps")
        
        for i, site_info in enumerate(TWO_FA_TEST_SITES, 1):
            print(f"\n📍 Testing site {i}/{total_sites}: {site_info['name']}")
            
            # Test the 2FA site
            site_results = await test_2fa_site(agent_executor, site_info, i, total_sites)
            all_results.append(site_results)
            
            if site_results["success"]:
                successful_tests += 1
                print(f"✅ {site_info['name']}: Success")
            else:
                print(f"❌ {site_info['name']}: {', '.join(site_results['errors'])}")
            
            # Brief pause between sites
            if i < total_sites:
                await asyncio.sleep(2)
        
        # Generate summary report
        print("\n" + "="*80)
        print("📊 2FA DEMO RESULTS SUMMARY")
        print("="*80)
        print(f"Total sites tested: {total_sites}")
        print(f"Successful tests: {successful_tests}")
        print(f"Success rate: {(successful_tests/total_sites)*100:.1f}%")
        print()
        
        # Detailed results for each site
        for result in all_results:
            status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
            print(f"{status} {result['site']} ({result['challenge_type']})")
            
            if result["human_intervention_used"]:
                print("   🤝 Human intervention: Required and handled")
            
            if result["intermediate_steps"]:
                print(f"   🔄 Steps: {len(result['intermediate_steps'])}")
            
            if result["errors"]:
                print(f"   ⚠️ Errors: {', '.join(result['errors'])}")
            print()
        
        print("="*80)
        print("🎯 DEMO INSIGHTS")
        print("="*80)
        print("This demo demonstrates the browser automation tool's capabilities for:")
        print("• Handling complex authentication flows with 2FA/MFA")
        print("• Identifying various security challenge types (SMS, TOTP, WebAuthn)")
        print("• Seamless human intervention for security-sensitive operations")
        print("• Working with modern authentication standards (FIDO2, WebAuthn)")
        print("• Providing detailed analysis of authentication workflows")
        print()
        print("The tool successfully bridges automated browsing with human security input,")
        print("making it ideal for testing and working with secure web applications.")
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
        success = await two_factor_auth_demo()
        
        if success:
            print("\n🎉 TWO-FACTOR AUTHENTICATION DEMO SUCCESSFUL!")
            print("Demonstrated handling of various 2FA challenges.")
        else:
            print("\n❌ Demo encountered issues")
            
    except Exception as e:
        print(f"💥 Demo failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
