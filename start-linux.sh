#!/bin/bash

echo "🚀 SmartSlide Generator - Linux Production"

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python not found. Install Python 3.8+"
    exit 1
fi

# Create directories
mkdir -p uploads outputs logs
chmod 755 uploads outputs logs

# Check environment
if [ ! -f ".env" ]; then
    if [ -f ".env.production" ]; then
        cp ".env.production" ".env"
        echo "✅ Using .env.production"
    else
        echo "❌ Create .env file with:"
        echo "GOOGLE_API_KEY=your_gemini_api_key"
        echo "PEXELS_API_KEY=your_pexels_api_key"
        exit 1
    fi
fi

# Install minimal dependencies
echo "📦 Installing dependencies..."
$PYTHON_CMD -m pip install -q -r requirements.txt

# Optional LibreOffice check (for better PDF conversion)
if ! command -v libreoffice &> /dev/null && ! command -v soffice &> /dev/null; then
    echo "ℹ️  LibreOffice not found (PDF conversion will use fallback)"
fi

echo
echo "🔧 Starting Production Server (Waitress WSGI)"
echo "🌐 http://localhost:5002"
echo

$PYTHON_CMD run.py
