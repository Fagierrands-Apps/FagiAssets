# Automatic Clock-Out System

## Overview
The automatic clock-out system ensures that employees are properly clocked out at specific times during the day, preventing overtime issues and ensuring accurate time tracking.

## Features

### 1. Lunch Break Clock-Out (1:30 PM)
- **Time**: 1:30 PM (13:30) daily
- **Action**: 
  - Automatically clocks out all employees who are currently clocked in
  - Immediately clocks them back in for the afternoon shift
  - This creates a break in the work session for lunch
- **Purpose**: Ensures lunch breaks are properly tracked and employees continue working after lunch

### 2. End-of-Day Clock-Out (10:00 PM)
- **Time**: 10:00 PM (22:00) daily
- **Action**: 
  - Automatically clocks out all employees who are still clocked in
  - Does NOT clock them back in
- **Purpose**: Prevents employees from being clocked in overnight and ensures accurate daily time tracking

## Implementation

### Management Command
The system uses a Django management command located at:
```
crm/management/commands/auto_clockout.py
```

### Command Usage

#### Automatic Mode (Run by Task Scheduler)
```bash
python manage.py auto_clockout
```
This checks the current time and performs the appropriate clock-out action.

#### Manual Mode with Specific Time
```bash
# Trigger lunch clock-out
python manage.py auto_clockout --time 13:30

# Trigger end-of-day clock-out
python manage.py auto_clockout --time 22:00
```

#### Force Mode (Testing)
```bash
# Force both clock-outs regardless of time
python manage.py auto_clockout --force
```

## Setup Instructions

### Windows Task Scheduler Setup

#### Option 1: Using PowerShell Script (Recommended)
1. Open PowerShell as Administrator
2. Navigate to the project directory:
   ```powershell
   cd c:\Users\a\Documents\GitHub\fagiassets\assetmanagement
   ```
3. Run the setup script:
   ```powershell
   .\setup_auto_clockout.ps1
   ```

#### Option 2: Using Batch Script
1. Open Command Prompt as Administrator
2. Navigate to the project directory:
   ```cmd
   cd c:\Users\a\Documents\GitHub\fagiassets\assetmanagement
   ```
3. Run the setup script:
   ```cmd
   setup_auto_clockout.bat
   ```

#### Option 3: Manual Setup
1. Open Task Scheduler (taskschd.msc)
2. Create a new task:
   - **Name**: CRM Auto Clock-Out Lunch
   - **Trigger**: Daily at 1:30 PM
   - **Action**: Start a program
     - Program: `python`
     - Arguments: `"c:\Users\a\Documents\GitHub\fagiassets\assetmanagement\manage.py" auto_clockout --time 13:30`
     - Start in: `c:\Users\a\Documents\GitHub\fagiassets\assetmanagement`
3. Create another task:
   - **Name**: CRM Auto Clock-Out End of Day
   - **Trigger**: Daily at 10:00 PM
   - **Action**: Start a program
     - Program: `python`
     - Arguments: `"c:\Users\a\Documents\GitHub\fagiassets\assetmanagement\manage.py" auto_clockout --time 22:00`
     - Start in: `c:\Users\a\Documents\GitHub\fagiassets\assetmanagement`

### Linux/Unix Cron Setup
Add these lines to your crontab (`crontab -e`):
```bash
# Lunch clock-out at 1:30 PM
30 13 * * * cd /path/to/project && python manage.py auto_clockout --time 13:30

# End-of-day clock-out at 10:00 PM
0 22 * * * cd /path/to/project && python manage.py auto_clockout --time 22:00
```

## How It Works

### Lunch Break Process (1:30 PM)
1. System identifies all employees currently clocked in
2. Creates a `punch_out` time entry at 1:30 PM with note "Automatic clock-out for lunch break"
3. Immediately creates a `punch_in` time entry at 1:30:01 PM with note "Automatic clock-in after lunch break"
4. Updates work sessions to reflect the break
5. Employees continue working without manual intervention

