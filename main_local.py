from dotenv import load_dotenv
import os
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from backend.app.routes.auth import auth_bp
from backend.app.routes.storage_routes_local import storage_bp

# Load .env at the top
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')
jwt = JWTManager(app)

# Enable CORS for http://localhost:3000
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(storage_bp, url_prefix='/api/storage')

@app.route('/')
def health_check():
    return {"status": "healthy", "message": "Secure Health Records API is running"}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
