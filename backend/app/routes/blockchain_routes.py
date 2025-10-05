# app/routes/blockchain_routes.py
from flask import Blueprint, request, jsonify
from backend.app.services.blockchain_service import log_access

blockchain_bp = Blueprint('blockchain', __name__, url_prefix='/blockchain')

@blockchain_bp.route('/log_access', methods=['POST'])
def log_access_endpoint():
    """API endpoint to log a new access event to the blockchain."""
    data = request.json
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
        
    required_fields = ['record_id', 'patient_id', 'accessor']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields: 'record_id', 'patient_id', 'accessor'"}), 400

    record_id = data.get('record_id')
    patient_id = data.get('patient_id')
    accessor = data.get('accessor')

    try:
        transaction_hash = log_access(record_id, patient_id, accessor)
        return jsonify({
            "message": "Access logged successfully",
            "transaction_hash": transaction_hash
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500