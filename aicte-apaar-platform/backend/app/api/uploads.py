import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import UploadBatch, UploadRowResult, Institution
from app.schemas import UploadBatchResponse, UploadRowResultResponse
from app.security import (
    require_role, AuthenticatedUser, check_institution_access
)
from app.services.upload_processor import process_student_upload

router = APIRouter(prefix="/uploads", tags=["Uploads"])


@router.post("", response_model=UploadBatchResponse)
async def upload_student_records(
    file: UploadFile = File(...),
    academic_year: str = Form("2025-26"),
    institution_id: Optional[uuid.UUID] = Form(None),
    current_user: AuthenticatedUser = Depends(
        require_role("institution_admin", "institution_operator", "aicte_admin")
    ),
    db: Session = Depends(get_db)
):
    """Synchronously upload and validate a student enrolment CSV/XLSX file.
    Idempotent on identical checksum. Enforces institution scope and row locking.
    """
    target_inst_id = institution_id
    if not current_user.is_aicte_admin:
        if not current_user.institution_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not affiliated with an institution"
            )
        target_inst_id = current_user.institution_id

    if not target_inst_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Institution identifier is required for upload"
        )

    check_institution_access(current_user, target_inst_id)

    # Read content
    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty"
        )

    try:
        batch, results = process_student_upload(
            db=db,
            institution_id=target_inst_id,
            file_content=content,
            file_name=file.filename or "upload.csv",
            academic_year=academic_year.strip(),
            uploaded_by=current_user.username
        )
        return UploadBatchResponse.model_validate(batch)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload processing failed: {str(e)}"
        )


@router.get("/{id}", response_model=UploadBatchResponse)
def get_upload_batch(
    id: uuid.UUID,
    current_user: AuthenticatedUser = Depends(
        require_role("institution_admin", "institution_operator", "aicte_admin", "auditor")
    ),
    db: Session = Depends(get_db)
):
    """Retrieve upload batch metadata. Enforces institution scope."""
    batch = db.query(UploadBatch).filter(UploadBatch.id == id).first()
    if not batch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload batch not found")

    check_institution_access(current_user, batch.institution_id)
    return UploadBatchResponse.model_validate(batch)


@router.get("/{id}/results", response_model=List[UploadRowResultResponse])
def get_upload_results(
    id: uuid.UUID,
    status_filter: Optional[str] = None,
    current_user: AuthenticatedUser = Depends(
        require_role("institution_admin", "institution_operator", "aicte_admin", "auditor")
    ),
    db: Session = Depends(get_db)
):
    """Retrieve row-level results for a batch."""
    batch = db.query(UploadBatch).filter(UploadBatch.id == id).first()
    if not batch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload batch not found")

    check_institution_access(current_user, batch.institution_id)

    query = db.query(UploadRowResult).filter(UploadRowResult.batch_id == id)
    if status_filter:
        query = query.filter(UploadRowResult.status == status_filter.strip().lower())

    results = query.order_by(UploadRowResult.row_number.asc()).all()
    return [UploadRowResultResponse.model_validate(r) for r in results]
