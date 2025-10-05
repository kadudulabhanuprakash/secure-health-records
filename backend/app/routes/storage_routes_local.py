from flask import Blueprint, request, send_file, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import cross_origin
from werkzeug.utils import secure_filename
from io import BytesIO
from datetime import datetime
from backend.app.models import db, Record, AccessLog
from backend.app.blockchain import log_access
import os

storage_bp = Blueprint('storage', __name__)

# Local storage configuration
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@storage_bp.route('/upload', methods=['POST', 'OPTIONS'])
@cross_origin()
@jwt_required()
def upload_file():
    """Upload file to local storage + save metadata to SQL DB."""
    if request.method == 'OPTIONS':
        return '', 200
    
    identity = get_jwt_identity()
    email, role = identity.split(':')
    current_user = {'email': email, 'role': role}
    
    file = request.files.get('file')
    patient_email = request.form.get('patientEmail', current_user['email'])

    if not file:
        return jsonify({"error": "No file provided"}), 400
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed. Allowed: pdf, docx, txt"}), 400

    filename = secure_filename(file.filename)
    local_filename = f"{patient_email}_{filename}"
    file_path = os.path.join(UPLOAD_FOLDER, local_filename)

    try:
        file.save(file_path)
        record = Record(
            patient_id=patient_email,
            filename=local_filename,
            blob_url=f"/uploads/{local_filename}",
            uploaded_at=datetime.utcnow()
        )
        db.session.add(record)
        db.session.commit()
        log_access(current_user['email'], local_filename, 'upload')
        return jsonify({
            "message": "File uploaded successfully",
            "record_id": record.id,
            "filename": local_filename,
            "patient_id": patient_email
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

@storage_bp.route('/list', methods=['GET', 'OPTIONS'])
@cross_origin()
@jwt_required()
def list_files():
    """List files for a patient (by email) from local storage + DB metadata."""
    if request.method == 'OPTIONS':
        return '', 200
    
    identity = get_jwt_identity()
    email, role = identity.split(':')
    current_user = {'email': email, 'role': role}
    
    patient_email = request.args.get('patient', current_user['email'])

    try:
        records = Record.query.filter_by(patient_id=patient_email).all()
        if current_user['role'] == 'doctor' and patient_email != current_user['email']:
            log_access(current_user['email'], patient_email, 'list')
        return jsonify({
            "files": [
                {
                    "id": r.id,
                    "patient_id": r.patient_id,
                    "filename": r.filename,
                    "upload_time": r.uploaded_at.isoformat()
                } for r in records
            ]
        }), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch records: {str(e)}"}), 500

@storage_bp.route('/download/<path:filename>', methods=['GET'])
@jwt_required()
def download_file(filename):
    """Download file from local storage + log access."""
    identity = get_jwt_identity()
    email, role = identity.split(':')
    current_user = {'email': email, 'role': role}
    
    try:
        record = Record.query.filter_by(filename=filename).first()
        if not record:
            return jsonify({"error": "Record not found"}), 404
        log = AccessLog(record_id=record.id, accessed_by=current_user['email'], access_time=datetime.utcnow())
        db.session.add(log)
        db.session.commit()
        if current_user['role'] == 'doctor' or not filename.startswith(current_user['email'] + '_'):
            log_access(current_user['email'], filename, 'download')
        
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found on disk"}), 404
            
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": f"Download failed: {str(e)}"}), 500

@storage_bp.route('/preview/<path:filename>', methods=['GET'])
@jwt_required()
def preview_file(filename):
    """Preview file content from local storage + log access."""
    identity = get_jwt_identity()
    email, role = identity.split(':')
    current_user = {'email': email, 'role': role}
    
    try:
        record = Record.query.filter_by(filename=filename).first()
        if not record:
            return jsonify({"error": "Record not found"}), 404
        log = AccessLog(record_id=record.id, accessed_by=current_user['email'], access_time=datetime.utcnow())
        db.session.add(log)
        db.session.commit()
        if current_user['role'] == 'doctor' or not filename.startswith(current_user['email'] + '_'):
            log_access(current_user['email'], filename, 'preview')
        
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found on disk"}), 404
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({"content": content}), 200
    except Exception as e:
        return jsonify({"error": f"Preview failed: {str(e)}"}), 500

@storage_bp.route('/access-logs/<patient_id>', methods=['GET'])
@jwt_required()
def access_logs(patient_id):
    """Get access logs for a patient's records."""
    identity = get_jwt_identity()
    email, role = identity.split(':')
    current_user = {'email': email, 'role': role}
    
    try:
        records = Record.query.filter_by(patient_id=patient_id).all()
        if not records:
            return jsonify({"message": "No records found for this patient"}), 404
        logs = AccessLog.query.filter(AccessLog.record_id.in_([r.id for r in records])).all()
        if current_user['role'] == 'doctor' and patient_id != current_user['email']:
            log_access(current_user['email'], patient_id, 'access_logs')
        return jsonify([
            {
                "record_id": log.record_id,
                "accessed_by": log.accessed_by,
                "access_time": log.access_time.isoformat()
            } for log in logs
        ]), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch access logs: {str(e)}"}), 500

@storage_bp.route('/records', methods=['GET'])
@jwt_required()
def list_all_records():
    """List all records (for testing purposes - requires authentication)."""
    identity = get_jwt_identity()
    email, role = identity.split(':')
    current_user = {'email': email, 'role': role}
    
    try:
        records = Record.query.all()
        return jsonify({
            "files": [
                {
                    "id": r.id,
                    "patient_id": r.patient_id,
                    "filename": r.filename,
                    "upload_time": r.uploaded_at.isoformat()
                } for r in records
            ]
        }), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch records: {str(e)}"}), 500
