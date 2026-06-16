# PowerShell script to setup Windows Task Scheduler for automatic clock-out

Write-Host "Setting up automatic clock-out tasks..." -ForegroundColor Green
Write-Host ""

# Get the current directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$managePy = Join-Path $scriptDir "manage.py"

# Get Python executable path
$pythonPath = (Get-Command python).Source

# Create task for 1:30 PM lunch clock-out
$action1 = New-ScheduledTaskAction -Execute $pythonPath -Argument "`"$managePy`" auto_clockout --time 13:30" -WorkingDirectory $scriptDir
$trigger1 = New-ScheduledTaskTrigger -Daily -At "13:30"
$settings1 = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName "CRM Auto Clock-Out Lunch" -Action $action1 -Trigger $trigger1 -Settings $settings1 -Force

# Create task for 10:00 PM end-of-day clock-out
$action2 = New-ScheduledTaskAction -Execute $pythonPath -Argument "`"$managePy`" auto_clockout --time 22:00" -WorkingDirectory $scriptDir
$trigger2 = New-ScheduledTaskTrigger -Daily -At "22:00"
$settings2 = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName "CRM Auto Clock-Out End of Day" -Action $action2 -Trigger $trigger2 -Settings $settings2 -Force

Write-Host ""
Write-Host "Tasks created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "To view the tasks, run: Get-ScheduledTask -TaskName 'CRM Auto Clock-Out*'" -ForegroundColor Yellow
Write-Host "To delete the tasks, run: Unregister-ScheduledTask -TaskName 'CRM Auto Clock-Out Lunch' -Confirm:`$false" -ForegroundColor Yellow
Write-Host "                          Unregister-ScheduledTask -TaskName 'CRM Auto Clock-Out End of Day' -Confirm:`$false" -ForegroundColor Yellow
Write-Host ""