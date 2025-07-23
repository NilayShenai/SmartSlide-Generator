@echo off
echo ==========================================
echo SmartSlide Generator - Production Server
echo ==========================================
echo.

REM Check Python and Gunicorn
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    pause
    exit /b 1
)

python -c "import gunicorn" >nul 2>&1
if errorlevel 1 (
    echo Installing Gunicorn...
    pip install gunicorn
    if errorlevel 1 (
        echo ERROR: Failed to install Gunicorn
        pause
        exit /b 1
    )
)

REM Check environment
echo Checking production environment...
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('✅ Production environment loaded'); print('DEBUG:', os.getenv('DEBUG')); print('PORT:', os.getenv('PORT')); print('WORKERS:', os.getenv('WORKERS')); print('API Keys configured:', bool(os.getenv('GOOGLE_API_KEY')))"

if errorlevel 1 (
    echo ERROR: Environment check failed
    pause
    exit /b 1
)

echo.
echo Starting Production WSGI Server (Gunicorn)...
echo.
echo Server Configuration:
echo - Workers: 4
echo - Timeout: 600 seconds
echo - Bind: 0.0.0.0:5001
echo - Access: http://localhost:5001
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start Gunicorn production server
gunicorn --workers 4 --timeout 600 --bind 0.0.0.0:5001 --access-logfile - --error-logfile - wsgi:application

echo.
echo Production server stopped.
pause
