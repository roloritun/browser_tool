"""
Action model definitions for browser automation.
These models represent the different actions that can be performed in the browser.
"""
from pydantic import BaseModel, Field
from typing import Optional

class Position(BaseModel):
    x: int = Field(..., description="X coordinate position")
    y: int = Field(..., description="Y coordinate position")

class ClickElementAction(BaseModel):
    selector: Optional[str] = Field(None, description="CSS selector for target element")
    index: Optional[int] = Field(0, description="Element index if multiple matches (0-based)")

class ClickCoordinatesAction(BaseModel):
    x: int = Field(..., description="X coordinate for click")
    y: int = Field(..., description="Y coordinate for click")

class GoToUrlAction(BaseModel):
    url: str = Field(..., description="URL to navigate to")

class InputTextAction(BaseModel):
    selector: Optional[str] = Field(None, description="CSS selector for input element")
    text: str = Field(..., description="Text to input")
    index: Optional[int] = Field(0, description="Element index if multiple matches (0-based)")

class ScrollAction(BaseModel):
    amount: Optional[int] = Field(None, description="Scroll amount in pixels (positive=down, negative=up)")

class SendKeysAction(BaseModel):
    keys: str = Field(..., description="Keys to send (e.g., 'Enter', 'Tab', 'Escape')")

class SearchGoogleAction(BaseModel):
    query: str = Field(..., description="Search query to execute on Google")

class SwitchTabAction(BaseModel):
    tab_index: int = Field(..., description="Primary tab index to switch to")
    page_id: Optional[int] = Field(None, description="Alternative page ID (fallback)")

class OpenTabAction(BaseModel):
    url: str = Field(..., description="URL to open in new tab")

class CloseTabAction(BaseModel):
    tab_index: int = Field(..., description="Primary tab index to close")
    page_id: Optional[int] = Field(None, description="Alternative page ID (fallback)")

class NoParamsAction(BaseModel):
    pass

class DragDropAction(BaseModel):
    source_selector: Optional[str] = Field(None, description="CSS selector for source element")
    target_selector: Optional[str] = Field(None, description="CSS selector for target element")
    element_source: Optional[str] = Field(None, description="Source element description")
    element_target: Optional[str] = Field(None, description="Target element description")
    element_source_offset: Optional[Position] = Field(None, description="Offset position within source element")
    element_target_offset: Optional[Position] = Field(None, description="Offset position within target element")
    coord_source_x: Optional[int] = Field(None, description="Source X coordinate for drag start")
    coord_source_y: Optional[int] = Field(None, description="Source Y coordinate for drag start")
    coord_target_x: Optional[int] = Field(None, description="Target X coordinate for drag end")
    coord_target_y: Optional[int] = Field(None, description="Target Y coordinate for drag end")
    steps: Optional[int] = Field(10, description="Number of steps for drag animation")
    delay_ms: Optional[int] = Field(5, description="Delay between steps in milliseconds")

class SwitchToFrameAction(BaseModel):
    frame_selector: str = Field(..., description="CSS selector, name, or ID of the frame to switch to")

class SetNetworkConditionsAction(BaseModel):
    offline: Optional[bool] = Field(False, description="Simulate offline network condition")
    latency: Optional[int] = Field(0, description="Additional network latency in milliseconds")
    downloadThroughput: Optional[int] = Field(-1, description="Download throughput in bytes per second (-1 for no limit)")
    uploadThroughput: Optional[int] = Field(-1, description="Upload throughput in bytes per second (-1 for no limit)")

class ScrollToTextAction(BaseModel):
    text: str = Field(..., description="Text content to scroll to on the page")

class SetCookieAction(BaseModel):
    name: str = Field(..., description="Cookie name")
    value: str = Field(..., description="Cookie value")
    domain: Optional[str] = Field(None, description="Cookie domain")
    path: Optional[str] = Field("/", description="Cookie path")
    expires: Optional[int] = Field(None, description="Cookie expiration timestamp")
    httpOnly: Optional[bool] = Field(False, description="HTTP-only cookie flag")
    secure: Optional[bool] = Field(False, description="Secure cookie flag (HTTPS only)")
    sameSite: Optional[str] = Field(None, description="SameSite cookie attribute")

class WaitAction(BaseModel):
    # Wait action uses the same fields as NoParamsAction
    pass

class ExtractContentAction(BaseModel):
    goal: Optional[str] = Field(None, description="Specific goal or focus for content extraction")

class PDFOptionsAction(BaseModel):
    format: Optional[str] = Field("A4", description="PDF page format (A4, Letter, etc.)")
    printBackground: Optional[bool] = Field(True, description="Include background graphics in PDF")
    displayHeaderFooter: Optional[bool] = Field(False, description="Display header and footer in PDF")
    headerTemplate: Optional[str] = Field(None, description="HTML template for PDF header")
    footerTemplate: Optional[str] = Field(None, description="HTML template for PDF footer")

class GetDropdownOptionsAction(BaseModel):
    index: int = Field(..., description="Index of the dropdown element (0-based)")

class SelectDropdownOptionAction(BaseModel):
    index: int = Field(..., description="Index of the dropdown element (0-based)")
    option_text: str = Field(..., description="Text content of the option to select")

class DoneAction(BaseModel):
    success: bool = Field(True, description="Whether the task completed successfully")
    text: str = Field("", description="Additional completion message or result")
