@echo off
echo Starting Asset Management System...
echo.

echo 1. Starting Django server...
cd /d "c:\Users\a\Downloads\assetmanagement"
start "Django Server" cmd /k "python manage.py runserver 0.0.0.0:8000"

echo 2. Waiting for server to start...
timeout /t 5 /nobreak > nul

echo 3. Starting Desktop App...
cd /d "c:\Users\a\Downloads\assetmanagement\desktop-app"
start "Asset Management Desktop" cmd /k "npm start"

echo 4. Opening API test page...
start "API Test" "test_desktop_api.html"

echo.
echo All components started!
echo - Django Server: http://10.246.23.10:8000 (Network accessible)
echo - Local Access: http://127.0.0.1:8000
echo - Desktop App: Should launch automatically
echo - API Test Page: Should open in browser
echo.
pause