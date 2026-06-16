# PowerShell Script to Setup Automatic KPI Calculation
# This script creates a Windows Scheduled Task to run KPI calculations daily

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Automatic KPI Calculation Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get the current directory (project root)
$ProjectRoot = $PSScriptRoot
$ManagePyPath = Join-Path $ProjectRoot "manage.py"

# Verify manage.py exists
if (-not (Test-Path $ManagePyPath)) {
    Write-Host "ERROR: manage.py not found at $ManagePyPath" -ForegroundColor Red
    Write-Host "Please run this script from the Django project root directory." -ForegroundColor Red
    exit 1
}

Write-Host "Project Root: $ProjectRoot" -ForegroundColor Green
Write-Host ""

# Find Python executable
$PythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $PythonPath) {
    Write-Host "ERROR: Python not found in PATH" -ForegroundColor Red
    Write-Host "Please ensure Python is installed and added to PATH." -ForegroundColor Red
    exit 1
}

Write-Host "Python Path: $PythonPath" -ForegroundColor Green
Write-Host ""

# Task Configuration
$TaskName = "CRM Auto Calculate KPIs"
$TaskDescription = "Automatically calculate employee KPIs daily at 11:30 PM"
$TaskTime = "23:30"  # 11:30 PM

Write-Host "Creating Scheduled Task: $TaskName" -ForegroundColor Yellow
Write-Host "Schedule: Daily at $TaskTime" -ForegroundColor Yellow
Write-Host ""

# Create the action (command to run)
$Action = New-ScheduledTaskAction `
    -Execute $PythonPath `
    -Argument "`"$ManagePyPath`" calculate_kpis" `
    -WorkingDirectory $ProjectRoot

# Create the trigger (daily at specified time)
$Trigger = New-ScheduledTaskTrigger -Daily -At $TaskTime

# Create task settings
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1)

# Create the principal (run as current user)
$Principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType S4U `
    -RunLevel Highest

try {
    # Check if task already exists
    $ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    
    if ($ExistingTask) {
        Write-Host "Task already exists. Updating..." -ForegroundColor Yellow
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    }
    
    # Register the scheduled task
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Description $TaskDescription `
        -Action $Action `
        -Trigger $Trigger `
        -Settings $Settings `
        -Principal $Principal | Out-Null
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  SUCCESS!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Scheduled Task Created Successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Task Details:" -ForegroundColor Cyan
    Write-Host "  Name: $TaskName" -ForegroundColor White
    Write-Host "  Schedule: Daily at $TaskTime" -ForegroundColor White
    Write-Host "  Command: python manage.py calculate_kpis" -ForegroundColor White
    Write-Host ""
    
    # Show next run time
    $Task = Get-ScheduledTask -TaskName $TaskName
    $TaskInfo = Get-ScheduledTaskInfo -TaskName $TaskName
    Write-Host "Next Run Time: $($TaskInfo.NextRunTime)" -ForegroundColor Yellow
    Write-Host ""
    
    Write-Host "Management Commands:" -ForegroundColor Cyan
    Write-Host "  View task: Get-ScheduledTask -TaskName '$TaskName'" -ForegroundColor White
    Write-Host "  Run now: Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor White
    Write-Host "  Disable: Disable-ScheduledTask -TaskName '$TaskName'" -ForegroundColor White
    Write-Host "  Remove: Unregister-ScheduledTask -TaskName '$TaskName'" -ForegroundColor White
    Write-Host ""
    
    Write-Host "Manual Testing:" -ForegroundColor Cyan
    Write-Host "  Test calculation: python manage.py calculate_kpis" -ForegroundColor White
    Write-Host "  Force recalculation: python manage.py calculate_kpis --force" -ForegroundColor White
    Write-Host "  Specific month: python manage.py calculate_kpis --month 2024-01" -ForegroundColor White
    Write-Host "  All months: python manage.py calculate_kpis --all-months --force" -ForegroundColor White
    Write-Host ""
    
    # Ask if user wants to run the task now
    $RunNow = Read-Host "Would you like to run the KPI calculation now? (Y/N)"
    if ($RunNow -eq 'Y' -or $RunNow -eq 'y') {
        Write-Host ""
        Write-Host "Running KPI calculation..." -ForegroundColor Yellow
        Start-ScheduledTask -TaskName $TaskName
        Write-Host "Task started! Check Task Scheduler for results." -ForegroundColor Green
    }
    
} catch {
    Write-Host ""
    Write-Host "ERROR: Failed to create scheduled task" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Please ensure you have administrator privileges." -ForegroundColor Yellow
    Write-Host "Try running PowerShell as Administrator." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host ""