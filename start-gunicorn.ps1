# SmartSlide Generator - Production Server (PowerShell)
Write-Host "==========================================" -ForegroundColor Green
Write-Host "SmartSlide Generator - Production Server" -ForegroundColor Green  
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Python not found" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check/Install Gunicorn
try {
    python -c "import gunicorn" 2>$null
    Write-Host "✅ Gunicorn available" -ForegroundColor Green
} catch {
    Write-Host "📦 Installing Gunicorn..." -ForegroundColor Yellow
    pip install gunicorn
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ ERROR: Failed to install Gunicorn" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Check environment
Write-Host "🔍 Checking production environment..." -ForegroundColor Cyan
try {
    $envCheck = python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('✅ Production environment loaded'); print('DEBUG:', os.getenv('DEBUG')); print('PORT:', os.getenv('PORT')); print('WORKERS:', os.getenv('WORKERS')); print('API Keys configured:', bool(os.getenv('GOOGLE_API_KEY')))" 2>&1
    Write-Host $envCheck -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Environment check failed" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "🚀 Starting Production WSGI Server (Gunicorn)..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Server Configuration:" -ForegroundColor Cyan
Write-Host "- Workers: 4" -ForegroundColor White
Write-Host "- Timeout: 600 seconds" -ForegroundColor White  
Write-Host "- Bind: 0.0.0.0:5001" -ForegroundColor White
Write-Host "- Access: http://localhost:5001" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start Gunicorn
try {
    gunicorn --workers 4 --timeout 600 --bind 0.0.0.0:5001 --access-logfile - --error-logfile - wsgi:application
} catch {
    Write-Host "❌ ERROR: Failed to start Gunicorn server" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
} finally {
    Write-Host ""
    Write-Host "Production server stopped." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
}
