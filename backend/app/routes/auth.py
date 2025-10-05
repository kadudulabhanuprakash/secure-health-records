# File: backend/app/routes/auth.py
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import create_access_token
from ..models import db, User

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')

    if not email or not password or role not in ['patient', 'doctor']:
        return jsonify({"error": "Invalid input"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "User already exists"}), 400

    hashed_password = current_app.bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(email=email, password=hashed_password, role=role)
    db.session.add(user)
    db.session.commit()

    # Create JWT token with string identity
    identity_str = f"{email}:{role}"
    access_token = create_access_token(identity=identity_str)
    return jsonify({"token": access_token, "message": "Registration successful"}), 200

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not current_app.bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Invalid email or password"}), 401

    # Create JWT token with string identity
    identity_str = f"{user.email}:{user.role}"
    access_token = create_access_token(identity=identity_str)
    return jsonify({"token": access_token, "message": "Login successful"}), 200