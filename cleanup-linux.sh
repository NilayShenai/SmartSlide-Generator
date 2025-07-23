#!/bin/bash

echo "🧹 Cleaning up bloat files..."

# Remove Docker files
rm -f Dockerfile docker-compose.yml deploy.sh deploy.bat

# Remove Python cache
echo "Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null

# Remove nginx if exists
rm -rf nginx/

# Remove other unnecessary files
rm -f .dockerignore wsgi.py

echo "✅ Cleanup complete!"
echo
echo "📋 Essential files kept:"
echo "- run.py (main entry point)"
echo "- requirements.txt (minimal dependencies)"
echo "- app/ (application code)"
echo "- .env (environment config)"
echo "- start-linux.sh (startup script)"
echo
