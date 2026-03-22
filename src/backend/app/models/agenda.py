from pydantic import BaseModel
from typing import Optional, List

class Agenda(BaseModel):
    title: str
    date: Optional[str] = None
    topics: List[str] = []
    risks: List[str] = []
    decisions: List[str] = []
    notes: Optional[str] = None