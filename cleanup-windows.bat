@echo off
echo 🧹 Cleaning up bloat files...

REM Remove Docker files
if exist "Dockerfile" del "Dockerfile"
if exist "docker-compose.yml" del "docker-compose.yml"
if exist "deploy.bat" del "deploy.bat"
if exist "deploy.sh" del "deploy.sh"

REM Remove Python cache
echo Removing Python cache files...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul

REM Remove nginx if exists
if exist "nginx" rmdir /s /q "nginx"

REM Remove other unnecessary files
if exist ".dockerignore" del ".dockerignore"
if exist "wsgi.py" del "wsgi.py"

echo ✅ Cleanup complete!
echo.
echo 📋 Essential files kept:
echo - run.py (main entry point)
echo - requirements.txt (minimal dependencies)
echo - app/ (application code)
echo - .env (environment config)
echo - start-windows.bat (startup script)
echo.
pause
