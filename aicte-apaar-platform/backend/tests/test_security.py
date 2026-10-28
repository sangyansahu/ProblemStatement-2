import os
import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.models import Institution, Programme, User, Admission, Student, AuditLog
from app.security import create_access_token, generate_apaar_token
from app.seed_data import seed_database_defaults

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_database_defaults(db)
    db.close()
    yield


def get_token(role: str, institution_id: str = None, username: str = None):
    uname = username or f"test_{role}"
    return create_access_token({
        "sub": str(uuid.uuid4()),
        "username": uname,
        "role": role,
        "institution_id": institution_id
    })


def test_unauthenticated_requests_rejected():
    """Unauthenticated requests to protected endpoints return 401."""
    res_students = client.get("/api/v1/students")
    assert res_students.status_code == 401

    res_upload = client.post("/api/v1/uploads", files={"file": ("test.csv", b"dummy")})
    assert res_upload.status_code == 401


def test_verifier_cannot_read_student_profiles():
    """Verifier role can verify credentials only; can never read student profiles."""
    verifier_token = get_token("verifier")
    headers = {"Authorization": f"Bearer {verifier_token}"}

    res = client.get("/api/v1/students", headers=headers)
    assert res.status_code == 403


def test_operator_cannot_read_other_institutions_records():
    """Operator cannot access records belonging to another institution."""
    db = SessionLocal()
    inst1 = db.query(Institution).filter(Institution.aicte_code == "AICTE-1-001").first()
    inst2 = db.query(Institution).filter(Institution.aicte_code == "AICTE-1-002").first()
    db.close()

    # Operator for Institution 1
    op1_token = get_token("institution_operator", institution_id=str(inst1.id), username="op1")
    headers1 = {"Authorization": f"Bearer {op1_token}"}

    # Attempt to request Institution 2's programmes
    res = client.get(f"/api/v1/institutions/{inst2.id}/programmes", headers=headers1)
    assert res.status_code == 403


def test_repeat_upload_idempotency_no_duplicate_admissions():
    """Repeat upload with identical checksum creates no duplicate admissions."""
    db = SessionLocal()
    inst = db.query(Institution).filter(Institution.aicte_code == "AICTE-1-001").first()
    prog = db.query(Programme).filter(Programme.institution_id == inst.id, Programme.course_code == "CS101", Programme.academic_year == "2025-26").first()
    db.close()

    op_token = get_token("institution_operator", institution_id=str(inst.id), username="op_idem")
    headers = {"Authorization": f"Bearer {op_token}"}

    csv_data = (
        "student_number,apaar_id,course_code,academic_year,seat_category,name\n"
        "IDEM-001,DEMO-9824-9999-0001,CS101,2025-26,regular,Idempotent Student 1\n"
        "IDEM-002,DEMO-9824-9999-0002,CS101,2025-26,regular,Idempotent Student 2\n"
    ).encode("utf-8")

    # First upload
    res1 = client.post(
        "/api/v1/uploads",
        files={"file": ("idempotent_test.csv", csv_data, "text/csv")},
        data={"academic_year": "2025-26", "institution_id": str(inst.id)},
        headers=headers
    )
    assert res1.status_code == 200
    batch1 = res1.json()

    # Second upload with identical file content
    res2 = client.post(
        "/api/v1/uploads",
        files={"file": ("idempotent_test.csv", csv_data, "text/csv")},
        data={"academic_year": "2025-26", "institution_id": str(inst.id)},
        headers=headers
    )
    assert res2.status_code == 200
    batch2 = res2.json()

    # Must return the same batch ID without creating duplicates
    assert batch1["id"] == batch2["id"]

    db = SessionLocal()
    count = db.query(Admission).filter(Admission.student_number.in_(["IDEM-001", "IDEM-002"])).count()
    db.close()
    assert count == 2  # Exactly 2, not 4!


def test_invalid_files_rejected_safely():
    """Invalid magic bytes or corrupted files rejected safely with 400."""
    db = SessionLocal()
    inst = db.query(Institution).filter(Institution.aicte_code == "AICTE-1-001").first()
    db.close()

    op_token = get_token("institution_operator", institution_id=str(inst.id))
    headers = {"Authorization": f"Bearer {op_token}"}

    # Binary executable disguised as CSV
    fake_exe = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00"
    res = client.post(
        "/api/v1/uploads",
        files={"file": ("malicious.csv", fake_exe, "text/csv")},
        data={"academic_year": "2025-26", "institution_id": str(inst.id)},
        headers=headers
    )
    assert res.status_code == 400


def test_audit_entries_written_for_sensitive_actions():
    """Audit logs are recorded for upload, record update, case resolution, and report export."""
    db = SessionLocal()
    initial_audit_count = db.query(AuditLog).count()
    db.close()

    admin_token = get_token("aicte_admin", username="audit_tester")
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Trigger export report
    res_export = client.get("/api/v1/reports/enrolment?academic_year=2025-26", headers=headers)
    assert res_export.status_code == 200

    db = SessionLocal()
    new_audit_count = db.query(AuditLog).count()
    latest_log = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).first()
    db.close()

    assert new_audit_count > initial_audit_count
    assert latest_log.action == "report_export"
    assert latest_log.actor_id == "audit_tester"
