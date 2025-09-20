from flask import Blueprint, jsonify
from datetime import datetime

career_feed_bp = Blueprint('career_feed', __name__)

@career_feed_bp.route('/', methods=['GET'])
def get_career_feed():
    """Minimal career feed endpoint to keep the app running.
    Replace this with real aggregation logic if needed.
    """
    return jsonify({
        'success': True,
        'data': [],
        'metadata': {
            'timestamp': datetime.utcnow().isoformat(),
            'note': 'Placeholder career feed; replace with real data source.'
        }
    })
