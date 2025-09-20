from flask import Blueprint, request, jsonify
from sqlalchemy import func
from typing import Optional
from app import db
from app.models import User, Idea, Vote, Comment
from .auth import verify_token

forum_bp = Blueprint('forum', __name__)


def current_user_id() -> Optional[int]:
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.replace('Bearer ', '').strip() if auth_header else None
    if not token:
        return None
    return verify_token(token)


def idea_to_dict(i: Idea, score: int | None = None) -> dict:
    return {
        'id': i.id,
        'content': i.content,
        'user': {'id': i.author.id, 'email': i.author.email, 'name': i.author.name},
        'created_at': i.created_at.isoformat(),
        'score': score if score is not None else 0,
        'comments_count': len(i.comments),
    }


@forum_bp.route('/ideas', methods=['GET'])
def list_ideas():
    # Aggregate votes to compute score
    score_subq = db.session.query(
        Vote.idea_id.label('idea_id'), func.coalesce(func.sum(Vote.value), 0).label('score')
    ).group_by(Vote.idea_id).subquery()

    ideas = db.session.query(Idea, func.coalesce(score_subq.c.score, 0)).outerjoin(
        score_subq, Idea.id == score_subq.c.idea_id
    ).order_by(func.coalesce(score_subq.c.score, 0).desc(), Idea.created_at.desc()).all()

    data = [idea_to_dict(i, s) for (i, s) in ideas]
    return jsonify({'success': True, 'data': data})


@forum_bp.route('/ideas/top', methods=['GET'])
def top_ideas():
    score_subq = db.session.query(
        Vote.idea_id.label('idea_id'), func.coalesce(func.sum(Vote.value), 0).label('score')
    ).group_by(Vote.idea_id).subquery()

    ideas = db.session.query(Idea, func.coalesce(score_subq.c.score, 0)).outerjoin(
        score_subq, Idea.id == score_subq.c.idea_id
    ).order_by(func.coalesce(score_subq.c.score, 0).desc(), Idea.created_at.desc()).limit(3).all()

    data = [idea_to_dict(i, s) for (i, s) in ideas]
    return jsonify({'success': True, 'data': data})


@forum_bp.route('/ideas', methods=['POST'])
def create_idea():
    uid = current_user_id()
    if not uid:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    payload = request.get_json(force=True, silent=True) or {}
    content = (payload.get('content') or '').strip()
    if not content:
        return jsonify({'success': False, 'error': 'Content is required'}), 400
    user = User.query.get(uid)
    if not user:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    idea = Idea(user_id=user.id, content=content)
    db.session.add(idea)
    db.session.commit()
    return jsonify({'success': True, 'data': idea_to_dict(idea, 0)})


@forum_bp.route('/ideas/<int:idea_id>/vote', methods=['POST'])
def vote_idea(idea_id: int):
    uid = current_user_id()
    if not uid:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    idea = Idea.query.get_or_404(idea_id)
    payload = request.get_json(force=True, silent=True) or {}
    try:
        value = int(payload.get('value'))
    except Exception:
        value = 0
    if value not in (-1, 1):
        return jsonify({'success': False, 'error': 'value must be -1 or 1'}), 400

    vote = Vote.query.filter_by(user_id=uid, idea_id=idea.id).first()
    if vote:
        vote.value = value
    else:
        vote = Vote(user_id=uid, idea_id=idea.id, value=value)
        db.session.add(vote)
    db.session.commit()

    # return updated score
    score = db.session.query(func.coalesce(func.sum(Vote.value), 0)).filter(Vote.idea_id == idea.id).scalar() or 0
    return jsonify({'success': True, 'data': {'idea_id': idea.id, 'score': score}})


@forum_bp.route('/ideas/<int:idea_id>/comments', methods=['GET'])
def list_comments(idea_id: int):
    idea = Idea.query.get_or_404(idea_id)
    comments = [
        {
            'id': c.id,
            'content': c.content,
            'user': {'id': c.author.id, 'email': c.author.email, 'name': c.author.name},
            'created_at': c.created_at.isoformat(),
        }
        for c in idea.comments
    ]
    return jsonify({'success': True, 'data': comments})


@forum_bp.route('/ideas/<int:idea_id>/comments', methods=['POST'])
def add_comment(idea_id: int):
    uid = current_user_id()
    if not uid:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    idea = Idea.query.get_or_404(idea_id)
    payload = request.get_json(force=True, silent=True) or {}
    content = (payload.get('content') or '').strip()
    if not content:
        return jsonify({'success': False, 'error': 'Content is required'}), 400
    c = Comment(idea_id=idea.id, user_id=uid, content=content)
    db.session.add(c)
    db.session.commit()
    return jsonify({'success': True, 'data': {'id': c.id, 'content': c.content, 'created_at': c.created_at.isoformat()}})
