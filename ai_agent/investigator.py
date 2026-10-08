from .agent import investigate
try:
    from .risk_engine import calculate_risk_signals
except ImportError:
    from risk_engine import calculate_risk_signals


def investigate_decision(
    decision: dict,
    changed_evidence: dict,
    dependency: dict,
    related_evidence: list[dict] | None = None,
):

    related_evidence = related_evidence or []

    risk_signals = calculate_risk_signals(
        decision=decision,
        changed_evidence=changed_evidence,
        dependency=dependency,
        related_evidence=related_evidence,
    )

    context = {
        "decision": decision,
        "changed_evidence": changed_evidence,
        "dependency": dependency,
        "related_evidence": related_evidence,
        "deterministic_risk_signals": risk_signals,
    }

    return investigate(context)