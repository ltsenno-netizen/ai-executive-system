from datetime import datetime
from enum import Enum
from typing import List
from uuid import uuid4

from pydantic import BaseModel, Field


class MetaDimension(str, Enum):
    INTENT = "INTENT"
    AGENTS = "AGENTS"
    AUTONOMOUS = "AUTONOMOUS"
    FRONTIER = "FRONTIER"
    CONSCIOUSNESS = "CONSCIOUSNESS"
    EVOLUTION = "EVOLUTION"
    NARRATIVE = "NARRATIVE"
    MEMORY = "MEMORY"


class MetaScore(BaseModel):
    dimension: MetaDimension
    score: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    rationale: str


class MetaBias(BaseModel):
    name: str
    description: str
    severity: float = Field(..., ge=0.0, le=1.0)
    affected_dimensions: List[MetaDimension]


class MetaCognitionReport(BaseModel):
    report_id: str = Field(default_factory=lambda: str(uuid4()))
    overall_score: float = Field(..., ge=0.0, le=1.0)
    scores: List[MetaScore]
    biases: List[MetaBias]
    recommendations: List[str]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
