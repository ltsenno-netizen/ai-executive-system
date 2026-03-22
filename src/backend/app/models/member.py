from pydantic import BaseModel
from typing import Optional, List
from .task import Task

class Member(BaseModel):
    id: int
    name: str
    role: str
    notes: Optional[str] = None
    recent_tasks: List[Task] = []
    strengths: Optional[List[str]] = []
    challenges: Optional[List[str]] = []