"""
Dialog handling actions for browser automation.
This module provides functionality for handling browser dialogs such as alerts, confirms, and prompts.
"""
import traceback
from typing import Dict, Any

from fastapi import Body
from ..models.action_models import NoParamsAction
from ..core.dom_handler import DOMHandler

class DialogActions:
    """Dialog handling browser actions"""
    
    @staticmethod
    async def accept_dialog(browser_instance, _: NoParamsAction = Body(...)):
        """Accept any dialog (alert, confirm, prompt)"""
        try:
            page = await browser_instance.get_current_page()
            
            try:
                # Set up dialog handler to accept dialogs
                await page.evaluate("""
                () => {
                    // Override window.alert
                    window.original_alert = window.alert;
                    window.alert = function(message) {
                        console.log('Alert accepted: ' + message);
                        return undefined;
                    };
                    
                    // Override window.confirm
                    window.original_confirm = window.confirm;
                    window.confirm = function(message) {
                        console.log('Confirm accepted: ' + message);
                        return true;
                    };
                    
                    // Override window.prompt
                    window.original_prompt = window.prompt;
                    window.prompt = function(message, default_value) {
                        console.log('Prompt accepted: ' + message);
                        return default_value || '';
                    };
                }
                """)
                
                success = True
                message = "Dialog handling set to accept dialogs"
                error = ""
            except Exception as dialog_error:
                print(f"Error setting up dialog handling: {dialog_error}")
                traceback.print_exc()
                success = False
                message = "Failed to set up dialog handling"
                error = str(dialog_error)
            
            # Get updated state after action
            dom_state, screenshot, elements, metadata = await DOMHandler.get_updated_browser_state(page, "accept_dialog")
            
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
            print(f"Unexpected error in accept_dialog: {e}")
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
    async def dismiss_dialog(browser_instance, _: NoParamsAction = Body(...)):
        """Dismiss any dialog (alert, confirm, prompt)"""
        try:
            page = await browser_instance.get_current_page()
            
            try:
                # Set up dialog handler to dismiss dialogs
                await page.evaluate("""
                () => {
                    // Override window.alert
                    window.original_alert = window.alert;
                    window.alert = function(message) {
                        console.log('Alert dismissed: ' + message);
                        return undefined;
                    };
                    
                    // Override window.confirm
                    window.original_confirm = window.confirm;
                    window.confirm = function(message) {
                        console.log('Confirm dismissed: ' + message);
                        return false;
                    };
                    
                    // Override window.prompt
                    window.original_prompt = window.prompt;
                    window.prompt = function(message, default_value) {
                        console.log('Prompt dismissed: ' + message);
                        return null;
                    };
                }
                """)
                
                success = True
                message = "Dialog handling set to dismiss dialogs"
                error = ""
            except Exception as dialog_error:
                print(f"Error setting up dialog handling: {dialog_error}")
                traceback.print_exc()
                success = False
                message = "Failed to set up dialog handling"
                error = str(dialog_error)
            
            # Get updated state after action
            dom_state, screenshot, elements, metadata = await DOMHandler.get_updated_browser_state(page, "dismiss_dialog")
            
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
            print(f"Unexpected error in dismiss_dialog: {e}")
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
