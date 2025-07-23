#!/usr/bin/env python3
"""
Smart Slide Generator - Startup Script
Comprehensive startup script with environment validation and debugging
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def validate_environment():
    """Validate required environment variables and dependencies"""
    print("🔍 Validating environment...")
    
    # Load environment variables
    load_dotenv()
    
    # Check required API keys
    google_key = os.getenv('GOOGLE_API_KEY')
    pexels_key = os.getenv('PEXELS_API_KEY')
    secret_key = os.getenv('SECRET_KEY')
    
    issues = []
    
    if not google_key or google_key == 'your_google_ai_api_key_here':
        issues.append("❌ GOOGLE_API_KEY not properly set")
    else:
        print("✅ Google AI API key configured")
    
    if not pexels_key or pexels_key == 'your_pexels_api_key_here':
        print("⚠️  Pexels API key not set - images will be disabled")
    else:
        print("✅ Pexels API key configured")
    
    if not secret_key or secret_key == 'your-secret-key-here':
        issues.append("❌ SECRET_KEY not properly set")
    else:
        print("✅ Secret key configured")
    
    # Check directories
    for folder in ['uploads', 'outputs']:
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
            print(f"📁 Created {folder} directory")
        else:
            print(f"✅ {folder} directory exists")
    
    if issues:
        print("\n⚠️  Issues found:")
        for issue in issues:
            print(f"  {issue}")
        print("\nPlease fix these issues before starting the application.")
        return False
    
    print("✅ Environment validation passed!")
    return True

def start_application():
    """Start the Flask application"""
    try:
        from app import create_app
        
        # Create Flask app
        app = create_app()
        
        # Get configuration from environment
        debug = os.getenv('DEBUG', 'False').lower() == 'true'
        host = os.getenv('HOST', '127.0.0.1')
        port = int(os.getenv('PORT', 5000))
        
        print(f"\n🚀 Starting SmartSlide Generator...")
        print(f"   Host: {host}")
        print(f"   Port: {port}")
        print(f"   Debug: {debug}")
        print(f"   URL: http://{host}:{port}")
        print("\n📝 Press Ctrl+C to stop the server\n")
        
        # Start the application
        app.run(debug=debug, host=host, port=port)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

def main():
    """Main entry point"""
    print("🎯 SmartSlide Generator - AI PowerPoint Generator")
    print("=" * 50)
    
    # Validate environment first
    if not validate_environment():
        sys.exit(1)
    
    # Start the application
    start_application()

if __name__ == "__main__":
    main()
