from flask import Blueprint, Response, stream_with_context
import json
import time
from datetime import datetime

stream_youth_opinions_bp = Blueprint('stream_youth_opinions', __name__)


def sse_format(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


@stream_youth_opinions_bp.route('/', methods=['GET'])
def stream_youth():
    def generate():
        posts = [
            {
                "platform": "twitter",
                "sentiment": {"overall": "positive", "confidence": 0.86},
                "content": "Campus hiring drives picking up this quarter!",
                "created_at": datetime.utcnow().isoformat(),
                "score": 123,
                "youth_keywords": ["jobs", "campus", "hiring"],
                "relevance_score": 0.78,
                "url": "https://twitter.com/example/status/1",
            }
        ]
        trends = {
            "sentiment_distribution": {"positive": 45, "neutral": 40, "negative": 15},
            "top_keywords": [["jobs", 15], ["education", 12], ["mental health", 9]],
            "platform_distribution": {"Twitter": 110, "Reddit": 70, "YouTube": 35},
            "total_posts": 215,
            "analysis_timestamp": datetime.utcnow().isoformat(),
        }
        payload = {"success": True, "data": {"posts": posts, "trends": trends}}
        yield sse_format(payload)
        time.sleep(1)
    return Response(stream_with_context(generate()), mimetype='text/event-stream')
