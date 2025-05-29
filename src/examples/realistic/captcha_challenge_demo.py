#!/usr/bin/env python3
"""
CAPTCHA Challenge Demo - Testing Human Intervention
=================================================

This demo tests the browser automation system's ability to handle various types of CAPTCHAs
and other security challenges that require human intervention. It demonstrates:

✅ Multiple CAPTCHA testing sites
✅ Automatic CAPTCHA detection
✅ Human intervention workflow
✅ NoVNC real-time monitoring
✅ Error handling and recovery
✅ Multiple challenge types (reCAPTCHA, hCaptcha, image CAPTCHAs)

Test Sites:
- https://2captcha.com/demo - Multiple CAPTCHA types
- https://www.mtcaptcha.com/test-multiple-captcha - MTCaptcha testing
- https://captcha.com/demos/features/captcha-demo.aspx - Image CAPTCHAs
- https://www.google.com/recaptcha/api2/demo - Google reCAPTCHA
- https://accounts.hcaptcha.com/demo - hCaptcha demo
"""

import sys
import os

from langchain_openai import AzureChatOpenAI
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


import asyncio
import os
import sys
import time
from dotenv import load_dotenv

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.tools.utilities.browser_tools_init import initialize_browser_tools
from src.tools.utilities.sandbox_manager import SandboxManager
from src.utils.logger import logger
from src.utils.enhanced_agent_formatting import create_enhanced_react_agent
from src.utils.novnc_viewer import generate_novnc_viewer

# Load environment variables
load_dotenv()

CAPTCHA_TEST_SITES = [
    {
        "name": "2Captcha Demo Site",
        "url": "https://2captcha.com/demo",
        "description": "Multiple CAPTCHA types including reCAPTCHA, hCaptcha, and image CAPTCHAs",
        "challenge_type": "Multiple",
        "expected_interventions": ["reCAPTCHA", "hCaptcha", "Image CAPTCHA"]
    },
    {
        "name": "MTCaptcha Test",
        "url": "https://www.mtcaptcha.com/test-multiple-captcha",
        "description": "MTCaptcha testing environment",
        "challenge_type": "MTCaptcha",
        "expected_interventions": ["MTCaptcha challenge"]
    },
    {
        "name": "Google reCAPTCHA Demo",
        "url": "https://www.google.com/recaptcha/api2/demo",
        "description": "Official Google reCAPTCHA testing page",
        "challenge_type": "reCAPTCHA v2",
        "expected_interventions": ["reCAPTCHA v2 challenge"]
    },
    {
        "name": "hCaptcha Demo",
        "url": "https://accounts.hcaptcha.com/demo",
        "description": "Official hCaptcha testing environment",
        "challenge_type": "hCaptcha",
        "expected_interventions": ["hCaptcha challenge"]
    },
    {
        "name": "Captcha.com Demo",
        "url": "https://captcha.com/demos/features/captcha-demo.aspx",
        "description": "Image-based CAPTCHA demonstrations",
        "challenge_type": "Image CAPTCHA",
        "expected_interventions": ["Image recognition"]
    }
]

async def test_captcha_site(agent, site_info, site_index, total_sites):
    """Test a specific CAPTCHA site"""
    logger.info(f"\n{'='*60}")
    logger.info(f"🔒 TESTING SITE {site_index}/{total_sites}: {site_info['name']}")
    logger.info(f"URL: {site_info['url']}")
    logger.info(f"Challenge Type: {site_info['challenge_type']}")
    logger.info(f"Description: {site_info['description']}")
    logger.info(f"{'='*60}")
    
    start_time = time.time()
    
    # Navigate to the CAPTCHA test site
    task = f"""
    Navigate to {site_info['url']} and analyze the page for CAPTCHA challenges.
    
    Your task:
    1. Navigate to the URL
    2. Look for any CAPTCHA challenges on the page
    3. Identify the type of CAPTCHA (reCAPTCHA, hCaptcha, image CAPTCHA, etc.)
    4. If you find a CAPTCHA, request human help to solve it
    5. Try to complete any forms or interactions that require CAPTCHA solving
    6. Report what you found and whether human intervention was needed
    
    Expected challenge type: {site_info['challenge_type']}
    
    If you encounter any CAPTCHA or security challenge:
    - Request human help immediately
    - Provide clear instructions on what needs to be done
    - Wait for human completion before proceeding
    
    Be thorough in your analysis and report all security challenges found.
    """
    
    try:
        logger.info(f"🤖 Starting automated analysis of {site_info['name']}...")
        result = agent.invoke(task)
        
        elapsed_time = time.time() - start_time
        logger.info(f"✅ Completed {site_info['name']} analysis in {elapsed_time:.1f}s")
        logger.info(f"📋 Result: {result}")
        
        return {
            "site": site_info['name'],
            "url": site_info['url'],
            "success": True,
            "result": result,
            "elapsed_time": elapsed_time,
            "challenge_type": site_info['challenge_type'],
            "human_intervention_used": "human help" in result.lower() or "intervention" in result.lower()
        }
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(f"❌ Error testing {site_info['name']}: {str(e)}")
        return {
            "site": site_info['name'],
            "url": site_info['url'],
            "success": False,
            "error": str(e),
            "elapsed_time": elapsed_time,
            "challenge_type": site_info['challenge_type'],
            "human_intervention_used": False
        }

