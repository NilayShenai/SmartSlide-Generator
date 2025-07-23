#!/bin/bash
set -e

# SmartSlide Generator Production Deployment Script
# This script deploys the application to a production server

echo "🚀 SmartSlide Generator - Production Deployment"
echo "=============================================="

# Configuration
APP_NAME="smartslide"
APP_DIR="/opt/${APP_NAME}"
SERVICE_NAME="${APP_NAME}.service"
USER_NAME="${APP_NAME}"
PYTHON_VERSION="3.11"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

print_status "Starting production deployment..."

# Update system packages
print_status "Updating system packages..."
apt update && apt upgrade -y

# Install system dependencies
print_status "Installing system dependencies..."
apt install -y python3-pip python3-venv python3-dev git nginx supervisor \
    build-essential curl wget unzip software-properties-common \
    libssl-dev libffi-dev libjpeg-dev libpng-dev

# Install Node.js for Playwright
print_status "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

# Create application user
if ! id "${USER_NAME}" &>/dev/null; then
    print_status "Creating application user..."
    useradd --system --shell /bin/bash --home ${APP_DIR} --create-home ${USER_NAME}
else
    print_warning "User ${USER_NAME} already exists"
fi

# Create application directory
print_status "Setting up application directory..."
mkdir -p ${APP_DIR}
chown ${USER_NAME}:${USER_NAME} ${APP_DIR}

# Create log directory
mkdir -p /var/log/${APP_NAME}
chown ${USER_NAME}:${USER_NAME} /var/log/${APP_NAME}

# Clone or update repository
if [ -d "${APP_DIR}/.git" ]; then
    print_status "Updating existing repository..."
    cd ${APP_DIR}
    sudo -u ${USER_NAME} git pull origin main
else
    print_status "Cloning repository..."
    sudo -u ${USER_NAME} git clone https://github.com/arnuvp/SmartSlide-Generator.git ${APP_DIR}
fi

cd ${APP_DIR}

# Create Python virtual environment
print_status "Creating Python virtual environment..."
sudo -u ${USER_NAME} python3 -m venv venv
sudo -u ${USER_NAME} ./venv/bin/pip install --upgrade pip

# Install Python dependencies
print_status "Installing Python dependencies..."
sudo -u ${USER_NAME} ./venv/bin/pip install -r requirements.txt

# Install Playwright browsers
print_status "Installing Playwright browsers..."
sudo -u ${USER_NAME} ./venv/bin/playwright install --with-deps

# Setup environment configuration
print_status "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.production .env
    print_warning "Please edit .env file with your API keys before starting the service"
fi

# Create required directories
sudo -u ${USER_NAME} mkdir -p uploads outputs
chmod 755 uploads outputs

# Install systemd service
print_status "Installing systemd service..."
cp ${SERVICE_NAME} /etc/systemd/system/
systemctl daemon-reload
systemctl enable ${SERVICE_NAME}

# Configure Nginx
print_status "Configuring Nginx..."
cat > /etc/nginx/sites-available/${APP_NAME} << EOF
server {
    listen 80;
    server_name _;
    
    client_max_body_size 16M;
    client_body_timeout 120s;
    proxy_read_timeout 600s;
    proxy_connect_timeout 60s;
    proxy_send_timeout 600s;
    
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_buffering off;
    }
    
    location /static {
        alias ${APP_DIR}/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://127.0.0.1:5001/api/health;
    }
}
EOF

# Enable Nginx site
ln -sf /etc/nginx/sites-available/${APP_NAME} /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx
systemctl enable nginx

# Configure firewall
print_status "Configuring firewall..."
ufw --force enable
ufw allow ssh
ufw allow 'Nginx Full'
ufw allow 5001

# Set proper permissions
chown -R ${USER_NAME}:${USER_NAME} ${APP_DIR}
chmod +x ${APP_DIR}/wsgi.py

print_success "Deployment completed successfully!"
print_status "Next steps:"
echo "1. Edit ${APP_DIR}/.env with your API keys"
echo "2. Start the service: sudo systemctl start ${SERVICE_NAME}"
echo "3. Check status: sudo systemctl status ${SERVICE_NAME}"
echo "4. View logs: sudo journalctl -u ${SERVICE_NAME} -f"
echo ""
print_status "Service management commands:"
echo "• Start:   sudo systemctl start ${SERVICE_NAME}"
echo "• Stop:    sudo systemctl stop ${SERVICE_NAME}"
echo "• Restart: sudo systemctl restart ${SERVICE_NAME}"
echo "• Status:  sudo systemctl status ${SERVICE_NAME}"
echo "• Logs:    sudo journalctl -u ${SERVICE_NAME} -f"
