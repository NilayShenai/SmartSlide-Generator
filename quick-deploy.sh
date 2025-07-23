#!/bin/bash

# SmartSlide Generator - Quick Linux VPS Deployment
# One-liner: curl -sSL https://raw.githubusercontent.com/yourusername/SmartSlide-Generator/main/quick-deploy.sh | bash

echo "🚀 SmartSlide Generator - Quick Deploy"

# Install essentials
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git libreoffice

# Setup application
cd ~ && mkdir -p smartslide && cd smartslide
python3 -m venv venv && source venv/bin/activate

# If files not present, download them
if [ ! -f "run.py" ]; then
    echo "📁 Please upload your SmartSlide files to $(pwd)"
    echo "Required: run.py, requirements.txt, app/, .env"
    exit 1
fi

# Install dependencies and setup
pip install -r requirements.txt
mkdir -p uploads outputs logs
chmod 755 uploads outputs logs

# Create basic .env if not exists
if [ ! -f ".env" ]; then
    cat > .env << EOF
DEBUG=false
HOST=0.0.0.0
PORT=5001
GOOGLE_API_KEY=REPLACE_WITH_YOUR_GEMINI_KEY
PEXELS_API_KEY=REPLACE_WITH_YOUR_PEXELS_KEY
SECRET_KEY=$(openssl rand -hex 32)
FLASK_ENV=production
EOF
    echo "⚠️  Edit .env file and add your API keys!"
fi

echo "✅ Quick setup complete!"
echo "🔧 Next: Edit .env file, then run: python run.py"
