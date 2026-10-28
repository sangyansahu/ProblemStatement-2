from datetime import datetime
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.institution import Institution
from app.models.student import Student
from app.models.upload import UploadBatch
from app.models.duplicate_case import DuplicateReviewCase
from app.models.programme import Programme
from app.models.audit import AuditLog
from app.models.user import User
from app.utils.auth_helper import get_current_user

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/v1/dashboard')

@dashboard_bp.route('/metrics', methods=['GET'])
@jwt_required()
def get_dashboard_metrics():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    if user.role == 'institute':
        inst_id = user.institution_id
        if not inst_id:
            return jsonify({'kpis': {}, 'recent_uploads': [], 'recent_activity': []}), 200

        total_students = Student.query.filter_by(institution_id=inst_id).count()
        verified_count = Student.query.filter_by(institution_id=inst_id, verification_status='verified').count()
        pending_count = Student.query.filter_by(institution_id=inst_id, verification_status='pending').count()
        invalid_count = Student.query.filter(
            Student.institution_id == inst_id,
            Student.verification_status.in_(['mismatch_detected', 'unable_to_verify', 'requires_manual_review', 'rejected'])
        ).count()
        duplicate_candidates = DuplicateReviewCase.query.filter(
            (DuplicateReviewCase.institution_id == inst_id) |
            (DuplicateReviewCase.secondary_institution_id == inst_id),
            DuplicateReviewCase.status.in_(['open', 'pending_institution_correction'])
        ).count()

        latest_upload = UploadBatch.query.filter_by(institution_id=inst_id).order_by(UploadBatch.created_at.desc()).first()
        recent_uploads = [u.to_dict() for u in UploadBatch.query.filter_by(institution_id=inst_id).order_by(UploadBatch.created_at.desc()).limit(5).all()]
        correction_needed = [s.to_dict() for s in Student.query.filter(
            Student.institution_id == inst_id,
            Student.verification_status.in_(['mismatch_detected', 'requires_manual_review'])
        ).limit(6).all()]
        open_duplicates = [dc.to_dict() for dc in DuplicateReviewCase.query.filter(
            (DuplicateReviewCase.institution_id == inst_id) | (DuplicateReviewCase.secondary_institution_id == inst_id),
            DuplicateReviewCase.status == 'open'
        ).limit(5).all()]

        return jsonify({
            'role': 'institute',
            'kpis': {
                'total_students': total_students,
                'verified_records': verified_count,
                'pending_verification': pending_count,
                'invalid_records': invalid_count,
                'duplicate_candidates': duplicate_candidates,
                'recent_upload_status': latest_upload.status if latest_upload else 'No uploads yet',
                'recent_upload_batch': latest_upload.batch_id if latest_upload else 'N/A'
            },
            'recent_uploads': recent_uploads,
            'records_requiring_correction': correction_needed,
            'open_duplicates': open_duplicates,
            'verification_distribution': {
                'verified': verified_count,
                'pending': pending_count,
                'mismatch': invalid_count,
                'not_submitted': Student.query.filter_by(institution_id=inst_id, verification_status='not_submitted').count()
            }
        }), 200

    elif user.role == 'admin':
        total_institutions = Institution.query.count()
        total_students = Student.query.count()
        verified_count = Student.query.filter_by(verification_status='verified').count()
        pending_count = Student.query.filter_by(verification_status='pending').count()
        potential_duplicates = DuplicateReviewCase.query.filter(DuplicateReviewCase.status != 'resolved').count()
        attention_uploads = UploadBatch.query.filter(UploadBatch.invalid_rows > 0).count()

        recent_institutions = [i.to_dict(include_stats=True) for i in Institution.query.order_by(Institution.updated_at.desc()).limit(6).all()]
        recent_uploads = [u.to_dict() for u in UploadBatch.query.order_by(UploadBatch.created_at.desc()).limit(6).all()]
        verification_queue = [s.to_dict() for s in Student.query.filter(Student.verification_status.in_(['pending', 'requires_manual_review'])).limit(6).all()]
        duplicate_queue = [dc.to_dict() for dc in DuplicateReviewCase.query.filter(DuplicateReviewCase.status == 'open').limit(5).all()]

        return jsonify({
            'role': 'admin',
            'kpis': {
                'total_institutions': total_institutions,
                'accessible_students': total_students,
                'verified_records': verified_count,
                'pending_verification': pending_count,
                'potential_duplicates': potential_duplicates,
                'uploads_requiring_attention': attention_uploads
            },
            'recent_institutions': recent_institutions,
            'recent_uploads': recent_uploads,
            'verification_queue': verification_queue,
            'duplicate_queue': duplicate_queue,
            'verification_distribution': {
                'verified': verified_count,
                'pending': pending_count,
                'mismatch': Student.query.filter(Student.verification_status.in_(['mismatch_detected', 'requires_manual_review', 'unable_to_verify'])).count(),
                'not_submitted': Student.query.filter_by(verification_status='not_submitted').count()
            }
        }), 200

    else: # super_admin
        total_institutions = Institution.query.count()
        active_institutions = Institution.query.filter_by(status='active').count()
        total_students = Student.query.count()
        verified_count = Student.query.filter_by(verification_status='verified').count()
        pending_count = Student.query.filter_by(verification_status='pending').count()
        duplicate_conflicts = DuplicateReviewCase.query.filter(DuplicateReviewCase.status != 'resolved').count()
        failed_import_batches = UploadBatch.query.filter(UploadBatch.status == 'failed').count()
        records_requiring_review = Student.query.filter(Student.verification_status.in_(['requires_manual_review', 'mismatch_detected'])).count()

        recent_uploads = [u.to_dict() for u in UploadBatch.query.order_by(UploadBatch.created_at.desc()).limit(6).all()]
        recent_activity = [a.to_dict() for a in AuditLog.query.order_by(AuditLog.created_at.desc()).limit(8).all()]
        duplicate_cases = [dc.to_dict() for dc in DuplicateReviewCase.query.filter(DuplicateReviewCase.status == 'open').limit(6).all()]
        
        # Enrolment intake stats
        programmes = Programme.query.all()
        total_approved_intake = sum(p.approved_intake for p in programmes)

        return jsonify({
            'role': 'super_admin',
            'kpis': {
                'total_institutions': total_institutions,
                'active_institutions': active_institutions,
                'total_students': total_students,
                'verified_records': verified_count,
                'pending_verification': pending_count,
                'potential_duplicate_conflicts': duplicate_conflicts,
                'failed_import_batches': failed_import_batches,
                'records_requiring_review': records_requiring_review,
                'total_approved_intake': total_approved_intake
            },
            'recent_uploads': recent_uploads,
            'recent_activity': recent_activity,
            'duplicate_cases': duplicate_cases,
            'verification_distribution': {
                'verified': verified_count,
                'pending': pending_count,
                'requires_review': records_requiring_review,
                'not_submitted': Student.query.filter_by(verification_status='not_submitted').count()
            }
        }), 200
