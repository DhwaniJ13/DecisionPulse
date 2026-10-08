"""Run:  python -m scripts.run_demo     (from repo root)"""
import json
from impact_engine import ImpactEngine, SessionLocal, init_db
from impact_engine.seed import reseed

init_db()
db = SessionLocal()
reseed(db)
eng = ImpactEngine(db)

print("\n--- 1) Noise: Acme risk score 32 -> 33 (should be filtered) ---")
print("Result:", eng.handle_evidence_update(3, new_value=33.0))

print("\n--- 2) Acme ISO certificate EXPIRES ---")
report = eng.handle_evidence_update(1, new_status="EXPIRED")
for a in report.affected_decisions:
    print(f"[{a.preliminary_impact_level:6}] {a.impact_score:.2f} {a.impact_type:8} {a.title}")
    print(f"           {a.reason}")
print("\nSummary:", report.summary)
print("\nFull JSON (what Members 2/3 receive):")
print(json.dumps(report.model_dump(mode="json"), indent=2)[:1500], "...")
