from flask import Blueprint

blockchain_logger_bp = Blueprint('blockchain_logger', __name__)

@blockchain_logger_bp.route("/log_access", methods=["POST"])
def log_access():
    return "Blockchain log endpoint works!"
