@echo off
REM SmartSlide Generator - Docker Build and Run Script for Windows
REM This script builds and runs the SmartSlide Generator in Docker containers

echo 🚀 Building SmartSlide Generator Docker containers...

REM Build the application
echo 📦 Building application container...
docker-compose build --no-cache
if %ERRORLEVEL% neq 0 (
    echo ❌ Docker build failed
    exit /b 1
)

REM Create necessary directories
echo 📁 Creating required directories...
if not exist "uploads" mkdir uploads
if not exist "outputs" mkdir outputs
if not exist "logs" mkdir logs

REM Start the services
echo 🔧 Starting services...
docker-compose up -d
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to start Docker services
    exit /b 1
)

REM Wait for services to be ready
echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check health
echo 🏥 Checking service health...
set MAX_RETRIES=30
set RETRY_COUNT=0

:healthcheck
if %RETRY_COUNT% geq %MAX_RETRIES% (
    echo ❌ Services failed to start properly
    echo 📋 Container status:
    docker-compose ps
    echo 📋 Application logs:
    docker-compose logs smartslide
    exit /b 1
)

curl -f http://localhost/api/health >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo ✅ Services are healthy!
    goto success
)

echo ⏳ Waiting for services to be ready... (attempt %RETRY_COUNT%/%MAX_RETRIES%)
timeout /t 2 /nobreak >nul
set /a RETRY_COUNT+=1
goto healthcheck

:success
echo 🎉 SmartSlide Generator is running!
echo 🌐 Access the application at: http://localhost
echo 🔍 Health check: http://localhost/api/health
echo.
echo 📋 To view logs: docker-compose logs -f
echo 🛑 To stop: docker-compose down
echo 🗑️  To stop and remove volumes: docker-compose down -v
pause
