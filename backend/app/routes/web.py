from flask import Blueprint, render_template, send_from_directory
import os

web_bp = Blueprint('web', __name__, template_folder='../templates', static_folder='../static')

@web_bp.route('/')
def home():
    return render_template('index.html')

# Optional: serve favicon if placed in static/
@web_bp.route('/favicon.ico')
def favicon():
    static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')
    return send_from_directory(static_dir, 'favicon.ico', mimetype='image/vnd.microsoft.icon')
