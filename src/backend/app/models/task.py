from pydantic import BaseModel
from typing import Optional
from datetime import date

class Task(BaseModel):
    id: int
    title: str
    description: str
    priority: str  # high, medium, low
    due_date: Optional[str] = None