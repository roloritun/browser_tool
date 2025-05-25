import asyncio
import sys
import traceback
import webbrowser
import os
from pathlib import Path
from asyncio.exceptions import TimeoutError
from typing import Optional, Type, Union

from browser_use import (
    ActionResult,
    Agent,
    Browser,
    BrowserConfig,
    BrowserContextConfig,
    Controller,
)
from langchain.tools import BaseTool
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel, Field
from utilities.sandbox_manager import SandboxManager
from dotenv import load_dotenv

# from logger_setup import logger

load_dotenv()

controller = Controller()


class BrowserToolInput(BaseModel):
    """Input for Browser Tool."""

    task: Union[str, dict] = Field(..., description="Task to perform on the web")


@controller.action("Pause for manual user navigation")
def manual_navigation(reason: str) -> ActionResult:
    print(f"\n🤖 Agent is requesting manual help: {reason}")
    input("🧑‍💻 Please perform the action in browser, then press ENTER to continue...")
    return ActionResult(extracted_content="User completed manual step.")


class BrowserTool(BaseTool):
    name: str = "BrowserTool"
    description: str = (
        "Use this tool to perform web searches and extract information from the web."
    )
    args_schema: Optional[Type[BaseModel]] = BrowserToolInput
    return_direct: bool = False

    _browser: Optional[Browser] = None
    # _connection_mode: Optional[str] = None  # "cdp" or "proxy"
    _cdp_url: Optional[str] = None
    _is_headless: bool = False
    llm: BaseChatModel
    browser_llm: BaseChatModel

    def _run(self, task: Union[str, dict]) -> str:
        if isinstance(task, dict) and "task" in task:
            task = task["task"]
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            future = asyncio.ensure_future(self._run_agent(task))
            return asyncio.get_event_loop().run_until_complete(future)
        else:
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                result = new_loop.run_until_complete(self._run_agent(task))
            finally:
                new_loop.close()
            return result

    async def _run_agent(self, task: str) -> str:
        browser = None
        try:
            browser = await self._create_browser()

            agent = Agent(
                task=task
                + "\nAsk the user for help if stuck. example - 'login in to the site",
                llm=self.browser_llm,
                planner_llm=self.llm,
                max_failures=4,
                browser=browser,
                controller=controller,
            )

            # Running the agent with a timeout to avoid hanging
            result = await asyncio.wait_for(agent.run(), timeout=1000)
            return result

        except TimeoutError:
            return "❌ The browser tool timed out while performing the task."
        except Exception as e:
            print(f"Error traceback:\n{''.join(traceback.format_exc())}")
            return f"❌ An unexpected error occurred: {str(e)}"

        finally:
            if browser:
                try:
                    await asyncio.shield(browser.close())
                except Exception as e:
                    print(f"Warning: Error during browser cleanup: {e}")

    async def _create_browser(self) -> Browser:
        """Create a browser instance if it doesn't exist using the selected connection mode."""
        print("Creating browser instance...")
        print(f"CDP URL: {self._cdp_url}")
        if self._browser is None:
            # Common config options
            base_config = {
                "headless": self._is_headless,
                "disable_security": True,
                "timeout": 60000,
                "context_config": BrowserContextConfig(
                    ignore_https_errors=True,
                    bypass_csp=True,
                    cdp_url=self._cdp_url,
                    retry_count=5,
                ),
            }
        self._browser = Browser(
            config=BrowserConfig(
                **base_config,
            )
        )

        return self._browser

    def get_browser_info(self) -> dict:
        """Return browser info for debugging purposes."""
        return {
            "connection_mode": self._connection_mode,
            "browser_active": self._browser is not None,
        }

    async def cleanup(self):
        """Explicitly close the browser when done."""
        if self._browser:
            try:
                await self._browser.close()
                self._browser = None
                print("Browser closed successfully")
            except Exception as e:
                print(f"Failed to close browser: {e}")

    async def _arun(self, task: Union[str, dict]) -> str:
        if isinstance(task, dict) and "task" in task:
            task = task["task"]
        return await self._run_agent(task)

    def generate_and_open_viewer(self, vnc_url: str, novnc_url: str, vnc_password: str = "secret"):
        """Generate and open an HTML viewer for VNC and noVNC URLs and password."""
        try:
            # Get the template path
            template_path = Path(__file__).parent / "templates" / "viewer.html"
            output_path = Path(__file__).parent / "templates" / "current_viewer.html"

            # Read the template
            with open(template_path, "r") as f:
                template_content = f.read()

            # Replace placeholders using string replacement
            html_content = (template_content
                .replace("__VNC_URL__", vnc_url)
                .replace("__NOVNC_URL__", novnc_url)
                .replace("__VNC_PASSWORD__", vnc_password))

            # Write the generated HTML
            os.makedirs(output_path.parent, exist_ok=True)
            with open(output_path, "w") as f:
                f.write(html_content)

            # Open in browser
            self.open_viewer(str(output_path))
        except Exception as e:
            print(f"Failed to generate viewer: {e}")

    def open_viewer(self, file_path: str):
        """Open the generated HTML file in the default web browser."""
        try:
            # Get the absolute path of the file
            abs_file_path = str(Path(file_path).resolve())

            # Construct the file URL
            file_url = f"file://{abs_file_path}"

            # Open the file in the default web browser
            webbrowser.open(file_url)

            print(f"Opened in browser: {file_url}")
        except Exception as e:
            print(f"Failed to open viewer: {e}")


if __name__ == "__main__":
    # Read task from command-line arguments or set a default task.
    task = sys.argv[1] if len(sys.argv) > 1 else "Perform a test navigation"

    # Create dummy LLMs for testing
    LLM = AzureChatOpenAI(
        api_key="AKzVvkeJL1wwcezXY05H3mtuUPB2A4yogKPPoRDHG8nbwlucFmt3JQQJ99BDAC5RqLJXJ3w3AAABACOGoJQL",
        azure_deployment="gpt-4o-eagle-eu",
        api_version="2024-12-01-preview",
        azure_endpoint="https://eagle-azure-openai-eu.openai.azure.com/"
    )

    # Instantiate the BrowserTool with dummy LLMs.
    sandbox = SandboxManager()
    id, cdp, vnc, novnc, api, web, _ = sandbox.create_sandbox()
    #sys.exit(1)
    browser_tool = BrowserTool(llm=LLM, browser_llm=LLM)

    # Optionally set the connection mode ("cdp", "proxy", or leave as None)
    browser_tool._cdp_url = cdp

    # Generate and open the viewer with VNC and noVNC URLs and password
    browser_tool.generate_and_open_viewer(vnc, novnc, vnc_password="vncpassword")

    # Run and print the resulting output.
    result = browser_tool._run(task)
    print("Result:", result)
    #sandbox.delete_sandbox(id)
