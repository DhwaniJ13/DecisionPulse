import os
import json

from dotenv import load_dotenv
from google import genai

from .models import InvestigationResult
from .prompts import SYSTEM_PROMPT
from .tools import (
    analyze_evidence_change,
    analyze_dependency,
    identify_mitigating_evidence,
)


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is not set in .env"
    )

client = genai.Client(api_key=api_key)


def investigate(context: dict) -> InvestigationResult:

    evidence_result = analyze_evidence_change(
        context["changed_evidence"]
    )

    dependency_result = analyze_dependency(
        context["dependency"]
    )

    mitigation_result = identify_mitigating_evidence(
        context.get("related_evidence", [])
    )

    investigation_context = {
        **context,

        "investigation_tools": {
            "evidence_analysis": evidence_result,
            "dependency_analysis": dependency_result,
            "mitigation_analysis": mitigation_result,
        }
    }

    response = client.models.generate_content(
        model="gemini-2.5-flash",

        contents=f"""
{SYSTEM_PROMPT}

You are now performing a deep investigation.

Use the following investigation results:

{json.dumps(investigation_context, indent=2)}

Based on the evidence, dependency, risk signals, and
mitigating evidence, produce your final investigation result.
""",

        config={
            "response_mime_type": "application/json",
            "response_schema": InvestigationResult,
        },
    )

    return InvestigationResult.model_validate_json(
        response.text
    )