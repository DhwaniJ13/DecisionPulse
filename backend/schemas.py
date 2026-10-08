from typing import List
from pydantic import BaseModel, Field


# ==========================================
# Base / Health Schemas
# ==========================================

class RootResponse(BaseModel):
    message: str = Field(..., example="DecisionPulse Backend is running")
    status: str = Field(..., example="healthy")


class HealthResponse(BaseModel):
    status: str = Field(..., example="ok")


# ==========================================
# Evidence & Decision Schemas
# ==========================================

class EvidenceUpdateRequest(BaseModel):
    evidence_id: str = Field(..., description="Unique identifier for the evidence", example="COMPLIANCE-101")
    new_status: str = Field(..., description="Updated status of the evidence", example="expired")


class EventInfo(BaseModel):
    evidence_id: str = Field(..., example="COMPLIANCE-101")
    new_status: str = Field(..., example="expired")


class AffectedDecision(BaseModel):
    decision_id: str = Field(..., example="DEC-101")
    decision: str = Field(..., example="Vendor Approval")
    reason: str = Field(..., example="Vendor approval depended on this compliance evidence")


class ImpactResult(BaseModel):
    evidence_id: str = Field(..., example="COMPLIANCE-101")
    status: str = Field(..., example="expired")
    affected_decisions: List[AffectedDecision] = Field(default_factory=list)
    affected_count: int = Field(..., example=1)


class AIResult(BaseModel):
    risk: str = Field(..., description="Risk level: LOW, MEDIUM, HIGH, CRITICAL", example="HIGH")
    score: int = Field(..., description="Confidence / risk score (0-100)", example=90)
    explanation: str = Field(..., example="The changed evidence affects an existing decision and requires revalidation.")
    recommendation: str = Field(..., example="Revalidate the affected vendor approval.")


class ActionResult(BaseModel):
    action: str = Field(..., description="Determined backend action: BLOCK, REVALIDATE, FLAG, NO_ACTION", example="REVALIDATE")
    notify: bool = Field(..., example=True)
    requires_revalidation: bool = Field(..., example=True)


class EvidenceUpdateResponse(BaseModel):
    event: EventInfo
    impact: ImpactResult
    ai: AIResult
    action: ActionResult
