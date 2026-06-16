# Automatic Lunch Break System

## Overview

The system automatically pauses work sessions for **1 hour at 1 PM (13:00 - 14:00)** for all employees except call center agents, Monday through Saturday.

## How It Works

### 1. **Middleware (Real-time)**
The `AutoLunchBreakMiddleware` runs on every request and:
- Checks if current time is between 1 PM - 2 PM
- Checks if today is Monday-Saturday (not Sunday)
- Excludes call center agents (`employee.role == 'call_center'`)
- Automatically creates `break_start` and `break_end` time entries
- The break entries are timestamped at exactly 13:00 and 14:00

### 2. **Management Command (Scheduled)**
For more reliable execution, you can also run the management command via cron/scheduler:

```bash
python manage.py auto_lunch_break
```

This command:
- Only runs between 13:00 - 13:05 to avoid duplicates
- Checks all active employees who are punched in
- Creates lunch break entries for non-call-center employees
- Skips employees who already have lunch break entries

## Configuration

### Lunch Break Settings
- **Start Time:** 1 PM (13:00)
- **End Time:** 2 PM (14:00)
- **Duration:** 1 hour
- **Days:** Monday - Saturday
- **Excluded:** Sunday
- **Exempt Roles:** `call_center`

### To Change Settings

Edit the middleware file: `crm/middleware/lunch_break_middleware.py`

```python
lunch_start = time(13, 0)  # Change to desired start time
lunch_end = time(14, 0)    # Change to desired end time
```

And the management command: `crm/management/commands/auto_lunch_break.py`

```python
lunch_start_time = time(13, 0)
lunch_end_time = time(14, 0)
```

## Setup Instructions

### Option 1: Middleware Only (Automatic)
✅ **Already Active!** The middleware is enabled in `settings.py` and will run automatically.

No additional setup needed. The system will automatically create lunch breaks when employees access the system during lunch hours.

### Option 2: Scheduled Task (Recommended for Production)

#### On Linux/Unix (crontab)

```bash
# Edit crontab
crontab -e

# Add this line to run at 1:00 PM every day
0 13 * * 1-6 cd /path/to/assetmanagement && python manage.py auto_lunch_break >> /var/log/lunch_break.log 2>&1
```

#### On Windows (Task Scheduler)

1. Open **Task Scheduler**
2. Click **Create Basic Task**
3. Name: "Auto Lunch Break"
4. Trigger: Daily at 1:00 PM
5. Action: Start a program
   - Program: `python`
   - Arguments: `c:\Users\a\Documents\GitHub\fagiassets\assetmanagement\manage.py auto_lunch_break`
   - Start in: `c:\Users\a\Documents\GitHub\fagiassets\assetmanagement`
6. Advanced: Set to run Monday-Saturday only

#### Using Django-Crontab (Python-based)

Install django-crontab:
```bash
pip install django-crontab
```

Add to `settings.py`:
```python
INSTALLED_APPS = [
    ...
    'django_crontab',
]

CRONJOBS = [
    ('0 13 * * 1-6', 'django.core.management.call_command', ['auto_lunch_break']),
]
```

Then run:
```bash
python manage.py crontab add
```

#### Using Celery Beat (Advanced)

If you're using Celery, add to `celery.py`:
```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    'auto-lunch-break': {
        'task': 'crm.tasks.auto_lunch_break',
        'schedule': crontab(hour=13, minute=0, day_of_week='1-6'),
    },
}
```

## How Employees Experience It

### For Regular Employees (Non-Call Center)

**Between 1 PM - 2 PM:**
1. If they're punched in, the system automatically creates break entries
2. Their timesheet will show:
   - Break Start: 1:00 PM (Automatic lunch break)
   - Break End: 2:00 PM (Automatic lunch break end)
3. The 1-hour break is automatically deducted from their worked hours
4. They don't need to manually start/end the break

**Example Timeline:**
```
08:00 AM - Punch In
01:00 PM - [AUTO] Break Start (Lunch)
02:00 PM - [AUTO] Break End (Lunch)
05:00 PM - Punch Out

Total Hours: 9 hours
Break Hours: 1 hour
Worked Hours: 8 hours ✓
```

