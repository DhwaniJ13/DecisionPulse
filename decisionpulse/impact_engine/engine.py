"""PUBLIC API of Member 1. Everyone else only needs this class."""
from datetime import datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import (Evidence, Decision, DecisionEvidence, DecisionDependency,
                     EvidenceChange, utcnow)
from .schemas import ImpactReport, ChangeInfo, AffectedDecision, EvidenceItem
from .change_detector import classify_change
from .graph import direct_links, downstream_map, propagate

ROLE_WEIGHT = {"CRITICAL": 1.0, "SUPPORTING": 0.5}
ACTIVE_STATUSES = {"APPROVED", "ACTIVE"}


class EvidenceNotFound(Exception):
    pass


def _level(score: float) -> str:
    return "HIGH" if score >= 0.7 else "MEDIUM" if score >= 0.35 else "LOW"


class ImpactEngine:
    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------ main entry
    def handle_evidence_update(self, evidence_id: int, new_status: Optional[str] = None,
                               new_value: Optional[float] = None,
                               new_expires_at: Optional[datetime] = None) -> Optional[ImpactReport]:
        """Apply an evidence update. Returns an ImpactReport, or None if the change is just noise."""
        ev = self.db.get(Evidence, evidence_id)
        if ev is None:
            raise EvidenceNotFound(f"Evidence {evidence_id} not found")

        old_status, old_value = ev.status, ev.value
        status = new_status or old_status
        value = new_value if new_value is not None else old_value

        verdict = classify_change(ev.evidence_type, old_status, status, old_value, value)

        ev.status, ev.value, ev.updated_at = status, value, utcnow()
        if new_expires_at is not None:
            ev.expires_at = new_expires_at

        if verdict is None:           # stage-1 filter: not meaningful
            self.db.commit()
            return None

        change_type, severity = verdict
        change = EvidenceChange(evidence_id=ev.id, change_type=change_type,
                                old_status=old_status, new_status=status,
                                old_value=old_value, new_value=value, severity=severity)
        self.db.add(change)
        self.db.flush()
        report = self._analyze(change, ev)
        change.report_json = report.model_dump(mode="json")
        self.db.commit()
        return report

    def scan_expirations(self, now: Optional[datetime] = None) -> list[ImpactReport]:
        """Marks VALID evidence past its expires_at as EXPIRED. Run on a schedule (Member 3)."""
        now = now or utcnow()
        due = self.db.scalars(select(Evidence).where(Evidence.status == "VALID",
                                                     Evidence.expires_at.is_not(None),
                                                     Evidence.expires_at <= now)).all()
        reports = []
        for ev in due:
            r = self.handle_evidence_update(ev.id, new_status="EXPIRED")
            if r:
                reports.append(r)
        return reports

    # ------------------------------------------------------------------ analysis
    def _analyze(self, change: EvidenceChange, ev: Evidence) -> ImpactReport:
        links = direct_links(self.db, ev.id)
        role_of = {l.decision_id: l.role for l in links}
        signal = {l.decision_id: change.severity * ROLE_WEIGHT.get(l.role, 0.5) for l in links}
        found = propagate(signal, downstream_map(self.db))

        affected = []
        for did, (sig, depth, parent) in found.items():
            d = self.db.get(Decision, did)
            if d.status not in ACTIVE_STATUSES:
                continue
            score = round(min(1.0, sig * d.criticality / 5), 3)
            level = _level(score)
            ev_items = self._evidence_items(did)
            valid = sum(1 for e in ev_items if e.status == "VALID")

            if depth == 0:
                path = [ev.name, d.title]
                reason = (f"{ev.evidence_type} '{ev.name}' changed {change.old_status} -> {change.new_status} "
                          f"and is {role_of[did]} evidence for this decision. "
                          f"{valid} of {len(ev_items)} evidence items are still valid.")
            else:
                chain = self._chain(found, did)
                path = [ev.name] + [self.db.get(Decision, x).title for x in chain]
                reason = (f"Indirectly affected: this decision depends on '{self.db.get(Decision, parent).title}', "
                          f"which relies on {ev.evidence_type} '{ev.name}' ({change.old_status} -> {change.new_status}).")

            if level in ("HIGH", "MEDIUM") and change.change_type != "RECOVERED":
                d.freshness_status = "POTENTIALLY_STALE"

            affected.append(AffectedDecision(
                decision_id=d.id, title=d.title, decision_type=d.decision_type, entity_name=d.entity_name,
                status=d.status, owner_name=d.owner_name, owner_email=d.owner_email, criticality=d.criticality,
                impact_type="DIRECT" if depth == 0 else "INDIRECT", depth=depth, impact_score=score,
                preliminary_impact_level=level, trigger_role=role_of.get(did), path=path, reason=reason,
                evidence=ev_items, valid_evidence_count=valid, total_evidence_count=len(ev_items)))

        affected.sort(key=lambda a: a.impact_score, reverse=True)
        summary = {"total_affected": len(affected),
                   "high": sum(a.preliminary_impact_level == "HIGH" for a in affected),
                   "medium": sum(a.preliminary_impact_level == "MEDIUM" for a in affected),
                   "low": sum(a.preliminary_impact_level == "LOW" for a in affected)}
        info = ChangeInfo(change_id=change.id, evidence_id=ev.id, evidence_name=ev.name,
                          evidence_type=ev.evidence_type, entity_name=ev.entity_name,
                          change_type=change.change_type, old_status=change.old_status,
                          new_status=change.new_status, old_value=change.old_value,
                          new_value=change.new_value, severity=change.severity,
                          detected_at=change.detected_at)
        return ImpactReport(change=info, affected_decisions=affected, summary=summary)

    def _evidence_items(self, decision_id: int) -> list[EvidenceItem]:
        links = self.db.scalars(select(DecisionEvidence).where(DecisionEvidence.decision_id == decision_id))
        return [EvidenceItem(id=l.evidence.id, name=l.evidence.name, evidence_type=l.evidence.evidence_type,
                             status=l.evidence.status, role=l.role) for l in links]

    @staticmethod
    def _chain(found, did):
        chain = []
        while did is not None:
            chain.append(did)
            did = found[did][2]
        return list(reversed(chain))

    # ------------------------------------------------------------------ read helpers (for API / frontend)
    def get_report(self, change_id: int) -> Optional[dict]:
        ch = self.db.get(EvidenceChange, change_id)
        return ch.report_json if ch else None

    def list_reports(self, limit: int = 20) -> list[dict]:
        rows = self.db.scalars(select(EvidenceChange).order_by(EvidenceChange.id.desc()).limit(limit))
        return [r.report_json for r in rows if r.report_json]

    def list_decisions(self) -> list[dict]:
        return [dict(id=d.id, title=d.title, type=d.decision_type, entity=d.entity_name, status=d.status,
                     freshness=d.freshness_status, criticality=d.criticality, owner=d.owner_name)
                for d in self.db.scalars(select(Decision).order_by(Decision.id))]

    def list_evidence(self) -> list[dict]:
        return [dict(id=e.id, name=e.name, type=e.evidence_type, entity=e.entity_name, status=e.status,
                     value=e.value, expires_at=e.expires_at.isoformat() if e.expires_at else None)
                for e in self.db.scalars(select(Evidence).order_by(Evidence.id))]

    def graph_json(self) -> dict:
        """Nodes + edges for the frontend graph view (pyvis / streamlit-agraph / react-flow)."""
        nodes = [{"id": f"E{e.id}", "label": e.name, "kind": "evidence", "status": e.status}
                 for e in self.db.scalars(select(Evidence))]
        nodes += [{"id": f"D{d.id}", "label": d.title, "kind": "decision", "status": d.status,
                   "freshness": d.freshness_status} for d in self.db.scalars(select(Decision))]
        edges = [{"source": f"E{l.evidence_id}", "target": f"D{l.decision_id}", "kind": l.role}
                 for l in self.db.scalars(select(DecisionEvidence))]
        edges += [{"source": f"D{x.depends_on_decision_id}", "target": f"D{x.decision_id}", "kind": "DEPENDS_ON"}
                  for x in self.db.scalars(select(DecisionDependency))]
        return {"nodes": nodes, "edges": edges}

    def reset_demo(self):
        """Wipe + reseed synthetic data (handy 'Reset demo' button)."""
        from .seed import reseed
        reseed(self.db)
