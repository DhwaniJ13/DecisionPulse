import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
ROOT_DIR = BACKEND_DIR.parent
for p in [str(BACKEND_DIR), str(ROOT_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from main import app
from services.action_service import determine_action
from ai_agent.models import InvestigationResult
from decisionpulse.impact_engine.db import get_session
from decisionpulse.impact_engine.seed import reseed


@pytest.fixture(autouse=True)
def reset_database():
    db = get_session()
    try:
        reseed(db)
    finally:
        db.close()


@pytest.fixture
def client():
    return TestClient(app)


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "DecisionPulse Backend is running" in data["message"]


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_action_service_deterministic_rules():
    assert determine_action({"risk": "CRITICAL"}) == {
        "action": "BLOCK",
        "notify": True,
        "requires_revalidation": True,
    }
    assert determine_action({"risk": "HIGH"}) == {
        "action": "REVALIDATE",
        "notify": True,
        "requires_revalidation": True,
    }
    assert determine_action({"risk": "MEDIUM"}) == {
        "action": "FLAG",
        "notify": True,
        "requires_revalidation": False,
    }
    assert determine_action({"risk": "LOW"}) == {
        "action": "NO_ACTION",
        "notify": False,
        "requires_revalidation": False,
    }


def test_evidence_update_missing_gemini_key_fails_at_ai_stage(client):
    # When GEMINI_API_KEY is missing, endpoint returns 500 explaining the missing key
    with patch.dict("os.environ", {}, clear=True):
        response = client.post(
            "/evidence/update",
            json={"evidence_id": "1", "new_status": "EXPIRED"},
        )
        assert response.status_code == 500
        assert "GEMINI_API_KEY is not set in .env" in response.json()["detail"]


def test_evidence_update_full_pipeline_success(client):
    mock_investigation = InvestigationResult(
        decision_id="1",
        impact_level="HIGH",
        risk_score=85,
        impact_summary="ISO 27001 certificate expired.",
        reasoning="Vendor approval directly depends on this critical certificate.",
        affected_factors=["ISO 27001 certificate"],
        recommended_action="REVALIDATE",
        confidence=0.95,
        evidence_sufficiency="SUFFICIENT",
    )

    with patch("ai_agent.investigator.investigate", return_value=mock_investigation):
        response = client.post(
            "/evidence/update",
            json={"evidence_id": "1", "new_status": "EXPIRED"},
        )

        assert response.status_code == 200
        data = response.json()

        # Check event
        assert data["event"]["evidence_id"] == "1"
        assert data["event"]["new_status"] == "EXPIRED"

        # Check impact
        assert data["impact"]["affected_count"] == 3
        assert len(data["impact"]["affected_decisions"]) == 3
        assert data["impact"]["affected_decisions"][0]["decision_id"] == "DEC-1"

        # Check ai
        assert data["ai"]["risk"] == "HIGH"
        assert data["ai"]["score"] == 85
        assert "ISO 27001" in data["ai"]["explanation"]

        # Check action
        assert data["action"]["action"] == "REVALIDATE"
        assert data["action"]["notify"] is True
        assert data["action"]["requires_revalidation"] is True
