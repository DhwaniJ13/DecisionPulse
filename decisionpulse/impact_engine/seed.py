"""Synthetic demo data: 2 vendors, 6 decisions, 8 evidence items."""
from datetime import timedelta
from sqlalchemy.orm import Session
from .models import (Base, Evidence, Decision, DecisionEvidence, DecisionDependency, utcnow)


def reseed(db: Session):
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())
    db.commit()
    seed(db)


def seed(db: Session):
    now = utcnow()
    E = lambda *a, **k: Evidence(*a, **k)
    ev = [
        E(id=1, name="Acme ISO 27001 Certificate", evidence_type="CERTIFICATE", entity_name="Acme Corp", status="VALID", expires_at=now + timedelta(days=2)),
        E(id=2, name="Acme SOC 2 Type II Report", evidence_type="DOCUMENT", entity_name="Acme Corp", expires_at=now + timedelta(days=200)),
        E(id=3, name="Acme Vendor Risk Score", evidence_type="RISK_SCORE", entity_name="Acme Corp", value=32.0),
        E(id=4, name="Acme Financial Health Report", evidence_type="FINANCIAL", entity_name="Acme Corp"),
        E(id=5, name="Acme Data Access Permission", evidence_type="ACCESS", entity_name="Acme Corp"),
        E(id=6, name="Globex ISO 27001 Certificate", evidence_type="CERTIFICATE", entity_name="Globex Ltd", expires_at=now + timedelta(days=300)),
        E(id=7, name="Globex Vendor Risk Score", evidence_type="RISK_SCORE", entity_name="Globex Ltd", value=18.0),
        E(id=8, name="Acme Insurance Certificate", evidence_type="CERTIFICATE", entity_name="Acme Corp", expires_at=now + timedelta(days=90)),
    ]
    dec = [
        Decision(id=1, title="Approve Acme Corp as vendor", decision_type="VENDOR_APPROVAL", entity_name="Acme Corp", criticality=5, owner_name="Priya Sharma", owner_email="priya@example.com"),
        Decision(id=2, title="Grant Acme access to customer database", decision_type="ACCESS_GRANT", entity_name="Acme Corp", criticality=5, owner_name="Rahul Verma", owner_email="rahul@example.com"),
        Decision(id=3, title="Renew Acme annual contract", decision_type="CONTRACT", entity_name="Acme Corp", criticality=3, owner_name="Anita Rao", owner_email="anita@example.com"),
        Decision(id=4, title="Onboard Acme to payments platform", decision_type="ONBOARDING", entity_name="Acme Corp", criticality=4, owner_name="Priya Sharma", owner_email="priya@example.com"),
        Decision(id=5, title="Approve Globex Ltd as vendor", decision_type="VENDOR_APPROVAL", entity_name="Globex Ltd", criticality=4, owner_name="Sam Lee", owner_email="sam@example.com"),
        Decision(id=6, title="Increase Acme purchase limit", decision_type="FINANCIAL_LIMIT", entity_name="Acme Corp", criticality=2, owner_name="Anita Rao", owner_email="anita@example.com"),
    ]
    C, S = "CRITICAL", "SUPPORTING"
    links = [(1, 1, C), (1, 2, C), (1, 3, S), (1, 4, S),        # vendor approval
             (2, 1, C), (2, 5, C), (2, 3, S),                   # DB access
             (3, 4, C), (3, 8, S), (3, 3, S),                   # contract renewal
             (4, 2, S),                                         # payments onboarding
             (5, 6, C), (5, 7, S),                              # Globex
             (6, 4, C)]                                         # purchase limit
    db.add_all(ev + dec)
    db.flush()
    db.add_all([DecisionEvidence(decision_id=d, evidence_id=e, role=r) for d, e, r in links])
    db.add_all([DecisionDependency(decision_id=4, depends_on_decision_id=1),   # onboarding depends on vendor approval
                DecisionDependency(decision_id=6, depends_on_decision_id=3)])  # limit depends on contract
    db.commit()
