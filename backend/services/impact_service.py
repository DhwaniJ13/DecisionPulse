from typing import Any, Dict, List


def run_impact_analysis(evidence_id: str, new_status: str) -> Dict[str, Any]:
    """
    ===========================================================================
    MEM1 CONNECTOR: Impact Engine Integration
    ===========================================================================
    This service acts as the integration boundary for Mem1's Impact Engine.
    Currently returns MOCK impact propagation data.

    REPLACE THIS IMPLEMENTATION WHEN MEM1 DELIVERS:
    Option A (Direct Function):
        from mem1_engine import calculate_impact
        return calculate_impact(evidence_id=evidence_id, status=new_status)

    Option B (Microservice / API Call):
        import httpx
        response = httpx.post("http://mem1-service/analyze", json={"evidence_id": evidence_id, "status": new_status})
        return response.json()
    ===========================================================================
    """
    normalized_status = new_status.strip().lower()

    # Determine mock affected decisions based on incoming status
    affected_decisions: List[Dict[str, str]] = []

    if normalized_status in ["expired", "failed", "revoked", "breached", "invalid", "rejected"]:
        affected_decisions.append({
            "decision_id": "DEC-101",
            "decision": "Vendor Approval",
            "reason": f"Vendor approval depended on this compliance evidence ({evidence_id})"
        })

        # Add additional dependent decision for severe statuses
        if normalized_status in ["breached", "revoked"]:
            affected_decisions.append({
                "decision_id": "DEC-204",
                "decision": "Payment Gateway Integration",
                "reason": f"Active payment clearance depended on valid security certificate ({evidence_id})"
            })
    elif normalized_status in ["valid", "active", "passed", "renewed", "approved"]:
        # Healthy status: no adverse impact on existing decisions
        affected_decisions = []
    else:
        # Default mock fallback for unclassified statuses
        affected_decisions.append({
            "decision_id": "DEC-101",
            "decision": "Vendor Approval",
            "reason": f"Status change to '{new_status}' requires review of dependent vendor policy ({evidence_id})"
        })

    return {
        "evidence_id": evidence_id,
        "status": new_status,
        "affected_decisions": affected_decisions,
        "affected_count": len(affected_decisions)
    }
