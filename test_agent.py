from ai_agent.investigator import investigate_decision


decision = {
    "decision_id": "DEC-001",
    "decision_type": "vendor_approval",
    "title": "Approve Vendor ABC",
    "status": "APPROVED",
    "owner": "Procurement",
}


changed_evidence = {
    "evidence_id": "EVID-001",
    "type": "compliance_certificate",
    "name": "ISO 27001",
    "old_value": {
        "status": "VALID",
    },
    "new_value": {
        "status": "EXPIRED",
    },
}


dependency = {
    "dependency_strength": "CRITICAL",
    "reason": "Vendor approval requires a valid compliance certificate",
}


related_evidence = [
    {
        "evidence_id": "EVID-002",
        "type": "security_assessment",
        "status": "PASSED",
    },
    {
        "evidence_id": "EVID-003",
        "type": "risk_score",
        "value": 35,
    },
]


result = investigate_decision(
    decision=decision,
    changed_evidence=changed_evidence,
    dependency=dependency,
    related_evidence=related_evidence,
)


print(result.model_dump_json(indent=2))