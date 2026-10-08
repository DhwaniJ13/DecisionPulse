def analyze_evidence_change(changed_evidence: dict) -> dict:
    """
    Analyze the nature and severity of an evidence change.
    """

    old_value = changed_evidence.get("old_value", {})
    new_value = changed_evidence.get("new_value", {})

    result = {
        "evidence_id": changed_evidence.get("evidence_id"),
        "evidence_type": changed_evidence.get("type"),
        "change_detected": True,
        "severity": "LOW",
        "change_description": "",
    }

    old_status = ""
    new_status = ""

    if isinstance(old_value, dict):
        old_status = str(
            old_value.get("status", "")
        ).upper()

    if isinstance(new_value, dict):
        new_status = str(
            new_value.get("status", "")
        ).upper()

    if new_status in ["EXPIRED", "REVOKED", "FAILED", "INVALID"]:
        result["severity"] = "HIGH"

    elif old_status != new_status:
        result["severity"] = "MEDIUM"

    result["change_description"] = (
        f"Evidence status changed from "
        f"{old_status or 'UNKNOWN'} to "
        f"{new_status or 'UNKNOWN'}."
    )

    return result


def analyze_dependency(dependency: dict) -> dict:
    """
    Determine how strongly the decision depends on the changed evidence.
    """

    strength = str(
        dependency.get(
            "dependency_strength",
            "LOW"
        )
    ).upper()

    weights = {
        "INFORMATIONAL": 1,
        "LOW": 2,
        "MEDIUM": 3,
        "HIGH": 4,
        "CRITICAL": 5,
    }

    return {
        "dependency_strength": strength,
        "dependency_weight": weights.get(strength, 2),
        "reason": dependency.get("reason", ""),
    }


def identify_mitigating_evidence(
    related_evidence: list[dict]
) -> dict:

    mitigating = []

    for evidence in related_evidence:

        status = str(
            evidence.get("status", "")
        ).upper()

        value = evidence.get("value")

        if status in ["PASSED", "VALID", "COMPLIANT"]:
            mitigating.append(evidence)

        elif isinstance(value, (int, float)):
            if value < 50:
                mitigating.append(evidence)

    return {
        "mitigating_evidence_found": len(mitigating) > 0,
        "count": len(mitigating),
        "evidence": mitigating,
    }