from typing import Any, Dict


def determine_action(ai_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    ===========================================================================
    BACKEND AUTOMATION SERVICE: Action Decision Engine
    ===========================================================================
    Applies deterministic business rules based on the AI investigation result.

    Rules Matrix:
    - CRITICAL -> action = BLOCK, notify = True, requires_revalidation = True
    - HIGH     -> action = REVALIDATE, notify = True, requires_revalidation = True
    - MEDIUM   -> action = FLAG, notify = True, requires_revalidation = False
    - LOW      -> action = NO_ACTION, notify = False, requires_revalidation = False
    ===========================================================================
    """
    risk_level = str(ai_result.get("risk", "LOW")).strip().upper()

    if risk_level == "CRITICAL":
        return {
            "action": "BLOCK",
            "notify": True,
            "requires_revalidation": True
        }
    elif risk_level == "HIGH":
        return {
            "action": "REVALIDATE",
            "notify": True,
            "requires_revalidation": True
        }
    elif risk_level == "MEDIUM":
        return {
            "action": "FLAG",
            "notify": True,
            "requires_revalidation": False
        }
    elif risk_level == "LOW":
        return {
            "action": "NO_ACTION",
            "notify": False,
            "requires_revalidation": False
        }
    else:
        # Fallback for unrecognized risk levels
        return {
            "action": "FLAG",
            "notify": True,
            "requires_revalidation": False
        }
