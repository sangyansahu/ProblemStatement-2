import hashlib
from datetime import datetime
from app.extensions import db
from app.models.student import Student
from app.models.change_history import RecordChangeHistory
from app.models.notification import Notification
from app.models.audit import AuditLog
from app.services.security_service import validate_apaar_format, decrypt_apaar

class VerificationAdapter:
    """
    Adapter interface for AICTE APAAR identity verification.
    Provides clear distinction between Simulated Verification (for sandbox/demo)
    and Authorized Official Registry API integration (when credentials become available).
    """

    @staticmethod
    def is_official_api_configured() -> bool:
        # Returns False unless official API endpoint and client credentials are configured
        return False

    @classmethod
    def execute_verification(cls, student: Student, mode: str = 'simulated') -> dict:
        """
        Executes verification workflow.
        Returns explicit status, source tag, and audit notes.
        """
        if not student.apaar_id_hmac and not student.apaar_id_encrypted:
            return {
                'status': 'not_submitted',
                'source': 'format_checker',
                'message': 'No APAAR identifier assigned to this student record.',
                'is_simulated': False
            }

        # Step 1: Format validation
        # Decrypt stored APAAR to verify format
        raw_apaar = decrypt_apaar(student.apaar_id_encrypted) if student.apaar_id_encrypted else None
        if raw_apaar:
            valid, msg = validate_apaar_format(raw_apaar)
            if not valid:
                return {
                    'status': 'mismatch_detected',
                    'source': 'format_checker',
                    'message': f"APAAR format validation failed: {msg}",
                    'is_simulated': False
                }

        # Step 2: Check official API vs Simulated Verification Adapter
        if cls.is_official_api_configured():
            # Future official endpoint call
            pass

        # Simulated Verification Mode with deterministic synthetic outcome
        # Deterministic based on student_id to ensure reliable test reproducibility
        h = int(hashlib.md5(student.student_id.encode('utf-8')).hexdigest(), 16)
        mod = h % 10

        if mod in [0, 1, 2, 3, 4, 5, 6]:
            status = 'verified'
            note = '[SIMULATED VERIFICATION] Record matched synthetic educational repository mock dataset.'
        elif mod in [7]:
            status = 'mismatch_detected'
            note = '[SIMULATED VERIFICATION] Student name or birth record mismatch flagged in simulated verification.'
        elif mod in [8]:
            status = 'requires_manual_review'
            note = '[SIMULATED VERIFICATION] Name variation detected against demographic mock database. Requires manual review.'
        else:
            status = 'unable_to_verify'
            note = '[SIMULATED VERIFICATION] Simulated lookup timed out or identifier unindexed in mock provider.'

        return {
            'status': status,
            'source': 'simulated',
            'message': note,
            'is_simulated': True,
            'timestamp': datetime.utcnow().isoformat()
        }

def trigger_student_verification(student_id_db: int, user_id: int = None, user_name: str = 'System') -> dict:
    student = Student.query.get(student_id_db)
    if not student:
        return {'success': False, 'error': 'Student not found'}

    res = VerificationAdapter.execute_verification(student)
    old_status = student.verification_status
    student.verification_status = res['status']
    student.verification_source = res['source']
    student.verification_notes = res['message']
    student.verified_at = datetime.utcnow()

    # Track history
    history = RecordChangeHistory(
        student_id=student.id,
        changed_by_user_id=user_id,
        changed_by_name=user_name,
        change_type='verification_update',
        field_name='verification_status',
        old_value=old_status,
        new_value=res['status'],
        reason=res['message'],
        timestamp=datetime.utcnow()
    )
    db.session.add(history)

    # Track audit
    audit = AuditLog(
        actor_id=user_id,
        actor_name=user_name,
        actor_role='system' if not user_id else 'reviewer',
        action='STUDENT_VERIFICATION_CHECK',
        target_type='student',
        target_id=str(student.id),
        details_json=f'{{"student_id": "{student.student_id}", "status": "{res["status"]}", "is_simulated": {str(res["is_simulated"]).lower()}}}',
        created_at=datetime.utcnow()
    )
    db.session.add(audit)

    db.session.commit()

    return {
        'success': True,
        'student_id': student.id,
        'verification_status': student.verification_status,
        'verification_source': student.verification_source,
        'verification_notes': student.verification_notes,
        'verified_at': student.verified_at.isoformat()
    }

def manual_verification_override(student_id_db: int, new_status: str, notes: str, user_id: int, user_name: str) -> dict:
    student = Student.query.get(student_id_db)
    if not student:
        return {'success': False, 'error': 'Student not found'}

    old_status = student.verification_status
    student.verification_status = new_status
    student.verification_source = 'manual_review'
    student.verification_notes = f"[MANUAL REVIEW OVERRIDE by {user_name}]: {notes}"
    student.verified_at = datetime.utcnow()

    history = RecordChangeHistory(
        student_id=student.id,
        changed_by_user_id=user_id,
        changed_by_name=user_name,
        change_type='manual_override',
        field_name='verification_status',
        old_value=old_status,
        new_value=new_status,
        reason=notes,
        timestamp=datetime.utcnow()
    )
    db.session.add(history)

    db.session.commit()

    return {
        'success': True,
        'student_id': student.id,
        'verification_status': student.verification_status,
        'verification_source': student.verification_source,
        'verification_notes': student.verification_notes,
        'verified_at': student.verified_at.isoformat()
    }
