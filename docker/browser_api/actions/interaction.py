"""
Element interaction actions for browser automation.
This module provides functionality for interacting with elements on the page.
"""
import traceback
from typing import Dict, Any

from fastapi import Body
from ..models.action_models import ClickElementAction, ClickCoordinatesAction, InputTextAction, SendKeysAction
from ..core.dom_handler import DOMHandler

class InteractionActions:
    """Element interaction browser actions"""
    
    @staticmethod
    async def click_element(browser_instance, action: ClickElementAction = Body(...)):
        """Click on an element by index"""
        try:
            index = action.index
            context = await browser_instance.get_current_context()
            
            # Get DOM state to find the element
            dom_state = await DOMHandler.get_dom_state(context)
            
            # Find the element in the selector map
            if index not in dom_state.selector_map:
                return browser_instance.build_action_result(
                    False,
                    f"Element with index {index} not found",
                    dom_state,
                    "",
                    "",
                    {},
                    error=f"Element with index {index} not found"
                )
            
            element = dom_state.selector_map[index]
            
            # If the element is an input, might need to focus first
            is_input = element.tag_name in ["input", "textarea", "select"]
            
            # Try to find a good selector for this element
            selector = None
            
            # Try to use ID first if available
            if "id" in element.attributes and element.attributes["id"]:
                selector = f"#{element.attributes['id']}"
            
            # Try name attribute next
            elif "name" in element.attributes and element.attributes["name"]:
                selector = f"[name='{element.attributes['name']}']"
                
            # Use element coordinates as fallback
            coordinates = None
            if element.page_coordinates:
                coordinates = {
                    "x": element.page_coordinates.x + (element.page_coordinates.width / 2),
                    "y": element.page_coordinates.y + (element.page_coordinates.height / 2)
                }
            
            try:
                if selector:
                    print(f"Clicking element with selector: {selector}")
                    # Focus first for input elements
                    if is_input:
                        try:
                            await context.focus(selector, timeout=5000)
                        except Exception as focus_error:
                            print(f"Error focusing element: {focus_error}")
                    
                    # Then click
                    await context.click(selector, timeout=5000)
                elif coordinates:
                    print(f"Clicking element at coordinates: {coordinates}")
                    await context.mouse.click(coordinates["x"], coordinates["y"])
                else:
                    return browser_instance.build_action_result(
                        False,
                        f"Could not find a way to click element with index {index}",
                        dom_state,
                        "",
                        "",
                        {},
                        error=f"No selector or coordinates available for element {index}"
                    )
                
                success = True
                message = f"Clicked element with index {index}"
                error = ""
            except Exception as click_error:
                print(f"Error clicking element: {click_error}")
                traceback.print_exc()
                
                # Try fallback to coordinates if selector failed
                if selector and coordinates:
                    try:
                        print(f"Trying fallback click at coordinates: {coordinates}")
                        await context.mouse.click(coordinates["x"], coordinates["y"])
                        success = True
                        message = f"Clicked element with index {index} using coordinates fallback"
                        error = ""
                    except Exception as fallback_error:
                        print(f"Error in fallback click: {fallback_error}")
                        success = False
                        message = f"Failed to click element with index {index}"
                        error = str(click_error)
                else:
                    success = False
                    message = f"Failed to click element with index {index}"
                    error = str(click_error)
            
            # Get updated state after action
            page = await browser_instance.get_current_page()
            dom_state, screenshot, elements, metadata = await DOMHandler.get_updated_browser_state(page, "click_element")
            
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
            print(f"Unexpected error in click_element: {e}")
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
    async def click_coordinates(browser_instance, action: ClickCoordinatesAction = Body(...)):
        """Click at specific coordinates on the page"""
        try:
            x = action.x
            y = action.y
            context = await browser_instance.get_current_context()
            
            try:
                # Click at the specified coordinates
                await context.mouse.click(x, y)
                
                success = True
                message = f"Clicked at coordinates ({x}, {y})"
                error = ""
            except Exception as click_error:
                print(f"Error clicking at coordinates ({x}, {y}): {click_error}")
                traceback.print_exc()
                success = False
                message = f"Failed to click at coordinates ({x}, {y})"
                error = str(click_error)
            
            # Get updated state after action
            page = await browser_instance.get_current_page()
            dom_state, screenshot, elements, metadata = await DOMHandler.get_updated_browser_state(page, "click_coordinates")
            
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
            print(f"Unexpected error in click_coordinates: {e}")
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
    async def input_text(browser_instance, action: InputTextAction = Body(...)):
        """Input text into an element by index"""
        try:
            index = action.index
            text = action.text
            context = await browser_instance.get_current_context()
            
            # Get DOM state to find the element
            dom_state = await DOMHandler.get_dom_state(context)
            
            # Find the element in the selector map
            if index not in dom_state.selector_map:
                return browser_instance.build_action_result(
                    False,
                    f"Element with index {index} not found",
                    dom_state,
                    "",
                    "",
                    {},
                    error=f"Element with index {index} not found"
                )
            
            element = dom_state.selector_map[index]
            
            # Try to find a good selector for this element
            selector = None
            
            # Try to use ID first if available
            if "id" in element.attributes and element.attributes["id"]:
                selector = f"#{element.attributes['id']}"
            
            # Try name attribute next
            elif "name" in element.attributes and element.attributes["name"]:
                selector = f"[name='{element.attributes['name']}']"
                
            # Use element coordinates as fallback
            coordinates = None
            if element.page_coordinates:
                coordinates = {
                    "x": element.page_coordinates.x + (element.page_coordinates.width / 2),
                    "y": element.page_coordinates.y + (element.page_coordinates.height / 2)
                }
            
            try:
                if selector:
                    print(f"Inputting text into element with selector: {selector}")
                    
                    # First clear the field
                    await context.fill(selector, "", timeout=5000)
                    
                    # Then input the text
                    await context.fill(selector, text, timeout=5000)
                elif coordinates:
                    print(f"Clicking at coordinates for text input: {coordinates}")
                    
                    # Click to focus
                    await context.mouse.click(coordinates["x"], coordinates["y"])
                    
                    # Type the text
                    await context.keyboard.type(text)
                else:
                    return browser_instance.build_action_result(
                        False,
                        f"Could not find a way to input text into element with index {index}",
                        dom_state,
                        "",
                        "",
                        {},
                        error=f"No selector or coordinates available for element {index}"
                    )
                
                success = True
                message = f"Input text into element with index {index}"
                error = ""
            except Exception as input_error:
                print(f"Error inputting text: {input_error}")
                traceback.print_exc()
                
                # Try fallback to coordinates and keyboard if selector failed
                if selector and coordinates:
                    try:
                        print(f"Trying fallback click at coordinates for text input: {coordinates}")
                        
                        # Click to focus
                        await context.mouse.click(coordinates["x"], coordinates["y"])
                        
                        # Select all text (Ctrl+A or Command+A)
                        await context.keyboard.press("Control+a")
                        
                        # Delete existing text
                        await context.keyboard.press("Backspace")
                        
                        # Type the text
                        await context.keyboard.type(text)
                        
                        success = True
                        message = f"Input text into element with index {index} using coordinates fallback"
                        error = ""
                    except Exception as fallback_error:
                        print(f"Error in fallback text input: {fallback_error}")
                        success = False
                        message = f"Failed to input text into element with index {index}"
                        error = str(input_error)
                else:
                    success = False
                    message = f"Failed to input text into element with index {index}"
                    error = str(input_error)
            
            # Get updated state after action
            page = await browser_instance.get_current_page()
            dom_state, screenshot, elements, metadata = await DOMHandler.get_updated_browser_state(page, "input_text")
            
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
            print(f"Unexpected error in input_text: {e}")
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
    async def send_keys(browser_instance, action: SendKeysAction = Body(...)):
        """Send keyboard keys to the active element"""
        try:
            keys = action.keys
            context = await browser_instance.get_current_context()
            
            try:
                # Send the keys
                await context.keyboard.type(keys)
                
                success = True
                message = f"Sent keys: {keys}"
                error = ""
            except Exception as keys_error:
                print(f"Error sending keys: {keys_error}")
                traceback.print_exc()
                success = False
                message = f"Failed to send keys: {keys}"
                error = str(keys_error)
            
            # Get updated state after action
            page = await browser_instance.get_current_page()
            dom_state, screenshot, elements, metadata = await DOMHandler.get_updated_browser_state(page, "send_keys")
            
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
            print(f"Unexpected error in send_keys: {e}")
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