### For Call Center Agents

**No automatic break!** They can work through lunch if needed, or manually take breaks using the punch in/out system.

## Verification

### Check if Middleware is Active

```bash
python manage.py shell
```

```python
from django.conf import settings
print('crm.middleware.lunch_break_middleware.AutoLunchBreakMiddleware' in settings.MIDDLEWARE)
# Should print: True
```

### Test the Management Command

```bash
python manage.py auto_lunch_break
```

Expected output:
```
✓ Created lunch break for John Doe
✓ Created lunch break for Jane Smith
⊘ Skipped: 3 employees (not punched in or already on break)

✓ Processed: 2 employees
⊘ Skipped: 3 employees
```

### View Lunch Break Entries

```bash
python manage.py shell
```

```python
from crm.models import TimeEntry
from django.utils import timezone

# Get today's automatic lunch breaks
today = timezone.now().date()
lunch_breaks = TimeEntry.objects.filter(
    timestamp__date=today,
    entry_type='break_start',
    notes__contains='Automatic lunch break'
)

for entry in lunch_breaks:
    print(f"{entry.employee.full_name}: {entry.timestamp}")
```

## Troubleshooting

### Lunch breaks not being created?

1. **Check if employee is punched in:**
   ```python
   employee.get_current_status()  # Should be 'punched_in' or 'working'
   ```

2. **Check employee role:**
   ```python
   employee.role  # Should NOT be 'call_center'
   ```

3. **Check current time:**
   ```python
   from django.utils import timezone
   now = timezone.now()
   print(now.time())  # Should be between 13:00 - 14:00
   print(now.weekday())  # Should be 0-5 (Monday-Saturday)
   ```

4. **Check if already created:**
   ```python
   TimeEntry.objects.filter(
       employee=employee,
       timestamp__date=today,
       entry_type='break_start',
       notes__contains='Automatic lunch break'
   ).exists()
   ```

### Duplicate lunch breaks?

The system prevents duplicates by checking if a lunch break entry already exists for today. If you see duplicates, check:
- Middleware and cron job both running (choose one method)
- System clock is correct
- Database timezone settings

### Lunch break not showing in timesheet?

The `WorkSession.calculate_hours()` method automatically includes all break entries when calculating worked hours. The lunch break will be included in the `break_hours` field.

## Customization

### Exempt Additional Roles

Edit `lunch_break_middleware.py`:
```python
# Exempt call center and sales roles
if employee.role not in ['call_center', 'sales']:
    # Apply lunch break
```

### Different Break Duration

Edit both files to change the end time:
```python
lunch_end = time(14, 30)  # 2:30 PM = 1.5 hour break
```

### Different Days

Edit the day check:
```python
# Only Monday-Friday
if current_day < 5:  # 0-4 = Monday-Friday
```

### Notification to Employees

Add to middleware after creating break:
```python
from django.contrib import messages
messages.info(request, 'Automatic lunch break (1 PM - 2 PM) has been applied to your timesheet.')
```

## Database Impact

Each automatic lunch break creates **2 TimeEntry records**:
1. `break_start` at 13:00
2. `break_end` at 14:00

**Daily records:** ~2 entries × number of active employees
**Monthly records:** ~2 entries × 26 days × number of employees

Example: 50 employees = ~2,600 records/month

This is minimal and won't impact performance.

## Reporting

### View Lunch Break Statistics

```python
from crm.models import TimeEntry
from django.utils import timezone
from datetime import timedelta

# Last 30 days
start_date = timezone.now().date() - timedelta(days=30)
lunch_breaks = TimeEntry.objects.filter(
    timestamp__date__gte=start_date,
    entry_type='break_start',
    notes__contains='Automatic lunch break'
)

print(f"Total automatic lunch breaks: {lunch_breaks.count()}")
print(f"Unique employees: {lunch_breaks.values('employee').distinct().count()}")
```

## Support

For issues or questions:
1. Check the logs: `tail -f /var/log/lunch_break.log`
2. Run the command manually to see errors
3. Check Django logs for middleware errors
4. Verify employee roles and status in admin panel

---

**Last Updated:** October 2025
**Version:** 1.0