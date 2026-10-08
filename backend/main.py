import logging
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

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("decisionpulse")

# Initialize FastAPI application
app = FastAPI(
    title="DecisionPulse Backend API",
    description="Backend orchestration layer for continuous decision revalidation when underlying evidence changes.",
    version="1.0.0",
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.post(
    "/evidence/update",
    response_model=EvidenceUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Evidence Status Update & Revalidation Pipeline",
    description="Orchestrates impact analysis (Mem1), AI investigation (Mem2), and automated action determination.",
    tags=["Evidence & Decision Pipeline"],
)
def update_evidence(payload: EvidenceUpdateRequest):
    logger.info("Received evidence update event: evidence_id=%s, new_status=%s", payload.evidence_id, payload.new_status)

    # Step 1: Mem1 Impact Engine Connector
    try:
        impact_data = run_impact_analysis(
            evidence_id=payload.evidence_id,
            new_status=payload.new_status,
        )
    except Exception as exc:
        logger.error("Error during Impact Analysis: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Impact analysis failed while evaluating affected decisions.",
        )

    # Step 2: Mem2 AI Revalidation Connector
    try:
        ai_data = run_ai_investigation(impact_data)
    except Exception as exc:
        logger.error("Error during AI Investigation: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI investigation failed while evaluating risk and recommendations.",
        )

    # Step 3: Backend Automation Action Service
    try:
        action_data = determine_action(ai_data)
    except Exception as exc:
        logger.error("Error during Action Determination: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Action determination failed while processing policy rules.",
        )

    # Construct and return validated response
    return EvidenceUpdateResponse(
        event=EventInfo(
            evidence_id=payload.evidence_id,
            new_status=payload.new_status,
        ),
        impact=ImpactResult(**impact_data),
        ai=AIResult(**ai_data),
        action=ActionResult(**action_data),
    )
