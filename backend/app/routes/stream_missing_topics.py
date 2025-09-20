from flask import Blueprint, Response, stream_with_context
import json
import time
from datetime import datetime

stream_missing_topics_bp = Blueprint('stream_missing_topics', __name__)


def sse_format(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


@stream_missing_topics_bp.route('/', methods=['GET'])
def stream_missing_topics():
    def generate():
        data = [
            {"topic": "Unemployment and Job Crisis", "youth_mentions": 52, "politician_mentions": 17, "gap_score": 35},
            {"topic": "Mental Health Awareness", "youth_mentions": 48, "politician_mentions": 16, "gap_score": 32},
            {"topic": "Education System Reform", "youth_mentions": 44, "politician_mentions": 22, "gap_score": 22},
        ]
        payload = {
            "data": data,
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "data_source": "stream_placeholder",
                "note": "SSE preview of missing topics",
            },
        }
        yield sse_format(payload)
        time.sleep(1)
    return Response(stream_with_context(generate()), mimetype='text/event-stream')
