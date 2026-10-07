"""Dependency graph traversal (plain Python BFS - no graph library needed)."""
from collections import defaultdict
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import DecisionEvidence, DecisionDependency

PROPAGATION_DECAY = 0.6   # signal weakens by 40% per hop between decisions
MAX_DEPTH = 3


def downstream_map(db: Session) -> dict[int, list[int]]:
    """decision_id -> [decisions that depend on it]"""
    m = defaultdict(list)
    for dep in db.scalars(select(DecisionDependency)):
        m[dep.depends_on_decision_id].append(dep.decision_id)
    return m


def direct_links(db: Session, evidence_id: int) -> list[DecisionEvidence]:
    return list(db.scalars(select(DecisionEvidence).where(DecisionEvidence.evidence_id == evidence_id)))


def propagate(direct_signal: dict[int, float], downstream: dict[int, list[int]]):
    """BFS from directly-affected decisions to decisions that depend on them.
    direct_signal: {decision_id: signal}.  Returns {decision_id: (signal, depth, parent_id)}."""
    found = {d: (s, 0, None) for d, s in direct_signal.items()}
    frontier = list(direct_signal)
    depth = 0
    while frontier and depth < MAX_DEPTH:
        depth += 1
        nxt = []
        for parent in frontier:
            for child in downstream.get(parent, []):
                sig = found[parent][0] * PROPAGATION_DECAY
                if child not in found or sig > found[child][0]:   # visited-check also stops cycles
                    if child not in found:
                        nxt.append(child)
                    found[child] = (sig, depth, parent)
        frontier = nxt
    return found
