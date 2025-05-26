import os
import sys
from typing import Tuple
from dotenv import load_dotenv

from daytona_sdk import Daytona, DaytonaConfig, CreateSandboxParams

load_dotenv()


class SandboxManager:
    def __init__(self):

        # Get Daytona API credentials with better error messages
        api_key = os.environ.get("DAYTONA_API_KEY")
        api_url = os.environ.get("DAYTONA_API_URL", "https://app.daytona.io/api")

        if not api_key:
            print("❌ Missing DAYTONA_API_KEY in environment variables.")
            print("Please check if your .env file contains DAYTONA_API_KEY.")
            print("To run without Daytona, use local_demo.py or azure_demo.py instead.")
            sys.exit(1)

        # Initialize Daytona client
        try:
            self.daytona = Daytona(
                DaytonaConfig(
                    api_key=api_key,
                    api_url=api_url,
                )
            )
            print(f"✅ Successfully initialized Daytona client with API KEY: {api_key}")
        except Exception as e:
            print(f"❌ Failed to initialize Daytona client: {str(e)}")
            print("Please check your DAYTONA_API_KEY and DAYTONA_API_URL.")
            sys.exit(1)

    def create_sandbox(self) -> Tuple[str, str, str, str, str, str, str]:
        """Create a Daytona sandbox with Chrome browser

        Returns:
            Tuple[str, str, str, str, str, str, str]: Returns:
                - sandbox_id: The ID of the created sandbox
                - cdp_url: Chrome DevTools Protocol URL
                - vnc_url: VNC URL for remote access
                - novnc_url: NoVNC URL for browser-based VNC
                - api_url: API server URL
                - web_url: Web interface URL
                - x_url: Additional URL (if any)
        """
        print("🚀 Creating Daytona sandbox with Chrome browser...")

        # Custom Docker image containing Chrome and necessary components
        image = "harbor-transient.internal.daytona.app/daytona/composer:4.0.0"
        # os.getenv(
        #     "DAYTONA_IMAGE",
        #     "harbor-transient.internal.daytona.app/daytona/roloritun/compose:0.0.1"
        # )

        try:
            # Create the sandbox
            sandbox = self.daytona.create(
                CreateSandboxParams(
                    # language="python",
                    image=image,
                    auto_stop_interval=0,
                    public=True,
                    env_vars={
                        "CHROME_PERSISTENT_SESSION": "true",
                        "ANONYMIZED_TELEMETRY": "false",
                        "CHROME_PATH": "",
                        "CHROME_USER_DATA": "",
                        "CHROME_DEBUGGING_PORT": "9222",
                        "CHROME_DEBUGGING_HOST": "localhost",
                        "CHROME_CDP": "",
                        "API_PORT": "8000",
                    },
                    resources={
                        "cpu": 2,
                        "memory": 4,
                        "disk": 5,
                    },
                )
            )
            print(f"✅ Sandbox created with ID: {sandbox.id}")

            # Get CDP URL for Chrome DevTools Protocol
            try:
                cdp = sandbox.get_preview_link(9222)
                cdp_url = cdp.url
                print(f"✅ Chrome DevTools Protocol URL: {cdp_url}")

                vnc = sandbox.get_preview_link(5901)  # VNC port
                vnc_url = vnc.url
                print(f"✅ VNC Protocol URL: {vnc_url}")

                novnc = sandbox.get_preview_link(6080)  # NoVNC port
                novnc_url = novnc.url
                print(f"✅ NOVNC Protocol URL: {novnc_url}")
                print(f"✅ NOVNC Protocol token: {novnc.token}")

                api = sandbox.get_preview_link(8000)  # API port (matching Docker container port)
                api_url = api.url
                print(f"✅ API Protocol URL: {api_url}")

                web = sandbox.get_preview_link(8080)  # Web interface port
                web_url = web.url
                print(f"✅ WEB Protocol URL: {web_url}")

                # Use web URL as x_url since we don't need another preview link
                x = sandbox.get_preview_link(8002)  # X port
                x_url = x.url
                print(f"✅ Using X URL as additional URL: {x_url}")

                return sandbox.id, cdp_url, vnc_url, novnc_url, api_url, web_url, x_url
            except Exception as e:
                print(f"❌ Error getting preview link: {str(e)}")
                print("The sandbox was created but couldn't get the CDP URL.")
                print("Please check if port 9222 is exposed in the sandbox.")
                sys.exit(1)

        except Exception as e:
            print(f"❌ Error creating Daytona sandbox: {str(e)}")
            print("Please check your Daytona API key, URL, and network connectivity.")
            print("To run without Daytona, use local_demo.py or azure_demo.py instead.")
            sys.exit(1)

    def delete_sandbox(self, sandbox_id: str):
        """Delete a Daytona sandbox by its ID

        Args:
            sandbox_id (str): The ID of the sandbox to delete
        """
        print(f"🗑️ Deleting Daytona sandbox with ID: {sandbox_id}...")

        try:
            sandbox = self.daytona.get_current_sandbox(sandbox_id)
            self.daytona.remove(sandbox)
            print(f"✅ Sandbox {sandbox_id} deleted successfully.")
        except Exception as e:
            print(f"❌ Error deleting sandbox {sandbox_id}: {str(e)}")
            # Don't try to call remove without arguments
