"""
Scrolling actions for browser automation.
This module provides functionality for scrolling the page.
"""
import traceback

from fastapi import Body
from browser_api.models.action_models import ScrollAction, ScrollToTextAction
from browser_api.core.dom_handler import DOMHandler

class ScrollActions:
    """Scrolling-related browser actions"""
    
    @staticmethod
    async def scroll_down(browser_instance, action: ScrollAction = Body(...)):
        """Scroll down on the current page"""
        try:
            page = await browser_instance.get_current_page()
            
            # Default scroll amount
            amount = action.amount if action.amount is not None else 300
            
            try:
                # Scroll down by the specified amount
                await page.evaluate(f"window.scrollBy(0, {amount})")
                
                success = True
                message = f"Scrolled down by {amount} pixels"
                error = ""
            except Exception as scroll_error:
                print(f"Error scrolling down: {scroll_error}")
                traceback.print_exc()
                success = False
                message = "Failed to scroll down"
                error = str(scroll_error)
            
            # Get updated state after action
            dom_state, screenshot, elements, metadata = await DOMHandler.get_updated_browser_state(page, "scroll_down")
            
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
            print(f"Unexpected error in scroll_down: {e}")
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
    async def scroll_up(browser_instance, action: ScrollAction = Body(...)):
        """Scroll up on the current page"""
        try:
            page = await browser_instance.get_current_page()
            
            # Default scroll amount (negative for scrolling up)
            amount = action.amount if action.amount is not None else 300
            amount = -amount  # Make it negative for scrolling up
            
            try:
                # Scroll up by the specified amount
                await page.evaluate(f"window.scrollBy(0, {amount})")
                
                success = True
                message = f"Scrolled up by {-amount} pixels"
                error = ""
            except Exception as scroll_error:
                print(f"Error scrolling up: {scroll_error}")
                traceback.print_exc()
                success = False
                message = "Failed to scroll up"
                error = str(scroll_error)
            
            # Get updated state after action
            dom_state, screenshot, elements, metadata = await DOMHandler.get_updated_browser_state(page, "scroll_up")
            
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
            print(f"Unexpected error in scroll_up: {e}")
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
    async def scroll_to_text(browser_instance, action: ScrollToTextAction = Body(...)):
        """Scroll to text on the current page"""
        try:
            page = await browser_instance.get_current_page()
            
            # Get the text to scroll to
            text = action.text
            if not text:
                return browser_instance.build_action_result(
                    False,
                    "No text provided to scroll to",
                    None,
                    "",
                    "",
                    {},
                    error="The 'text' parameter is required"
                )
            
            try:
                # JavaScript to find and scroll to text
                scroll_result = await page.evaluate(f"""
                () => {{
                    const searchText = "{text}";
                    
                    // Function to find text in the document
                    function findTextInNode(node, searchText) {{
                        if (node.nodeType === Node.TEXT_NODE) {{
                            return node.textContent.includes(searchText);
                        }}
                        
                        if (node.nodeType === Node.ELEMENT_NODE) {{
                            for (const child of node.childNodes) {{
                                if (findTextInNode(child, searchText)) {{
                                    return true;
                                }}
                            }}
                        }}
                        
                        return false;
                    }}
                    
                    // Find all elements containing the text
                    const elements = [];
                    const walk = document.createTreeWalker(
                        document.body,
                        NodeFilter.SHOW_TEXT,
                        {{ acceptNode: node => node.textContent.includes(searchText) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT }}
                    );
                    
                    while (walk.nextNode()) {{
                        let node = walk.currentNode;
                        // Get the parent element
                        while (node && node.nodeType !== Node.ELEMENT_NODE) {{
                            node = node.parentNode;
                        }}
                        if (node) {{
                            elements.push(node);
                        }}
                    }}
                    
                    if (elements.length === 0) {{
                        return {{ success: false, message: "Text not found" }};
                    }}
                    
                    // Scroll to the first element containing the text
                    const element = elements[0];
                    const rect = element.getBoundingClientRect();
                    const y = rect.top + window.pageYOffset - 100; // Offset by 100px for better visibility
                    
                    window.scrollTo(0, y);
                    
                    return {{ 
                        success: true, 
                        message: "Scrolled to text", 
                        position: {{ x: rect.left, y: rect.top }},
                        elementInfo: {{ 
                            tag: element.tagName,
                            id: element.id,
                            className: element.className
                        }}
                    }};
                }}
                """)
                
                if scroll_result.get("success", False):
                    success = True
                    message = f"Scrolled to text: '{text}'"
                    error = ""
                else:
                    success = False
                    message = f"Failed to find text: '{text}'"
                    error = "Text not found on page"
            except Exception as scroll_error:
                print(f"Error scrolling to text: {scroll_error}")
                traceback.print_exc()
                success = False
                message = f"Failed to scroll to text: '{text}'"
                error = str(scroll_error)
            
            # Get updated state after action
            dom_state, screenshot, elements, metadata = await DOMHandler.get_updated_browser_state(page, "scroll_to_text")
            
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
            print(f"Unexpected error in scroll_to_text: {e}")
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
    async def scroll_to_top(browser_instance, action = Body(...)):
        """Scroll to the top of the page"""
        try:
            page = await browser_instance.get_current_page()
            
            try:
                # Scroll to the top of the page
                await page.evaluate("window.scrollTo(0, 0)")
                
                success = True
                message = "Scrolled to top of page"
                error = ""
            except Exception as scroll_error:
                print(f"Error scrolling to top: {scroll_error}")
                traceback.print_exc()
                success = False
                message = "Failed to scroll to top"
                error = str(scroll_error)
            
            # Get updated state after action
            dom_state, screenshot, elements, metadata = await DOMHandler.get_updated_browser_state(page, "scroll_to_top")
            
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
            print(f"Unexpected error in scroll_to_top: {e}")
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
    async def scroll_to_bottom(browser_instance, action = Body(...)):
        """Scroll to the bottom of the page"""
        try:
            page = await browser_instance.get_current_page()
            
            try:
                # Scroll to the bottom of the page
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                
                success = True
                message = "Scrolled to bottom of page"
                error = ""
            except Exception as scroll_error:
                print(f"Error scrolling to bottom: {scroll_error}")
                traceback.print_exc()
                success = False
                message = "Failed to scroll to bottom"
                error = str(scroll_error)
            
            # Get updated state after action
            dom_state, screenshot, elements, metadata = await DOMHandler.get_updated_browser_state(page, "scroll_to_bottom")
            
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
            print(f"Unexpected error in scroll_to_bottom: {e}")
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
