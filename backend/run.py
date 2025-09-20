from app import create_app
import os

flask_app = create_app()

if __name__ == '__main__':
    # Ensure instance dir exists for SQLite, etc.
    os.makedirs('instance', exist_ok=True)
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '1') == '1'
    flask_app.run(debug=debug, host='0.0.0.0', port=port)
