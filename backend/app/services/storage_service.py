from azure.storage.blob import BlobServiceClient
import os

AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = "records"

blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

def upload_to_blob(file, filename):
    blob_client = container_client.get_blob_client(filename)
    blob_client.upload_blob(file, overwrite=True)
    return blob_client.url
# app/routes/storage_routes.py
from flask import Blueprint, jsonify, request
from app.models import Record

storage_bp = Blueprint('storage', __name__)

@storage_bp.route('/view-record/<patient_id>', methods=['GET'])
def view_record(patient_id):
    try:
        records = Record.query.filter_by(patient_id=patient_id).all()
        if not records:
            return jsonify({"message": "No records found for this patient"}), 404

        # Return metadata + blob URLs
        record_list = [
            {
                "id": r.id,
                "filename": r.filename,
                "blob_url": r.blob_url,
                "uploaded_at": r.upload_time
            } for r in records
        ]
        return jsonify(record_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
