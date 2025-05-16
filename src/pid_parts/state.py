"""
State management for PID parts extraction.

This module defines the data models used to track the state of extracted items
and the overall application state.
"""

from pydantic import BaseModel
from typing import Optional, Tuple, Dict


class Item(BaseModel):
    """Represents a single extracted item from a PID drawing.

    Each item has identifying information, position data, and metadata about
    the extraction process.
    """

    tag: str
    type: str
    size: Optional[str] = None
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    conf: float  # Confidence score from the detection model
    status: str = "INGESTED"  # Tracks the processing state of the item


class State(BaseModel):
    """Maintains the overall application state during processing.

    Tracks all extracted items, generated markdown, and any pending questions
    that need resolution.
    """

    items: Dict[str, Item] = {}  # Dictionary of items keyed by their tag
    markdown: str = ""  # Generated markdown representation of the items
    pending_questions: list[str] = []  # Questions that need user input
