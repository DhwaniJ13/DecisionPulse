"""Decides: is this evidence change meaningful? How severe is it?
Returns None for noise (so nothing downstream runs)."""
from typing import Optional

BAD_STATUSES = {"EXPIRED", "REVOKED", "INVALID"}
NOISE_THRESHOLD = 0.10  # ignore numeric changes smaller than 10%


def classify_change(evidence_type: str, old_status: str, new_status: str,
                    old_value: Optional[float], new_value: Optional[float]):
    """-> (change_type, severity 0..1) or None if not meaningful."""
    if new_status != old_status:
        if new_status in BAD_STATUSES:
            return (new_status, 1.0)          # EXPIRED / REVOKED / INVALID
        if new_status == "DEGRADED":
            return ("DEGRADED", 0.6)
        if new_status == "VALID" and old_status in BAD_STATUSES:
            return ("RECOVERED", 0.2)         # evidence got fixed -> maybe revalidate
        return ("STATUS_CHANGED", 0.4)

    if old_value is not None and new_value is not None and old_value != new_value:
        rel = abs(new_value - old_value) / max(abs(old_value), 1e-9)
        if rel < NOISE_THRESHOLD:
            return None                        # noise
        return ("VALUE_CHANGED", round(min(0.9, rel), 3))

    return None
