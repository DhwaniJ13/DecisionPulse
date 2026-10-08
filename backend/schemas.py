from typing import List
from pydantic import BaseModel, Field


# ==========================================
# Base / Health Schemas
# ==========================================

class RootResponse(BaseModel):
    message: str = Field(..., examples=["DecisionPulse Backend is running"])
    status: str = Field(..., examples=["healthy"])


class HealthResponse(BaseModel):
    status: str = Field(..., examples=["ok"])


# ==========================================
# Evidence & Decision Schemas
# ==========================================

class EvidenceUpdateRequest(BaseModel):
    evidence_id: str = Field(..., description="Unique identifier for the evidence", examples=["1", "COMPLIANCE-101"])
    new_status: str = Field(..., description="Updated status of the evidence", examples=["EXPIRED", "REVOKED"])


class EventInfo(BaseModel):
    evidence_id: str = Field(..., examples=["1", "COMPLIANCE-101"])
    new_status: str = Field(..., examples=["EXPIRED"])


class AffectedDecision(BaseModel):
    decision_id: str = Field(..., examples=["DEC-1"])
    decision: str = Field(..., examples=["Approve Acme Corp as vendor"])
    reason: str = Field(..., examples=["Vendor approval depended on this compliance evidence"])


class ImpactResult(BaseModel):
    evidence_id: str = Field(..., examples=["1"])
    status: str = Field(..., examples=["EXPIRED"])
    affected_decisions: List[AffectedDecision] = Field(default_factory=list)
    affected_count: int = Field(..., examples=[1])


class AIResult(BaseModel):
    risk: str = Field(..., description="Risk level: LOW, MEDIUM, HIGH, CRITICAL", examples=["HIGH"])
    score: int = Field(..., description="Confidence / risk score (0-100)", examples=[85])
    explanation: str = Field(..., examples=["The changed evidence affects an existing decision and requires revalidation."])
    recommendation: str = Field(..., examples=["Revalidate the affected vendor approval."])


class ActionResult(BaseModel):
    action: str = Field(..., description="Determined backend action: BLOCK, REVALIDATE, FLAG, NO_ACTION", examples=["REVALIDATE"])
    notify: bool = Field(..., examples=[True])
    requires_revalidation: bool = Field(..., examples=[True])


class EvidenceUpdateResponse(BaseModel):
    event: EventInfo
    impact: ImpactResult
    ai: AIResult
    action: ActionResult
