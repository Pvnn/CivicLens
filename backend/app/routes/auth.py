from flask import Blueprint, request, jsonify, current_app
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from datetime import timedelta
from app import db
from app.models import User
from typing import Optional


auth_bp = Blueprint('auth', __name__)


def _get_serializer():
    secret = current_app.config.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    return URLSafeTimedSerializer(secret_key=secret, salt='auth-token')


def generate_token(user_id: int) -> str:
    s = _get_serializer()
    return s.dumps({'uid': user_id})


def verify_token(token: str, max_age_days: int = 30) -> Optional[int]:
    s = _get_serializer()
    try:
        data = s.loads(token, max_age=timedelta(days=max_age_days).total_seconds())
        return int(data.get('uid'))
    except (BadSignature, SignatureExpired, Exception):
        return None


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(force=True, silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    password = (data.get('password') or '').strip()
    name = (data.get('name') or '').strip() or None
    if not email or not password:
        return jsonify({'success': False, 'error': 'Email and password are required'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'error': 'Email already registered'}), 409
    user = User(email=email, name=name)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    token = generate_token(user.id)
    return jsonify({'success': True, 'token': token, 'user': {'id': user.id, 'email': user.email, 'name': user.name}})


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(force=True, silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    password = (data.get('password') or '').strip()
    if not email or not password:
        return jsonify({'success': False, 'error': 'Email and password are required'}), 400
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
    token = generate_token(user.id)
    return jsonify({'success': True, 'token': token, 'user': {'id': user.id, 'email': user.email, 'name': user.name}})


@auth_bp.route('/me', methods=['GET'])
def me():
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.replace('Bearer ', '').strip() if auth_header else None
    if not token:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    uid = verify_token(token)
    if not uid:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    user = User.query.get(uid)
    if not user:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    return jsonify({'success': True, 'user': {'id': user.id, 'email': user.email, 'name': user.name}})
