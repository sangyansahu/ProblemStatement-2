from typing import Dict, Any, Optional


def calculate_excess(reported_enrolment: int, approved_intake: int, approved_extra_seats: int = 0) -> int:
    """Calculate excess capacity over approved intake and extra seats.
    Formula: max(0, reported_enrolment - (approved_intake + approved_extra_seats))
    Tests required:
    137 vs 120 + 0  -> 17
    137 vs 120 + 20 -> 0
    """
    total_allowed = max(0, approved_intake) + max(0, approved_extra_seats)
    return max(0, reported_enrolment - total_allowed)


def validate_intake_exceeded(
    reported_enrolment: int,
    approved_intake: int,
    approved_extra_seats: int = 0,
    row_number: int = 0,
    course_code: str = ""
) -> Optional[Dict[str, Any]]:
    """INTAKE_EXCEEDED rule: only statuses 'enrolled' and 'active' count."""
    excess = calculate_excess(reported_enrolment, approved_intake, approved_extra_seats)
    if excess > 0:
        total_allowed = approved_intake + approved_extra_seats
        return {
            "rule_code": "INTAKE_EXCEEDED",
            "severity": "error",
            "row_number": row_number,
            "message": (
                f"Course {course_code} capacity exceeded: active enrolment ({reported_enrolment}) "
                f"surpasses approved ceiling ({total_allowed}) by {excess} seats"
            ),
            "action": "flag_case",
            "requires_review": True
        }
    return None


def calculate_enrolment_growth(current_enrolment: int, previous_enrolment: int) -> float:
    """Rule-based growth%: (E_t - E_{t-1}) / max(E_{t-1}, 1) * 100."""
    denom = max(previous_enrolment, 1)
    return ((current_enrolment - previous_enrolment) / denom) * 100.0


def validate_enrolment_growth_anomaly(
    current_enrolment: int,
    previous_enrolment: int,
    threshold_pct: float = 100.0,
    row_number: int = 0,
    course_code: str = ""
) -> Optional[Dict[str, Any]]:
    """ENROLMENT_GROWTH_ANOMALY: rule-based only, no machine learning."""
    if previous_enrolment <= 0:
        return None  # Baseline year
    growth = calculate_enrolment_growth(current_enrolment, previous_enrolment)
    if growth > threshold_pct:
        return {
            "rule_code": "ENROLMENT_GROWTH_ANOMALY",
            "severity": "warning",
            "row_number": row_number,
            "message": (
                f"Course {course_code} shows unusual enrolment growth of {growth:.1f}% "
                f"over previous cycle (threshold: {threshold_pct:.0f}%)"
            ),
            "action": "flag_case",
            "requires_review": True
        }
    return None
