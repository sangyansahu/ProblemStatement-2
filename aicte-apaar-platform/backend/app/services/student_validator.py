import re
from datetime import datetime
from typing import Dict, Any, Optional, Set

ALLOWED_SEAT_CATEGORIES: Set[str] = {"regular", "supernumerary", "nri", "oci", "fn"}
ACADEMIC_YEAR_REGEX = re.compile(r"^\d{4}-\d{2,4}$")


def validate_missing_apaar(apaar_id: Optional[str], row_number: int = 0) -> Optional[Dict[str, Any]]:
    """MISSING_APAAR (error)."""
    val = str(apaar_id or "").strip()
    if not val:
        return {
            "rule_code": "MISSING_APAAR",
            "severity": "error",
            "row_number": row_number,
            "message": "APAAR identifier is missing from record",
            "action": "reject_row",
            "requires_review": True
        }
    return None


def validate_demo_identifier(apaar_id: str, row_number: int = 0) -> Optional[Dict[str, Any]]:
    """DEMO_IDENTIFIER_NOT_REAL (warning; any value starting with 'DEMO-')."""
    val = str(apaar_id or "").strip().upper()
    if val.startswith("DEMO-"):
        return {
            "rule_code": "DEMO_IDENTIFIER_NOT_REAL",
            "severity": "warning",
            "row_number": row_number,
            "message": "Synthetic test identifier detected in demonstration sandbox",
            "action": "flag_warning",
            "requires_review": False
        }
    return None


def validate_seat_category(seat_category: str, row_number: int = 0) -> Optional[Dict[str, Any]]:
    """INVALID_SEAT_CATEGORY (error; allowed: regular, supernumerary, nri, oci, fn)."""
    val = str(seat_category or "").strip().lower()
    if val not in ALLOWED_SEAT_CATEGORIES:
        return {
            "rule_code": "INVALID_SEAT_CATEGORY",
            "severity": "error",
            "row_number": row_number,
            "message": f"Seat category '{seat_category}' is invalid. Allowed: regular, supernumerary, nri, oci, fn",
            "action": "reject_row",
            "requires_review": True
        }
    return None


def validate_academic_year(academic_year: str, row_number: int = 0) -> Optional[Dict[str, Any]]:
    """INVALID_ACADEMIC_YEAR (error). Must match format YYYY-YY or YYYY-YYYY."""
    val = str(academic_year or "").strip()
    if not val or not ACADEMIC_YEAR_REGEX.match(val):
        return {
            "rule_code": "INVALID_ACADEMIC_YEAR",
            "severity": "error",
            "row_number": row_number,
            "message": f"Academic cycle format '{academic_year}' is invalid. Expected format YYYY-YY (e.g. 2025-26)",
            "action": "reject_row",
            "requires_review": True
        }
    return None


def validate_admission_date(admission_date: Optional[str], row_number: int = 0) -> Optional[Dict[str, Any]]:
    """INVALID_ADMISSION_DATE (error). Optional field, but if supplied must parse."""
    val = str(admission_date or "").strip()
    if not val:
        return None  # Optional field

    parsed = False
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            datetime.strptime(val, fmt)
            parsed = True
            break
        except ValueError:
            continue

    if not parsed:
        return {
            "rule_code": "INVALID_ADMISSION_DATE",
            "severity": "error",
            "row_number": row_number,
            "message": f"Admission date '{admission_date}' does not match standard date syntax (YYYY-MM-DD)",
            "action": "reject_row",
            "requires_review": True
        }
    return None


def validate_status_transition(current_status: str, new_status: str, row_number: int = 0) -> Optional[Dict[str, Any]]:
    """INVALID_STATUS_TRANSITION (error).
    Permitted:
    enrolled -> active, withdrawn, cancelled
    active -> withdrawn, cancelled
    terminal states (withdrawn, cancelled, rejected) cannot transition back to active/enrolled.
    """
    cur = str(current_status or "").strip().lower()
    nxt = str(new_status or "").strip().lower()

    if cur == nxt:
        return None

    terminal = {"withdrawn", "cancelled", "rejected"}
    if cur in terminal and nxt in {"enrolled", "active"}:
        return {
            "rule_code": "INVALID_STATUS_TRANSITION",
            "severity": "error",
            "row_number": row_number,
            "message": f"Disallowed status transition from terminal state '{cur}' to '{nxt}'",
            "action": "reject_update",
            "requires_review": True
        }
    return None
