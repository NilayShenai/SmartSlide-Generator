#!/usr/bin/env python3
"""
Restart the production server
"""

import sys
import subprocess
import time
import requests

def check_server_status():
    """Check if server is running"""
    try:
        response = requests.get("http://localhost:5002/api/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    print("🔄 Restarting SmartSlide Generator...")
    
    # Check if server is running
    if check_server_status():
        print("⏹️  Server is running, stopping it...")
        # Try to kill any Python processes running our server
        try:
            subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], 
                           capture_output=True, check=False)
        except:
            pass
        
        # Wait a moment
        time.sleep(2)
    
    print("🚀 Starting production server with updated routes...")
    
    # Start the server
    try:
        subprocess.run([sys.executable, 'start-production-server.py'], check=False)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")

if __name__ == "__main__":
    main()
