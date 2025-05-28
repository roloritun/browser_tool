"""
Content extraction and PDF generation actions for browser automation.
This module provides functionality for extracting content and generating PDFs.
"""
import traceback
import asyncio
from typing import Dict, Any

from fastapi import Body
from browser_api.models.action_models import NoParamsAction, ExtractContentAction
from browser_api.core.dom_handler import DOMHandler
from browser_api.utils.pdf_utils import PDFUtils
from browser_api.utils.screenshot_utils import ScreenshotUtils

class ContentActions:
    """Content extraction and PDF generation browser actions"""
    
    @staticmethod
    async def extract_content(browser_instance, action: ExtractContentAction = Body(...)):
        """Extract content from the current page"""
        try:
            page = await browser_instance.get_current_page()
            
            try:
                # Get all text content from the page
                content = await page.evaluate("""
                () => {
                    return document.body.innerText;
                }
                """)
                
                success = True
                message = "Extracted content from page"
                if action.goal:
                    message += f" (Goal: {action.goal})"
                error = ""
            except Exception as extract_error:
                print(f"Error extracting content: {extract_error}")
                traceback.print_exc()
                success = False
                message = "Failed to extract content from page"
                error = str(extract_error)
                content = ""
            
            # Get updated state after action
            dom_state, screenshot, elements, metadata = await DOMHandler.get_updated_browser_state(page, "extract_content")
            
            # Add OCR text if screenshot is available
            ocr_text = None
            if screenshot:
                try:
                    ocr_text = ScreenshotUtils.extract_text_from_image(screenshot)
                except Exception as ocr_error:
                    print(f"Error extracting OCR text: {ocr_error}")
            
            result = browser_instance.build_action_result(
                success,
                message,
                dom_state,
                screenshot,
                elements,
                metadata,
                error=error,
                content=content
            )
            
            # Add OCR text if available
            if ocr_text:
                result.ocr_text = ocr_text
                
            return result
        except Exception as e:
            print(f"Unexpected error in extract_content: {e}")
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
    async def save_pdf(browser_instance, pdf_options: Dict[str, Any] = Body(None)):
        """Save the current page as a PDF"""
        try:
            page = await browser_instance.get_current_page()
            
            try:
                # Generate PDF
                pdf_content = await PDFUtils.generate_pdf(page, pdf_options)
                
                success = pdf_content != ""
                message = "Saved page as PDF" if success else "Failed to save page as PDF"
                error = "" if success else "PDF generation failed"
            except Exception as pdf_error:
                print(f"Error saving PDF: {pdf_error}")
                traceback.print_exc()
                success = False
                message = "Failed to save page as PDF"
                error = str(pdf_error)
                pdf_content = ""
            
            # Get updated state after action
            dom_state, screenshot, elements, metadata = await DOMHandler.get_updated_browser_state(page, "save_pdf")
            
            return browser_instance.build_action_result(
                success,
                message,
                dom_state,
                screenshot,
                elements,
                metadata,
                error=error,
                content=pdf_content
            )
        except Exception as e:
            print(f"Unexpected error in save_pdf: {e}")
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
    async def generate_pdf(browser_instance, pdf_options: Dict[str, Any] = Body(None)):
        """Generate a PDF of the current page and return as base64 encoded string"""
        # This is essentially the same as save_pdf, but kept for backwards compatibility
        return await ContentActions.save_pdf(browser_instance, pdf_options)
    
    @staticmethod
    async def take_screenshot(browser_instance, action: NoParamsAction = Body(...)):
        """Take a screenshot of the current page"""
        try:
            page = await browser_instance.get_current_page()
            
            try:
                # Take a screenshot of the full page
                screenshot_bytes = await page.screenshot(full_page=True)
                
                # Convert to base64 for JSON response
                import base64
                screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
                
                success = True
                message = "Screenshot taken successfully"
                error = ""
            except Exception as screenshot_error:
                print(f"Error taking screenshot: {screenshot_error}")
                traceback.print_exc()
                success = False
                message = "Failed to take screenshot"
                error = str(screenshot_error)
                screenshot_base64 = ""
            
            # Get updated state after action
            dom_state, screenshot, elements, metadata = await DOMHandler.get_updated_browser_state(page, "take_screenshot")
            
            return browser_instance.build_action_result(
                success,
                message,
                dom_state,
                screenshot_base64,  # Use the new screenshot we just took
                elements,
                metadata,
                error=error,
                content=screenshot_base64
            )
        except Exception as e:
            print(f"Unexpected error in take_screenshot: {e}")
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
