from __future__ import annotations
from typing import List
from pydantic import BaseModel, Field

class OrganizationUnit(BaseModel):
    name: str
    headcount: int
    children: List[OrganizationUnit] = Field(default_factory=list)

    model_config = {
        "extra": "forbid"
    }

    def dict(self, *args, **kwargs):
        return super().model_dump(*args, **kwargs)

class OrganizationModel(BaseModel):
    company_name: str
    ceo: str
    structure: OrganizationUnit

    model_config = {
        "extra": "forbid"
    }
