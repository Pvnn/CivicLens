from flask import Blueprint, jsonify
from datetime import datetime


youth_sentiment_bp = Blueprint('youth_sentiment', __name__)


@youth_sentiment_bp.route('/', methods=['GET'])
def get_youth_sentiment():
    """Minimal youth sentiment endpoint compatible with friend's frontend."""
    data = {
        "overall_sentiment": {"positive": 42.5, "neutral": 37.0, "negative": 20.5},
        "top_concerns": ["jobs", "mental health", "education", "inflation", "housing"],
        "platform_activity": {"Twitter": 120, "Reddit": 85, "YouTube": 48},
        "total_opinions_analyzed": 253,
        "analysis_timestamp": datetime.utcnow().isoformat(),
    }
    return jsonify({
        "success": True,
        "data": data,
        "metadata": {"timestamp": datetime.utcnow().isoformat(), "note": "Placeholder youth sentiment"},
    })
