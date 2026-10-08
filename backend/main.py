import logging
import sys
from pathlib import Path

# Ensure backend directory and workspace root are in sys.path
BACKEND_DIR = Path(__file__).resolve().parent
ROOT_DIR = BACKEND_DIR.parent

for p in [str(BACKEND_DIR), str(ROOT_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from schemas import (
    RootResponse,
    HealthResponse,
    EvidenceUpdateRequest,
    EvidenceUpdateResponse,
    EventInfo,
    ImpactResult,
    AIResult,
    ActionResult,
)

from services.impact_service import run_impact_analysis
from services.ai_service import run_ai_investigation
from services.action_service import determine_action


# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger("decisionpulse")


# ---------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------

app = FastAPI(
    title="DecisionPulse Backend API",
    description=(
        "Backend orchestration layer for continuous decision "
        "revalidation when underlying evidence changes."
    ),
    version="1.0.0",
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# General Endpoints
# ---------------------------------------------------------

@app.get(
    "/",
    response_model=RootResponse,
    summary="Root Endpoint",
    tags=["General"],
)
def read_root():
    return {
        "message": "DecisionPulse Backend is running",
        "status": "healthy",
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    tags=["General"],
)
def read_health():
    return {
        "status": "ok",
    }


# ---------------------------------------------------------
# Evidence Update Pipeline
# ---------------------------------------------------------

@app.post(
    "/evidence/update",
    response_model=EvidenceUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Evidence Status Update & Revalidation Pipeline",
    description=(
        "Orchestrates impact analysis (Mem1), "
        "AI investigation (Mem2), and automated "
        "action determination."
    ),
    tags=["Evidence & Decision Pipeline"],
)
def update_evidence(payload: EvidenceUpdateRequest):

    logger.info(
        "Received evidence update event: evidence_id=%s, new_status=%s",
        payload.evidence_id,
        payload.new_status,
    )

    # =====================================================
    # STEP 1 — IMPACT ENGINE
    # =====================================================

    try:

        impact_data = run_impact_analysis(
            evidence_id=payload.evidence_id,
            new_status=payload.new_status,
        )

        logger.info(
            "Impact analysis complete: affected_count=%s",
            impact_data.get("affected_count", 0),
        )

    except Exception as exc:

        logger.error(
            "Error during Impact Analysis: %s",
            exc,
            exc_info=True,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Impact analysis failed: {str(exc)}",
        )


    # =====================================================
    # STEP 2 — AI INVESTIGATION
    # =====================================================

    try:

        ai_data = run_ai_investigation(impact_data)

        logger.info(
            "AI investigation completed successfully."
        )

    except Exception as exc:

        # -------------------------------------------------
        # IMPORTANT:
        # Gemini failure must NOT break the complete demo.
        # We fall back to deterministic risk evaluation.
        # -------------------------------------------------

        logger.warning(
            "AI Investigation unavailable. "
            "Using deterministic fallback. Error: %s",
            exc,
        )

        affected_count = impact_data.get(
            "affected_count",
            0,
        )

        affected_decisions = impact_data.get(
            "affected_decisions",
            [],
        )

        # Count HIGH-risk decisions returned by Impact Engine
        high_count = 0

        for decision in affected_decisions:

            raw = decision.get("_raw")

            if raw is not None:

                level = getattr(
                    raw,
                    "preliminary_impact_level",
                    "",
                )

                if str(level).upper() == "HIGH":
                    high_count += 1

        # -------------------------------------------------
        # Deterministic fallback
        # -------------------------------------------------

        if affected_count > 0:

            if high_count > 0:

                ai_data = {
                    "risk": "HIGH",
                    "score": 85,
                    "explanation": (
                        f"{affected_count} active decision(s) "
                        "are affected by the evidence change. "
                        "The changed evidence is directly linked "
                        "to business decisions and requires "
                        "immediate revalidation."
                    ),
                    "recommendation": (
                        "Revalidate affected decisions and "
                        "hold high-risk decisions until the "
                        "evidence is restored, renewed, or replaced."
                    ),
                }

            else:

                ai_data = {
                    "risk": "MEDIUM",
                    "score": 60,
                    "explanation": (
                        f"{affected_count} active decision(s) "
                        "are affected by the evidence change. "
                        "The affected decisions should be "
                        "reviewed before continuing."
                    ),
                    "recommendation": (
                        "Flag affected decisions for review "
                        "and revalidate the underlying evidence."
                    ),
                }

        else:

            ai_data = {
                "risk": "LOW",
                "score": 10,
                "explanation": (
                    "No active decisions are affected by "
                    "this evidence change."
                ),
                "recommendation": (
                    "Record the evidence change in the "
                    "audit log."
                ),
            }


    # =====================================================
    # STEP 3 — ACTION ENGINE
    # =====================================================

    try:

        action_data = determine_action(ai_data)

        logger.info(
            "Action determination completed: %s",
            action_data,
        )

    except Exception as exc:

        logger.error(
            "Error during Action Determination: %s",
            exc,
            exc_info=True,
        )

        # -------------------------------------------------
        # Safe fallback for action layer
        # -------------------------------------------------

        risk = str(
            ai_data.get("risk", "LOW")
        ).upper()

        if risk == "HIGH":

            action_data = {
                "action": "REVALIDATE",
                "notify": True,
                "requires_revalidation": True,
            }

        elif risk == "MEDIUM":

            action_data = {
                "action": "FLAG_FOR_REVIEW",
                "notify": True,
                "requires_revalidation": True,
            }

        else:

            action_data = {
                "action": "NO_ACTION",
                "notify": False,
                "requires_revalidation": False,
            }


    # =====================================================
    # STEP 4 — FINAL RESPONSE
    # =====================================================

    return EvidenceUpdateResponse(

        event=EventInfo(
            evidence_id=payload.evidence_id,
            new_status=payload.new_status,
        ),

        impact=ImpactResult(
            evidence_id=impact_data["evidence_id"],
            status=impact_data["status"],
            affected_decisions=impact_data[
                "affected_decisions"
            ],
            affected_count=impact_data[
                "affected_count"
            ],
        ),

        ai=AIResult(**ai_data),

        action=ActionResult(**action_data),
    )