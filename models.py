from pydantic import BaseModel
from typing import List, Dict, Union

class TextElement(BaseModel):
    type: str
    text: str
    className: str

class IconElement(BaseModel):
    type: str
    iconName: str
    label: str
    className: str
    iconURL: str = None

class ImageElement(BaseModel):
    type: str
    src: str
    className: str

Element = Union[TextElement, IconElement, ImageElement]

class BlockContent(BaseModel):
    elements: List[Dict]

class BlockStyle(BaseModel):
    background: str
    textColor: str

class BlockPosition(BaseModel):
    colSpan: int
    rowSpan: int

class LayoutBlock(BaseModel):
    id: str
    type: str
    position: BlockPosition
    content: BlockContent
    style: BlockStyle

class LayoutResponse(BaseModel):
    id: str
    title: str
    layout: List[LayoutBlock]
