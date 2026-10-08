from pydantic import BaseModel, Field
from typing import Literal


class InvestigationResult(BaseModel):
    decision_id: str

    impact_level: Literal[
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL"
    ]

    risk_score: int = Field(ge=0, le=100)

    impact_summary: str
    reasoning: str

    affected_factors: list[str]

    recommended_action: Literal[
        "NO_ACTION",
        "MONITOR",
        "REVIEW",
        "REVALIDATE",
        "HOLD",
        "BLOCK"
    ]

    confidence: float = Field(ge=0, le=1)

    evidence_sufficiency: Literal[
        "SUFFICIENT",
        "PARTIAL",
        "INSUFFICIENT"
    ]