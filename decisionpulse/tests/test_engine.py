import pytest
from impact_engine.db import make_engine, init_db
from impact_engine import ImpactEngine
from impact_engine.seed import seed
from sqlalchemy.orm import sessionmaker


@pytest.fixture()
def eng():
    e = make_engine("sqlite:///:memory:")
    init_db(e)
    db = sessionmaker(bind=e, expire_on_commit=False)()
    seed(db)
    yield ImpactEngine(db)
    db.close()


def test_noise_is_filtered(eng):
    assert eng.handle_evidence_update(3, new_value=33.0) is None   # ~3% change


def test_expired_cert_hits_direct_and_indirect(eng):
    r = eng.handle_evidence_update(1, new_status="EXPIRED")
    ids = {a.decision_id: a for a in r.affected_decisions}
    assert set(ids) == {1, 2, 4}                    # vendor approval, DB access, onboarding (indirect)
    assert ids[1].impact_type == "DIRECT" and ids[1].preliminary_impact_level == "HIGH"
    assert ids[4].impact_type == "INDIRECT" and ids[4].depth == 1
    assert r.affected_decisions[0].impact_score >= r.affected_decisions[-1].impact_score


def test_unrelated_decisions_not_affected(eng):
    r = eng.handle_evidence_update(1, new_status="EXPIRED")
    assert 5 not in {a.decision_id for a in r.affected_decisions}   # Globex untouched


def test_decision_marked_stale_and_report_saved(eng):
    r = eng.handle_evidence_update(1, new_status="EXPIRED")
    assert any(d["freshness"] == "POTENTIALLY_STALE" for d in eng.list_decisions())
    assert eng.get_report(r.change.change_id)["summary"]["total_affected"] == 3


def test_supporting_evidence_scores_lower(eng):
    r = eng.handle_evidence_update(8, new_status="EXPIRED")   # insurance cert: SUPPORTING for contract only
    assert [a.decision_id for a in r.affected_decisions][0] == 3
    assert r.affected_decisions[0].preliminary_impact_level in ("LOW", "MEDIUM")


def test_unknown_evidence_raises(eng):
    from impact_engine import EvidenceNotFound
    with pytest.raises(EvidenceNotFound):
        eng.handle_evidence_update(999, new_status="EXPIRED")
