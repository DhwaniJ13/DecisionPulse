from typing import Any


def calculate_risk_signals(
    decision: dict,
    changed_evidence: dict,
    dependency: dict,
    related_evidence: list[dict] | None = None,
) -> dict[str, Any]:

    related_evidence = related_evidence or []

    score = 0
    signals = []

    # 1. Dependency strength
    dependency_strength = dependency.get(
        "dependency_strength", "LOW"
    ).upper()

    dependency_scores = {
        "INFORMATIONAL": 5,
        "LOW": 10,
        "MEDIUM": 20,
        "HIGH": 30,
        "CRITICAL": 40,
    }

    score += dependency_scores.get(
        dependency_strength, 10
    )

    if dependency_strength in ["HIGH", "CRITICAL"]:
        signals.append("strong_decision_dependency")

    # 2. Determine what changed
    new_value = changed_evidence.get("new_value", {})

    if isinstance(new_value, dict):
        new_status = str(
            new_value.get("status", "")
        ).upper()

        if new_status == "EXPIRED":
            score += 40
            signals.append("evidence_expired")

        elif new_status in ["REVOKED", "FAILED", "INVALID"]:
            score += 45
            signals.append("evidence_invalidated")

    # 3. Is the decision currently active?
    decision_status = str(
        decision.get("status", "")
    ).upper()

    if decision_status in [
        "APPROVED",
        "ACTIVE",
        "IN_USE"
    ]:
        score += 10
        signals.append("active_decision")

    # 4. Related evidence
    for evidence in related_evidence:

        evidence_type = str(
            evidence.get("type", "")
        ).lower()

        value = evidence.get("value")

        # Large risk score increases
        if evidence_type == "risk_score":

            try:
                risk_value = float(value)

                if risk_value >= 80:
                    score += 20
                    signals.append(
                        "high_related_risk_score"
                    )

            except (TypeError, ValueError):
                pass

    score = min(score, 100)

    return {
        "base_risk_score": score,
        "risk_signals": signals,
        "dependency_strength": dependency_strength,
        "decision_status": decision_status,
    }