async def captcha_challenge_demo():
    """Comprehensive CAPTCHA challenge demonstration"""
    
    logger.info("🔒 Starting CAPTCHA Challenge Demo")
    logger.info("=" * 60)
    logger.info("🎯 This demo tests various CAPTCHA types and human intervention")
    logger.info("📋 Testing multiple CAPTCHA providers and challenge types")
    logger.info("🛡️ Demonstrating robust security challenge handling")
    logger.info("=" * 60)
    
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
        logger.info("👀 Monitor the browser automation in real-time")
        logger.info("🤝 Be ready to help solve CAPTCHAs when requested")
    except Exception as e:
        logger.warning(f"⚠️ Could not start NoVNC viewer: {e}")
        logger.info("💡 Demo will continue without viewer")
    
    # Initialize browser tools
    tools = await initialize_browser_tools(api_url, sandbox_id)

     # Initialize Azure OpenAI with OPTIMAL settings
    llm = AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            temperature=0.0,  # Maximum determinism - CRITICAL for consistency
            max_tokens=2000,  # Sufficient but not excessive
            top_p=0.1,        # Very focused sampling - CRITICAL for format adherence
            frequency_penalty=0.0,
            presence_penalty=0.0,
            request_timeout=60,
            max_retries=3
        )
        
    
    # Create enhanced agent with human intervention capabilities
    agent = create_enhanced_react_agent(tools, llm)
    
    # Test results storage
    test_results = []
    total_sites = len(CAPTCHA_TEST_SITES)
    
    logger.info(f"\n🚀 Testing {total_sites} CAPTCHA challenge sites...")
    
    # Test each CAPTCHA site
    for i, site_info in enumerate(CAPTCHA_TEST_SITES, 1):
        try:
            # Add delay between tests to avoid rate limiting
            if i > 1:
                logger.info("⏳ Waiting 3 seconds between tests...")
                await asyncio.sleep(3)
            
            result = await test_captcha_site(agent, site_info, i, total_sites)
            test_results.append(result)
            
        except Exception as e:
            logger.error(f"❌ Unexpected error testing site {i}: {str(e)}")
            test_results.append({
                "site": site_info['name'],
                "url": site_info['url'],
                "success": False,
                "error": str(e),
                "elapsed_time": 0,
                "challenge_type": site_info['challenge_type'],
                "human_intervention_used": False
            })
    
    # Generate comprehensive report
    logger.info("\n" + "="*60)
    logger.info("📊 CAPTCHA CHALLENGE DEMO RESULTS")
    logger.info("="*60)
    
    successful_tests = sum(1 for r in test_results if r['success'])
    intervention_used = sum(1 for r in test_results if r.get('human_intervention_used', False))
    total_time = sum(r.get('elapsed_time', 0) for r in test_results)
    
    logger.info(f"🎯 Sites Tested: {total_sites}")
    logger.info(f"✅ Successful: {successful_tests}/{total_sites}")
    logger.info(f"🤝 Human Interventions: {intervention_used}")
    logger.info(f"⏱️ Total Time: {total_time:.1f}s")
    logger.info(f"📈 Success Rate: {(successful_tests/total_sites)*100:.1f}%")
    
    logger.info("\n📋 Detailed Results:")
    for result in test_results:
        status = "✅" if result['success'] else "❌"
        intervention = "🤝" if result.get('human_intervention_used', False) else "🤖"
        logger.info(f"{status} {intervention} {result['site']} ({result['challenge_type']}) - {result.get('elapsed_time', 0):.1f}s")
        if not result['success'] and 'error' in result:
            logger.info(f"     Error: {result['error']}")
    
    logger.info("\n🔒 CAPTCHA Types Tested:")
    challenge_types = list(set(r['challenge_type'] for r in test_results))
    for challenge_type in challenge_types:
        type_results = [r for r in test_results if r['challenge_type'] == challenge_type]
        type_success = sum(1 for r in type_results if r['success'])
        logger.info(f"   • {challenge_type}: {type_success}/{len(type_results)} successful")
    
    # Summary assessment
    if successful_tests >= total_sites * 0.8:
        logger.info("\n🎉 EXCELLENT: CAPTCHA handling system is working well!")
        logger.info(f"🛡️ Successfully handled {intervention_used} human interventions")
    elif successful_tests >= total_sites * 0.6:
        logger.info("\n✅ GOOD: Most CAPTCHA challenges handled successfully")
        logger.info("🔧 Some challenges may need refinement")
    else:
        logger.info("\n⚠️ NEEDS IMPROVEMENT: Many CAPTCHA challenges failed")
        logger.info("🛠️ Consider reviewing intervention mechanisms")
    
    logger.info(f"\n🖥️ NoVNC Viewer remains open for further testing: {viewer_path}")
    logger.info("🧪 You can manually test more CAPTCHA challenges if needed")
    
    return test_results

if __name__ == "__main__":
    try:
        results = asyncio.run(captcha_challenge_demo())
        logger.info("\n🏁 CAPTCHA Challenge Demo completed successfully!")
    except KeyboardInterrupt:
        logger.info("\n⚠️ Demo interrupted by user")
    except Exception as e:
        logger.error(f"\n❌ Demo failed with error: {str(e)}")
        sys.exit(1)
