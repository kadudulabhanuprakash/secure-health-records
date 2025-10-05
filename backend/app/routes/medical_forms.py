from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import cross_origin
from ..models import db, MedicalForm, Prescription
from datetime import datetime
import json

medical_forms_bp = Blueprint('medical_forms', __name__)

@medical_forms_bp.route('/forms', methods=['POST', 'OPTIONS'])
@cross_origin()
@jwt_required()
def submit_form():
    """Submit a medical form"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        identity = get_jwt_identity()
        email, role = identity.split(':')
        
        if role.lower() != 'patient':
            return jsonify({"error": "Only patients can submit medical forms"}), 403
        
        data = request.get_json()
        form_type = data.get('form_type')
        form_data = data.get('form_data')
        
        if not form_type or not form_data:
            return jsonify({"error": "form_type and form_data are required"}), 400
        
        valid_types = ['health_profile', 'symptoms', 'vitals', 'medications', 'family_history']
        if form_type not in valid_types:
            return jsonify({"error": f"Invalid form_type. Must be one of: {valid_types}"}), 400
        
        # Create new medical form
        medical_form = MedicalForm(
            patient_email=email,
            form_type=form_type,
            form_data=json.dumps(form_data),
            submitted_at=datetime.utcnow(),
            status='pending'
        )
        
        db.session.add(medical_form)
        db.session.commit()
        
        return jsonify({
            "message": "Form submitted successfully",
            "form_id": medical_form.id,
            "status": medical_form.status
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to submit form: {str(e)}"}), 500

@medical_forms_bp.route('/forms', methods=['GET', 'OPTIONS'])
@cross_origin()
@jwt_required()
def get_forms():
    """Get medical forms for the current user"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        identity = get_jwt_identity()
        email, role = identity.split(':')
        
        if role.lower() == 'patient':
            # Patients can see their own forms
            forms = MedicalForm.query.filter_by(patient_email=email).order_by(MedicalForm.submitted_at.desc()).all()
        elif role.lower() == 'doctor':
            # Doctors can see all pending forms and forms they've reviewed
            forms = MedicalForm.query.filter(
                (MedicalForm.status == 'pending') | (MedicalForm.doctor_email == email)
            ).order_by(MedicalForm.submitted_at.desc()).all()
        else:
            return jsonify({"error": "Invalid role"}), 403
        
        forms_data = []
        for form in forms:
            forms_data.append({
                "id": form.id,
                "patient_email": form.patient_email,
                "form_type": form.form_type,
                "form_data": json.loads(form.form_data),
                "submitted_at": form.submitted_at.isoformat(),
                "doctor_email": form.doctor_email,
                "status": form.status
            })
        
        return jsonify({"forms": forms_data}), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get forms: {str(e)}"}), 500

@medical_forms_bp.route('/forms/<int:form_id>/review', methods=['POST', 'OPTIONS'])
@cross_origin()
@jwt_required()
def review_form():
    """Doctor reviews a medical form"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        identity = get_jwt_identity()
        email, role = identity.split(':')
        
        if role.lower() != 'doctor':
            return jsonify({"error": "Only doctors can review forms"}), 403
        
        form_id = request.view_args['form_id']
        data = request.get_json()
        status = data.get('status', 'reviewed')
        
        if status not in ['reviewed', 'approved']:
            return jsonify({"error": "Status must be 'reviewed' or 'approved'"}), 400
        
        form = MedicalForm.query.get(form_id)
        if not form:
            return jsonify({"error": "Form not found"}), 404
        
        form.doctor_email = email
        form.status = status
        db.session.commit()
        
        return jsonify({
            "message": f"Form {status} successfully",
            "form_id": form.id,
            "status": form.status
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to review form: {str(e)}"}), 500

@medical_forms_bp.route('/prescriptions', methods=['POST', 'OPTIONS'])
@cross_origin()
@jwt_required()
def create_prescription():
    """Doctor creates a prescription"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        identity = get_jwt_identity()
        email, role = identity.split(':')
        
        if role.lower() != 'doctor':
            return jsonify({"error": "Only doctors can create prescriptions"}), 403
        
        data = request.get_json()
        patient_email = data.get('patient_email')
        medication_name = data.get('medication_name')
        dosage = data.get('dosage')
        frequency = data.get('frequency')
        duration = data.get('duration')
        instructions = data.get('instructions', '')
        
        if not all([patient_email, medication_name, dosage, frequency, duration]):
            return jsonify({"error": "Missing required fields"}), 400
        
        prescription = Prescription(
            patient_email=patient_email,
            doctor_email=email,
            medication_name=medication_name,
            dosage=dosage,
            frequency=frequency,
            duration=duration,
            instructions=instructions,
            created_at=datetime.utcnow(),
            status='active'
        )
        
        db.session.add(prescription)
        db.session.commit()
        
        return jsonify({
            "message": "Prescription created successfully",
            "prescription_id": prescription.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create prescription: {str(e)}"}), 500

@medical_forms_bp.route('/prescriptions', methods=['GET', 'OPTIONS'])
@cross_origin()
@jwt_required()
def get_prescriptions():
    """Get prescriptions for the current user"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        identity = get_jwt_identity()
        email, role = identity.split(':')
        
        if role.lower() == 'patient':
            prescriptions = Prescription.query.filter_by(patient_email=email).order_by(Prescription.created_at.desc()).all()
        elif role.lower() == 'doctor':
            prescriptions = Prescription.query.filter_by(doctor_email=email).order_by(Prescription.created_at.desc()).all()
        else:
            return jsonify({"error": "Invalid role"}), 403
        
        prescriptions_data = []
        for prescription in prescriptions:
            prescriptions_data.append({
                "id": prescription.id,
                "patient_email": prescription.patient_email,
                "doctor_email": prescription.doctor_email,
                "medication_name": prescription.medication_name,
                "dosage": prescription.dosage,
                "frequency": prescription.frequency,
                "duration": prescription.duration,
                "instructions": prescription.instructions,
                "created_at": prescription.created_at.isoformat(),
                "status": prescription.status
            })
        
        return jsonify({"prescriptions": prescriptions_data}), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get prescriptions: {str(e)}"}), 500

@medical_forms_bp.route('/prescriptions/<int:prescription_id>/status', methods=['PUT', 'OPTIONS'])
@cross_origin()
@jwt_required()
def update_prescription_status():
    """Update prescription status"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        identity = get_jwt_identity()
        email, role = identity.split(':')
        
        prescription_id = request.view_args['prescription_id']
        data = request.get_json()
        status = data.get('status')
        
        if status not in ['active', 'completed', 'cancelled']:
            return jsonify({"error": "Invalid status"}), 400
        
        prescription = Prescription.query.get(prescription_id)
        if not prescription:
            return jsonify({"error": "Prescription not found"}), 404
        
        # Check permissions
        if role.lower() == 'patient' and prescription.patient_email != email:
            return jsonify({"error": "Unauthorized"}), 403
        elif role.lower() == 'doctor' and prescription.doctor_email != email:
            return jsonify({"error": "Unauthorized"}), 403
        
        prescription.status = status
        db.session.commit()
        
        return jsonify({
            "message": "Prescription status updated successfully",
            "prescription_id": prescription.id,
            "status": prescription.status
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update prescription: {str(e)}"}), 500
