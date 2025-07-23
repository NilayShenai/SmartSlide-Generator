# 🚀 SmartSlide Generator - Production Deployment

## Overview

This document provides comprehensive instructions for deploying SmartSlide Generator to production using multiple deployment methods.

## Deployment Options

### 1. 🐳 Docker Deployment (Recommended)
Easiest and most reliable deployment method.

### 2. 🖥️ Traditional Server Deployment
Direct installation on Ubuntu/Debian servers.

### 3. ☁️ Cloud Platform Deployment
Instructions for various cloud providers.

---

## 🐳 Docker Deployment

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/arnuvp/SmartSlide-Generator.git
cd SmartSlide-Generator

# 2. Configure environment
cp .env.production .env
nano .env  # Add your API keys

# 3. Build and run
docker-compose up -d

# 4. Check status
docker-compose ps
docker-compose logs -f
```

### Environment Configuration

Edit `.env` file with your API keys:

```bash
GOOGLE_API_KEY=your_actual_google_api_key
SECRET_KEY=your_secure_secret_key
PEXELS_API_KEY=your_pexels_api_key  # Optional
```

### Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# View logs
docker-compose logs -f smartslide
docker-compose logs -f nginx

# Update application
git pull origin main
docker-compose build smartslide
docker-compose up -d smartslide

# Backup data
docker run --rm -v smartslide_uploads:/data -v $(pwd):/backup alpine tar czf /backup/uploads-backup.tar.gz -C /data .
```

---

## 🖥️ Traditional Server Deployment

### One-Line Installation

```bash
wget -O - https://raw.githubusercontent.com/arnuvp/SmartSlide-Generator/main/deploy.sh | sudo bash
```

### Manual Installation

1. **System Setup**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv python3-dev git nginx build-essential curl
```

2. **Install Node.js**
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo bash -
sudo apt install -y nodejs
```

3. **Create User and Directory**
```bash
sudo useradd --system --shell /bin/bash --home /opt/smartslide --create-home smartslide
sudo git clone https://github.com/arnuvp/SmartSlide-Generator.git /opt/smartslide
sudo chown -R smartslide:smartslide /opt/smartslide
```

4. **Setup Python Environment**
```bash
cd /opt/smartslide
sudo -u smartslide python3 -m venv venv
sudo -u smartslide ./venv/bin/pip install -r requirements.txt
sudo -u smartslide ./venv/bin/playwright install --with-deps
```

5. **Configure Environment**
```bash
sudo cp .env.production .env
sudo nano .env  # Add your API keys
sudo chown smartslide:smartslide .env
```

6. **Setup Service**
```bash
sudo cp smartslide.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable smartslide
sudo systemctl start smartslide
```

7. **Configure Nginx**
```bash
sudo cp nginx.conf /etc/nginx/sites-available/smartslide
sudo ln -s /etc/nginx/sites-available/smartslide /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

### Management Commands

```bash
# Using the management script
sudo python3 /opt/smartslide/manage.py status
sudo python3 /opt/smartslide/manage.py start
sudo python3 /opt/smartslide/manage.py stop
sudo python3 /opt/smartslide/manage.py restart
sudo python3 /opt/smartslide/manage.py update
python3 /opt/smartslide/manage.py logs --follow
python3 /opt/smartslide/manage.py health
```

---

## ☁️ Cloud Platform Deployment

### Digital Ocean Droplet

1. **Create Droplet**
   - Ubuntu 22.04 LTS
   - 2GB RAM minimum
   - Enable monitoring

2. **Deploy**
```bash
# SSH to your droplet
ssh root@your-droplet-ip

# Run deployment script
wget -O - https://raw.githubusercontent.com/arnuvp/SmartSlide-Generator/main/deploy.sh | bash

# Configure domain (if you have one)
sudo nano /etc/nginx/sites-available/smartslide
# Replace 'server_name _;' with 'server_name your-domain.com;'
sudo systemctl restart nginx
```

### AWS EC2

1. **Launch Instance**
   - Ubuntu 22.04 LTS
   - t3.small or larger
   - Security group: Allow HTTP (80), HTTPS (443), SSH (22)

2. **Deploy**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install git
sudo apt install -y git

# Clone and deploy
git clone https://github.com/arnuvp/SmartSlide-Generator.git
cd SmartSlide-Generator
sudo ./deploy.sh
```

