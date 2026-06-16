Write-Host "Starting Asset Management System..." -ForegroundColor Green
Write-Host ""

Write-Host "1. Starting Django server..." -ForegroundColor Yellow
Set-Location "c:\Users\a\Downloads\assetmanagement"
Start-Job -Name "DjangoServer" -ScriptBlock { python manage.py runserver 0.0.0.0:8000 }

Write-Host "2. Waiting for server to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "3. Starting Desktop App..." -ForegroundColor Yellow
Set-Location "c:\Users\a\Downloads\assetmanagement\desktop-app"
Start-Job -Name "DesktopApp" -ScriptBlock { npm start }

Write-Host "4. Opening API test page..." -ForegroundColor Yellow
Start-Process "test_desktop_api.html"

Write-Host ""
Write-Host "All components started!" -ForegroundColor Green
Write-Host "- Django Server: http://10.246.23.10:8000 (Network accessible)" -ForegroundColor Cyan
Write-Host "- Local Access: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "- Desktop App: Should launch automatically" -ForegroundColor Cyan
Write-Host "- API Test Page: Should open in browser" -ForegroundColor Cyan
Write-Host ""

Write-Host "Jobs running:" -ForegroundColor Yellow
Get-Job

Write-Host ""
Write-Host "Press any key to view job output or Ctrl+C to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host ""
Write-Host "Django Server Output:" -ForegroundColor Yellow
Receive-Job -Name "DjangoServer"

Write-Host ""
Write-Host "Desktop App Output:" -ForegroundColor Yellow
Receive-Job -Name "DesktopApp"