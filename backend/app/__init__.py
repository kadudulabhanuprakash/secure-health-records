from flask import Flask
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from .models import db
import os

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///users.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Tokens don't expire for demo
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    bcrypt = Bcrypt(app)
    CORS(app, origins=['http://localhost:3000'], supports_credentials=True, methods=['GET', 'POST', 'PUT', 'OPTIONS'], allow_headers=['*'])
    
    # Store bcrypt in app context for use in routes
    app.bcrypt = bcrypt
    
    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.storage_routes_local import storage_bp
    from .routes.blockchain_routes import blockchain_bp
    from .routes.medical_forms import medical_forms_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(storage_bp, url_prefix='/api/storage')
    app.register_blueprint(blockchain_bp, url_prefix='/api/blockchain')
    app.register_blueprint(medical_forms_bp, url_prefix='/api/medical')
    
    # Add root endpoints
    @app.route('/')
    def root():
        return {"message": "Secure Health Records API is running", "status": "healthy"}, 200

    @app.route('/health')
    def health():
        return {"status": "healthy", "message": "API is running"}, 200
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app