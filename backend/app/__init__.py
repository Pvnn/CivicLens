from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from dotenv import load_dotenv

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    load_dotenv()
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///policypulse.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Register blueprints
    from app.routes.policies import policies_bp
    app.register_blueprint(policies_bp, url_prefix='/api/policies')

    # Frontend web UI
    from app.routes.web import web_bp
    app.register_blueprint(web_bp)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app
