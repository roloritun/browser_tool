#!/usr/bin/env python3
"""
NoVNC Human Intervention Demo - Simplified
==========================================

A focused demo that showcases the NoVNC web viewer for watching browser automation
and demonstrates human intervention capabilities with test sites.

Key Features:
✅ Opens beautiful NoVNC web viewer automatically
✅ Tests real CAPTCHA sites requiring human intervention
✅ Demonstrates pause/resume automation workflow
✅ Shows intervention detection in action
✅ Clean UI for monitoring automation progress

Test Sites:
- https://2captcha.com/demo
- https://www.mtcaptcha.com/test-multiple-captcha
"""

import asyncio
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.tools.utilities.browser_tools_init import initialize_browser_tools
from src.tools.utilities.sandbox_manager import SandboxManager
from src.utils.logger import logger
from src.utils.enhanced_agent_formatting import create_enhanced_react_agent
from src.utils.novnc_viewer import generate_novnc_viewer

# Load environment variables
load_dotenv()


def create_simple_novnc_viewer(novnc_url: str) -> str:
    """Create a simple, beautiful NoVNC viewer"""
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 Browser Automation - Live View</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            flex-direction: column;
        }}
        
        .header {{
            background: rgba(0,0,0,0.9);
            color: white;
            padding: 20px;
            text-align: center;
            border-bottom: 3px solid #4CAF50;
        }}
        
        .header h1 {{
            font-size: 28px;
            margin-bottom: 8px;
        }}
        
        .header .subtitle {{
            font-size: 16px;
            opacity: 0.8;
        }}
        
        .intervention-banner {{
            background: #ff4444;
            color: white;
            padding: 15px;
            text-align: center;
            font-weight: bold;
            font-size: 18px;
            display: none;
            animation: pulse 2s infinite;
        }}
        
        @keyframes pulse {{
            0% {{ background: #ff4444; }}
            50% {{ background: #cc3333; }}
            100% {{ background: #ff4444; }}
        }}
        
        .viewer-container {{
            flex: 1;
            background: #000;
            border: 3px solid #34495e;
            margin: 15px;
            border-radius: 10px;
            overflow: hidden;
            position: relative;
        }}
        
        .novnc-frame {{
            width: 100%;
            height: 100%;
            border: none;
        }}
        
        .controls {{
            background: rgba(0,0,0,0.9);
            padding: 20px;
            display: flex;
            gap: 20px;
            justify-content: center;
            flex-wrap: wrap;
        }}
        
        .btn {{
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            font-size: 16px;
            transition: all 0.3s ease;
        }}
        
        .btn-success {{
            background: #27ae60;
            color: white;
        }}
        
        .btn-warning {{
            background: #f39c12;
            color: white;
        }}
        
        .btn-danger {{
            background: #e74c3c;
            color: white;
        }}
        
        .btn:hover {{
            transform: translateY(-3px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.3);
        }}
        
        .loading {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: white;
            font-size: 20px;
            text-align: center;
        }}
        
        .spinner {{
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 Live Browser Automation Viewer</h1>
        <div class="subtitle">Watch the automation in real-time • Provide help when needed</div>
    </div>
    
    <div class="intervention-banner" id="intervention-banner">
        🚨 HUMAN INTERVENTION NEEDED - Please help solve the challenge and click "Task Complete"
    </div>
    
    <div class="viewer-container">
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <div>Connecting to browser...</div>
        </div>
        <iframe class="novnc-frame" src="{novnc_url}" id="novnc-frame"></iframe>
    </div>
    
    <div class="controls">
        <button class="btn btn-success" onclick="taskComplete()">✅ Task Complete</button>
        <button class="btn btn-warning" onclick="needHelp()">❓ Need Help</button>
        <button class="btn btn-danger" onclick="stopDemo()">🛑 Stop Demo</button>
    </div>

    <script>
        // Hide loading after iframe loads
        document.getElementById('novnc-frame').onload = function() {{
            setTimeout(() => {{
                document.getElementById('loading').style.display = 'none';
            }}, 3000);
        }};
        
        function taskComplete() {{
            alert('✅ Task marked as complete! The automation will continue.');
            hideInterventionBanner();
        }}
        
        function needHelp() {{
            alert('❓ Help request noted. Check the console for guidance.');
        }}
        
        function stopDemo() {{
            if (confirm('🛑 Stop the demo? This will end the automation.')) {{
                alert('Demo stopped.');
                window.close();
            }}
        }}
        
        function showInterventionBanner() {{
            document.getElementById('intervention-banner').style.display = 'block';
        }}
        
        function hideInterventionBanner() {{
            document.getElementById('intervention-banner').style.display = 'none';
        }}
        
        // Demo: Show intervention banner after 45 seconds to simulate CAPTCHA encounter
        setTimeout(showInterventionBanner, 45000);
    </script>
</body>
</html>"""
    
    # Save the HTML file
    viewer_dir = Path(__file__).parent / "viewers"
    viewer_dir.mkdir(exist_ok=True)
    viewer_file = viewer_dir / "simple_novnc_demo.html"
    
    with open(viewer_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return str(viewer_file.absolute())


async def run_intervention_scenarios(tools, agent):
    """Run specific scenarios that require human intervention"""
    
    scenarios = [
        {
            "name": "2Captcha Demo Site",
            "task": """Navigate to https://2captcha.com/demo and explore the page. Look for any CAPTCHA challenges or interactive elements. If you encounter a CAPTCHA or similar challenge that you cannot solve automatically, use the smart_auto_detect_intervention tool to check if human intervention is needed, and if so, use smart_request_intervention to ask for help. Wait for human assistance and then continue."""
        },
        {
            "name": "MTCaptcha Test",
            "task": """Go to https://www.mtcaptcha.com/test-multiple-captcha and try to interact with any CAPTCHA elements you find. Use the intervention detection tools when you encounter challenges that require human assistance."""
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(scenarios, 1):
        logger.info(f"\n🧪 Running Scenario {i}: {scenario['name']}")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        try:
            result = await agent.ainvoke({"input": scenario['task']})
            execution_time = time.time() - start_time
            
            logger.info(f"✅ Scenario completed in {execution_time:.1f} seconds")
            
            results.append({
                "name": scenario['name'],
                "status": "success",
                "time": execution_time,
                "result": str(result)
            })
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ Scenario failed: {str(e)}")
            
            results.append({
                "name": scenario['name'],
                "status": "failed",
                "time": execution_time,
                "error": str(e)
            })
        
        # Brief pause between scenarios
        await asyncio.sleep(3)
    
    return results


async def novnc_human_intervention_demo():
    """Main demo function"""
    
    print("🚀 Starting NoVNC Human Intervention Demo")
    print("=" * 60)
    print("This demo will:")
    print("• Open a beautiful web viewer showing the browser automation")
    print("• Test sites that require human intervention (CAPTCHAs)")
    print("• Demonstrate pause/resume functionality")
    print("• Show how the system detects when help is needed")
    print("=" * 60)
    
    # Create sandbox
    logger.info("🔧 Creating browser sandbox...")
    sandbox_manager = SandboxManager()
    sandbox_id, cdp_url, vnc_url, novnc_url, api_url, web_url, x_url = sandbox_manager.create_sandbox()
    
    logger.info(f"✅ Sandbox created: {sandbox_id}")
    logger.info(f"🌐 NoVNC URL: {novnc_url}")
    
    try:
        # Create and open the NoVNC viewer
        logger.info("🖥️ Creating NoVNC viewer...")
        try:
            viewer_path = generate_novnc_viewer(
                novnc_url=novnc_url,
                vnc_password=os.getenv('VNC_PASSWORD', 'vncpassword'),
                auto_open=True
            )
            logger.info(f"✅ Viewer created: {viewer_path}")
            logger.info("🌐 NoVNC viewer opened in your browser...")
        except Exception as e:
            logger.warning(f"⚠️ Could not start NoVNC viewer: {e}")
            logger.info("💡 Demo will continue without viewer")
        
        # Wait for viewer to load
        logger.info("⏳ Waiting for viewer to load...")
        await asyncio.sleep(8)
        
        # Initialize tools
        logger.info("🔧 Initializing browser tools...")
        tools = await initialize_browser_tools(api_url, sandbox_id)
        
        # Enhanced LLM Configuration (proven settings)
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
        
        # Create agent
        logger.info("🤖 Creating intervention-aware agent...")
        agent = create_enhanced_react_agent(
            llm=llm,
            tools=tools,
            max_iterations=12,
            max_execution_time=600
        )
        
        print("\n🎯 DEMO READY!")
        print("=" * 60)
        print("1. A web viewer has opened showing the live browser")
        print("2. Watch as the automation navigates to test sites")
        print("3. When you see a CAPTCHA, the system will detect it")
        print("4. You can manually solve it through the viewer")
        print("5. Click 'Task Complete' to let automation continue")
        print("=" * 60)
        
        input("📱 Press Enter when you can see the browser viewer...")
        
        # Run the intervention scenarios
        logger.info("🎬 Starting intervention test scenarios...")
        results = await run_intervention_scenarios(tools, agent)
        
        # Show results
        print("\n📊 DEMO RESULTS:")
        print("=" * 40)
        for result in results:
            status = "✅" if result['status'] == 'success' else "❌"
            print(f"{status} {result['name']} - {result['time']:.1f}s")
        print("=" * 40)
        
        print("\n🎉 Demo completed!")
        print("💡 The viewer will stay open for you to explore")
        
        input("📱 Press Enter to end the demo...")
        
    except KeyboardInterrupt:
        logger.info("⚠️ Demo interrupted by user")
    except Exception as e:
        logger.error(f"❌ Demo failed: {str(e)}")
        raise
    finally:
        # Cleanup
        logger.info("🧹 Cleaning up...")
        try:
            sandbox_manager.delete_sandbox(sandbox_id)
            logger.info("✅ Cleanup completed")
        except Exception as e:
            logger.error(f"⚠️ Cleanup error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(novnc_human_intervention_demo())
