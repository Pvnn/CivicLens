from flask import Blueprint, jsonify
from datetime import datetime

youth_opinions_bp = Blueprint('youth_opinions', __name__)

@youth_opinions_bp.route('/', methods=['GET'])
def get_youth_opinions():
    """
    Minimal youth opinions endpoint.
    Returns a placeholder structure compatible with the React MissingTopics page.
    """
    sample_posts = [
        {
            "platform": "Twitter",
            "sentiment": "positive",
            "content": "Students are concerned about job opportunities in 2025.",
            "timestamp": datetime.utcnow().isoformat(),
            "engagement": 42,
        },
        {
            "platform": "Reddit",
            "sentiment": "neutral",
            "content": "Discussion about mental health resources at colleges.",
            "timestamp": datetime.utcnow().isoformat(),
            "engagement": 18,
        },
        {
            "platform": "YouTube",
            "sentiment": "negative",
            "content": "Rising living costs impacting freshers in metro cities.",
            "timestamp": datetime.utcnow().isoformat(),
            "engagement": 67,
        },
    ]

    trends = {
        "total_posts": len(sample_posts),
        "sentiment_distribution": {"positive": 38, "neutral": 42, "negative": 20},
        "top_keywords": [["jobs", 12], ["mental health", 8], ["cost of living", 7], ["education", 6]],
        "platform_distribution": {"Twitter": 45, "Reddit": 30, "YouTube": 25},
    }

    return jsonify({
        "success": True,
        "data": {
            "posts": sample_posts,
            "trends": trends,
        },
        "metadata": {
            "timestamp": datetime.utcnow().isoformat(),
            "data_source": "placeholder",
        },
    })
