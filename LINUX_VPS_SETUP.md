# SmartSlide Generator - Linux VPS Deployment Guide

## 🚀 Quick Setup on Fresh Linux VPS

### Method 1: Automated Setup (Recommended)

1. **Upload files to VPS:**
   ```bash
   # On your local machine, upload files via SCP
   scp -r SmartSlide-Generator/ user@your-vps-ip:/home/user/
   
   # Or clone if you have a git repository
   ssh user@your-vps-ip
   git clone https://github.com/yourusername/SmartSlide-Generator.git
   cd SmartSlide-Generator
   ```

2. **Run automated setup:**
   ```bash
   chmod +x setup-linux-vps.sh
   ./setup-linux-vps.sh
   ```

3. **Configure API keys:**
   ```bash
   nano .env
   # Add your API keys:
   # GOOGLE_API_KEY=your_actual_gemini_key
   # PEXELS_API_KEY=your_actual_pexels_key
   ```

4. **Restart service:**
   ```bash
   sudo systemctl restart smartslide
   ```

---

### Method 2: Manual Setup

#### Step 1: System Prerequisites
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and essential packages
sudo apt install -y python3 python3-pip python3-venv git curl

# Install LibreOffice for PDF conversion
sudo apt install -y libreoffice fonts-liberation fonts-dejavu-core
```

#### Step 2: Application Setup
```bash
# Create directory and navigate
mkdir -p ~/smartslide-generator
cd ~/smartslide-generator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p uploads outputs logs
chmod 755 uploads outputs logs
```

#### Step 3: Environment Configuration
```bash
# Create .env file
cat > .env << EOF
DEBUG=false
HOST=0.0.0.0
PORT=5001
GOOGLE_API_KEY=your_gemini_api_key_here
PEXELS_API_KEY=your_pexels_api_key_here
SECRET_KEY=$(openssl rand -hex 32)
FLASK_ENV=production
PYTHONUNBUFFERED=1
EOF

# Edit with your actual API keys
nano .env
```

#### Step 4: Test Run
```bash
# Activate virtual environment
source venv/bin/activate

# Test the application
python run.py
```

#### Step 5: Production Service (Optional)
```bash
# Create systemd service
sudo tee /etc/systemd/system/smartslide.service > /dev/null << EOF
[Unit]
Description=SmartSlide Generator
After=network.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$HOME/smartslide-generator
Environment=PATH=$HOME/smartslide-generator/venv/bin
ExecStart=$HOME/smartslide-generator/venv/bin/python run.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable smartslide
sudo systemctl start smartslide
```

---

## 🌐 Access and Management

### Access URLs
- **Direct:** `http://your-vps-ip:5001`
- **With Nginx:** `http://your-vps-ip` (if nginx is configured)

### Service Management
```bash
# Check status
sudo systemctl status smartslide

# View logs
sudo journalctl -u smartslide -f

# Restart service
sudo systemctl restart smartslide

# Stop service
sudo systemctl stop smartslide
```

### Firewall Configuration
```bash
# Allow required ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 5001/tcp  # SmartSlide direct
sudo ufw allow 80/tcp    # HTTP (if using nginx)
sudo ufw enable
```

---

## 🔧 Troubleshooting

### Common Issues

1. **Service won't start:**
   ```bash
   sudo journalctl -u smartslide --no-pager -n 50
   ```

2. **Permission errors:**
   ```bash
   sudo chown -R $USER:$USER ~/smartslide-generator
   chmod +x ~/smartslide-generator/run.py
   ```

3. **Port already in use:**
   ```bash
   sudo lsof -i :5001
   # Kill the process or change port in .env
   ```

4. **Python dependencies issues:**
   ```bash
   cd ~/smartslide-generator
   source venv/bin/activate
   pip install --upgrade -r requirements.txt
   ```

### Log Locations
- **Application logs:** `~/smartslide-generator/logs/`
- **System service logs:** `sudo journalctl -u smartslide`
- **Nginx logs:** `/var/log/nginx/`

---

## 📦 File Structure
```
~/smartslide-generator/
├── run.py                 # Main application
├── requirements.txt       # Python dependencies
├── .env                   # Environment configuration
├── app/                   # Application code
├── uploads/               # Uploaded files
├── outputs/               # Generated presentations
├── logs/                  # Application logs
└── venv/                  # Python virtual environment
```

---

## 🔑 Required API Keys

1. **Google Gemini API:**
   - Go to: https://makersuite.google.com/app/apikey
   - Create API key
   - Add to .env: `GOOGLE_API_KEY=your_key_here`

2. **Pexels API (for images):**
   - Go to: https://www.pexels.com/api/
   - Create account and get API key
   - Add to .env: `PEXELS_API_KEY=your_key_here`

---

## 🚀 Production Tips

1. **Use a domain name:** Point your domain to the VPS IP
2. **Setup SSL:** Use Let's Encrypt with nginx
3. **Monitor resources:** Check CPU/RAM usage regularly
4. **Backup regularly:** Backup your .env and application data
5. **Update regularly:** Keep system and dependencies updated

---

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review application logs
3. Ensure all API keys are correctly configured
4. Verify all dependencies are installed
