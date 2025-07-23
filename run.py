import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables
load_dotenv()

app = create_app()

if __name__ == "__main__":
    # Get configuration from environment variables
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5001))
    
    # Use Waitress for production, Flask dev server for development
    if debug:
        print("🚨 Running in DEBUG mode - using Flask development server")
        app.run(debug=debug, host=host, port=port)
    else:
        print("🚀 Running in PRODUCTION mode - using Waitress WSGI server")
        try:
            from waitress import serve
            print(f"🌐 Server starting on http://{host}:{port}")
            serve(app, host=host, port=port, threads=4, cleanup_interval=30, channel_timeout=120)
        except ImportError:
            print("⚠️  Waitress not installed, falling back to Flask dev server")
            print("   Install with: pip install waitress")
            app.run(debug=False, host=host, port=port)
