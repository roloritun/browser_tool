"""
Drag and drop actions for browser automation.
This module provides functionality for drag and drop operations.
"""
import asyncio
import traceback

from fastapi import Body
from browser_api.models.action_models import DragDropAction
from browser_api.core.dom_handler import DOMHandler

class DragDropActions:
    """Drag and drop browser actions"""
    
    @staticmethod
    async def drag_drop(browser_instance, action: DragDropAction = Body(...)):
        """Perform a drag and drop operation"""
        try:
            context = await browser_instance.get_current_context()
            
            # Get source and target, supporting both field name variants
            source_selector = action.source_selector or action.element_source
            target_selector = action.target_selector or action.element_target
            
            # We need either element selectors or coordinates
            if (not source_selector and (action.coord_source_x is None or action.coord_source_y is None)) or \
               (not target_selector and (action.coord_target_x is None or action.coord_target_y is None)):
                return browser_instance.build_action_result(
                    False,
                    "Missing source or target for drag and drop",
                    None,
                    "",
                    "",
                    {},
                    error="You must provide either element selectors or coordinates for both source and target"
                )
            
            # Get the DOM state for element lookup
            if source_selector or target_selector:
                dom_state = await DOMHandler.get_dom_state(context)
            
            # Determine source coordinates
            source_x = None
            source_y = None
            
            if source_selector:
                # Find the element in the selector map
                try:
                    source_index = int(source_selector)
                    if source_index not in dom_state.selector_map:
                        return browser_instance.build_action_result(
                            False,
                            f"Source element with index {source_index} not found",
                            dom_state,
                            "",
                            "",
                            {},
                            error=f"Source element with index {source_index} not found"
                        )
                    
                    source_element = dom_state.selector_map[source_index]
                    
                    if source_element.page_coordinates:
                        # Use the element's coordinates
                        source_x = source_element.page_coordinates.x + (source_element.page_coordinates.width / 2)
                        source_y = source_element.page_coordinates.y + (source_element.page_coordinates.height / 2)
                        
                        # Apply offset if provided
                        if action.element_source_offset:
                            source_x += action.element_source_offset.x
                            source_y += action.element_source_offset.y
                    else:
                        return browser_instance.build_action_result(
                            False,
                            f"Could not determine coordinates for source element {source_index}",
                            dom_state,
                            "",
                            "",
                            {},
                            error=f"No coordinates available for source element {source_index}"
                        )
                except ValueError:
                    # Not a numeric index, try as a selector
                    try:
                        element = await context.query_selector(source_selector)
                        if not element:
                            return browser_instance.build_action_result(
                                False,
                                f"Source element with selector '{source_selector}' not found",
                                dom_state,
                                "",
                                "",
                                {},
                                error=f"Source element with selector '{source_selector}' not found"
                            )
                        
                        # Get element's bounding box
                        bounding_box = await element.bounding_box()
                        if not bounding_box:
                            return browser_instance.build_action_result(
                                False,
                                f"Could not determine bounding box for source element '{source_selector}'",
                                dom_state,
                                "",
                                "",
                                {},
                                error=f"No bounding box available for source element '{source_selector}'"
                            )
                        
                        # Use the element's center coordinates
                        source_x = bounding_box["x"] + (bounding_box["width"] / 2)
                        source_y = bounding_box["y"] + (bounding_box["height"] / 2)
                        
                        # Apply offset if provided
                        if action.element_source_offset:
                            source_x += action.element_source_offset.x
                            source_y += action.element_source_offset.y
                    except Exception as selector_error:
                        return browser_instance.build_action_result(
                            False,
                            f"Error finding source element with selector '{source_selector}'",
                            dom_state,
                            "",
                            "",
                            {},
                            error=str(selector_error)
                        )
            else:
                # Use provided coordinates
                source_x = action.coord_source_x
                source_y = action.coord_source_y
            
            # Determine target coordinates
            target_x = None
            target_y = None
            
            if target_selector:
                # Find the element in the selector map
                try:
                    target_index = int(target_selector)
                    if target_index not in dom_state.selector_map:
                        return browser_instance.build_action_result(
                            False,
                            f"Target element with index {target_index} not found",
                            dom_state,
                            "",
                            "",
                            {},
                            error=f"Target element with index {target_index} not found"
                        )
                    
                    target_element = dom_state.selector_map[target_index]
                    
                    if target_element.page_coordinates:
                        # Use the element's coordinates
                        target_x = target_element.page_coordinates.x + (target_element.page_coordinates.width / 2)
                        target_y = target_element.page_coordinates.y + (target_element.page_coordinates.height / 2)
                        
                        # Apply offset if provided
                        if action.element_target_offset:
                            target_x += action.element_target_offset.x
                            target_y += action.element_target_offset.y
                    else:
                        return browser_instance.build_action_result(
                            False,
                            f"Could not determine coordinates for target element {target_index}",
                            dom_state,
                            "",
                            "",
                            {},
                            error=f"No coordinates available for target element {target_index}"
                        )
                except ValueError:
                    # Not a numeric index, try as a selector
                    try:
                        element = await context.query_selector(target_selector)
                        if not element:
                            return browser_instance.build_action_result(
                                False,
                                f"Target element with selector '{target_selector}' not found",
                                dom_state,
                                "",
                                "",
                                {},
                                error=f"Target element with selector '{target_selector}' not found"
                            )
                        
                        # Get element's bounding box
                        bounding_box = await element.bounding_box()
                        if not bounding_box:
                            return browser_instance.build_action_result(
                                False,
                                f"Could not determine bounding box for target element '{target_selector}'",
                                dom_state,
                                "",
                                "",
                                {},
                                error=f"No bounding box available for target element '{target_selector}'"
                            )
                        
                        # Use the element's center coordinates
                        target_x = bounding_box["x"] + (bounding_box["width"] / 2)
                        target_y = bounding_box["y"] + (bounding_box["height"] / 2)
                        
                        # Apply offset if provided
                        if action.element_target_offset:
                            target_x += action.element_target_offset.x
                            target_y += action.element_target_offset.y
                    except Exception as selector_error:
                        return browser_instance.build_action_result(
                            False,
                            f"Error finding target element with selector '{target_selector}'",
                            dom_state,
                            "",
                            "",
                            {},
                            error=str(selector_error)
                        )
            else:
                # Use provided coordinates
                target_x = action.coord_target_x
                target_y = action.coord_target_y
            
            try:
                # Perform the drag and drop operation
                steps = action.steps if action.steps is not None else 10
                delay_ms = action.delay_ms if action.delay_ms is not None else 5
                
                # Always use page for mouse operations (frames don't have mouse attribute)
                page = await browser_instance.get_current_page()
                
                # Move to start position
                await page.mouse.move(source_x, source_y)
                
                # Press and hold
                await page.mouse.down()
                
                # Move to target position in steps
                x_step = (target_x - source_x) / steps
                y_step = (target_y - source_y) / steps
                
                for i in range(1, steps + 1):
                    current_x = source_x + (x_step * i)
                    current_y = source_y + (y_step * i)
                    await page.mouse.move(current_x, current_y)
                    
                    # Small delay between steps for smoother drag
                    if delay_ms > 0:
                        await asyncio.sleep(delay_ms / 1000)
                
                # Release at target position
                await page.mouse.up()
                
                success = True
                message = "Drag and drop operation completed"
                error = ""
            except Exception as drag_error:
                print(f"Error performing drag and drop: {drag_error}")
                traceback.print_exc()
                success = False
                message = "Failed to perform drag and drop operation"
                error = str(drag_error)
            
            # Get updated state after action
            page = await browser_instance.get_current_page()
            dom_state, screenshot, elements, metadata = await DOMHandler.get_updated_browser_state(page, "drag_drop")
            
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
            print(f"Unexpected error in drag_drop: {e}")
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
