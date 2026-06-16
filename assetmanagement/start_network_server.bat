@echo off
echo Starting Asset Management System on Network...
echo.
echo Network IP: 10.246.23.10
echo Server URL: http://10.246.23.10:8000/
echo.
echo Press Ctrl+C to stop the server
echo.
python manage.py runserver 0.0.0.0:8000
pause
