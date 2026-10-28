import pytest
from app.services.intake_validator import calculate_excess, validate_intake_exceeded, validate_enrolment_growth_anomaly
from app.services.student_validator import (
    validate_missing_apaar, validate_demo_identifier, validate_seat_category,
    validate_academic_year, validate_admission_date, validate_status_transition
)
from app.services.duplicate_detector import detect_duplicate_in_upload
from app.services.apaar_provider import MockApaarProvider


def test_calculate_excess():
    """calculate_excess: 137 vs 120 + 0 -> 17; 137 vs 120 + 20 -> 0."""
    assert calculate_excess(137, 120, 0) == 17
    assert calculate_excess(137, 120, 20) == 0
    assert calculate_excess(100, 120, 0) == 0


def test_rule_missing_apaar():
    """MISSING_APAAR rule positive and negative tests."""
    # Negative test (valid APAAR)
    assert validate_missing_apaar("DEMO-9824-0001-1234") is None
    assert validate_missing_apaar("982412345678") is None

    # Positive test (missing APAAR)
    res = validate_missing_apaar("", row_number=5)
    assert res is not None
    assert res["rule_code"] == "MISSING_APAAR"
    assert res["severity"] == "error"

    res_none = validate_missing_apaar(None, row_number=6)
    assert res_none is not None
    assert res_none["rule_code"] == "MISSING_APAAR"


def test_rule_demo_identifier():
    """DEMO_IDENTIFIER_NOT_REAL rule positive and negative tests."""
    # Positive test (synthetic identifier flagged as warning)
    res = validate_demo_identifier("DEMO-9824-1111-2222", row_number=2)
    assert res is not None
    assert res["rule_code"] == "DEMO_IDENTIFIER_NOT_REAL"
    assert res["severity"] == "warning"

    # Negative test (standard numeric identifier)
    assert validate_demo_identifier("982411112222") is None


def test_rule_seat_category():
    """INVALID_SEAT_CATEGORY rule positive and negative tests."""
    # Negative test (allowed categories)
    for cat in ["regular", "supernumerary", "nri", "oci", "fn", "REGULAR", "NRI"]:
        assert validate_seat_category(cat) is None

    # Positive test (invalid category)
    res = validate_seat_category("management_quota", row_number=8)
    assert res is not None
    assert res["rule_code"] == "INVALID_SEAT_CATEGORY"
    assert res["severity"] == "error"


def test_rule_academic_year():
    """INVALID_ACADEMIC_YEAR rule positive and negative tests."""
    # Negative test (valid formats)
    assert validate_academic_year("2025-26") is None
    assert validate_academic_year("2024-2025") is None

    # Positive test (invalid format)
    res = validate_academic_year("invalid-year", row_number=3)
    assert res is not None
    assert res["rule_code"] == "INVALID_ACADEMIC_YEAR"
    assert res["severity"] == "error"


def test_rule_admission_date():
    """INVALID_ADMISSION_DATE rule positive and negative tests."""
    # Negative test (valid dates and empty optional)
    assert validate_admission_date("2025-07-15") is None
    assert validate_admission_date("15/07/2025") is None
    assert validate_admission_date(None) is None
    assert validate_admission_date("") is None

    # Positive test (invalid date)
    res = validate_admission_date("not-a-date", row_number=4)
    assert res is not None
    assert res["rule_code"] == "INVALID_ADMISSION_DATE"
    assert res["severity"] == "error"


def test_rule_status_transition():
    """INVALID_STATUS_TRANSITION rule positive and negative tests."""
    # Negative test (valid transitions)
    assert validate_status_transition("enrolled", "active") is None
    assert validate_status_transition("active", "withdrawn") is None
    assert validate_status_transition("enrolled", "cancelled") is None

    # Positive test (disallowed transition from terminal state)
    res = validate_status_transition("withdrawn", "active", row_number=7)
    assert res is not None
    assert res["rule_code"] == "INVALID_STATUS_TRANSITION"
    assert res["severity"] == "error"


def test_rule_duplicate_in_upload():
    """DUPLICATE_IN_UPLOAD rule positive and negative tests."""
    seen = set()
    # Negative test (first occurrence)
    assert detect_duplicate_in_upload(seen, "DEMO-123", row_number=1) is None
    assert detect_duplicate_in_upload(seen, "DEMO-456", row_number=2) is None

    # Positive test (repeated occurrence)
    res = detect_duplicate_in_upload(seen, "DEMO-123", row_number=3)
    assert res is not None
    assert res["rule_code"] == "DUPLICATE_IN_UPLOAD"
    assert res["severity"] == "error"


def test_rule_intake_exceeded():
    """INTAKE_EXCEEDED rule positive and negative tests."""
    # Negative test (within approved limits)
    assert validate_intake_exceeded(60, 60, 5, course_code="CS101") is None
    assert validate_intake_exceeded(50, 60, 0, course_code="CS101") is None

    # Positive test (exceeded)
    res = validate_intake_exceeded(75, 60, 5, row_number=12, course_code="CS101")
    assert res is not None
    assert res["rule_code"] == "INTAKE_EXCEEDED"
    assert res["severity"] == "error"


def test_rule_enrolment_growth_anomaly():
    """ENROLMENT_GROWTH_ANOMALY rule positive and negative tests."""
    # Negative test (normal growth)
    assert validate_enrolment_growth_anomaly(60, 50, threshold_pct=100.0) is None

    # Positive test (growth > 100%)
    res = validate_enrolment_growth_anomaly(120, 50, threshold_pct=100.0, course_code="CS101")
    assert res is not None
    assert res["rule_code"] == "ENROLMENT_GROWTH_ANOMALY"
    assert res["severity"] == "warning"


def test_apaar_provider_timeout_never_verified():
    """Provider timeout = 'unavailable', NEVER 'failed' or 'verified'."""
    provider = MockApaarProvider()
    res = provider.verify("DEMO-TIMEOUT-9999")
    assert res.status == "unavailable"
    assert res.status != "verified"
    assert res.status != "failed"

    # Deterministic test
    valid_res = provider.verify("DEMO-9824-0001-0001")
    assert valid_res.status == "verified"
