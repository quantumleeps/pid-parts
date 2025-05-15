# src/pid_parts/state.py
from pydantic import BaseModel
from typing import Optional, Tuple, Dict


class Item(BaseModel):
    tag: str
    type: str
    size: Optional[str] = None
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    conf: float
    status: str = "INGESTED"


class State(BaseModel):
    items: Dict[str, Item] = {}
    markdown: str = ""
    pending_questions: list[str] = []
