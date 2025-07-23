#!/usr/bin/env python3
"""
Production Server for SmartSlide Generator using Waitress
Optimized for Windows production deployment
"""

import os
import sys
from dotenv import load_dotenv

# Load production environment
load_dotenv()

def main():
    print("=" * 50)
    print("🚀 SmartSlide Generator - Production Server")
    print("=" * 50)
    print()
    
    # Validate environment
    google_key = os.getenv('GOOGLE_API_KEY')
    secret_key = os.getenv('SECRET_KEY')
    
    if not google_key or 'your_' in google_key:
        print("❌ ERROR: GOOGLE_API_KEY not properly configured")
        return 1
    
    if not secret_key or 'your-' in secret_key:
        print("❌ ERROR: SECRET_KEY not properly configured")
        return 1
    
    print("✅ Environment validation passed")
    print(f"✅ Debug mode: {os.getenv('DEBUG', 'True').lower() == 'false'}")
    print(f"✅ Port: {os.getenv('PORT', '5001')}")
    print(f"✅ Google API configured: {bool(google_key)}")
    print()
    
    # Import and test application
    try:
        from wsgi import application
        print("✅ WSGI application loaded successfully")
    except Exception as e:
        print(f"❌ ERROR: Failed to load WSGI application: {e}")
        return 1
    
    # Start Waitress server
    try:
        from waitress import serve
        
        host = os.getenv('HOST', '127.0.0.1')
        port = int(os.getenv('PORT', 5001))
        
        print(f"🌐 Starting production server on {host}:{port}")
        print(f"🔗 Access URL: http://{host}:{port}")
        print("📝 Press Ctrl+C to stop the server")
        print()
        print("Server logs:")
        print("-" * 30)
        
        serve(
            application,
            host=host,
            port=port,
            threads=8,  # Number of threads for handling requests
            connection_limit=1000,
            cleanup_interval=30,
            channel_timeout=120
        )
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ ERROR: Server failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
