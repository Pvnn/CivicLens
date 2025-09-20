from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from dotenv import load_dotenv
import importlib
import logging

db = SQLAlchemy()

def create_app():
    flask_app = Flask(__name__)
    
    # Configuration
    load_dotenv()
    flask_app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///policypulse.db')
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(flask_app)
    CORS(flask_app)

    # Ensure ORM models are loaded early to avoid import races
    try:
        import app.models  # noqa: F401
    except Exception as e:
        flask_app.logger.warning(f"Early models import failed (will retry later): {e}")

    # Register blueprints
    from app.routes.policies import policies_bp
    flask_app.register_blueprint(policies_bp, url_prefix='/api/policies')

    # RTI API
    from app.routes.policies import rti_bp
    flask_app.register_blueprint(rti_bp, url_prefix='/api/rti')

    # Core auth and forum modules (after models imported)
    try:
        from app.routes.auth import auth_bp
        flask_app.register_blueprint(auth_bp, url_prefix='/api/auth')
    except Exception as e:
        flask_app.logger.warning(f"Auth blueprint not registered: {e}")
    try:
        from app.routes.forum import forum_bp
        flask_app.register_blueprint(forum_bp, url_prefix='/api/forum')
    except Exception as e:
        flask_app.logger.warning(f"Forum blueprint not registered: {e}")

    # Frontend web UI (Jinja) vs React build
    serve_react = os.environ.get('SERVE_REACT', '0') == '1'
    react_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist'))
    has_react_build = os.path.isdir(react_dist) and os.path.isfile(os.path.join(react_dist, 'index.html'))

    if not (serve_react or has_react_build):
        # Keep legacy Jinja UI if React build not present
        from app.routes.web import web_bp
        flask_app.register_blueprint(web_bp)
    else:
        # Serve React build as the frontend
        @flask_app.route('/', defaults={'path': ''})
        @flask_app.route('/<path:path>')
        def serve_frontend(path):
            # Do not intercept API routes
            if path.startswith('api/'):
                from flask import abort
                return abort(404)
            full_path = os.path.join(react_dist, path)
            if path and os.path.exists(full_path):
                return send_from_directory(react_dist, path)
            return send_from_directory(react_dist, 'index.html')
    
    # Optional routes from friend's module (register only if available)
    optional_blueprints = [
        ('app.routes.missing_topics', 'missing_topics_bp', '/api/missing-topics'),
        ('app.routes.career_feed', 'career_feed_bp', '/api/career-feed'),
        ('app.routes.health', 'health_bp', '/api/health'),
        ('app.routes.youth_opinions', 'youth_opinions_bp', '/api/youth-opinions'),
        ('app.routes.youth_sentiment', 'youth_sentiment_bp', '/api/youth-sentiment'),
        ('app.routes.youth_topics', 'youth_topics_bp', '/api/youth-topics'),
        ('app.routes.social_media_status', 'social_media_status_bp', '/api/social-media-status'),
        ('app.routes.stream_youth_opinions', 'stream_youth_opinions_bp', '/api/stream/youth-opinions'),
        ('app.routes.stream_missing_topics', 'stream_missing_topics_bp', '/api/stream/missing-topics'),
    ]
    for module_path, bp_name, url_prefix in optional_blueprints:
        try:
            mod = importlib.import_module(module_path)
            bp = getattr(mod, bp_name)
            flask_app.register_blueprint(bp, url_prefix=url_prefix)
        except ModuleNotFoundError as e:
            flask_app.logger.warning(f"Optional module not found: {module_path} ({e})")
        except Exception as e:
            flask_app.logger.warning(f"Failed to register optional blueprint {module_path}.{bp_name}: {e}")
    
    # Create tables (retry models import just in case)
    with flask_app.app_context():
        try:
            import app.models  # noqa: F401
        except Exception as e:
            flask_app.logger.warning(f"Models import failed: {e}")
        db.create_all()

    return flask_app
