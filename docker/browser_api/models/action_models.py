"""
Action model definitions for browser automation.
These models represent the different actions that can be performed in the browser.
"""
from pydantic import BaseModel
from typing import Optional

class Position(BaseModel):
    x: int
    y: int

class ClickElementAction(BaseModel):
    selector: Optional[str] = None
    index: Optional[int] = 0

class ClickCoordinatesAction(BaseModel):
    x: int
    y: int

class GoToUrlAction(BaseModel):
    url: str

class InputTextAction(BaseModel):
    selector: Optional[str] = None
    text: str
    index: Optional[int] = 0

class ScrollAction(BaseModel):
    amount: Optional[int] = None

class SendKeysAction(BaseModel):
    keys: str

class SearchGoogleAction(BaseModel):
    query: str

class SwitchTabAction(BaseModel):
    tab_index: int
    page_id: Optional[int] = None

class OpenTabAction(BaseModel):
    url: str

class CloseTabAction(BaseModel):
    tab_index: int
    page_id: Optional[int] = None

class NoParamsAction(BaseModel):
    pass

class DragDropAction(BaseModel):
    source_selector: Optional[str] = None
    target_selector: Optional[str] = None
    element_source: Optional[str] = None
    element_target: Optional[str] = None
    element_source_offset: Optional[Position] = None
    element_target_offset: Optional[Position] = None
    coord_source_x: Optional[int] = None
    coord_source_y: Optional[int] = None
    coord_target_x: Optional[int] = None
    coord_target_y: Optional[int] = None
    steps: Optional[int] = 10
    delay_ms: Optional[int] = 5

class SwitchToFrameAction(BaseModel):
    frame_selector: str  # Can be frame name, ID, or selector

class SetNetworkConditionsAction(BaseModel):
    offline: Optional[bool] = False
    latency: Optional[int] = 0  # Additional latency in ms
    downloadThroughput: Optional[int] = -1  # Bytes per second, -1 means no limit
    uploadThroughput: Optional[int] = -1  # Bytes per second, -1 means no limit

class ScrollToTextAction(BaseModel):
    text: str

class SetCookieAction(BaseModel):
    name: str
    value: str
    domain: Optional[str] = None
    path: Optional[str] = "/"
    expires: Optional[int] = None
    httpOnly: Optional[bool] = False
    secure: Optional[bool] = False
    sameSite: Optional[str] = None

class WaitAction(BaseModel):
    # Wait action uses the same fields as NoParamsAction
    pass

class ExtractContentAction(BaseModel):
    goal: Optional[str] = None

class PDFOptionsAction(BaseModel):
    format: Optional[str] = "A4"
    printBackground: Optional[bool] = True
    displayHeaderFooter: Optional[bool] = False
    headerTemplate: Optional[str] = None
    footerTemplate: Optional[str] = None

class GetDropdownOptionsAction(BaseModel):
    index: int

class SelectDropdownOptionAction(BaseModel):
    index: int
    option_text: str

class DoneAction(BaseModel):
    success: bool = True
    text: str = ""
