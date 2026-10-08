import os
import sys
from pathlib import Path
from typing import Any, Dict, List

# Ensure workspace root is in sys.path for importing decisionpulse and ai_agent
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from dotenv import load_dotenv
from ai_agent.investigator import investigate_decision

load_dotenv()


def run_ai_investigation(impact_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    ===========================================================================
    MEM2 CONNECTOR: AI Revalidation & Investigation Integration
    ===========================================================================
    Calls ai_agent.investigator.investigate_decision(...) with real data
    produced by Mem1 ImpactEngine.
    ===========================================================================
    """
    affected_decisions = impact_result.get("affected_decisions", [])
    affected_count = impact_result.get("affected_count", 0)
    status = str(impact_result.get("status", "")).strip().upper()
    rep = impact_result.get("report_object")

    # If no decisions are affected (or change is classified as noise), return baseline response
    if affected_count == 0 or not affected_decisions:
        return {
            "risk": "LOW",
            "score": 10,
            "explanation": "No prior company decisions depend on this evidence item or the update is non-breaking.",
            "recommendation": "Record evidence status update in audit log."
        }

    # Inspect the primary affected decision (highest impact score)
    primary = affected_decisions[0]
    raw_d = primary.get("_raw")

    # Construct Mem2 decision payload
    decision_payload = {
        "decision_id": str(getattr(raw_d, "decision_id", primary.get("decision_id"))),
        "decision_type": str(getattr(raw_d, "decision_type", "VENDOR_APPROVAL")).lower(),
        "title": str(getattr(raw_d, "title", primary.get("decision", "Decision"))),
        "status": str(getattr(raw_d, "status", "APPROVED")),
        "owner": str(getattr(raw_d, "owner_name", "Procurement")),
    }

    # Construct Mem2 changed_evidence payload
    changed_evidence_payload = {
        "evidence_id": str(rep.change.evidence_id if rep else impact_result.get("resolved_evidence_id", "1")),
        "type": str(rep.change.evidence_type if rep else impact_result.get("evidence_type", "CERTIFICATE")).lower(),
        "name": str(rep.change.evidence_name if rep else impact_result.get("evidence_name", "Evidence")),
        "old_value": {
            "status": str(rep.change.old_status if rep else "VALID"),
            "value": rep.change.old_value if rep else None,
        },
        "new_value": {
            "status": status,
            "value": rep.change.new_value if rep else None,
        },
    }

    # Construct Mem2 dependency payload
    trigger_role = getattr(raw_d, "trigger_role", None)
    criticality = getattr(raw_d, "criticality", 3)
    dep_strength = trigger_role or ("CRITICAL" if criticality >= 4 else "MEDIUM")

    dependency_payload = {
        "dependency_strength": str(dep_strength).upper(),
        "reason": str(getattr(raw_d, "reason", primary.get("reason", "Decision depends on this evidence"))),
    }

    # Construct Mem2 related_evidence payload
    related_evidence_payload: List[Dict[str, Any]] = []
    if raw_d and hasattr(raw_d, "evidence") and raw_d.evidence:
        change_ev_id = rep.change.evidence_id if rep else None
        for e in raw_d.evidence:
            if change_ev_id is not None and e.id == change_ev_id:
                continue
            related_evidence_payload.append({
                "evidence_id": f"EVID-{e.id}",
                "type": str(e.evidence_type).lower(),
                "status": str(e.status).upper(),
                "role": str(e.role),
            })

    # Execute real AI investigation
    investigation = investigate_decision(
        decision=decision_payload,
        changed_evidence=changed_evidence_payload,
        dependency=dependency_payload,
        related_evidence=related_evidence_payload,
    )

    # Normalize response to match Backend AIResult schema
    impact_level = str(investigation.impact_level).strip().upper()
    risk_score = int(investigation.risk_score)
    explanation = f"{investigation.impact_summary} {investigation.reasoning}".strip()
    recommendation = f"{investigation.recommended_action}: {investigation.impact_summary}".strip()

    return {
        "risk": impact_level,
        "score": risk_score,
        "explanation": explanation,
        "recommendation": recommendation,
    }
