from flask import Blueprint, jsonify
from datetime import datetime

social_media_status_bp = Blueprint('social_media_status', __name__)

@social_media_status_bp.route('/', methods=['GET'])
def social_status():
    return jsonify({
        "success": True,
        "services": {
            "reddit": {"status": "ok"},
            "twitter": {"status": "ok"},
            "youtube": {"status": "ok"},
        },
        "metadata": {"timestamp": datetime.utcnow().isoformat()},
    })
