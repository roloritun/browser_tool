"""
Network condition actions for browser automation.
This module provides functionality for modifying network conditions.
"""
import traceback

from browser_api.core.dom_handler import DOMHandler

class NetworkActions:
    """Network condition browser actions"""
    
    @staticmethod
    async def set_network_conditions(browser_instance, conditions):
        """Set network conditions like offline mode, throttling, etc."""
        try:
            page = await browser_instance.get_current_page()
            
            # Extract network condition parameters from Pydantic model
            offline = conditions.offline
            latency = conditions.latency  # Additional latency in ms
            download_throughput = conditions.downloadThroughput  # Bytes per second, -1 means no limit
            upload_throughput = conditions.uploadThroughput  # Bytes per second, -1 means no limit
            
            try:
                # Apply network conditions
                client = await page.context.new_cdp_session(page)
                
                await client.send("Network.emulateNetworkConditions", {
                    "offline": offline,
                    "latency": latency,
                    "downloadThroughput": download_throughput,
                    "uploadThroughput": upload_throughput
                })
                
                # Build a description of the applied conditions
                condition_descriptions = []
                if offline:
                    condition_descriptions.append("offline mode")
                if latency > 0:
                    condition_descriptions.append(f"{latency}ms latency")
                if download_throughput > 0:
                    download_speed = download_throughput / 1024  # Convert to KB/s
                    if download_speed > 1024:
                        download_speed = download_speed / 1024  # Convert to MB/s
                        condition_descriptions.append(f"{download_speed:.2f} MB/s download")
                    else:
                        condition_descriptions.append(f"{download_speed:.2f} KB/s download")
                if upload_throughput > 0:
                    upload_speed = upload_throughput / 1024  # Convert to KB/s
                    if upload_speed > 1024:
                        upload_speed = upload_speed / 1024  # Convert to MB/s
                        condition_descriptions.append(f"{upload_speed:.2f} MB/s upload")
                    else:
                        condition_descriptions.append(f"{upload_speed:.2f} KB/s upload")
                
                condition_description = ", ".join(condition_descriptions) if condition_descriptions else "default"
                
                success = True
                message = f"Set network conditions: {condition_description}"
                error = ""
            except Exception as network_error:
                print(f"Error setting network conditions: {network_error}")
                traceback.print_exc()
                success = False
                message = "Failed to set network conditions"
                error = str(network_error)
            
            # Get updated state after action
            dom_state, screenshot, elements, metadata = await DOMHandler.get_updated_browser_state(page, "set_network_conditions")
            
            return browser_instance.build_action_result(
                success,
                message,
                dom_state,
                screenshot,
                elements,
                metadata,
                error=error
            )
        except Exception as e:
            print(f"Unexpected error in set_network_conditions: {e}")
            traceback.print_exc()
            return browser_instance.build_action_result(
                False,
                str(e),
                None,
                "",
                "",
                {},
                error=str(e)
            )
