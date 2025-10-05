from flask import Blueprint, request, send_from_directory, jsonify
from flask_login import login_user, login_required, current_user
import os
from blockchain.web3_config import log_access, log_upload, get_access_logs
from models import users
from main import app  # Import app for static_folder

records_bp = Blueprint('records', __name__)

@records_bp.route('/')
def index():
    return jsonify({"message": "Welcome to Secure Health Records API"}), 200

@records_bp.route('/login', methods=['POST'])
def login():
    user_id = request.form.get('user_id')
    user = users.get(user_id)
    if user:
        login_user(user)
        return jsonify({"message": f"Logged in as {user.username}"}), 200
    return jsonify({"error": "User not found"}), 401

@records_bp.route('/upload-record', methods=['POST'])
@login_required
def upload_record():
    record_id = request.form.get('record_id')
    patient_id = request.form.get('patient_id')
    file = request.files.get('file')

    if not all([record_id, patient_id, file]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        record_id = int(record_id)
        patient_id = int(patient_id)
    except ValueError:
        return jsonify({"error": "record_id and patient_id must be integers"}), 400

    try:
        file_path = os.path.join(app.static_folder, file.filename)
        file.save(file_path)
    except Exception as e:
        return jsonify({"error": f"File save failed: {str(e)}"}), 500

    try:
        log_upload(record_id, patient_id, current_user.username)
    except Exception as e:
        return jsonify({"error": f"Blockchain logging failed: {str(e)}"}), 500

    return jsonify({"message": "File uploaded and logged", "filename": file.filename}), 200

@records_bp.route('/view-record', methods=['GET'])
@login_required
def view_record():
    record_id = request.args.get('record_id')
    patient_id = request.args.get('patient_id')
    filename = request.args.get('filename')

    if not all([record_id, patient_id, filename]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        record_id = int(record_id)
        patient_id = int(patient_id)
    except ValueError:
        return jsonify({"error": "record_id and patient_id must be integers"}), 400

    try:
        log_access(record_id, patient_id, current_user.username)
    except Exception as e:
        return jsonify({"error": f"Blockchain logging failed: {str(e)}"}), 500

    try:
        return send_from_directory(app.static_folder, filename)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

@records_bp.route('/access-logs', methods=['GET'])
@login_required
def access_logs():
    try:
        logs = get_access_logs()
        return jsonify({"logs": logs}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch logs: {str(e)}"}), 500

@records_bp.route('/favicon.ico')
def favicon():
    return '', 204

from app import db
from datetime import datetime

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    blob_url = db.Column(db.String(500), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
