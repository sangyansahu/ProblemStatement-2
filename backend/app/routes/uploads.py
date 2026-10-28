import io
import csv
import json
from datetime import datetime
from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.upload import UploadBatch
from app.services.csv_import_service import (
    get_csv_template_content,
    parse_and_validate_csv,
    commit_csv_import
)
from app.utils.auth_helper import get_current_user

uploads_bp = Blueprint('uploads', __name__, url_prefix='/api/v1/uploads')

@uploads_bp.route('/template', methods=['GET'])
def download_template():
    csv_text = get_csv_template_content()
    return Response(
        csv_text,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=aicte_student_upload_template.csv'}
    )

@uploads_bp.route('/preview', methods=['POST'])
@jwt_required()
def preview_upload():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'No file part in request'}), 400

    file = request.files['file']
    if not file or file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not file.filename.lower().endswith('.csv'):
        return jsonify({'error': 'Only .csv format files are accepted'}), 400

    # Determine institution context strictly
    if user.role == 'institute':
        if not user.institution_id:
            return jsonify({'error': 'User is not assigned to an institution'}), 403
        institution_id = user.institution_id
    else:
        inst_id = request.form.get('institution_id', type=int)
        if not inst_id:
            return jsonify({'error': 'institution_id is required for administrative upload'}), 400
        institution_id = inst_id

    file_bytes = file.read()
    if len(file_bytes) > 16 * 1024 * 1024:
        return jsonify({'error': 'File exceeds maximum 16MB limit'}), 400

    preview_res = parse_and_validate_csv(file_bytes, institution_id)
    if not preview_res.get('success'):
        return jsonify(preview_res), 400

    preview_res['file_name'] = file.filename
    preview_res['file_size_bytes'] = len(file_bytes)

    return jsonify(preview_res), 200

@uploads_bp.route('/commit', methods=['POST'])
@jwt_required()
def commit_upload():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json() or {}
    file_name = data.get('file_name', 'students_import.csv')
    file_size = data.get('file_size_bytes', 0)
    row_results = data.get('row_results', [])

    if not row_results:
        return jsonify({'error': 'No validation rows provided to commit'}), 400

    if user.role == 'institute':
        if not user.institution_id:
            return jsonify({'error': 'User not assigned to an institution'}), 403
        institution_id = user.institution_id
    else:
        institution_id = data.get('institution_id')
        if not institution_id:
            return jsonify({'error': 'institution_id is required'}), 400

    try:
        commit_res = commit_csv_import(
            institution_id=institution_id,
            user_id=user.id,
            file_name=file_name,
            file_size=file_size,
            row_results=row_results
        )
        return jsonify(commit_res), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"Failed to commit import batch: {str(e)}"}), 500

@uploads_bp.route('/batches', methods=['GET'])
@jwt_required()
def list_batches():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    query = UploadBatch.query
    if user.role == 'institute':
        query = query.filter(UploadBatch.institution_id == user.institution_id)
    else:
        inst_id = request.args.get('institution_id', type=int)
        if inst_id:
            query = query.filter(UploadBatch.institution_id == inst_id)

    batches = query.order_by(UploadBatch.created_at.desc()).limit(100).all()
    return jsonify({'batches': [b.to_dict() for b in batches]}), 200

@uploads_bp.route('/batches/<int:batch_id>', methods=['GET'])
@jwt_required()
def get_batch(batch_id):
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    batch = UploadBatch.query.get(batch_id)
    if not batch:
        return jsonify({'error': 'Upload batch not found'}), 404

    if user.role == 'institute' and batch.institution_id != user.institution_id:
        return jsonify({'error': 'Forbidden'}), 403

    return jsonify({'batch': batch.to_dict(include_errors=True)}), 200

@uploads_bp.route('/batches/<int:batch_id>/error-report', methods=['GET'])
@jwt_required()
def download_batch_error_report(batch_id):
    user = get_current_user()
    batch = UploadBatch.query.get(batch_id)
    if not batch:
        return jsonify({'error': 'Upload batch not found'}), 404

    if user.role == 'institute' and batch.institution_id != user.institution_id:
        return jsonify({'error': 'Forbidden'}), 403

    errors = []
    if batch.error_report_json:
        try:
            errors = json.loads(batch.error_report_json)
        except Exception:
            errors = []

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Row Number', 'Student ID', 'Field', 'Error Message', 'Suggested Correction'])
    for err in errors:
        writer.writerow([
            err.get('row_number', ''),
            err.get('student_id', ''),
            err.get('field', ''),
            err.get('error', ''),
            err.get('suggestion', '')
        ])

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=error_report_{batch.batch_id}.csv'}
    )
