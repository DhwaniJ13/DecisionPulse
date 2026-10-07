# DecisionPulse — Member 1: Decision Impact Engine

**One job:** when evidence changes, answer *"which decisions are affected, why, and how strongly?"* and hand a clean JSON report to everyone else.

```
Evidence update ─► [change_detector]  noise? -> stop (returns None)
                        │ meaningful
                        ▼
                  [graph.py] evidence ─► decisions ─► dependent decisions (BFS)
                        ▼
                  score + reason + owner + evidence snapshot
                        ▼
                  ImpactReport (JSON)  ─► Member 2 (AI) ─► Member 3 (actions) ─► Frontend
```

## 1. Stack (deliberately boring)
| Need | Choice | Why |
|---|---|---|
| Language | Python 3.10+ | team standard |
| DB | PostgreSQL (docker) — SQLite for solo testing | same code, one env var flips it |
| ORM | SQLAlchemy 2.0 | works on both DBs |
| Data contracts | Pydantic v2 | FastAPI (Member 3) uses it natively |
| Graph | plain Python BFS | no Neo4j / networkx needed for a demo |
| Tests | pytest | |

## 2. Setup
```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m scripts.run_demo        # works immediately on SQLite
python -m pytest -q               # 6 tests should pass
```
PostgreSQL for the team: `docker compose up -d`, then set
`DATABASE_URL=postgresql+psycopg2://dp_user:dp_pass@localhost:5432/decisionpulse`.

## 3. Folder structure
```
impact_engine/
  models.py           5 tables (below)
  schemas.py          ImpactReport JSON contract  <-- the thing others depend on
  change_detector.py  noise filter + severity
  graph.py            dependency traversal
  engine.py           ImpactEngine class = the ONLY public API
  seed.py             synthetic demo data
  db.py               engine/session/get_db() for FastAPI
scripts/run_demo.py   end-to-end demo in the terminal
tests/test_engine.py  6 tests
```

## 4. Database schema
- `evidence(id, name, evidence_type, entity_name, status, value, expires_at, updated_at)`
- `decisions(id, title, decision_type, entity_name, status, freshness_status, criticality 1-5, owner_name, owner_email, decided_at)`
- `decision_evidence(decision_id, evidence_id, role CRITICAL|SUPPORTING)`  ← decision→evidence edges
- `decision_dependencies(decision_id, depends_on_decision_id)`  ← decision→decision edges
- `evidence_changes(..., severity, report_json)`  ← audit log + stored report

## 5. How scoring works (simple on purpose, explain this to judges)
```
signal = severity(change) × role_weight(CRITICAL=1.0, SUPPORTING=0.5)
signal × 0.6 per hop for decisions depending on other decisions
impact_score = signal × criticality/5          →  ≥0.7 HIGH · ≥0.35 MEDIUM · else LOW
```
Severity: EXPIRED/REVOKED/INVALID = 1.0, DEGRADED = 0.6, numeric change <10% = noise (dropped), else = relative change (cap 0.9).
This is a **preliminary** level. Member 2's AI gives the final risk call.

## 6. Public API (what others call)
```python
from impact_engine import ImpactEngine, SessionLocal, init_db
init_db()
eng = ImpactEngine(SessionLocal())

eng.handle_evidence_update(evidence_id=1, new_status="EXPIRED")   # -> ImpactReport | None
eng.handle_evidence_update(3, new_value=45.0)                     # risk score change
eng.scan_expirations()                                            # -> [ImpactReport]  (run on a timer)
eng.get_report(change_id) / eng.list_reports(limit=20)            # stored JSON dicts
eng.list_decisions() / eng.list_evidence()                        # tables for dashboard
eng.graph_json()                                                  # {nodes, edges} for graph view
eng.reset_demo()                                                  # reseed synthetic data
```
`None` = the change was noise. Member 3 must handle that (return `{"filtered": true}`).

## 7. Connections
**Member 3 (backend)** — wraps my class in FastAPI. Suggested starter (they own it):
```python
@app.post("/evidence/{evidence_id}/update")
def update(evidence_id: int, body: EvidenceUpdate, db: Session = Depends(get_db)):
    try:
        report = ImpactEngine(db).handle_evidence_update(evidence_id, body.new_status, body.new_value)
    except EvidenceNotFound:
        raise HTTPException(404, "Evidence not found")
    return report or {"filtered": True}
```
Endpoints I expect them to expose: `POST /evidence/{id}/update`, `POST /scan-expirations`, `GET /decisions`, `GET /evidence`, `GET /reports`, `GET /graph`, `POST /demo/reset`.
They own the action engine: read `affected_decisions[].preliminary_impact_level` (or Member 2's final level) → notify `owner_email` / flag / block (set `decisions.status = "BLOCKED"`).

**Member 2 (AI)** — input = one `AffectedDecision` + the `change` block from my report (it already contains the evidence list, owner, criticality, reason). Output I expect from them: `{decision_id, risk_level, explanation, recommended_action}` per decision. Agree on this with them on day 1. My `reason` string is a deterministic fallback if Azure OpenAI is down — use it in the demo.

**Frontend (Member 4)** — needs `GET /graph` (nodes/edges), `GET /decisions` (show `freshness_status` badge), the report JSON (impact table sorted by `impact_score`), and a "Expire certificate" button calling `POST /evidence/1/update {"new_status":"EXPIRED"}`.

**Inputs I need:** evidence updates (id + new status/value). Real or synthetic — nothing else.

## 8. Sample report (trimmed)
```json
{
  "change": {"change_id": 1, "evidence_name": "Acme ISO 27001 Certificate", "change_type": "EXPIRED",
             "old_status": "VALID", "new_status": "EXPIRED", "severity": 1.0},
  "affected_decisions": [
    {"decision_id": 1, "title": "Approve Acme Corp as vendor", "impact_type": "DIRECT",
     "impact_score": 1.0, "preliminary_impact_level": "HIGH", "owner_email": "priya@example.com",
     "reason": "CERTIFICATE '...' changed VALID -> EXPIRED and is CRITICAL evidence ... 3 of 4 evidence items are still valid.",
     "valid_evidence_count": 3, "total_evidence_count": 4}
  ],
  "summary": {"total_affected": 3, "high": 2, "medium": 1, "low": 0}
}
```

## 9. Common mistakes
- Hard-coding SQLite paths — always use `DATABASE_URL`.
- Changing field names in `schemas.py` late — others parse them. Announce changes in the group chat.
- Forgetting `init_db()` before first use on a fresh Postgres.
- Using real company data in the demo — stay synthetic.
- Adding Neo4j/Kafka/etc. Don't. The demo wins on clarity.

## 10. Commit checklist
`impact_engine/`, `scripts/`, `tests/`, `requirements.txt`, `docker-compose.yml`, `.env.example`, `.gitignore`, this README. Branch `feature/impact-engine` → PR to `main`. Do **not** commit `.env` or `*.db`. Tell the team the import line: `from impact_engine import ImpactEngine`.

## 11. Nice-to-haves if time remains (in order)
1. Seed bigger data (20 decisions) so the graph looks impressive.
2. `GET /decisions/{id}/evidence` tree for drill-down.
3. Per-evidence-type severity tweaks in `change_detector.py`.
