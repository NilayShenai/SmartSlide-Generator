from flask import Flask
from flask_cors import CORS
import os
import threading

def create_app():
    app = Flask(__name__)
    
    # Enable CORS for frontend integration
    CORS(app)
    
    # Configuration
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Use environment-appropriate paths
    if os.environ.get('DYNO'):  # Check if running on Heroku
        app.config['UPLOAD_FOLDER'] = '/tmp'
        app.config['OUTPUT_FOLDER'] = '/tmp'
    else:
        app.config['UPLOAD_FOLDER'] = 'uploads'
        app.config['OUTPUT_FOLDER'] = 'outputs'
        # Ensure directories exist (only for local development)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    
    # Register blueprints
    from .routes import main
    app.register_blueprint(main)
    
    # Start cleanup task
    def schedule_cleanup():
        import time
        from .utils import cleanup_old_files
        while True:
            time.sleep(3600)  # Run every hour
            try:
                cleanup_old_files()
            except Exception as e:
                print(f"Cleanup error: {e}")
    
    cleanup_thread = threading.Thread(target=schedule_cleanup)
    cleanup_thread.daemon = True
    cleanup_thread.start()
    
    return app
