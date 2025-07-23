@echo off
echo 🚀 SmartSlide Generator - Windows Production
echo.

REM Check Python
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Python not found. Install Python 3.8+ and add to PATH
    pause & exit /b 1
)

REM Create directories
if not exist "uploads" mkdir uploads
if not exist "outputs" mkdir outputs  
if not exist "logs" mkdir logs

REM Check environment
if not exist ".env" (
    if exist ".env.production" (
        copy ".env.production" ".env" >nul
        echo ✅ Using .env.production
    ) else (
        echo ❌ Create .env file with:
        echo GOOGLE_API_KEY=your_gemini_api_key
        echo PEXELS_API_KEY=your_pexels_api_key
        pause & exit /b 1
    )
)

REM Install minimal dependencies
echo 📦 Installing dependencies...
pip install -q -r requirements.txt

echo.
echo 🔧 Starting Production Server (Waitress WSGI)
echo 🌐 http://localhost:5001
echo.
python run.py
