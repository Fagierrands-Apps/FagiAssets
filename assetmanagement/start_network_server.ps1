# Asset Management System Network Startup Script
Write-Host "Starting Asset Management System on Network..." -ForegroundColor Green
Write-Host ""
Write-Host "Network IP: 10.246.23.10" -ForegroundColor Yellow
Write-Host "Server URL: http://10.246.23.10:8000/" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Cyan
Write-Host ""

# Start the Django server
python manage.py runserver 0.0.0.0:8000
