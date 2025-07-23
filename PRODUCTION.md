# SmartSlide Generator - Production Deployment Guide

## Quick Deploy Commands

### For Ubuntu/Debian servers:

```bash
# 1. Download and run deployment script
wget https://raw.githubusercontent.com/arnuvp/SmartSlide-Generator/main/deploy.sh
chmod +x deploy.sh
sudo ./deploy.sh

# 2. Configure environment variables
sudo nano /opt/smartslide/.env

# 3. Start the service
sudo systemctl start smartslide

# 4. Check status
sudo python3 /opt/smartslide/manage.py status
```

## Manual Production Setup

### 1. System Requirements
- Ubuntu 20.04+ or similar Linux distribution
- Python 3.8+
- Node.js 16+
- Nginx
- 2GB+ RAM
- 10GB+ disk space

### 2. Environment Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv python3-dev git nginx \
    build-essential curl wget unzip

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo bash -
sudo apt install -y nodejs

# Create application user
sudo useradd --system --shell /bin/bash --home /opt/smartslide --create-home smartslide
```

### 3. Application Installation

```bash
# Clone repository
sudo git clone https://github.com/arnuvp/SmartSlide-Generator.git /opt/smartslide
sudo chown -R smartslide:smartslide /opt/smartslide

# Setup Python environment
cd /opt/smartslide
sudo -u smartslide python3 -m venv venv
sudo -u smartslide ./venv/bin/pip install -r requirements.txt

# Install Playwright browsers
sudo -u smartslide ./venv/bin/playwright install --with-deps

# Create directories
sudo -u smartslide mkdir -p uploads outputs
sudo mkdir -p /var/log/smartslide
sudo chown smartslide:smartslide /var/log/smartslide
```

### 4. Configuration

```bash
# Copy production environment template
sudo cp /opt/smartslide/.env.production /opt/smartslide/.env

# Edit configuration (add your API keys)
sudo nano /opt/smartslide/.env
```

**Required .env configuration:**
```bash
GOOGLE_API_KEY=your_actual_google_api_key
SECRET_KEY=your_secure_secret_key_here
PEXELS_API_KEY=your_pexels_api_key  # Optional
```

### 5. Service Setup

```bash
# Install systemd service
sudo cp /opt/smartslide/smartslide.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable smartslide
sudo systemctl start smartslide
```

### 6. Nginx Configuration

```bash
# Copy nginx configuration
sudo cp /opt/smartslide/nginx.conf /etc/nginx/sites-available/smartslide

# Enable site
sudo ln -s /etc/nginx/sites-available/smartslide /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test and restart nginx
sudo nginx -t
sudo systemctl restart nginx
```

### 7. Firewall Setup

```bash
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
```

## Production Management

Use the management script for common operations:

```bash
# Check status
sudo python3 /opt/smartslide/manage.py status

# Start/stop/restart service
sudo python3 /opt/smartslide/manage.py start
sudo python3 /opt/smartslide/manage.py stop
sudo python3 /opt/smartslide/manage.py restart

# View logs
python3 /opt/smartslide/manage.py logs
python3 /opt/smartslide/manage.py logs --follow

# Update application
sudo python3 /opt/smartslide/manage.py update

# Health check
python3 /opt/smartslide/manage.py health

# View configuration
python3 /opt/smartslide/manage.py config
```

## SSL/HTTPS Setup (Optional but Recommended)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate (replace with your domain)
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

## Monitoring and Logs

### Service logs
```bash
sudo journalctl -u smartslide -f
```

### Nginx logs
```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Application logs
```bash
sudo tail -f /var/log/smartslide/app.log
```

## Troubleshooting

### Service won't start
1. Check logs: `sudo journalctl -u smartslide`
2. Verify environment: `python3 /opt/smartslide/manage.py config`
3. Test manually: `cd /opt/smartslide && sudo -u smartslide ./venv/bin/python wsgi.py`

### High memory usage
1. Reduce Gunicorn workers in service file
2. Monitor with: `python3 /opt/smartslide/manage.py status`

### Slow response times
1. Increase Gunicorn timeout in service file
2. Check server resources
3. Enable nginx caching

## Security Considerations

1. **API Keys**: Never commit real API keys to version control
2. **Firewall**: Only open necessary ports (80, 443, 22)
3. **Updates**: Keep system and dependencies updated
4. **Backups**: Regular backups of application and data
5. **SSL**: Always use HTTPS in production
6. **User Permissions**: Run application as non-root user

## Performance Optimization

1. **Gunicorn Workers**: Set to 2 × CPU cores + 1
2. **Nginx Caching**: Enable for static assets
3. **Gzip Compression**: Enabled in nginx configuration
4. **Resource Monitoring**: Use tools like htop, iotop
5. **Log Rotation**: Configure logrotate for application logs

## Backup Strategy

```bash
# Create backup script
sudo tee /usr/local/bin/backup-smartslide.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/smartslide/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r /opt/smartslide "$BACKUP_DIR/"
tar -czf "$BACKUP_DIR.tar.gz" -C /backup/smartslide "$(basename "$BACKUP_DIR")"
rm -rf "$BACKUP_DIR"
echo "Backup created: $BACKUP_DIR.tar.gz"
EOF

sudo chmod +x /usr/local/bin/backup-smartslide.sh

# Add to crontab for daily backups
echo "0 2 * * * root /usr/local/bin/backup-smartslide.sh" | sudo tee -a /etc/crontab
```
