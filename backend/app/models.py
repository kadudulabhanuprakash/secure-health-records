# File: backend/app/models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'patient' or 'doctor'

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(120), nullable=False)  # email of the patient
    filename = db.Column(db.String(255), nullable=False)
    blob_url = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, nullable=False)

class AccessLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey('record.id'), nullable=False)
    accessed_by = db.Column(db.String(120), nullable=False)  # email of user accessing
    access_time = db.Column(db.DateTime, nullable=False)

class MedicalForm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_email = db.Column(db.String(120), nullable=False)
    form_type = db.Column(db.String(50), nullable=False)  # 'health_profile', 'symptoms', 'vitals', 'medications', 'family_history'
    form_data = db.Column(db.Text, nullable=False)  # JSON string of form data
    submitted_at = db.Column(db.DateTime, nullable=False)
    doctor_email = db.Column(db.String(120), nullable=True)  # Doctor who reviewed it
    status = db.Column(db.String(20), default='pending')  # 'pending', 'reviewed', 'approved'

class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_email = db.Column(db.String(120), nullable=False)
    doctor_email = db.Column(db.String(120), nullable=False)
    medication_name = db.Column(db.String(200), nullable=False)
    dosage = db.Column(db.String(100), nullable=False)
    frequency = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.String(100), nullable=False)
    instructions = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='active')  # 'active', 'completed', 'cancelled'