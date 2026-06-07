from pydantic import BaseModel
from typing import List


class ReportSection(BaseModel):
    title: str
    body: str
    order: int


class ExecutiveReport(BaseModel):
    period: str
    title: str
    management_summary: str
    sections: List[ReportSection]
