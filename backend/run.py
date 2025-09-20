from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Create database directory if it doesn't exist
    os.makedirs('instance', exist_ok=True)
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)