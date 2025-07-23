@echo off
echo ========================================
echo SmartSlide Generator - Production Mode
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "run.py" (
    echo ERROR: run.py not found. Please run this script from the SmartSlide-Generator directory
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo ERROR: .env file not found. Please copy .env.production to .env and configure your API keys
    pause
    exit /b 1
)

echo Checking environment configuration...
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('✅ Environment loaded'); print('Production mode:', os.getenv('DEBUG', 'True').lower() == 'false'); print('Port:', os.getenv('PORT', '5000')); print('Host:', os.getenv('HOST', '127.0.0.1')); print('Google API Key configured:', bool(os.getenv('GOOGLE_API_KEY')))"

if errorlevel 1 (
    echo ERROR: Environment configuration failed
    pause
    exit /b 1
)

echo.
echo Starting SmartSlide Generator in Production Mode...
echo Press Ctrl+C to stop the server
echo.
echo Server will be available at: http://localhost:5001
echo.

REM Start the application
python run.py

echo.
echo SmartSlide Generator stopped.
pause
