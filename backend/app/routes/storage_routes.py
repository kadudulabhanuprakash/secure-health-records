# File: backend/app/routes/storage_routes.py
from flask import Blueprint, request, send_file, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from azure.storage.blob import BlobServiceClient
from werkzeug.utils import secure_filename
from io import BytesIO
from datetime import datetime
from backend.app.models import db, Record, AccessLog
#from backend.app.blockchain import log_access  # SKIPPED for deployment
import os

storage_bp = Blueprint('storage', __name__)

# Global variables initialized later
blob_service_client = None
container_client = None
container_name = "patient-records"

def init_storage():
    """Initialize Azure Blob Storage connection after .env is loaded."""
    global blob_service_client, container_client
    if blob_service_client is not None:
        return  # Already initialized

    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_string:
        raise ValueError("storage_routes.py - AZURE_STORAGE_CONNECTION_STRING is not set in .env file")
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    # Ensure container exists
    try:
        container_client.create_container()
        print("storage_routes.py - Container created:", container_name)
    except Exception as e:
        print("storage_routes.py - Container creation skipped:", str(e))

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_identity(identity_str):
    """Parse string identity to dict."""
    email, role = identity_str.split(':')
    return {'email': email, 'role': role}

@storage_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    init_storage()  # Ensure initialized

    identity_str = get_jwt_identity()  # String like "email:role"
    current_user = parse_identity(identity_str)
    print(f"storage_routes.py - upload_file: Current user: {current_user}")
    file = request.files.get('file')
    patient_email = request.form.get('patientEmail', current_user['email'])

    if not file:
        return jsonify({"error": "No file provided"}), 422
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 422
    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed. Allowed: pdf, docx, txt"}), 422

    filename = secure_filename(file.filename)
    blob_name = f"{patient_email}/{filename}"
    print(f"storage_routes.py - upload_file: Uploading {blob_name} for {patient_email}")

    try:
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(file, overwrite=True)
        record = Record(
            patient_id=patient_email,
            filename=blob_name,
            blob_url=f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{blob_name}",
            uploaded_at=datetime.utcnow()
        )
        db.session.add(record)
        db.session.commit()
        # log_access(current_user['email'], blob_name, 'upload')  # SKIPPED for deployment
        print(f"storage_routes.py - SKIPPED blockchain log for upload: {current_user['email']} on {blob_name}")
        return jsonify({
            "message": "File uploaded successfully",
            "record_id": record.id,
            "filename": blob_name,
            "patient_id": patient_email
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

@storage_bp.route('/list', methods=['GET'])
@jwt_required()
def list_files():
    # No blob client needed for list (DB only), but initialize for consistency
    init_storage()

    identity_str = get_jwt_identity()  # String like "email:role"
    current_user = parse_identity(identity_str)
    print(f"storage_routes.py - list_files: Current user: {current_user}")
    patient_email = request.args.get('patient', current_user['email'])

    try:
        records = Record.query.filter_by(patient_id=patient_email).all()
        if current_user['role'] == 'doctor' and patient_email != current_user['email']:
            # log_access(current_user['email'], patient_email, 'list')  # SKIPPED for deployment
            print(f"storage_routes.py - SKIPPED blockchain log for list: {current_user['email']} on {patient_email}")
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
    init_storage()

    identity_str = get_jwt_identity()  # String like "email:role"
    current_user = parse_identity(identity_str)
    try:
        record = Record.query.filter_by(filename=filename).first()
        if not record:
            return jsonify({"error": "Record not found"}), 404
        log = AccessLog(record_id=record.id, accessed_by=current_user['email'], access_time=datetime.utcnow())
        db.session.add(log)
        db.session.commit()
        if current_user['role'] == 'doctor' or not filename.startswith(current_user['email'] + '/'):
            # log_access(current_user['email'], filename, 'download')  # SKIPPED for deployment
            print(f"storage_routes.py - SKIPPED blockchain log for download: {current_user['email']} on {filename}")
        blob_client = container_client.get_blob_client(filename)
        blob_data = blob_client.download_blob().readall()
        return send_file(
            BytesIO(blob_data),
            download_name=filename.split('/')[-1],
            as_attachment=True
        )
    except Exception as e:
        return jsonify({"error": f"Download failed: {str(e)}"}), 500

@storage_bp.route('/preview/<path:filename>', methods=['GET'])
@jwt_required()
def preview_file(filename):
    init_storage()

    identity_str = get_jwt_identity()  # String like "email:role"
    current_user = parse_identity(identity_str)
    try:
        record = Record.query.filter_by(filename=filename).first()
        if not record:
            return jsonify({"error": "Record not found"}), 404
        log = AccessLog(record_id=record.id, accessed_by=current_user['email'], access_time=datetime.utcnow())
        db.session.add(log)
        db.session.commit()
        if current_user['role'] == 'doctor' or not filename.startswith(current_user['email'] + '/'):
            # log_access(current_user['email'], filename, 'preview')  # SKIPPED for deployment
            print(f"storage_routes.py - SKIPPED blockchain log for preview: {current_user['email']} on {filename}")
        blob_client = container_client.get_blob_client(filename)
        blob_data = blob_client.download_blob().readall().decode('utf-8')
        return jsonify({"content": blob_data}), 200
    except Exception as e:
        return jsonify({"error": f"Preview failed: {str(e)}"}), 500

@storage_bp.route('/access-logs/<patient_id>', methods=['GET'])
@jwt_required()
def access_logs(patient_id):
    init_storage()

    identity_str = get_jwt_identity()  # String like "email:role"
    current_user = parse_identity(identity_str)
    try:
        records = Record.query.filter_by(patient_id=patient_id).all()
        if not records:
            return jsonify({"message": "No records found for this patient"}), 404
        logs = AccessLog.query.filter(AccessLog.record_id.in_([r.id for r in records])).all()
        if current_user['role'] == 'doctor' and patient_id != current_user['email']:
            # log_access(current_user['email'], patient_id, 'access_logs')  # SKIPPED for deployment
            print(f"storage_routes.py - SKIPPED blockchain log for access_logs: {current_user['email']} on {patient_id}")
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
def list_all_records():
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