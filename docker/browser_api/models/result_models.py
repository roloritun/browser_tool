"""
Browser action result models for browser automation.
These models represent the results of browser actions.
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class BrowserActionResult(BaseModel):
    success: bool = True
    message: str = ""
    error: str = ""
    
    # Extended state information
    url: Optional[str] = None
    title: Optional[str] = None
    elements: Optional[str] = None  # Formatted string of clickable elements
    screenshot_base64: Optional[str] = None
    pixels_above: int = 0
    pixels_below: int = 0
    content: Optional[str] = None
    ocr_text: Optional[str] = None  # Added field for OCR text
    
    # Additional metadata
    element_count: int = 0  # Number of interactive elements found
    interactive_elements: Optional[List[Dict[str, Any]]] = None  # Simplified list of interactive elements
    viewport_width: Optional[int] = None
    viewport_height: Optional[int] = None
    
    class Config:
        arbitrary_types_allowed = True
