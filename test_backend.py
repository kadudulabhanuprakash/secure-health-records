from backend.app.models import db, User
from main import app
with app.app_context():
    user = User.query.filter_by(email='ram@gmail.com').first()
    print(user.email, user.role)