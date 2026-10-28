import io
import csv
from datetime import datetime
from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.student import Student
from app.models.institution import Institution
from app.models.upload import UploadBatch
from app.models.duplicate_case import DuplicateReviewCase
from app.models.programme import Programme
from app.utils.auth_helper import get_current_user

reports_bp = Blueprint('reports', __name__, url_prefix='/api/v1/reports')

@reports_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_reports_summary():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    inst_id = user.institution_id if user.role == 'institute' else request.args.get('institution_id', type=int)

    # Student Query
    s_query = Student.query
    if inst_id:
        s_query = s_query.filter(Student.institution_id == inst_id)

    total_students = s_query.count()
    verified_count = s_query.filter(Student.verification_status == 'verified').count()
    pending_count = s_query.filter(Student.verification_status == 'pending').count()
    mismatch_count = s_query.filter(Student.verification_status == 'mismatch_detected').count()
    review_count = s_query.filter(Student.verification_status == 'requires_manual_review').count()
    unable_count = s_query.filter(Student.verification_status == 'unable_to_verify').count()
    unassigned_count = s_query.filter(Student.verification_status == 'not_submitted').count()

    # Programme distributions
    prog_data = db.session.query(
        Student.programme_name, db.func.count(Student.id)
    )
    if inst_id:
        prog_data = prog_data.filter(Student.institution_id == inst_id)
    prog_summary = [{'programme': p[0], 'count': p[1]} for p in prog_data.group_by(Student.programme_name).all()]

    # Academic Year distributions
    ay_data = db.session.query(
        Student.academic_year, db.func.count(Student.id)
    )
    if inst_id:
        ay_data = ay_data.filter(Student.institution_id == inst_id)
    ay_summary = [{'academic_year': a[0], 'count': a[1]} for a in ay_data.group_by(Student.academic_year).all()]

    # Duplicate cases
    dup_query = DuplicateReviewCase.query
    if inst_id:
        dup_query = dup_query.filter(
            (DuplicateReviewCase.institution_id == inst_id) |
            (DuplicateReviewCase.secondary_institution_id == inst_id)
        )
    open_dups = dup_query.filter(DuplicateReviewCase.status == 'open').count()
    resolved_dups = dup_query.filter(DuplicateReviewCase.status == 'resolved').count()

    return jsonify({
        'overview': {
            'total_students': total_students,
            'verified_records': verified_count,
            'pending_records': pending_count,
            'mismatch_records': mismatch_count,
            'requires_review': review_count,
            'unable_to_verify': unable_count,
            'not_submitted': unassigned_count,
            'open_duplicate_cases': open_dups,
            'resolved_duplicate_cases': resolved_dups,
            'verification_rate': round((verified_count / total_students * 100), 1) if total_students > 0 else 0
        },
        'by_programme': prog_summary,
        'by_academic_year': ay_summary
    }), 200

@reports_bp.route('/export/<report_type>', methods=['GET'])
@jwt_required()
def export_report_csv(report_type):
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    inst_id = user.institution_id if user.role == 'institute' else request.args.get('institution_id', type=int)

    output = io.StringIO()
    writer = csv.writer(output)

    if report_type == 'verification':
        writer.writerow(['Student ID', 'Student Name', 'Institution', 'Programme', 'APAAR (Masked)', 'Verification Status', 'Source', 'Notes'])
        query = Student.query
        if inst_id:
            query = query.filter(Student.institution_id == inst_id)
        for s in query.limit(2000).all():
            writer.writerow([
                s.student_id,
                s.student_name,
                s.institution.name if s.institution else 'N/A',
                s.programme_name,
                s.apaar_id_masked or 'Not Assigned',
                s.verification_status,
                s.verification_source,
                s.verification_notes or ''
            ])
        filename = f"verification_report_{datetime.utcnow().strftime('%Y%m%d')}.csv"

    elif report_type == 'duplicates':
        writer.writerow(['Case Ref', 'Issue Type', 'Primary Institution', 'Secondary Institution', 'Student ID', 'Student Name', 'Status', 'Severity', 'Resolution Decision'])
        query = DuplicateReviewCase.query
        if inst_id:
            query = query.filter((DuplicateReviewCase.institution_id == inst_id) | (DuplicateReviewCase.secondary_institution_id == inst_id))
        for d in query.all():
            writer.writerow([
                d.case_reference,
                d.issue_type,
                d.institution.name if d.institution else 'N/A',
                d.secondary_institution.name if d.secondary_institution else 'N/A',
                d.student_id,
                d.student_name or '',
                d.status,
                d.severity,
                d.resolution_decision or 'Unresolved'
            ])
        filename = f"duplicate_conflicts_report_{datetime.utcnow().strftime('%Y%m%d')}.csv"

    elif report_type == 'intake':
        writer.writerow(['Institution', 'Code', 'Programme', 'Branch', 'Level', 'Academic Year', 'Approved Intake', 'Supernumerary Intake', 'Enrolled Students', 'Utilization Rate (%)', 'Discrepancy Status'])
        query = Programme.query
        if inst_id:
            query = query.filter(Programme.institution_id == inst_id)
        for p in query.all():
            d = p.to_dict()
            writer.writerow([
                d['institution_name'],
                d['programme_code'],
                d['programme_name'],
                d['branch_or_department'],
                d['level'],
                d['academic_year'],
                d['approved_intake'],
                d['supernumerary_intake'],
                d['actual_enrolment'],
                f"{d['utilization_rate']}%",
                d['discrepancy_status']
            ])
        filename = f"enrolment_intake_report_{datetime.utcnow().strftime('%Y%m%d')}.csv"

    else:
        return jsonify({'error': 'Unknown report type. Allowed: verification, duplicates, intake'}), 400

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )
