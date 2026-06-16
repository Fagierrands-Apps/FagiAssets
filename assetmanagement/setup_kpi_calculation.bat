@echo off
REM Batch Script to Setup Automatic KPI Calculation
REM This script creates a Windows Scheduled Task to run KPI calculations daily

echo ========================================
echo   Automatic KPI Calculation Setup
echo ========================================
echo.

REM Get the current directory
set PROJECT_ROOT=%~dp0
set MANAGE_PY=%PROJECT_ROOT%manage.py

REM Verify manage.py exists
if not exist "%MANAGE_PY%" (
    echo ERROR: manage.py not found at %MANAGE_PY%
    echo Please run this script from the Django project root directory.
    pause
    exit /b 1
)

echo Project Root: %PROJECT_ROOT%
echo.

REM Find Python executable
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found in PATH
    echo Please ensure Python is installed and added to PATH.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('where python') do set PYTHON_PATH=%%i
echo Python Path: %PYTHON_PATH%
echo.

REM Task Configuration
set TASK_NAME=CRM Auto Calculate KPIs
set TASK_TIME=23:30

echo Creating Scheduled Task: %TASK_NAME%
echo Schedule: Daily at %TASK_TIME%
echo.

REM Delete existing task if it exists
schtasks /query /tn "%TASK_NAME%" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Task already exists. Deleting...
    schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1
)

REM Create the scheduled task
schtasks /create ^
    /tn "%TASK_NAME%" ^
    /tr "\"%PYTHON_PATH%\" \"%MANAGE_PY%\" calculate_kpis" ^
    /sc daily ^
    /st %TASK_TIME% ^
    /rl HIGHEST ^
    /f

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   SUCCESS!
    echo ========================================
    echo.
    echo Scheduled Task Created Successfully!
    echo.
    echo Task Details:
    echo   Name: %TASK_NAME%
    echo   Schedule: Daily at %TASK_TIME%
    echo   Command: python manage.py calculate_kpis
    echo.
    echo Management Commands:
    echo   View task: schtasks /query /tn "%TASK_NAME%"
    echo   Run now: schtasks /run /tn "%TASK_NAME%"
    echo   Delete: schtasks /delete /tn "%TASK_NAME%" /f
    echo.
    echo Manual Testing:
    echo   Test calculation: python manage.py calculate_kpis
    echo   Force recalculation: python manage.py calculate_kpis --force
    echo   Specific month: python manage.py calculate_kpis --month 2024-01
    echo   All months: python manage.py calculate_kpis --all-months --force
    echo.
    
    set /p RUN_NOW="Would you like to run the KPI calculation now? (Y/N): "
    if /i "%RUN_NOW%"=="Y" (
        echo.
        echo Running KPI calculation...
        schtasks /run /tn "%TASK_NAME%"
        echo Task started! Check Task Scheduler for results.
    )
) else (
    echo.
    echo ERROR: Failed to create scheduled task
    echo Please ensure you have administrator privileges.
    echo Try running this script as Administrator.
    pause
    exit /b 1
)

echo.
echo Setup Complete!
echo.
pause