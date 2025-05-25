"""
DOM structure models for browser automation.
These models represent the DOM structure of the browser page.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from functools import cached_property

@dataclass
class CoordinateSet:
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0

@dataclass
class ViewportInfo:
    width: int = 0
    height: int = 0
    scroll_x: int = 0
    scroll_y: int = 0

@dataclass
class HashedDomElement:
    tag_name: str
    attributes: Dict[str, str]
    is_visible: bool
    page_coordinates: Optional[CoordinateSet] = None

@dataclass
class DOMBaseNode:
    is_visible: bool
    parent: Optional['DOMElementNode'] = None

@dataclass
class DOMTextNode(DOMBaseNode):
    text: str = field(default="")
    type: str = 'TEXT_NODE'
    
    def has_parent_with_highlight_index(self) -> bool:
        current = self.parent
        while current is not None:
            if current.highlight_index is not None:
                return True
            current = current.parent
        return False

@dataclass
class DOMElementNode(DOMBaseNode):
    tag_name: str = field(default="")
    xpath: str = field(default="")
    attributes: Dict[str, str] = field(default_factory=dict)
    children: List['DOMBaseNode'] = field(default_factory=list)
    
    is_interactive: bool = False
    is_top_element: bool = False
    is_in_viewport: bool = False
    shadow_root: bool = False
    highlight_index: Optional[int] = None
    viewport_coordinates: Optional[CoordinateSet] = None
    page_coordinates: Optional[CoordinateSet] = None
    viewport_info: Optional[ViewportInfo] = None
    
    def __repr__(self) -> str:
        tag_str = f'<{self.tag_name}'
        for key, value in self.attributes.items():
            tag_str += f' {key}="{value}"'
        tag_str += '>'
        
        extras = []
        if self.is_interactive:
            extras.append('interactive')
        if self.is_top_element:
            extras.append('top')
        if self.highlight_index is not None:
            extras.append(f'highlight:{self.highlight_index}')
        
        if extras:
            tag_str += f' [{", ".join(extras)}]'
            
        return tag_str
    
    @cached_property
    def hash(self) -> HashedDomElement:
        return HashedDomElement(
            tag_name=self.tag_name,
            attributes=self.attributes,
            is_visible=self.is_visible,
            page_coordinates=self.page_coordinates
        )
    
    def get_all_text_till_next_clickable_element(self, max_depth: int = -1) -> str:
        text_parts = []
        
        def collect_text(node: DOMBaseNode, current_depth: int) -> None:
            if max_depth != -1 and current_depth > max_depth:
                return
                
            if isinstance(node, DOMElementNode) and node != self and node.highlight_index is not None:
                return
                
            if isinstance(node, DOMTextNode):
                text_parts.append(node.text)
            elif isinstance(node, DOMElementNode):
                for child in node.children:
                    collect_text(child, current_depth + 1)
                    
        collect_text(self, 0)
        return '\n'.join(text_parts).strip()
    
    def clickable_elements_to_string(self, include_attributes: List[str] | None = None) -> str:
        """Convert the processed DOM content to HTML."""
        formatted_text = []
        
        def process_node(node: DOMBaseNode, depth: int) -> None:
            if isinstance(node, DOMElementNode):
                # Add element with highlight_index
                if node.highlight_index is not None:
                    attributes_str = ''
                    text = node.get_all_text_till_next_clickable_element()
                    
                    # Process attributes for display
                    display_attributes = []
                    if include_attributes:
                        for key, value in node.attributes.items():
                            if key in include_attributes and value and value != node.tag_name:
                                if text and value in text:
                                    continue  # Skip if attribute value is already in the text
                                display_attributes.append(str(value))
                    
                    attributes_str = ';'.join(display_attributes)
                    
                    # Build the element string
                    line = f'[{node.highlight_index}]<{node.tag_name}'
                    
                    # Add important attributes for identification
                    for attr_name in ['id', 'href', 'name', 'value', 'type']:
                        if attr_name in node.attributes and node.attributes[attr_name]:
                            line += f' {attr_name}="{node.attributes[attr_name]}"'
                    
                    # Add the text content if available
                    if text:
                        line += f'> {text}'
                    elif attributes_str:
                        line += f'> {attributes_str}'
                    else:
                        # If no text and no attributes, use the tag name
                        line += f'> {node.tag_name.upper()}'
                    
                    line += ' </>'
                    formatted_text.append(line)
                
                # Process children regardless
                for child in node.children:
                    process_node(child, depth + 1)
                    
            elif isinstance(node, DOMTextNode):
                # Add text only if it doesn't have a highlighted parent
                if not node.has_parent_with_highlight_index() and node.is_visible:
                    if node.text and node.text.strip():
                        formatted_text.append(node.text)
                    
        process_node(self, 0)
        result = '\n'.join(formatted_text)
        return result if result.strip() else "No interactive elements found"

@dataclass
class DOMState:
    element_tree: DOMElementNode
    selector_map: Dict[int, DOMElementNode]
    url: str = ""
    title: str = ""
    pixels_above: int = 0
    pixels_below: int = 0