### Google Cloud Platform

Similar to AWS EC2 setup. Use Ubuntu 22.04 LTS on Compute Engine.

### Heroku

1. **Create Heroku App**
```bash
heroku create your-app-name
```

2. **Set Environment Variables**
```bash
heroku config:set GOOGLE_API_KEY=your_key
heroku config:set SECRET_KEY=your_secret
heroku config:set PEXELS_API_KEY=your_pexels_key
```

3. **Deploy**
```bash
git push heroku main
```

---

## 🔒 SSL/HTTPS Setup

### Using Let's Encrypt (Recommended)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate (replace with your domain)
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

### Using Custom SSL Certificate

1. Place certificate files in `/etc/ssl/certs/`
2. Update nginx configuration
3. Restart nginx

---

## 📊 Monitoring and Maintenance

### Health Checks

```bash
# Application health
curl http://localhost:5001/api/health

# Service status
sudo systemctl status smartslide
sudo systemctl status nginx

# Resource usage
python3 /opt/smartslide/manage.py status
```

### Log Monitoring

```bash
# Application logs
sudo journalctl -u smartslide -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Application-specific logs
sudo tail -f /var/log/smartslide/app.log
```

### Performance Tuning

1. **Gunicorn Workers**: Adjust based on CPU cores
```bash
# Edit service file
sudo nano /etc/systemd/system/smartslide.service
# Change --workers value to (2 × CPU cores + 1)
```

2. **Nginx Caching**
```bash
# Add to nginx configuration
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### Backup Strategy

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

# Schedule daily backups
echo "0 2 * * * root /usr/local/bin/backup-smartslide.sh" | sudo tee -a /etc/crontab
```

---

## 🚨 Troubleshooting

### Common Issues

1. **Service Won't Start**
```bash
sudo journalctl -u smartslide --no-pager
python3 /opt/smartslide/manage.py config
```

2. **High Memory Usage**
```bash
# Check processes
ps aux | grep gunicorn
# Reduce workers in service file
```

3. **Slow Response**
```bash
# Check timeout settings
sudo nano /etc/systemd/system/smartslide.service
# Increase --timeout value
```

4. **File Upload Issues**
```bash
# Check nginx client_max_body_size
sudo nano /etc/nginx/sites-available/smartslide
```

### Emergency Recovery

```bash
# Stop all services
sudo systemctl stop smartslide nginx

# Restore from backup
sudo tar -xzf /backup/smartslide/backup-file.tar.gz -C /

# Start services
sudo systemctl start smartslide nginx
```

---

## 📈 Scaling Considerations

### Horizontal Scaling

1. **Load Balancer**: Use nginx or cloud load balancer
2. **Multiple Instances**: Deploy on multiple servers
3. **Shared Storage**: Use NFS or cloud storage for uploads/outputs

### Vertical Scaling

1. **Increase Workers**: More Gunicorn workers
2. **More RAM**: Better for concurrent processing
3. **Faster Storage**: SSD for better I/O performance

---

## 🔐 Security Best Practices

1. **Firewall Configuration**
```bash
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
```

2. **Regular Updates**
```bash
sudo apt update && sudo apt upgrade -y
python3 /opt/smartslide/manage.py update
```

3. **Secret Management**
   - Use environment variables
   - Never commit secrets to version control
   - Rotate API keys regularly

4. **Access Control**
   - Use SSH keys, not passwords
   - Limit sudo access
   - Monitor access logs

---

## 📞 Support

For deployment issues:
1. Check the troubleshooting section
2. Review logs for error messages
3. Create an issue on GitHub
4. Check the documentation

---

## 📋 Deployment Checklist

- [ ] System requirements met
- [ ] API keys obtained and configured
- [ ] Environment variables set
- [ ] Application deployed and running
- [ ] Nginx configured and running
- [ ] SSL certificate installed (if needed)
- [ ] Firewall configured
- [ ] Monitoring set up
- [ ] Backup strategy implemented
- [ ] Health checks passing
- [ ] Performance tested
- [ ] Security review completed

---

**Deployment complete! 🎉**

Your SmartSlide Generator should now be running in production mode.
