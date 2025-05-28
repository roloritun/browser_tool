#!/usr/bin/env python3
"""
Advanced examples of using browser automation tools for common tasks.
Now includes noVNC viewer for real-time browser automation viewing!
"""

import asyncio
import os
import sys
import time
import webbrowser
from pathlib import Path
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI
from src.utils.logger import logger
from src.tools.utilities.browser_tools_init import initialize_browser_tools

# Load environment variables
load_dotenv()


async def create_browser_agent(llm, browser_tools):
    """Create a specialized browser automation agent with context management."""
    # Create a prompt template specifically for browser automation
    prompt_template = """You are an expert web browser automation assistant with experience in handling complex web interfaces.
You have access to the following tools:

{tools}

Use these tools to automate browser tasks efficiently.
When navigating websites:
1. First check if the page has loaded properly
2. Extract key information to understand the page structure
3. Use the appropriate tools to interact with elements
4. Handle any errors or unexpected situations that may arise

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}"""

    prompt = PromptTemplate.from_template(prompt_template)
    
    # Create the agent
    agent = create_react_agent(llm, browser_tools, prompt)
    
    # Create agent executor with aggressive context management
    agent_executor = AgentExecutor(
        agent=agent,
        tools=browser_tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5,  # Very conservative to prevent context buildup
        early_stopping_method="force",  # Using 'force' instead of 'generate' which is no longer supported
        max_execution_time=300  # 5 minute timeout per task
    )
    
    return agent_executor


class ContextManagedAgentExecutor:
    """Wrapper for AgentExecutor that manages context length."""
    
    def __init__(self, agent_executor, max_context_tokens=60000):
        self.agent_executor = agent_executor
        self.max_context_tokens = max_context_tokens
        self.conversation_history = []
    
    def _estimate_tokens(self, text):
        """More accurate token estimation (1 token ≈ 3.5 characters for typical text)."""
        return len(str(text)) // 3
    
    def _trim_context(self, inputs):
        """Aggressively trim context to stay within token limits."""
        # Extract the main input
        input_text = str(inputs.get('input', ''))
        
        # Keep inputs very short and focused
        if len(input_text) > 1000:  # Limit input length
            input_text = input_text[:1000] + "... [truncated]"
            inputs['input'] = input_text
        
        return inputs
    
    async def ainvoke(self, inputs):
        """Async invoke with aggressive context management."""
        # Trim inputs
        inputs = self._trim_context(inputs)
        
        # Clear any memory to prevent context accumulation
        if hasattr(self.agent_executor.agent, 'memory') and self.agent_executor.agent.memory:
            self.agent_executor.agent.memory.clear()
        
        # Reset agent scratchpad if it exists
        if hasattr(self.agent_executor, '_call'):
            # Force a fresh start for each call
            self.agent_executor._call = None
        
        return await self.agent_executor.ainvoke(inputs)
    
    def invoke(self, inputs):
        """Sync invoke with aggressive context management."""
        # Trim inputs
        inputs = self._trim_context(inputs)
        
        # Clear any memory to prevent context accumulation
        if hasattr(self.agent_executor.agent, 'memory') and self.agent_executor.agent.memory:
            self.agent_executor.agent.memory.clear()
        
        # Reset agent scratchpad if it exists
        if hasattr(self.agent_executor, '_call'):
            # Force a fresh start for each call
            self.agent_executor._call = None
        
        return self.agent_executor.invoke(inputs)


