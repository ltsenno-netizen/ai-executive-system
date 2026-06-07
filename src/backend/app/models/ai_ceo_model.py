from pydantic import BaseModel, Field


class AICeoPersona(BaseModel):
    aggressiveness: float = Field(..., ge=0.0, le=1.0)
    risk_tolerance: float = Field(..., ge=0.0, le=1.0)
    brand_priority: float = Field(..., ge=0.0, le=1.0)
    short_term_focus: float = Field(..., ge=0.0, le=1.0)
    long_term_focus: float = Field(..., ge=0.0, le=1.0)