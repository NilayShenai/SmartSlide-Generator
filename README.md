# 🎯 AI PowerPoint Generator

An intelligent web application that automatically generates professional PowerPoint presentations using AI. Built with Flask, LangChain, and Google's Gemini AI, featuring advanced visual elements like flowcharts, images, and multiple themes.

**🌐 Live Demo:** [http://64.227.185.133:5001](http://64.227.185.133:5001)

---

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Deployment Guide](#deployment-guide)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Known Issues](#known-issues)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Resources](#resources)

---

## ✨ Features

### 🤖 AI-Powered Content Generation
- **Smart Content Creation**: Generate presentations from topics or documents
- **Document Analysis**: Upload `.txt`, `.docx`, or `.pdf` files for content extraction
- **Intelligent Slide Prediction**: AI determines optimal number of slides based on content
- **Multi-format Support**: Text, DOCX, and PDF input processing

### 🎨 Visual Enhancement
- **Dynamic Images**: Automatic image fetching from Pexels API based on content
- **Flowchart Generation**: AI-generated Mermaid.js flowcharts for processes and workflows
- **6 Professional Themes**: Corporate, Technology, Creative, Academic, Health, Environment
- **Responsive Text Sizing**: Small, Medium, Large options
- **Gradient Backgrounds**: Modern styling with custom color schemes

### 🚀 Advanced Features
- **Background Processing**: Asynchronous job handling for large presentations
- **Real-time Progress**: WebSocket-based progress tracking
- **File Management**: Automatic cleanup of temporary files
- **Theme Customization**: Professional color palettes and typography
- **Error Handling**: Comprehensive error logging and user feedback

### 🌐 Web Interface
- **Modern UI**: Clean, responsive design
- **Progress Tracking**: Real-time generation status
- **Multiple Downloads**: PPTX format with planned PDF support
- **Configuration API**: Dynamic theme and setting management

---

## 🛠 Tech Stack

### Backend
- **Framework**: Flask 3.1.1 with Flask-CORS
- **AI/ML**: 
  - LangChain 0.3.26 for AI orchestration
  - Google Generative AI (Gemini-1.5-Pro)
- **Document Processing**:
  - python-pptx 1.0.2 for PowerPoint generation
  - python-docx 1.2.0 for Word documents
  - PyPDF2 3.0.1 for PDF processing
- **Visual Generation**:
  - Playwright 1.52.0 for flowchart rendering
  - Pillow 11.2.1 for image processing
  - Requests for Pexels API integration

### Frontend
- **HTML5/CSS3**: Modern responsive design
- **JavaScript**: Vanilla JS with async/await
- **UI Components**: Custom styled forms and progress indicators

### Deployment
- **Server**: Gunicorn 23.0.0 WSGI server
- **OS**: Ubuntu 22.04 LTS (Digital Ocean Droplet)
- **Process Management**: systemd service daemon
- **Environment**: Python 3.12 virtual environment

### External APIs
- **Google AI Studio**: Gemini API for content generation
- **Pexels API**: High-quality stock images
- **Mermaid.js**: Flowchart and diagram generation

---

## 📁 Project Structure

```
ai_ppt_maker_langchain_web/
├── 📄 run.py                      # Application entry point
├── 📄 ppt_maker_flo.py           # Core AI presentation logic
├── 📄 Procfile                   # Process configuration
├── 📄 requirements.txt           # Python dependencies
├── 📄 .env                       # Environment variables
├── 📄 README.md                  # This file
│
├── 📁 app/                       # Flask application package
│   ├── 📄 __init__.py           # App factory and configuration
│   ├── 📄 routes.py             # API endpoints and web routes
│   ├── 📄 utils.py              # Utility functions and helpers
│   └── 📁 templates/            # HTML templates
│       ├── 📄 index.html        # Main web interface
│       └── 📄 base.html         # Base template
│
├── 📁 uploads/                   # Temporary file uploads
├── 📁 outputs/                   # Generated presentations
├── 📁 env/                       # Virtual environment
└── 📁 __pycache__/              # Python cache files
```

### Key Files Breakdown

#### Core Components
- **`run.py`**: Flask application entry point with production configuration
- **`ppt_maker_flo.py`**: Advanced AI presentation generator with visual enhancements
- **`app/__init__.py`**: Flask app factory with CORS, file handling, and cleanup tasks
- **`app/routes.py`**: RESTful API endpoints for file upload, processing, and download
- **`app/utils.py`**: Utility functions for document processing and job management

#### Configuration
- **`requirements.txt`**: All Python dependencies with pinned versions
- **`.env`**: Environment variables for API keys and settings

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.9+ (3.12 recommended)
- pip package manager
- Virtual environment support
- Git (for cloning)

### Local Development Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/Innotronix-labs/ai-ppt-maker.git
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv env
   source env/bin/activate  # Linux/Mac
   # or
   env\Scripts\activate     # Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright Browsers**
   ```bash
   python -m playwright install
   python -m playwright install-deps
   ```

5. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

6. **Create Required Directories**
   ```bash
   mkdir -p uploads outputs
   chmod 755 uploads outputs
   ```

7. **Run Development Server**
   ```bash
   python run.py
   ```

### Environment Variables

Create a `.env` file in the project root:

```env
# Required: Google AI API Key
GOOGLE_API_KEY=your_google_ai_api_key_here

# Optional: Pexels API for images
PEXELS_API_KEY=your_pexels_api_key_here

# Application Configuration
SECRET_KEY=your-secret-key-here
DEBUG=False
PORT=5001
HOST=0.0.0.0

# Production Settings
FLASK_ENV=production
PYTHONUNBUFFERED=1
```

**🔑 Getting API Keys:**
- **Google AI**: [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
- **Pexels**: [https://www.pexels.com/api/](https://www.pexels.com/api/)

---

## 🌐 Deployment Guide

### Digital Ocean Droplet Setup

#### 1. Server Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv git nginx -y

# Install Playwright system dependencies
sudo apt install libnss3 libnspr4 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 \
libdrm2 libxkbcommon0 libgtk-3-0 libasound2 -y
```

#### 2. Application Deployment
```bash
# Clone repository
cd /root
git clone https://github.com/Innotronix-labs/ai-ppt-maker.git ai-ppt-maker
cd ai-ppt-maker

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
python -m playwright install
python -m playwright install-deps

# Set up environment
cp .env.example .env
nano .env  # Add your API keys

# Create directories
mkdir -p uploads outputs logs
chmod 755 uploads outputs
```

#### 3. Systemd Service Setup

Create `/etc/systemd/system/ai-ppt-maker.service`:
```ini
[Unit]
Description=Gunicorn instance to serve Flask app
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/root/ai-ppt-maker
Environment="PATH=/root/ai-ppt-maker/venv/bin"
ExecStart=/root/ai-ppt-maker/venv/bin/gunicorn --workers 4 --timeout 600 --bind 0.0.0.0:5001 run:app
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 4. Service Management
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable ai-ppt-maker

# Start service
sudo systemctl start ai-ppt-maker

# Check status
sudo systemctl status ai-ppt-maker

# Monitor logs
sudo journalctl -u ai-ppt-maker -f

# Restart service
sudo systemctl restart ai-ppt-maker
```

### Key Service Configuration Features

- **4 Workers**: Handles multiple concurrent requests efficiently
- **600-second timeout**: Allows for long AI processing tasks (10 minutes)
- **Auto-restart**: Service automatically restarts on failure
- **Port 5001**: Direct binding configured in `run.py`
- **Root user**: Full system access for file operations and Playwright browsers

#### 5. Firewall Configuration
```bash
# Allow application port
sudo ufw allow 5001/tcp

# Allow SSH (if not already configured)
sudo ufw allow ssh

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

### Nginx Reverse Proxy (Optional)

Create `/etc/nginx/sites-available/ai-ppt-maker`:
```nginx
server {
    listen 80;
    server_name 64.227.185.133;

    client_max_body_size 16M;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
    }
}
```

Enable and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/ai-ppt-maker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 📚 API Documentation

### Core Endpoints

#### Health Check
```http
GET /api/health
```
**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-07T14:30:00Z",
  "version": "1.0.0"
}
```

#### Configuration
```http
GET /api/config
```
**Response:**
```json
{
  "themes": ["corporate", "technology", "creative", "academic", "health", "environment"],
  "text_sizes": ["small", "medium", "large"],
  "tones": ["professional", "friendly", "urgent", "academic", "casual", "inspiring"],
  "audiences": ["general public", "technical professionals", "students", "executives"],
  "output_formats": ["pptx"],
  "max_slides": 20,
  "min_slides": 3,
  "supported_file_types": ["txt", "docx", "pdf"]
}
```

#### File Upload
```http
POST /api/upload
Content-Type: multipart/form-data

file: <uploaded_file>
```
**Response:**
```json
{
  "message": "File uploaded successfully",
  "filename": "20250707_143000_document.txt",
  "filepath": "/path/to/uploads/20250707_143000_document.txt",
  "content_preview": "Document content preview...",
  "content_length": 1250,
  "predicted_slides": 5
}
```

#### Generate Presentation
```http
POST /api/generate
Content-Type: application/json

{
  "mode": "topic",
  "topic": "Machine Learning Basics",
  "num_slides": 5,
  "theme": "technology",
  "text_size": "medium",
  "tone": "professional",
  "audience": "students",
  "filename": "ml_presentation"
}
```

**For Document Mode:**
```json
{
  "mode": "document",
  "filepath": "/path/to/document.txt",
  "num_slides": 8,
  "theme": "academic",
  "text_size": "medium",
  "tone": "academic",
  "audience": "students",
  "filename": "document_summary"
}
```

#### Job Status
```http
GET /api/job/{job_id}/status
```

#### Download File
```http
GET /api/download/{filename}
```

---

## ⚙️ Configuration

### Theme Customization

The application supports 6 built-in themes, each with unique color schemes and typography:

#### Corporate Theme
```python
"corporate": {
    "colors": {
        "primary": RGBColor(26, 35, 126),    # Indigo
        "secondary": RGBColor(144, 164, 174), # Blue-gray  
        "accent": RGBColor(255, 87, 34)       # Deep orange
    },
    "background": {
        "type": "gradient",
        "colors": [RGBColor(236, 239, 241), RGBColor(207, 216, 220)]
    },
    "fonts": {"title": "Segoe UI Semibold", "body": "Segoe UI"}
}
```

#### Technology Theme
```python
"technology": {
    "colors": {
        "primary": RGBColor(0, 230, 118),     # Neon green
        "secondary": RGBColor(3, 169, 244),   # Bright blue
        "accent": RGBColor(255, 64, 129)      # Electric pink
    },
    "background": {
        "type": "gradient", 
        "colors": [RGBColor(0, 0, 0), RGBColor(48, 48, 48)]
    },
    "fonts": {"title": "Roboto", "body": "Roboto"}
}
```

### Text Size Options
- **Small**: Title 26pt, Body 16pt, Subtitle 20pt
- **Medium**: Title 30pt, Body 20pt, Subtitle 24pt  
- **Large**: Title 34pt, Body 24pt, Subtitle 28pt

### Visual Elements
- **Images**: Automatic fetching from Pexels based on slide content
- **Flowcharts**: Mermaid.js syntax support for processes and workflows
- **Bullet Points**: Intelligent formatting without manual symbols

---

## 🐛 Known Issues

### Current Problems

#### 1. PDF Export Functionality
- **Issue**: PDF conversion not working in Linux environment
- **Cause**: `comtypes` library is Windows-specific
- **Status**: 🔴 Active Issue
- **Workaround**: Only PPTX format currently supported

#### 2. Frontend Generation Issues  
- **Issue**: Some frontend interaction problems during generation process
- **Symptoms**: Progress tracking inconsistencies, UI freezing
- **Status**: 🔴 Active Issue
- **Impact**: User experience during presentation generation

#### 3. Worker Timeout Issues (Resolved)
- **Issue**: Gunicorn workers timing out during AI processing
- **Solution**: ✅ Implemented increased timeout (600s) and proper worker configuration
- **Status**: 🟢 Resolved

### Temporary Limitations
- PDF export disabled on Linux servers
- Maximum file upload size: 16MB
- Processing timeout: 10 minutes
- Concurrent user limit: 2 workers

---

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes and test thoroughly
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Code Standards
- Follow PEP 8 for Python code
- Add docstrings for all functions
- Include error handling for external API calls
- Test on both development and production environments

### Reporting Issues
Please include:
- Python version and OS
- Error logs and stack traces  
- Steps to reproduce
- Expected vs actual behavior

---

## 📚 Resources

### Documentation
- **Flask**: [https://flask.palletsprojects.com/](https://flask.palletsprojects.com/)
- **LangChain**: [https://python.langchain.com/](https://python.langchain.com/)
- **Google AI**: [https://ai.google.dev/](https://ai.google.dev/)
- **python-pptx**: [https://python-pptx.readthedocs.io/](https://python-pptx.readthedocs.io/)
- **Playwright**: [https://playwright.dev/python/](https://playwright.dev/python/)

### API References
- **Gemini API**: [https://ai.google.dev/api/rest](https://ai.google.dev/api/rest)
- **Pexels API**: [https://www.pexels.com/api/documentation/](https://www.pexels.com/api/documentation/)
- **Mermaid.js**: [https://mermaid.js.org/syntax/flowchart.html](https://mermaid.js.org/syntax/flowchart.html)

### Deployment Guides
- **Digital Ocean**: [https://docs.digitalocean.com/products/droplets/](https://docs.digitalocean.com/products/droplets/)
- **Gunicorn**: [https://docs.gunicorn.org/](https://docs.gunicorn.org/)
- **systemd**: [https://systemd.io/](https://systemd.io/)

### Design Resources
- **Color Palettes**: [https://coolors.co/](https://coolors.co/)
- **Typography**: [https://fonts.google.com/](https://fonts.google.com/)
- **Icons**: [https://heroicons.com/](https://heroicons.com/)

---

## 🙏 Acknowledgments

- **Google AI** for Gemini API access
- **Pexels** for high-quality stock images
- **LangChain** for AI orchestration framework
- **Digital Ocean** for reliable hosting infrastructure
- **Open Source Community** for the amazing libraries and tools

---

## 📞 Support

- **🌐 Live Demo**: [http://64.227.185.133:5001](http://64.227.185.133:5001)
- **📧 Email**: [paularnav27@gmail.com]
- **🐛 Issues**: [GitHub Issues Page]
- **📖 Documentation**: [Wiki Page]

---

**Made with ❤️ by Arnav Paul**

*Transform your ideas into stunning presentations with the power of AI!*