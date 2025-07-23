#!/bin/bash

# SmartSlide Generator - Production Deployment Script (No Docker)
# This script sets up and runs the SmartSlide Generator in production mode

set -e

echo "🚀 Starting SmartSlide Generator (Production Mode)"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ Python is not installed or not in PATH"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "✅ Using Python: $($PYTHON_CMD --version)"

# Check if required directories exist
echo "📁 Creating required directories..."
mkdir -p uploads outputs logs
chmod 755 uploads outputs logs

# Install dependencies
echo "📦 Installing/updating dependencies..."
$PYTHON_CMD -m pip install -r requirements.txt

# Check environment file
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Using .env.production"
    if [ -f ".env.production" ]; then
        cp ".env.production" ".env"
    else
        echo "❌ No environment configuration found"
        echo "Please create a .env file with your API keys"
        exit 1
    fi
fi

# Start the application
echo "🔧 Starting SmartSlide Generator..."
echo "🌐 Application will be available at: http://localhost:5001"
echo "🔍 Health check: http://localhost:5001/api/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

$PYTHON_CMD run.py
