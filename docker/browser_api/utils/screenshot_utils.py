"""
Screenshot utilities for browser automation.
This module provides functionality for taking and manipulating screenshots.
"""
import base64
import os
import random
from datetime import datetime
import io
from PIL import Image
import pytesseract

class ScreenshotUtils:
    """Utilities for working with screenshots"""
    
    @staticmethod
    async def take_screenshot(page) -> str:
        """Take a screenshot and return as base64 encoded string"""
        try:
            screenshot_bytes = await page.screenshot(type='jpeg', quality=60, full_page=False)
            return base64.b64encode(screenshot_bytes).decode('utf-8')
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            # Return an empty string rather than failing
            return ""
    
    @staticmethod
    async def save_screenshot_to_file(page, screenshot_dir) -> str:
        """Take a screenshot and save to file, returning the path"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            random_id = random.randint(1000, 9999)
            filename = f"screenshot_{timestamp}_{random_id}.jpg"
            filepath = os.path.join(screenshot_dir, filename)
            
            await page.screenshot(path=filepath, type='jpeg', quality=60, full_page=False)
            return filepath
        except Exception as e:
            print(f"Error saving screenshot: {e}")
            return ""
    
    @staticmethod
    def extract_text_from_image(screenshot_base64: str) -> str:
        """Extract text from a screenshot using OCR"""
        try:
            # Decode base64 image
            image_data = base64.b64decode(screenshot_base64)
            image = Image.open(io.BytesIO(image_data))
            
            # Use pytesseract to extract text
            text = pytesseract.image_to_string(image)
            
            # Clean up the text
            text = text.strip()
            
            return text
        except Exception as e:
            print(f"Error extracting text from image: {e}")
            import traceback
            traceback.print_exc()
            return ""
            print(f"Error extracting text from image: {e}")
            return ""
            return text
        except Exception as e:
            print(f"Error extracting text from image: {e}")
            return ""
