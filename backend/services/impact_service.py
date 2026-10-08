import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure workspace root is in sys.path for importing decisionpulse and ai_agent
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy import select
from decisionpulse.impact_engine.db import get_session, init_db
from decisionpulse.impact_engine.engine import ImpactEngine, EvidenceNotFound
from decisionpulse.impact_engine.models import Evidence
from decisionpulse.impact_engine.schemas import ImpactReport
from decisionpulse.impact_engine.seed import seed


def _ensure_db_initialized(db) -> None:
    """Ensure database schema and initial seed data exist."""
    init_db()
    has_data = db.scalar(select(Evidence).limit(1))
    if not has_data:
        seed(db)


def _resolve_evidence(db, evidence_id: Any) -> Optional[Evidence]:
    """Resolve an incoming evidence identifier to an Evidence DB record."""
    # 1. Direct integer lookup if numeric
    if isinstance(evidence_id, int):
        ev = db.get(Evidence, evidence_id)
        if ev:
            return ev

    str_id = str(evidence_id).strip()

    if str_id.isdigit():
        ev = db.get(Evidence, int(str_id))
        if ev:
            return ev

    # 2. Extract digits from string like 'EVID-1' or 'COMPLIANCE-1'
    digits = re.findall(r"\d+", str_id)
    if digits:
        extracted_id = int(digits[0])
        ev = db.get(Evidence, extracted_id)
        if ev:
            return ev

    # 3. Lookup by name or entity if passed string name
    ev = db.scalar(
        select(Evidence).where(
            Evidence.name.ilike(f"%{str_id}%") | Evidence.entity_name.ilike(f"%{str_id}%")
        ).limit(1)
    )
    if ev:
        return ev

    # 4. Fallback to first available evidence if ID is out of range demo id
    return db.scalar(select(Evidence).order_by(Evidence.id).limit(1))


def run_impact_analysis(evidence_id: str, new_status: str) -> Dict[str, Any]:
    """
    ===========================================================================
    MEM1 CONNECTOR: Impact Engine Integration
    ===========================================================================
    Connects to the real Mem1 ImpactEngine (decisionpulse/impact_engine/engine.py).
    Evaluates evidence changes against decision graphs and dependency trees.
    ===========================================================================
    """
    db = get_session()
    try:
        _ensure_db_initialized(db)

        ev_record = _resolve_evidence(db, evidence_id)
        if not ev_record:
            raise EvidenceNotFound(f"Evidence '{evidence_id}' could not be resolved.")

        engine = ImpactEngine(db)
        status_upper = new_status.strip().upper()

        report: Optional[ImpactReport] = engine.handle_evidence_update(
            evidence_id=ev_record.id,
            new_status=status_upper,
        )

        affected_decisions: List[Dict[str, Any]] = []

        if report and report.affected_decisions:
            for item in report.affected_decisions:
                affected_decisions.append({
                    "decision_id": f"DEC-{item.decision_id}",
                    "decision": item.title,
                    "reason": item.reason,
                    # Internal rich object passed to Mem2 AI service
                    "_raw": item,
                })

        return {
            "evidence_id": str(evidence_id),
            "status": new_status,
            "resolved_evidence_id": ev_record.id,
            "evidence_name": ev_record.name,
            "evidence_type": ev_record.evidence_type,
            "affected_decisions": affected_decisions,
            "affected_count": len(affected_decisions),
            "raw_report": report.model_dump() if report else None,
            "report_object": report,
        }
    finally:
        db.close()
