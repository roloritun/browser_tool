"""
Action model definitions for browser automation.
These models represent the different actions that can be performed in the browser.
"""
from pydantic import BaseModel
from typing import Optional, List, Dict

class Position(BaseModel):
    x: int
    y: int

class ClickElementAction(BaseModel):
    index: int

class ClickCoordinatesAction(BaseModel):
    x: int
    y: int

class GoToUrlAction(BaseModel):
    url: str

class InputTextAction(BaseModel):
    index: int
    text: str

class ScrollAction(BaseModel):
    amount: Optional[int] = None

class SendKeysAction(BaseModel):
    keys: str

class SearchGoogleAction(BaseModel):
    query: str

class SwitchTabAction(BaseModel):
    page_id: int

class OpenTabAction(BaseModel):
    url: str

class CloseTabAction(BaseModel):
    page_id: int

class NoParamsAction(BaseModel):
    pass

class DragDropAction(BaseModel):
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

class DoneAction(BaseModel):
    success: bool = True
    text: str = ""
