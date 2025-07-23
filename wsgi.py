#!/usr/bin/env python3
"""
Production WSGI Server for SmartSlide Generator
Optimized for production deployment with proper logging and error handling
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load production environment
env_file = '.env.production' if os.path.exists('.env.production') else '.env'
load_dotenv(env_file)

def setup_logging():
    """Setup production logging"""
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_file = os.getenv('LOG_FILE', 'logs/app.log')
    
    # Create log directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific loggers
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

def setup_directories():
    """Setup required directories for production"""
    upload_folder = os.getenv('UPLOAD_FOLDER', 'uploads')
    output_folder = os.getenv('OUTPUT_FOLDER', 'outputs')
    
    for folder in [upload_folder, output_folder]:
        os.makedirs(folder, exist_ok=True)
        # Set proper permissions for production (Windows compatible)
        try:
            os.chmod(folder, 0o755)
        except (OSError, NotImplementedError):
            # chmod may not work on Windows, that's okay
            pass

def validate_production_config():
    """Validate production configuration"""
    required_vars = ['GOOGLE_API_KEY', 'SECRET_KEY']
    missing = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.startswith('your_'):
            missing.append(var)
    
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

# Setup production environment
try:
    setup_logging()
    setup_directories()
    validate_production_config()
    
    # Import and create Flask app
    from app import create_app
    
    app = create_app()
    
    # Production-specific configuration
    app.config.update({
        'SESSION_COOKIE_SECURE': os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true',
        'SESSION_COOKIE_HTTPONLY': os.getenv('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true',
        'SESSION_COOKIE_SAMESITE': os.getenv('SESSION_COOKIE_SAMESITE', 'Lax'),
    })
    
    # Log startup info
    logging.info("SmartSlide Generator starting in PRODUCTION mode")
    logging.info(f"Debug mode: {app.config.get('DEBUG', False)}")
    logging.info(f"Environment file: {env_file}")
    
except Exception as e:
    logging.error(f"Failed to initialize application: {e}")
    sys.exit(1)

# WSGI application entry point
application = app

if __name__ == "__main__":
    # Development fallback
    port = int(os.getenv('PORT', 5001))
    host = os.getenv('HOST', '0.0.0.0')
    app.run(host=host, port=port, debug=False)
