"""Database tables. Five tables only - keep it simple."""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import ForeignKey, String, Integer, Float, DateTime, Boolean, JSON, UniqueConstraint, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)  # naive UTC everywhere


class Base(DeclarativeBase):
    pass


class Evidence(Base):
    """A piece of evidence: certificate, risk score, financial report, permission..."""
    __tablename__ = "evidence"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    evidence_type: Mapped[str] = mapped_column(String(50))   # CERTIFICATE | RISK_SCORE | FINANCIAL | ACCESS | DOCUMENT
    entity_name: Mapped[str] = mapped_column(String(200))    # e.g. vendor name
    status: Mapped[str] = mapped_column(String(30), default="VALID")  # VALID | EXPIRED | REVOKED | INVALID | DEGRADED
    value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)   # e.g. risk score
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Decision(Base):
    """A business decision that relies on evidence."""
    __tablename__ = "decisions"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(300))
    decision_type: Mapped[str] = mapped_column(String(50))   # VENDOR_APPROVAL | ACCESS_GRANT | CONTRACT | ...
    entity_name: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(30), default="APPROVED")  # APPROVED | ACTIVE | BLOCKED | CLOSED
    freshness_status: Mapped[str] = mapped_column(String(30), default="FRESH")  # FRESH | POTENTIALLY_STALE
    criticality: Mapped[int] = mapped_column(Integer, default=3)  # 1 (low) .. 5 (business critical)
    owner_name: Mapped[str] = mapped_column(String(100), default="")
    owner_email: Mapped[str] = mapped_column(String(200), default="")
    decided_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class DecisionEvidence(Base):
    """Edge: decision --relies on--> evidence."""
    __tablename__ = "decision_evidence"
    __table_args__ = (UniqueConstraint("decision_id", "evidence_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    decision_id: Mapped[int] = mapped_column(ForeignKey("decisions.id"))
    evidence_id: Mapped[int] = mapped_column(ForeignKey("evidence.id"))
    role: Mapped[str] = mapped_column(String(20), default="CRITICAL")  # CRITICAL | SUPPORTING
    decision: Mapped[Decision] = relationship()
    evidence: Mapped[Evidence] = relationship()


class DecisionDependency(Base):
    """Edge: decision --depends on--> another decision (for indirect impact)."""
    __tablename__ = "decision_dependencies"
    __table_args__ = (UniqueConstraint("decision_id", "depends_on_decision_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    decision_id: Mapped[int] = mapped_column(ForeignKey("decisions.id"))
    depends_on_decision_id: Mapped[int] = mapped_column(ForeignKey("decisions.id"))


class EvidenceChange(Base):
    """Log of every meaningful evidence change + the impact report we produced."""
    __tablename__ = "evidence_changes"
    id: Mapped[int] = mapped_column(primary_key=True)
    evidence_id: Mapped[int] = mapped_column(ForeignKey("evidence.id"))
    change_type: Mapped[str] = mapped_column(String(30))
    old_status: Mapped[str] = mapped_column(String(30))
    new_status: Mapped[str] = mapped_column(String(30))
    old_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    new_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    severity: Mapped[float] = mapped_column(Float)
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    report_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    evidence: Mapped[Evidence] = relationship()