### End-of-Day Process (10:00 PM)
1. System identifies all employees currently clocked in
2. Creates a `punch_out` time entry at 10:00 PM with note "Automatic end-of-day clock-out"
3. Updates work sessions to mark them as complete
4. Employees must manually clock in the next day

### Work Session Updates
After each clock-out operation, the system:
- Calculates total hours worked
- Calculates break hours
- Calculates net worked hours (total - breaks)
- Updates the `WorkSession` model with accurate data
- Marks sessions as complete when punch-out is recorded

## Database Impact

### TimeEntry Model
New entries are created with:
- `entry_type`: 'punch_out' or 'punch_in'
- `timestamp`: The scheduled time (1:30 PM or 10:00 PM)
- `location`: 'System Auto Clock-Out' or 'System Auto Clock-In'
- `notes`: Descriptive message about the automatic action

### WorkSession Model
Updated fields:
- `punch_out`: Set to the clock-out time
- `total_hours`: Calculated from punch_in to punch_out
- `break_hours`: Sum of all break durations
- `worked_hours`: total_hours - break_hours
- `is_complete`: Set to True when punch_out is recorded

## Testing

### Test Lunch Clock-Out
```bash
python manage.py auto_clockout --time 13:30
```

### Test End-of-Day Clock-Out
```bash
python manage.py auto_clockout --time 22:00
```

### Test Both (Force Mode)
```bash
python manage.py auto_clockout --force
```

### Verify Results
1. Check the TimeEntry records in the admin panel
2. Check the WorkSession records to see updated hours
3. View the employee timesheet to see the automatic entries

## Monitoring

### Check Task Status (Windows)
```powershell
Get-ScheduledTask -TaskName "CRM Auto Clock-Out*"
```

### View Task History (Windows)
1. Open Task Scheduler
2. Navigate to Task Scheduler Library
3. Find "CRM Auto Clock-Out Lunch" or "CRM Auto Clock-Out End of Day"
4. Click on the "History" tab

### Check Logs
The management command outputs to stdout, which can be captured by the task scheduler or cron.

## Troubleshooting

### Task Not Running
1. Verify Python is in the system PATH
2. Check Task Scheduler history for errors
3. Ensure the working directory is correct
4. Test the command manually first

### Employees Not Being Clocked Out
1. Check if employees are actually clocked in
2. Verify the employee status is 'active'
3. Check the time window (command runs for 5 minutes after scheduled time)
4. Review the command output for errors

### Work Sessions Not Updating
1. Ensure TimeEntry records are being created
2. Check for database errors in Django logs
3. Verify the WorkSession model is properly configured

## Benefits

1. **Accurate Time Tracking**: Ensures all work hours are properly recorded
2. **Prevents Overtime Issues**: Automatically clocks out employees at end of day
3. **Lunch Break Compliance**: Ensures lunch breaks are tracked
4. **Reduced Manual Errors**: Eliminates forgotten clock-outs
5. **Audit Trail**: All automatic actions are logged with notes
6. **Seamless Experience**: Employees continue working after lunch without manual clock-in

## Future Enhancements

- [ ] Email notifications to employees when auto clock-out occurs
- [ ] Configurable clock-out times per employee or department
- [ ] Support for multiple shifts with different schedules
- [ ] Integration with holiday calendar to skip auto clock-out on holidays
- [ ] SMS notifications for end-of-day clock-outs
- [ ] Dashboard widget showing auto clock-out statistics

## Related Files

- `crm/management/commands/auto_clockout.py` - Main command implementation
- `crm/models.py` - TimeEntry and WorkSession models
- `crm/views.py` - Employee timesheet view
- `setup_auto_clockout.ps1` - PowerShell setup script
- `setup_auto_clockout.bat` - Batch setup script

## Support

For issues or questions, contact the system administrator or refer to the Django management command documentation.