import uuid
from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field, ConfigDict


# Auth & User
class UserBase(BaseModel):
    username: str
    email: str
    full_name: str
    role: str
    institution_id: Optional[uuid.UUID] = None


class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenPayload(BaseModel):
    sub: str
    username: str
    role: str
    institution_id: Optional[str] = None
    exp: Optional[int] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# Institution & Programme
class InstitutionResponse(BaseModel):
    id: uuid.UUID
    aicte_code: str
    name: str
    state: str
    district: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProgrammeResponse(BaseModel):
    id: uuid.UUID
    institution_id: uuid.UUID
    course_code: str
    programme_name: str
    academic_year: str
    approved_intake: int
    approved_extra_seats: int
    enrolled_count: Optional[int] = 0
    utilisation_pct: Optional[float] = 0.0

    model_config = ConfigDict(from_attributes=True)


# Student & Admission
class AdmissionResponse(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    programme_id: uuid.UUID
    institution_id: uuid.UUID
    student_number: str
    academic_year: str
    seat_category: str
    admission_date: Optional[str] = None
    status: str
    course_code: Optional[str] = None
    programme_name: Optional[str] = None
    institution_name: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StudentDetailResponse(BaseModel):
    id: uuid.UUID
    apaar_token_masked: str
    name: Optional[str] = None
    admissions: List[AdmissionResponse] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StudentPatchRequest(BaseModel):
    name: Optional[str] = None
    seat_category: Optional[str] = None
    status: Optional[str] = None  # permitted status change


# Uploads
class UploadBatchResponse(BaseModel):
    id: uuid.UUID
    institution_id: uuid.UUID
    academic_year: str
    file_name: str
    file_checksum: str
    status: str
    total_rows: int
    accepted_rows: int
    rejected_rows: int
    flagged_rows: int
    uploaded_by: str
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UploadRowResultResponse(BaseModel):
    id: uuid.UUID
    batch_id: uuid.UUID
    row_number: int
    student_number: Optional[str] = None
    apaar_token_masked: Optional[str] = None
    rule_code: Optional[str] = None
    severity: str
    status: str
    message: str
    action_taken: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# Validation Cases
class ValidationCaseResponse(BaseModel):
    id: uuid.UUID
    institution_id: uuid.UUID
    institution_name: Optional[str] = None
    programme_id: Optional[uuid.UUID] = None
    course_code: Optional[str] = None
    student_id: Optional[uuid.UUID] = None
    rule_code: str
    severity: str
    academic_year: str
    message: str
    status: str
    resolution_note: Optional[str] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResolveCaseRequest(BaseModel):
    resolution_note: str = Field(..., min_length=3, description="Required justification note")
    action: Optional[str] = "resolve"  # resolve or dismiss


# Credential Verification
class VerificationRequestCreate(BaseModel):
    admission_id: uuid.UUID


class CredentialResponse(BaseModel):
    id: uuid.UUID
    institution_id: uuid.UUID
    student_id: uuid.UUID
    admission_id: uuid.UUID
    opaque_reference: str
    credential_type: str
    status: str
    qr_data: str
    issued_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PublicVerifyResult(BaseModel):
    issuing_institution: str
    credential_type: str
    status: str  # valid, revoked, expired, not_found
    issued_at: Optional[str] = None
    verified_at: str


# Analytics
class EnrolmentYearStat(BaseModel):
    academic_year: str
    enrolment_count: int


class NationalAnalyticsResponse(BaseModel):
    institutions_reporting: int
    students_reported: int
    records_flagged: int
    pending_reviews: int
    total_approved_intake: int
    overall_utilisation_pct: float
    enrolment_by_year: List[EnrolmentYearStat]


class InstitutionAnalyticsResponse(BaseModel):
    institution_id: uuid.UUID
    institution_name: str
    total_reported_enrolment: int
    approved_intake: int
    capacity_utilisation_pct: float
    pending_validation_cases: int
    programmes: List[ProgrammeResponse]


# Audit Log
class AuditLogResponse(BaseModel):
    id: uuid.UUID
    actor_id: str
    actor_role: str
    institution_id: Optional[uuid.UUID] = None
    action: str
    target_reference: str
    outcome: str
    details: Optional[str] = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
