import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy import select

from decisionpulse.impact_engine.db import get_session, init_db
from decisionpulse.impact_engine.engine import ImpactEngine, EvidenceNotFound
from decisionpulse.impact_engine.models import Evidence
from decisionpulse.impact_engine.schemas import ImpactReport
from decisionpulse.impact_engine.seed import seed


def _ensure_db_initialized(db):
    init_db()

    has_data = db.scalar(
        select(Evidence).limit(1)
    )

    if not has_data:
        seed(db)


def _resolve_evidence(db, evidence_id):

    # Direct numeric ID
    try:
        numeric_id = int(str(evidence_id).strip())

        record = db.get(Evidence, numeric_id)

        if record:
            return record

    except (ValueError, TypeError):
        pass

    # Search by exact ID-like text
    text = str(evidence_id).strip()

    match = re.search(r"\d+", text)

    if match:

        record = db.get(
            Evidence,
            int(match.group())
        )

        if record:
            return record

    # Search by evidence name
    record = db.scalar(
        select(Evidence).where(
            Evidence.name.ilike(f"%{text}%")
        )
    )

    if record:
        return record

    # Search by entity
    record = db.scalar(
        select(Evidence).where(
            Evidence.entity_name.ilike(f"%{text}%")
        )
    )

    if record:
        return record

    return None


def run_impact_analysis(
    evidence_id,
    new_status,
):

    db = get_session()

    try:

        _ensure_db_initialized(db)

        ev_record = _resolve_evidence(
            db,
            evidence_id
        )

        if not ev_record:
            raise EvidenceNotFound(
                f"Evidence {evidence_id} not found"
            )

        requested_status = (
            str(new_status)
            .strip()
            .upper()
        )

        # -------------------------------------------------
        # DEMO REPLAY SAFETY
        #
        # If the same EXPIRED event is submitted again,
        # reset the evidence to VALID first so the demo
        # can replay:
        #
        # VALID -> EXPIRED -> Impact -> AI -> Action
        #
        # This prevents an already-processed demo event
        # from returning zero impact.
        # -------------------------------------------------

        if (
            ev_record.status == requested_status
            and requested_status in {
                "EXPIRED",
                "REVOKED",
                "INVALID",
            }
        ):

            ev_record.status = "VALID"
            db.commit()

        engine = ImpactEngine(db)

        report = engine.handle_evidence_update(
            evidence_id=ev_record.id,
            new_status=requested_status,
        )

        # -------------------------------------------------
        # IMPORTANT:
        # If the change is noise/no-op, return an empty
        # impact report instead of crashing.
        # -------------------------------------------------

        affected_decisions = []

        if report and report.affected_decisions:

            for item in report.affected_decisions:

                affected_decisions.append(
                    {
                        "decision_id": f"DEC-{item.decision_id}",
                        "decision": item.title,
                        "reason": item.reason,
                        "_raw": item,
                    }
                )

        return {
            "evidence_id": str(evidence_id),
            "status": requested_status,
            "resolved_evidence_id": ev_record.id,
            "evidence_name": ev_record.name,
            "evidence_type": ev_record.evidence_type,
            "affected_decisions": affected_decisions,
            "affected_count": len(
                affected_decisions
            ),
            "raw_report": (
                report.model_dump()
                if report
                else None
            ),
            "report_object": report,
        }

    finally:

        db.close()