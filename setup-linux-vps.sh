#!/bin/bash

# SmartSlide Generator - Fresh Linux VPS Setup Script
# This script sets up everything needed on a fresh Ubuntu/Debian VPS

set -e

echo "🚀 SmartSlide Generator - Fresh Linux VPS Setup"
echo "================================================"
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please don't run this script as root. Run as a regular user with sudo access."
    exit 1
fi

# Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install essential packages
print_status "Installing essential packages..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release

# Install LibreOffice for PDF conversion
print_status "Installing LibreOffice for PDF conversion..."
sudo apt install -y libreoffice

# Install additional fonts for better PDF rendering
print_status "Installing additional fonts..."
sudo apt install -y \
    fonts-liberation \
    fonts-dejavu-core \
    fonts-noto \
    ttf-mscorefonts-installer

# Create application directory
APP_DIR="/home/$(whoami)/smartslide-generator"
print_status "Creating application directory: $APP_DIR"
mkdir -p "$APP_DIR"
cd "$APP_DIR"

# Clone or download the repository
if [ ! -d ".git" ]; then
    print_status "Downloading SmartSlide Generator..."
    # If you have the files locally, you can copy them here
    # For now, we'll assume the files are already present
    if [ ! -f "run.py" ]; then
        print_error "SmartSlide Generator files not found!"
        print_status "Please copy your SmartSlide Generator files to: $APP_DIR"
        print_status "Required files:"
        echo "  - run.py"
        echo "  - requirements.txt"
        echo "  - app/ directory"
        echo "  - .env.production (rename to .env and configure)"
        exit 1
    fi
fi

# Create Python virtual environment
print_status "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
if [ -f "requirements.txt" ]; then
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
else
    print_error "requirements.txt not found!"
    exit 1
fi

# Create necessary directories
print_status "Creating application directories..."
mkdir -p uploads outputs logs
chmod 755 uploads outputs logs

# Setup environment configuration
if [ ! -f ".env" ]; then
    if [ -f ".env.production" ]; then
        print_status "Copying .env.production to .env..."
        cp .env.production .env
        print_warning "Please edit .env file and configure your API keys:"
        echo "  - GOOGLE_API_KEY=your_gemini_api_key"
        echo "  - PEXELS_API_KEY=your_pexels_api_key"
    else
        print_status "Creating .env file template..."
        cat > .env << EOF
# SmartSlide Generator Environment Configuration
DEBUG=false
HOST=0.0.0.0
PORT=5001

# API Keys (REQUIRED - Replace with your actual keys)
GOOGLE_API_KEY=your_gemini_api_key_here
PEXELS_API_KEY=your_pexels_api_key_here

# Security
SECRET_KEY=$(openssl rand -hex 32)

# Flask Configuration
FLASK_ENV=production
PYTHONUNBUFFERED=1
EOF
        print_warning "Created .env file. Please edit it and add your API keys!"
    fi
fi

# Create systemd service for auto-start
print_status "Creating systemd service..."
sudo tee /etc/systemd/system/smartslide.service > /dev/null << EOF
[Unit]
Description=SmartSlide Generator
After=network.target

[Service]
Type=simple
User=$(whoami)
Group=$(whoami)
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/python run.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
print_status "Enabling and starting SmartSlide service..."
sudo systemctl daemon-reload
sudo systemctl enable smartslide
sudo systemctl start smartslide

# Setup firewall (if ufw is available)
if command -v ufw &> /dev/null; then
    print_status "Configuring firewall..."
    sudo ufw allow 22/tcp  # SSH
    sudo ufw allow 5001/tcp  # SmartSlide
    sudo ufw --force enable
fi

# Setup nginx reverse proxy (optional)
read -p "Do you want to install Nginx reverse proxy? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Installing and configuring Nginx..."
    sudo apt install -y nginx
    
    # Create nginx configuration
    sudo tee /etc/nginx/sites-available/smartslide > /dev/null << EOF
server {
    listen 80;
    server_name _;
    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
    }
}
EOF

    # Enable the site
    sudo ln -sf /etc/nginx/sites-available/smartslide /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    sudo systemctl restart nginx
    sudo systemctl enable nginx
    
    # Allow HTTP traffic
    sudo ufw allow 80/tcp
    
    print_success "Nginx configured! SmartSlide will be available on port 80"
fi

# Get server IP
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')

# Final status check
print_status "Checking service status..."
sleep 5
if sudo systemctl is-active --quiet smartslide; then
    print_success "SmartSlide Generator is running!"
else
    print_error "SmartSlide service failed to start. Checking logs..."
    sudo journalctl -u smartslide --no-pager -n 20
fi

echo
echo "🎉 Setup Complete!"
echo "===================="
echo
print_success "SmartSlide Generator has been installed and configured!"
echo
echo "📋 Service Management:"
echo "  Start:   sudo systemctl start smartslide"
echo "  Stop:    sudo systemctl stop smartslide"
echo "  Restart: sudo systemctl restart smartslide"
echo "  Status:  sudo systemctl status smartslide"
echo "  Logs:    sudo journalctl -u smartslide -f"
echo
echo "🌐 Access URLs:"
if command -v nginx &> /dev/null && sudo systemctl is-active --quiet nginx; then
    echo "  HTTP:  http://$SERVER_IP"
    echo "  Direct: http://$SERVER_IP:5001"
else
    echo "  Direct: http://$SERVER_IP:5001"
fi
echo
echo "⚙️  Configuration:"
echo "  App Directory: $APP_DIR"
echo "  Environment:   $APP_DIR/.env"
echo "  Logs:          $APP_DIR/logs/"
echo
print_warning "Important: Edit $APP_DIR/.env and configure your API keys!"
echo
echo "🔧 Next Steps:"
echo "1. Edit .env file: nano $APP_DIR/.env"
echo "2. Add your API keys (Google Gemini, Pexels)"
echo "3. Restart service: sudo systemctl restart smartslide"
echo "4. Check status: sudo systemctl status smartslide"
echo
