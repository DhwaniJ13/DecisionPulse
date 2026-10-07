"""Output contract shared with Member 2 (AI), Member 3 (backend) and the frontend."""
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel

Level = Literal["HIGH", "MEDIUM", "LOW"]


class EvidenceItem(BaseModel):
    id: int
    name: str
    evidence_type: str
    status: str
    role: str  # CRITICAL | SUPPORTING


class AffectedDecision(BaseModel):
    decision_id: int
    title: str
    decision_type: str
    entity_name: str
    status: str
    owner_name: str
    owner_email: str
    criticality: int
    impact_type: Literal["DIRECT", "INDIRECT"]
    depth: int                       # 0 = direct, 1+ = through other decisions
    impact_score: float              # 0..1  (engine's rule-based score)
    preliminary_impact_level: Level  # Member 2's AI gives the FINAL risk level
    trigger_role: Optional[str]      # role of the changed evidence for this decision
    path: list[str]                  # human-readable propagation path
    reason: str                      # deterministic explanation (AI can improve it)
    evidence: list[EvidenceItem]     # all evidence this decision relies on
    valid_evidence_count: int
    total_evidence_count: int


class ChangeInfo(BaseModel):
    change_id: int
    evidence_id: int
    evidence_name: str
    evidence_type: str
    entity_name: str
    change_type: str
    old_status: str
    new_status: str
    old_value: Optional[float]
    new_value: Optional[float]
    severity: float
    detected_at: datetime


class ImpactReport(BaseModel):
    change: ChangeInfo
    affected_decisions: list[AffectedDecision]  # sorted, highest score first
    summary: dict
