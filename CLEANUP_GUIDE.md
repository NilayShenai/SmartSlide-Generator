# Bloat Files to Remove (Optional Cleanup)

## Docker Files (since not using Docker):
- Dockerfile
- docker-compose.yml
- deploy.sh
- deploy.bat

## Unnecessary Config Files:
- .dockerignore (if exists)
- nginx/ directory (if not using nginx)

## Development Files (if not needed):
- .gitignore entries for unnecessary items
- __pycache__ directories
- .pyc files

## Optional Cleanup Commands:

### Windows:
```batch
REM Remove Docker files
del Dockerfile
del docker-compose.yml
del deploy.bat

REM Remove Python cache
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc

REM Remove nginx config if not needed
rmdir /s /q nginx
```

### Linux:
```bash
# Remove Docker files
rm -f Dockerfile docker-compose.yml deploy.sh

# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete

# Remove nginx config if not needed
rm -rf nginx/
```

## Keep These Essential Files:
- run.py (main entry point)
- requirements.txt (dependencies)
- .env / .env.production (environment config)
- app/ directory (application code)
- start-windows.bat / start-linux.sh (startup scripts)
- README.md (documentation)
