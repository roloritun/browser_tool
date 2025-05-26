"""
Frame handling actions for browser automation.
This module provides functionality for interacting with frames in the browser.
"""
import traceback

from fastapi import Body
from browser_api.models.action_models import NoParamsAction, SwitchToFrameAction
from browser_api.core.dom_handler import DOMHandler

class FrameActions:
    """Frame handling browser actions"""
    
    @staticmethod
    async def switch_to_frame(browser_instance, action: SwitchToFrameAction = Body(...)):
        """Switch to a frame by name, ID, or index"""
        try:
            # Get the frame identifier
            frame_selector = action.frame_selector
            if not frame_selector:
                return browser_instance.build_action_result(
                    False,
                    "No frame selector provided",
                    None,
                    "",
                    "",
                    {},
                    error="The 'frame_selector' parameter is required"
                )
            
            page = await browser_instance.get_current_page()
            
            try:
                # Try to find the frame by name, ID, or index
                # First check if it's a numeric string (index)
                try:
                    frame_index = int(frame_selector)
                    # Find by index
                    frames = page.frames
                    if frame_index < 0 or frame_index >= len(frames):
                        return browser_instance.build_action_result(
                            False,
                            f"Invalid frame index: {frame_index}. Found {len(frames)} frames.",
                            None,
                            "",
                            "",
                            {},
                            error=f"Frame index must be between 0 and {len(frames) - 1}"
                        )
                    
                    browser_instance.current_frame = frames[frame_index]
                except ValueError:
                    # Not a number, treat as name/ID selector
                    # Find by name or ID (as a CSS selector)
                    # First try using the built-in frame method
                    frame = page.frame(name=frame_selector)
                    
                    if not frame:
                        # Try finding the iframe element and then get its content frame
                        iframe_element = await page.query_selector(f"iframe[name='{frame_selector}'], iframe[id='{frame_selector}'], iframe")
                        if not iframe_element:
                            return browser_instance.build_action_result(
                                False,
                                f"Frame not found: {frame_selector}",
                                None,
                                "",
                                "",
                                {},
                                error=f"No frame with name or ID '{frame_selector}' found"
                            )
                        
                        frame = await iframe_element.content_frame()
                        if not frame:
                            return browser_instance.build_action_result(
                                False,
                                f"Could not access frame content: {frame_selector}",
                                None,
                                "",
                                "",
                                {},
                                error=f"Failed to access frame content for '{frame_selector}'"
                            )
                    
                    browser_instance.current_frame = frame
                
                success = True
                message = f"Switched to frame: {frame_selector}"
                error = ""
            except Exception as frame_error:
                print(f"Error switching to frame: {frame_error}")
                traceback.print_exc()
                success = False
                message = f"Failed to switch to frame: {frame_selector}"
                error = str(frame_error)
            
            # Get updated state after action
            context = await browser_instance.get_current_context()
            dom_state, screenshot, elements, metadata = await DOMHandler.get_updated_browser_state(context, "switch_to_frame")
            
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
            print(f"Unexpected error in switch_to_frame: {e}")
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
    
    @staticmethod
    async def switch_to_main_frame(browser_instance, _: NoParamsAction = Body(...)):
        """Switch back to the main frame"""
        try:
            # Reset the current frame
            browser_instance.current_frame = None
            
            page = await browser_instance.get_current_page()
            
            success = True
            message = "Switched to main frame"
            error = ""
            
            # Get updated state after action
            dom_state, screenshot, elements, metadata = await DOMHandler.get_updated_browser_state(page, "switch_to_main_frame")
            
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
            print(f"Unexpected error in switch_to_main_frame: {e}")
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
