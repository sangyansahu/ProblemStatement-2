import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, DateTime, Boolean, ForeignKey,
    CheckConstraint, UniqueConstraint, Index, Text
)
from sqlalchemy.orm import relationship
from app.database import Base, GUID


class Institution(Base):
    __tablename__ = "institutions"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    aicte_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    state = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    programmes = relationship("Programme", back_populates="institution", cascade="all, delete-orphan")
    users = relationship("User", back_populates="institution")
    upload_batches = relationship("UploadBatch", back_populates="institution")
    admissions = relationship("Admission", back_populates="institution")
    validation_cases = relationship("ValidationCase", back_populates="institution")


class Programme(Base):
    __tablename__ = "programmes"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    institution_id = Column(GUID, ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False)
    course_code = Column(String(50), nullable=False)
    programme_name = Column(String(255), nullable=False)
    academic_year = Column(String(20), nullable=False)
    approved_intake = Column(Integer, nullable=False, default=60)
    approved_extra_seats = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("institution_id", "course_code", "academic_year", name="uq_programme_inst_course_year"),
        CheckConstraint("approved_intake >= 0", name="chk_approved_intake_non_negative"),
        CheckConstraint("approved_extra_seats >= 0", name="chk_approved_extra_seats_non_negative"),
    )

    institution = relationship("Institution", back_populates="programmes")
    admissions = relationship("Admission", back_populates="programme")


class Student(Base):
    __tablename__ = "students"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    apaar_id_token = Column(String(64), unique=True, nullable=False, index=True)  # HMAC-SHA256 hex
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    admissions = relationship("Admission", back_populates="student")
    credentials = relationship("Credential", back_populates="student")


class Admission(Base):
    __tablename__ = "admissions"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    student_id = Column(GUID, ForeignKey("students.id"), nullable=False)
    programme_id = Column(GUID, ForeignKey("programmes.id"), nullable=False)
    institution_id = Column(GUID, ForeignKey("institutions.id"), nullable=False, index=True)
    student_number = Column(String(100), nullable=False)
    academic_year = Column(String(20), nullable=False)
    seat_category = Column(String(50), nullable=False)  # regular, supernumerary, nri, oci, fn
    admission_date = Column(String(30), nullable=True)
    status = Column(String(30), nullable=False, default="enrolled")  # enrolled, active, withdrawn, cancelled, rejected
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("programme_id", "academic_year", "student_number", name="uq_admission_prog_year_num"),
        Index("ix_admissions_prog_status", "programme_id", "status"),
        Index("ix_admissions_student_id", "student_id"),
    )

    student = relationship("Student", back_populates="admissions")
    programme = relationship("Programme", back_populates="admissions")
    institution = relationship("Institution", back_populates="admissions")
    credentials = relationship("Credential", back_populates="admission")


class ValidationCase(Base):
    __tablename__ = "validation_cases"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    institution_id = Column(GUID, ForeignKey("institutions.id"), nullable=False, index=True)
    programme_id = Column(GUID, ForeignKey("programmes.id"), nullable=True)
    student_id = Column(GUID, ForeignKey("students.id"), nullable=True)
    rule_code = Column(String(60), nullable=False)
    severity = Column(String(20), nullable=False)  # error, warning, notice
    academic_year = Column(String(20), nullable=False)
    message = Column(String(500), nullable=False)
    status = Column(String(30), nullable=False, default="open")  # open, resolved, dismissed
    resolution_note = Column(Text, nullable=True)
    resolved_by = Column(String(100), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    institution = relationship("Institution", back_populates="validation_cases")
    programme = relationship("Programme")
    student = relationship("Student")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    actor_id = Column(String(100), nullable=False)
    actor_role = Column(String(50), nullable=False)
    institution_id = Column(GUID, nullable=True)
    action = Column(String(80), nullable=False)
    target_reference = Column(String(255), nullable=False)
    outcome = Column(String(20), nullable=False)  # success, failed, rejected
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class User(Base):
    __tablename__ = "users"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    keycloak_id = Column(String(100), unique=True, nullable=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # aicte_admin, institution_admin, institution_operator, verifier, auditor
    institution_id = Column(GUID, ForeignKey("institutions.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    institution = relationship("Institution", back_populates="users")


class UploadBatch(Base):
    __tablename__ = "upload_batches"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    institution_id = Column(GUID, ForeignKey("institutions.id"), nullable=False, index=True)
    academic_year = Column(String(20), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_checksum = Column(String(64), nullable=False, index=True)  # SHA-256
    status = Column(String(30), nullable=False, default="received")  # received, validating, completed, failed
    total_rows = Column(Integer, default=0, nullable=False)
    accepted_rows = Column(Integer, default=0, nullable=False)
    rejected_rows = Column(Integer, default=0, nullable=False)
    flagged_rows = Column(Integer, default=0, nullable=False)
    uploaded_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    institution = relationship("Institution", back_populates="upload_batches")
    row_results = relationship("UploadRowResult", back_populates="batch", cascade="all, delete-orphan")


class UploadRowResult(Base):
    __tablename__ = "upload_row_results"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    batch_id = Column(GUID, ForeignKey("upload_batches.id", ondelete="CASCADE"), nullable=False, index=True)
    row_number = Column(Integer, nullable=False)
    student_number = Column(String(100), nullable=True)
    apaar_token_masked = Column(String(30), nullable=True)
    rule_code = Column(String(60), nullable=True)
    severity = Column(String(20), nullable=False)  # accepted, error, warning, notice
    status = Column(String(30), nullable=False)  # accepted, rejected, flagged
    message = Column(String(500), nullable=False)
    action_taken = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    batch = relationship("UploadBatch", back_populates="row_results")


class Credential(Base):
    __tablename__ = "credentials"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    institution_id = Column(GUID, ForeignKey("institutions.id"), nullable=False)
    student_id = Column(GUID, ForeignKey("students.id"), nullable=False)
    admission_id = Column(GUID, ForeignKey("admissions.id"), nullable=False)
    opaque_reference = Column(String(64), unique=True, nullable=False, index=True)
    credential_type = Column(String(100), nullable=False, default="Enrolment Certificate")
    status = Column(String(30), nullable=False, default="valid")  # valid, revoked, expired
    jwt_token = Column(Text, nullable=False)
    qr_data = Column(Text, nullable=False)
    issued_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    revocation_reason = Column(String(255), nullable=True)

    student = relationship("Student", back_populates="credentials")
    admission = relationship("Admission", back_populates="credentials")
    institution = relationship("Institution")