def open_novnc_viewer(novnc_url: str, vnc_password: str = "vncpassword"):
    """Generate and open an HTML viewer for noVNC access."""
    try:
        # Create a simple HTML file for noVNC access
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Browser Automation Viewer - noVNC Access</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .info-box {{
            border: 1px solid #ddd;
            padding: 20px;
            margin: 10px 0;
            border-radius: 5px;
            background-color: #f9f9f9;
        }}
        .info-box h3 {{
            margin-top: 0;
            color: #333;
        }}
        .info-box a {{
            color: #0066cc;
            text-decoration: none;
            display: inline-block;
            padding: 8px 16px;
            background-color: #007acc;
            color: white;
            border-radius: 4px;
            margin: 5px 0;
        }}
        .info-box a:hover {{
            background-color: #005c99;
        }}
        .password-info {{
            background-color: #e8f5e8;
            border-color: #4caf50;
        }}
        .instructions {{
            background-color: #fff3cd;
            border-color: #ffc107;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Browser Automation Viewer</h1>
        <p>Watch your browser automation in real-time!</p>
        
        <div class="info-box">
            <h3>🖥️ noVNC Browser Access</h3>
            <p>Click the link below to open the browser automation viewer in your web browser:</p>
            <a href="{novnc_url}" target="_blank">🌐 Open noVNC Viewer</a>
            <p><small>URL: {novnc_url}</small></p>
        </div>
        
        <div class="info-box password-info">
            <h3>🔑 VNC Password</h3>
            <p>If prompted for a password, use: <strong>{vnc_password}</strong></p>
        </div>
        
        <div class="info-box instructions">
            <h3>📋 Instructions</h3>
            <ul>
                <li>Click the noVNC link above to open the remote desktop viewer</li>
                <li>You'll see a virtual desktop with a Chrome browser</li>
                <li>Watch as the automation script controls the browser automatically</li>
                <li>You can interact with the browser manually if needed</li>
                <li>Keep this viewer open while running the advanced examples</li>
            </ul>
        </div>
        
        <div class="info-box">
            <h3>🤖 What You'll See</h3>
            <p>The advanced examples will perform these tasks automatically:</p>
            <ul>
                <li>Navigate to Wikipedia and search for 'browser automation'</li>
                <li>Visit example.com and extract links</li>
                <li>Browse Hacker News for top stories</li>
                <li>Fill out forms on httpbin.org</li>
                <li>Get weather information from weather.gov</li>
            </ul>
        </div>
    </div>
</body>
</html>
        """
        
        # Create viewer file in a temp directory
        viewer_path = Path.home() / "tmp" / "browser_automation_viewer.html"
        viewer_path.parent.mkdir(exist_ok=True)
        
        with open(viewer_path, "w") as f:
            f.write(html_content)
        
        # Open in default browser
        webbrowser.open(f"file://{viewer_path}")
        logger.info(f"🌐 noVNC viewer opened in browser: file://{viewer_path}")
        logger.info(f"🔗 Direct noVNC URL: {novnc_url}")
        logger.info(f"🔑 VNC Password: {vnc_password}")
        
        return str(viewer_path)
        
    except Exception as e:
        logger.error(f"Failed to open noVNC viewer: {e}")
        logger.info(f"You can manually open this URL in your browser: {novnc_url}")
        return None


async def run_advanced_browser_tasks():
    """Run a series of advanced browser automation tasks with shared browser session."""
    try:
        # Initialize Azure OpenAI with aggressive token limits
        logger.info("Initializing Azure OpenAI...")
        llm = AzureChatOpenAI(
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15"),
            max_tokens=2000,  # Very conservative response length limit
            temperature=0.1  # Lower temperature for more deterministic results
        )
        
        # Create sandbox and get URLs including noVNC
        logger.info("Creating browser sandbox with noVNC viewer...")
        from src.tools.utilities.sandbox_manager import SandboxManager
        sandbox_manager = SandboxManager()
        sandbox_id, cdp_url, vnc_url, novnc_url, api_url, web_url, x_url = sandbox_manager.create_sandbox()
        
        logger.info("🎯 Sandbox created successfully!")
        logger.info(f"📱 Sandbox ID: {sandbox_id}")
        logger.info(f"🌐 API URL: {api_url}")
        logger.info(f"🖥️ noVNC Viewer: {novnc_url}")
        
        # Open noVNC viewer so user can watch the automation
        logger.info("🚀 Opening noVNC viewer for real-time browser viewing...")
        viewer_path = open_novnc_viewer(novnc_url, vnc_password="vncpassword")
        
        if viewer_path:
            logger.info("✅ noVNC viewer opened! You can now watch the browser automation in real-time.")
        else:
            logger.warning("⚠️ Could not open viewer automatically. Please open this URL manually:")
            logger.info(f"   {novnc_url}")
        
        # Wait a moment for viewer to open and user to see it
        logger.info("⏳ Waiting 10 seconds for viewer to load...")
        await asyncio.sleep(10)
        
        # Initialize browser tools with the created sandbox
        logger.info("Initializing browser tools with shared sandbox session...")
        browser_tools = await initialize_browser_tools(api_url=api_url, sandbox_id=sandbox_id)
        logger.info("✅ Browser tools initialized - all tasks will use the same browser session")
        
        # List of tasks to demonstrate various capabilities
        tasks = [
            "Navigate to wikipedia.org and search for 'browser automation'",
            "Go to example.com, extract all links, then navigate to the first link",
            "Navigate to news.ycombinator.com and find the top 3 stories",
            "Go to httpbin.org/forms/post and fill out the form with name 'Test User' and submit it",
            "Visit weather.gov and get the current weather for New York City for today",
        ]
        
        logger.info("🎬 Starting automated browser tasks...")
        logger.info("👀 Watch the browser automation live in your noVNC viewer!")
        logger.info("=" * 80)
        
        # Run each task with a fresh agent but reusing the same browser session
        for i, task in enumerate(tasks, 1):
            logger.info("=" * 80)
            logger.info(f"🤖 TASK {i}/{len(tasks)}: {task}")
            logger.info("📺 Watch this task execute in your noVNC viewer...")
            logger.info("=" * 80)
            
            # Create a fresh agent for each task (context isolation) but reuse browser tools
            base_agent_executor = await create_browser_agent(llm, browser_tools)
            agent_executor = ContextManagedAgentExecutor(
                base_agent_executor, 
                max_context_tokens=60000  # Conservative limit
            )
            
            try:
                logger.info(f"▶️ Starting task {i}...")
                result = await agent_executor.ainvoke({"input": task})
                logger.info(f"✅ Task {i} completed successfully!")
                logger.info(f"📄 Result: {result.get('output', '')}")
            except Exception as task_error:
                logger.error(f"❌ Task {i} failed: {str(task_error)}")
                # Continue with next task
                continue
            
            # Pause between tasks to let user observe
            if i < len(tasks):
                logger.info("⏸️ Pausing 8 seconds between tasks...")
                logger.info("👀 Check your noVNC viewer to see what happened!")
                await asyncio.sleep(8)
        
        logger.info("=" * 80)
        logger.info("🎉 All tasks completed using the same browser session!")
        logger.info("🔄 Browser session reuse optimization working perfectly!")
        logger.info("📺 You can keep the noVNC viewer open to explore the final browser state")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Error in advanced browser tasks: {str(e)}")
        return 1
    
    return 0


def main():
    """Main function to run the advanced browser automation examples."""
    start_time = time.time()
    logger.info("🚀 Starting advanced browser automation examples with noVNC viewer...")
    logger.info("📺 A browser viewer will open automatically to watch the automation!")
    
    try:
        exit_code = asyncio.run(run_advanced_browser_tasks())
        elapsed_time = time.time() - start_time
        logger.info("=" * 80)
        logger.info(f"🏁 Advanced examples completed in {elapsed_time:.2f} seconds")
        logger.info("✅ Browser session reuse optimization demonstrated successfully!")
        logger.info("📺 noVNC viewer remains open for inspection")
        logger.info("=" * 80)
        return exit_code
    except KeyboardInterrupt:
        logger.info("⏹️ Examples interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"❌ Unhandled exception: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
