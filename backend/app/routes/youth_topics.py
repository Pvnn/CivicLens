from flask import Blueprint, jsonify
from datetime import datetime


youth_topics_bp = Blueprint('youth_topics', __name__)


@youth_topics_bp.route('/', methods=['GET'])
def get_youth_topics():
    """Trending youth topics derived shape compatible with friend's frontend."""
    keywords = [
        ("jobs", 15), ("mental health", 11), ("education", 13),
        ("inflation", 9), ("housing", 8), ("climate", 7), ("women safety", 6),
        ("startup", 5), ("privacy", 4), ("transport", 3)
    ]
    data = []
    for kw, freq in keywords:
        youth_mentions = min(freq * 3, 60)
        politician_mentions = max(5, int(youth_mentions * 0.5))
        gap = youth_mentions - politician_mentions
        data.append({
            "topic": kw.title(),
            "youth_mentions": youth_mentions,
            "politician_mentions": politician_mentions,
            "gap_score": gap,
            "frequency": freq,
        })
    data.sort(key=lambda x: x["gap_score"], reverse=True)
    return jsonify({
        "success": True,
        "data": data,
        "metadata": {"timestamp": datetime.utcnow().isoformat(), "note": "Placeholder youth topics"},
    })
