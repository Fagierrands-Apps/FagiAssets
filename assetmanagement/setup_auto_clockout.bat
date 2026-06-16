@echo off
REM Setup Windows Task Scheduler for automatic clock-out

echo Setting up automatic clock-out tasks...
echo.

REM Get the current directory
set SCRIPT_DIR=%~dp0

REM Create task for 1:30 PM lunch clock-out
schtasks /create /tn "CRM Auto Clock-Out Lunch" /tr "python \"%SCRIPT_DIR%manage.py\" auto_clockout --time 13:30" /sc daily /st 13:30 /f

REM Create task for 10:00 PM end-of-day clock-out
schtasks /create /tn "CRM Auto Clock-Out End of Day" /tr "python \"%SCRIPT_DIR%manage.py\" auto_clockout --time 22:00" /sc daily /st 22:00 /f

echo.
echo Tasks created successfully!
echo.
echo To view the tasks, run: schtasks /query /tn "CRM Auto Clock-Out*"
echo To delete the tasks, run: schtasks /delete /tn "CRM Auto Clock-Out Lunch" /f
echo                           schtasks /delete /tn "CRM Auto Clock-Out End of Day" /f
echo.
pause