"""Initial schema migration for AICTE APAAR Platform

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-10-28 23:30:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 1. Institutions
    op.create_table(
        "institutions",
        sa.Column("id", sa.CHAR(36), primary_key=True),
        sa.Column("aicte_code", sa.String(50), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("state", sa.String(100), nullable=False),
        sa.Column("district", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_institutions_aicte_code", "institutions", ["aicte_code"])

    # 2. Programmes
    op.create_table(
        "programmes",
        sa.Column("id", sa.CHAR(36), primary_key=True),
        sa.Column("institution_id", sa.CHAR(36), sa.ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("course_code", sa.String(50), nullable=False),
        sa.Column("programme_name", sa.String(255), nullable=False),
        sa.Column("academic_year", sa.String(20), nullable=False),
        sa.Column("approved_intake", sa.Integer(), nullable=False, default=60),
        sa.Column("approved_extra_seats", sa.Integer(), nullable=False, default=0),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("institution_id", "course_code", "academic_year", name="uq_programme_inst_course_year"),
        sa.CheckConstraint("approved_intake >= 0", name="chk_approved_intake_non_negative"),
        sa.CheckConstraint("approved_extra_seats >= 0", name="chk_approved_extra_seats_non_negative"),
    )

    # 3. Students
    op.create_table(
        "students",
        sa.Column("id", sa.CHAR(36), primary_key=True),
        sa.Column("apaar_id_token", sa.String(64), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_students_apaar_id_token", "students", ["apaar_id_token"])

    # 4. Admissions
    op.create_table(
        "admissions",
        sa.Column("id", sa.CHAR(36), primary_key=True),
        sa.Column("student_id", sa.CHAR(36), sa.ForeignKey("students.id"), nullable=False),
        sa.Column("programme_id", sa.CHAR(36), sa.ForeignKey("programmes.id"), nullable=False),
        sa.Column("institution_id", sa.CHAR(36), sa.ForeignKey("institutions.id"), nullable=False),
        sa.Column("student_number", sa.String(100), nullable=False),
        sa.Column("academic_year", sa.String(20), nullable=False),
        sa.Column("seat_category", sa.String(50), nullable=False),
        sa.Column("admission_date", sa.String(30), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, default="enrolled"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("programme_id", "academic_year", "student_number", name="uq_admission_prog_year_num"),
    )
    op.create_index("ix_admissions_student_id", "admissions", ["student_id"])
    op.create_index("ix_admissions_prog_status", "admissions", ["programme_id", "status"])
    op.create_index("ix_admissions_institution_id", "admissions", ["institution_id"])

    # 5. Validation Cases
    op.create_table(
        "validation_cases",
        sa.Column("id", sa.CHAR(36), primary_key=True),
        sa.Column("institution_id", sa.CHAR(36), sa.ForeignKey("institutions.id"), nullable=False),
        sa.Column("programme_id", sa.CHAR(36), sa.ForeignKey("programmes.id"), nullable=True),
        sa.Column("student_id", sa.CHAR(36), sa.ForeignKey("students.id"), nullable=True),
        sa.Column("rule_code", sa.String(60), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("academic_year", sa.String(20), nullable=False),
        sa.Column("message", sa.String(500), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, default="open"),
        sa.Column("resolution_note", sa.Text(), nullable=True),
        sa.Column("resolved_by", sa.String(100), nullable=True),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_validation_cases_institution_id", "validation_cases", ["institution_id"])

    # 6. Audit Logs
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.CHAR(36), primary_key=True),
        sa.Column("actor_id", sa.String(100), nullable=False),
        sa.Column("actor_role", sa.String(50), nullable=False),
        sa.Column("institution_id", sa.CHAR(36), nullable=True),
        sa.Column("action", sa.String(80), nullable=False),
        sa.Column("target_reference", sa.String(255), nullable=False),
        sa.Column("outcome", sa.String(20), nullable=False),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_audit_logs_timestamp", "audit_logs", ["timestamp"])

    # 7. Users
    op.create_table(
        "users",
        sa.Column("id", sa.CHAR(36), primary_key=True),
        sa.Column("keycloak_id", sa.String(100), nullable=True, unique=True),
        sa.Column("username", sa.String(100), nullable=False, unique=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("institution_id", sa.CHAR(36), sa.ForeignKey("institutions.id"), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    # 8. Upload Batches
    op.create_table(
        "upload_batches",
        sa.Column("id", sa.CHAR(36), primary_key=True),
        sa.Column("institution_id", sa.CHAR(36), sa.ForeignKey("institutions.id"), nullable=False),
        sa.Column("academic_year", sa.String(20), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_checksum", sa.String(64), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, default="received"),
        sa.Column("total_rows", sa.Integer(), nullable=False, default=0),
        sa.Column("accepted_rows", sa.Integer(), nullable=False, default=0),
        sa.Column("rejected_rows", sa.Integer(), nullable=False, default=0),
        sa.Column("flagged_rows", sa.Integer(), nullable=False, default=0),
        sa.Column("uploaded_by", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_upload_batches_checksum", "upload_batches", ["file_checksum"])

    # 9. Upload Row Results
    op.create_table(
        "upload_row_results",
        sa.Column("id", sa.CHAR(36), primary_key=True),
        sa.Column("batch_id", sa.CHAR(36), sa.ForeignKey("upload_batches.id", ondelete="CASCADE"), nullable=False),
        sa.Column("row_number", sa.Integer(), nullable=False),
        sa.Column("student_number", sa.String(100), nullable=True),
        sa.Column("apaar_token_masked", sa.String(30), nullable=True),
        sa.Column("rule_code", sa.String(60), nullable=True),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("message", sa.String(500), nullable=False),
        sa.Column("action_taken", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_upload_row_results_batch_id", "upload_row_results", ["batch_id"])

    # 10. Credentials
    op.create_table(
        "credentials",
        sa.Column("id", sa.CHAR(36), primary_key=True),
        sa.Column("institution_id", sa.CHAR(36), sa.ForeignKey("institutions.id"), nullable=False),
        sa.Column("student_id", sa.CHAR(36), sa.ForeignKey("students.id"), nullable=False),
        sa.Column("admission_id", sa.CHAR(36), sa.ForeignKey("admissions.id"), nullable=False),
        sa.Column("opaque_reference", sa.String(64), nullable=False, unique=True),
        sa.Column("credential_type", sa.String(100), nullable=False, default="Enrolment Certificate"),
        sa.Column("status", sa.String(30), nullable=False, default="valid"),
        sa.Column("jwt_token", sa.Text(), nullable=False),
        sa.Column("qr_data", sa.Text(), nullable=False),
        sa.Column("issued_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column("revocation_reason", sa.String(255), nullable=True),
    )
    op.create_index("ix_credentials_opaque_reference", "credentials", ["opaque_reference"])


def downgrade():
    op.drop_table("credentials")
    op.drop_table("upload_row_results")
    op.drop_table("upload_batches")
    op.drop_table("users")
    op.drop_table("audit_logs")
    op.drop_table("validation_cases")
    op.drop_table("admissions")
    op.drop_table("students")
    op.drop_table("programmes")
    op.drop_table("institutions")
