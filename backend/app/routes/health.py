from flask import Blueprint, jsonify
from datetime import datetime

health_bp = Blueprint('health', __name__)

@health_bp.route('/', methods=['GET'])
def health():
    return jsonify({
        "ok": True,
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    })
