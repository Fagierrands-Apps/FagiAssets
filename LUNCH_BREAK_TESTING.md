# 🧪 Automatic Lunch Break System - Testing Guide

## 📋 Test Scenarios

### ✅ Scenario 1: Regular Employee During Lunch Hour

**Setup:**
- Employee: John Doe (role: 'sales')
- Time: 1:15 PM (13:15)
- Day: Wednesday
- Status: Punched in at 9:00 AM

**Expected Results:**
1. ✅ Alert banner appears: "Lunch Break Time (1:00 PM - 2:00 PM)"
2. ✅ Two TimeEntry records created:
   - break_start at 13:00
   - break_end at 14:00
3. ✅ Employee status shows: "On Break"
4. ✅ Recent entries show both break entries
5. ✅ Notes field contains: "Automatic lunch break"

**Test Commands:**
```bash
python manage.py shell
```

```python
from crm.models import Employee, TimeEntry
from django.utils import timezone

# Get employee
employee = Employee.objects.get(user__username='johndoe')

# Check status
print(f"Status: {employee.get_current_status()}")
# Expected: 'on_break'

# Check time entries
today = timezone.now().date()
lunch_entries = TimeEntry.objects.filter(
    employee=employee,
    timestamp__date=today,
    notes__icontains='Automatic lunch break'
)

print(f"Lunch entries count: {lunch_entries.count()}")
# Expected: 2

for entry in lunch_entries:
    print(f"{entry.entry_type} at {entry.timestamp.strftime('%H:%M')}")
# Expected:
# break_start at 13:00
# break_end at 14:00
```

---

### ✅ Scenario 2: Call Center Agent During Lunch Hour

**Setup:**
- Employee: Jane Smith (role: 'call_center')
- Time: 1:15 PM (13:15)
- Day: Wednesday
- Status: Punched in at 9:00 AM

**Expected Results:**
1. ❌ No alert banner appears
2. ❌ No automatic TimeEntry records created
3. ✅ Employee status shows: "Working"
4. ✅ Can continue working normally
5. ✅ Full 8 hours counted (no lunch deduction)

**Test Commands:**
```python
from crm.models import Employee, TimeEntry
from django.utils import timezone

# Get employee
employee = Employee.objects.get(user__username='janesmith')

# Check role
print(f"Role: {employee.role}")
# Expected: 'call_center'

# Check status
print(f"Status: {employee.get_current_status()}")
# Expected: 'punched_in' or 'working'

# Check for lunch entries
today = timezone.now().date()
lunch_entries = TimeEntry.objects.filter(
    employee=employee,
    timestamp__date=today,
    notes__icontains='Automatic lunch break'
)

print(f"Lunch entries count: {lunch_entries.count()}")
# Expected: 0 (no automatic lunch break)
```

---

### ✅ Scenario 3: Employee Not Punched In

**Setup:**
- Employee: Bob Johnson (role: 'project_manager')
- Time: 1:15 PM (13:15)
- Day: Wednesday
- Status: Not punched in

**Expected Results:**
1. ❌ No alert banner appears
2. ❌ No automatic TimeEntry records created
3. ✅ Employee status shows: "Not Punched In"
4. ✅ System skips lunch break creation

**Test Commands:**
```python
from crm.models import Employee, TimeEntry
from django.utils import timezone

# Get employee
employee = Employee.objects.get(user__username='bobjohnson')

# Check status
print(f"Status: {employee.get_current_status()}")
# Expected: 'not_punched_in'

# Check for lunch entries
today = timezone.now().date()
lunch_entries = TimeEntry.objects.filter(
    employee=employee,
    timestamp__date=today,
    notes__icontains='Automatic lunch break'
)

print(f"Lunch entries count: {lunch_entries.count()}")
# Expected: 0 (not punched in, so no lunch break)
```

---

### ✅ Scenario 4: Sunday (Excluded Day)

**Setup:**
- Employee: Alice Brown (role: 'sales')
- Time: 1:15 PM (13:15)
- Day: Sunday
- Status: Punched in at 9:00 AM

**Expected Results:**
1. ❌ No alert banner appears
2. ❌ No automatic TimeEntry records created
3. ✅ Employee status shows: "Working"
4. ✅ System skips lunch break (Sunday excluded)

**Test Commands:**
```python
from django.utils import timezone

# Check current day
now = timezone.now()
print(f"Day of week: {now.weekday()}")
# Expected: 6 (Sunday)

print(f"Is lunch day? {now.weekday() < 6}")
# Expected: False (Sunday is excluded)
```

---

### ✅ Scenario 5: Outside Lunch Hours

**Setup:**
- Employee: Charlie Davis (role: 'sales')
- Time: 10:30 AM (10:30)
- Day: Wednesday
- Status: Punched in at 9:00 AM

**Expected Results:**
1. ❌ No alert banner appears
2. ❌ No automatic TimeEntry records created
3. ✅ Employee status shows: "Working"
4. ✅ System skips lunch break (not lunch time)

**Test Commands:**
```python
from django.utils import timezone

# Check current hour
now = timezone.now()
print(f"Current hour: {now.hour}")
# Expected: 10 (not 13)

print(f"Is lunch time? {now.hour == 13}")
# Expected: False
```

---

### ✅ Scenario 6: Duplicate Prevention

**Setup:**
- Employee: David Wilson (role: 'sales')
- Time: 1:15 PM (13:15)
- Day: Wednesday
- Status: Punched in at 9:00 AM
- **Already has lunch break entries from earlier request**

**Expected Results:**
1. ✅ Alert banner still appears (visual feedback)
2. ❌ No duplicate TimeEntry records created
3. ✅ Only 2 lunch entries exist (not 4)
4. ✅ System detects existing entries and skips creation

**Test Commands:**
```python
from crm.models import Employee, TimeEntry
from django.utils import timezone

# Get employee
employee = Employee.objects.get(user__username='davidwilson')

# Check for existing lunch entries
today = timezone.now().date()
existing_lunch = TimeEntry.objects.filter(
    employee=employee,
    timestamp__date=today,
    timestamp__hour=13,
    entry_type='break_start',
    notes__icontains='Automatic lunch break'
).exists()

print(f"Existing lunch break: {existing_lunch}")
# Expected: True

# Count total lunch entries
lunch_entries = TimeEntry.objects.filter(
    employee=employee,
    timestamp__date=today,
    notes__icontains='Automatic lunch break'
)

print(f"Total lunch entries: {lunch_entries.count()}")
# Expected: 2 (not 4, duplicate prevented)
```

---

### ✅ Scenario 7: Hour Calculation After Punch Out

**Setup:**
- Employee: Emma Taylor (role: 'sales')
- Punch in: 9:00 AM
- Automatic lunch: 1:00 PM - 2:00 PM
- Punch out: 5:00 PM

**Expected Results:**
1. ✅ Total hours: 8.0 (17:00 - 09:00)
2. ✅ Break hours: 1.0 (14:00 - 13:00)
3. ✅ Worked hours: 7.0 (8.0 - 1.0)
4. ✅ WorkSession correctly calculated

**Test Commands:**
```python
from crm.models import Employee, WorkSession
from django.utils import timezone

# Get employee
employee = Employee.objects.get(user__username='emmataylor')

# Get today's work session
today = timezone.now().date()
work_session = WorkSession.objects.get(
    employee=employee,
    date=today
)

print(f"Total hours: {work_session.total_hours}")
# Expected: 8.0

print(f"Break hours: {work_session.break_hours}")
# Expected: 1.0

print(f"Worked hours: {work_session.worked_hours}")
# Expected: 7.0

# Verify calculation
assert work_session.worked_hours == work_session.total_hours - work_session.break_hours
print("✅ Hour calculation correct!")
```

---

## 🔧 Manual Testing Procedures

### Test 1: Middleware Activation

**Steps:**
1. Open `assetmanager/settings.py`
2. Verify middleware is in MIDDLEWARE list:
   ```python
   'crm.middleware.lunch_break_middleware.AutoLunchBreakMiddleware'
   ```
3. Check it's not commented out
4. Restart Django server

**Verification:**
```bash
python manage.py shell
```

```python
from django.conf import settings
middleware_active = 'crm.middleware.lunch_break_middleware.AutoLunchBreakMiddleware' in settings.MIDDLEWARE
print(f"Middleware active: {middleware_active}")
# Expected: True
```

---

### Test 2: Management Command

**Steps:**
1. Open terminal
2. Navigate to project directory
3. Run command:
   ```bash
   cd assetmanagement
   python manage.py auto_lunch_break
   ```

**Expected Output (if not lunch time):**
```
Checking for automatic lunch breaks...
Current time: 10:30 AM
Not lunch time (must be between 1:00 PM - 2:00 PM), skipping...
```

**Expected Output (if lunch time):**
```
Checking for automatic lunch breaks...
Current time: 1:15 PM
Processing lunch breaks for active employees...

✅ Created lunch break for: John Doe
✅ Created lunch break for: Alice Brown
⏭️ Skipped Jane Smith (call center agent)
⏭️ Skipped Bob Johnson (not punched in)

Summary:
- Total employees processed: 4
- Lunch breaks created: 2
- Skipped (call center): 1
- Skipped (not working): 1
```

---

### Test 3: Visual Alert Banner

**Steps:**
1. Login as regular employee (not call center)
2. Ensure you're punched in
3. Change system time to 1:15 PM (or wait until lunch time)
4. Navigate to Time Tracking page
5. Look for yellow alert banner at top

**Expected Result:**
```
┌─────────────────────────────────────────────────────┐
│ 🍽️ Lunch Break Time (1:00 PM - 2:00 PM)            │
│                                                     │
│ ℹ️ Your work session is automatically paused       │
│ during lunch break. This hour will not be counted  │
│ in your worked hours. Enjoy your meal! 🍽️          │
│                                                [X]  │
└─────────────────────────────────────────────────────┘
```

**Verification:**
- Alert has yellow/warning color
- Utensils icon (🍽️) is visible
- Message is clear and informative
- Close button (X) works
- Alert only shows during 1:00 PM - 1:59 PM

---

### Test 4: Database Verification

**Steps:**
1. Open Django shell
2. Run verification queries

**Commands:**
```python
from crm.models import Employee, TimeEntry, WorkSession
from django.utils import timezone
from django.db.models import Count

# Get today's date
today = timezone.now().date()

# Count automatic lunch breaks created today
lunch_count = TimeEntry.objects.filter(
    timestamp__date=today,
    notes__icontains='Automatic lunch break'
).count()

print(f"Automatic lunch breaks today: {lunch_count}")

# List employees with lunch breaks
employees_with_lunch = Employee.objects.filter(
    time_entries__timestamp__date=today,
    time_entries__notes__icontains='Automatic lunch break'
).distinct()

print(f"\nEmployees with automatic lunch breaks:")
for emp in employees_with_lunch:
    print(f"  - {emp.user.get_full_name()} ({emp.role})")

# Check for duplicates
duplicates = TimeEntry.objects.filter(
    timestamp__date=today,
    notes__icontains='Automatic lunch break'
).values('employee').annotate(
    count=Count('id')
).filter(count__gt=2)

if duplicates.exists():
    print(f"\n⚠️ WARNING: Found {duplicates.count()} employees with duplicate lunch breaks!")
else:
    print(f"\n✅ No duplicates found - system working correctly!")

# Verify work session calculations
sessions = WorkSession.objects.filter(
    date=today,
    break_hours__gte=1.0
)

print(f"\nWork sessions with lunch break deduction:")
for session in sessions:
    print(f"  - {session.employee.user.get_full_name()}: "
          f"Total: {session.total_hours}h, "
          f"Break: {session.break_hours}h, "
          f"Worked: {session.worked_hours}h")
```

---

### Test 5: Role-Based Exemption

**Steps:**
1. Create test employees with different roles
2. Run lunch break system during lunch hour
3. Verify only non-call-center employees get breaks

**Setup Commands:**
```python
from django.contrib.auth.models import User
from crm.models import Employee

# Create test users
users_data = [
    ('sales_user', 'sales'),
    ('pm_user', 'project_manager'),
    ('cc_user', 'call_center'),
    ('admin_user', 'admin'),
]

for username, role in users_data:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'first_name': username.replace('_', ' ').title(),
            'email': f'{username}@test.com'
        }
    )
    
    if created:
        employee = Employee.objects.create(
            user=user,
            role=role,
            employment_status='active'
        )
        print(f"Created: {username} ({role})")
```

**Verification:**
```python
from crm.models import Employee, TimeEntry
from django.utils import timezone

today = timezone.now().date()

# Check each role
for role in ['sales', 'project_manager', 'call_center', 'admin']:
    employees = Employee.objects.filter(role=role)
    
    for emp in employees:
        lunch_entries = TimeEntry.objects.filter(
            employee=emp,
            timestamp__date=today,
            notes__icontains='Automatic lunch break'
        ).count()
        
        expected = 0 if role == 'call_center' else 2
        status = "✅" if lunch_entries == expected else "❌"
        
        print(f"{status} {emp.user.username} ({role}): {lunch_entries} entries (expected: {expected})")
```

---

## 📊 Performance Testing

### Test 1: Load Test (Multiple Employees)

**Scenario:** 100 employees access system during lunch hour

**Setup:**
```python
from django.contrib.auth.models import User
from crm.models import Employee
import time

# Create 100 test employees
start_time = time.time()

for i in range(100):
    user, created = User.objects.get_or_create(
        username=f'test_user_{i}',
        defaults={
            'first_name': f'Test',
            'last_name': f'User {i}',
            'email': f'test_user_{i}@test.com'
        }
    )
    
    if created:
        Employee.objects.create(
            user=user,
            role='sales',
            employment_status='active'
        )

end_time = time.time()
print(f"Created 100 employees in {end_time - start_time:.2f} seconds")
```

**Run Load Test:**
```bash
python manage.py auto_lunch_break
```

**Expected:**
- Command completes in < 5 seconds
- All 100 employees get lunch breaks
- No duplicate entries
- No errors in logs

---

### Test 2: Duplicate Prevention Stress Test

**Scenario:** Run command multiple times in quick succession

**Steps:**
```bash
# Run command 5 times quickly
for i in {1..5}; do
    python manage.py auto_lunch_break
    sleep 1
done
```

**Verification:**
```python
from crm.models import TimeEntry
from django.utils import timezone

today = timezone.now().date()

# Check for duplicates
from django.db.models import Count

duplicates = TimeEntry.objects.filter(
    timestamp__date=today,
    notes__icontains='Automatic lunch break'
).values('employee', 'entry_type').annotate(
    count=Count('id')
).filter(count__gt=1)

if duplicates.exists():
    print(f"❌ FAILED: Found {duplicates.count()} duplicate entries!")
    for dup in duplicates:
        print(f"  Employee ID: {dup['employee']}, Type: {dup['entry_type']}, Count: {dup['count']}")
else:
    print("✅ PASSED: No duplicates found!")
```

---

## 🐛 Debugging Tests

### Debug Test 1: Check Middleware Execution

**Add debug logging to middleware:**

Edit `lunch_break_middleware.py`:

```python
import logging
logger = logging.getLogger(__name__)

def process_request(self, request):
    logger.info(f"Middleware executed for user: {request.user}")
    # ... rest of code
```

**Run test:**
```bash
# Watch logs
tail -f assetmanagement/logs/django.log

# In another terminal, access the site
curl http://localhost:8000/crm/punch-in-out/
```

**Expected in logs:**
```
INFO: Middleware executed for user: johndoe
INFO: Current time: 13:15, Day: 2 (Wednesday)
INFO: Lunch break conditions met
INFO: Created lunch break for johndoe
```

---

### Debug Test 2: Check Time Calculations

**Test script:**
```python
from django.utils import timezone
from datetime import datetime, time

# Test time detection
now = timezone.now()
print(f"Current time: {now}")
print(f"Hour: {now.hour}")
print(f"Is lunch time? {now.hour == 13}")
print(f"Weekday: {now.weekday()}")
print(f"Is Mon-Sat? {now.weekday() < 6}")

# Test break time creation
break_start = now.replace(hour=13, minute=0, second=0, microsecond=0)
break_end = now.replace(hour=14, minute=0, second=0, microsecond=0)

print(f"\nBreak start: {break_start}")
print(f"Break end: {break_end}")
print(f"Duration: {(break_end - break_start).total_seconds() / 3600} hours")
```

---

## ✅ Acceptance Criteria Checklist

### Functional Requirements

- [ ] System creates lunch breaks at 1:00 PM
- [ ] Lunch break duration is exactly 1 hour (1:00 PM - 2:00 PM)
- [ ] Active Monday through Saturday only
- [ ] Sunday is excluded
- [ ] Call center agents are exempt
- [ ] Only applies to punched-in employees
- [ ] Prevents duplicate entries
- [ ] Integrates with work session calculations
- [ ] Visual alert appears during lunch hour
- [ ] Alert only shows to non-call-center employees

### Non-Functional Requirements

- [ ] Middleware executes in < 100ms
- [ ] Command handles 100+ employees in < 5 seconds
- [ ] No database errors or exceptions
- [ ] Proper error handling and logging
- [ ] No impact on system performance
- [ ] Works with existing time tracking features
- [ ] Documentation is complete and accurate

### User Experience

- [ ] Alert banner is visually appealing
- [ ] Message is clear and informative
- [ ] Status updates correctly
- [ ] Timesheet shows lunch breaks
- [ ] Worked hours are accurate
- [ ] No confusion for call center agents
- [ ] System is transparent and predictable

---

## 📝 Test Report Template

```markdown
# Lunch Break System Test Report

**Date:** [Date]
**Tester:** [Name]
**Environment:** [Development/Staging/Production]

## Test Results

### Scenario 1: Regular Employee During Lunch
- Status: ✅ PASS / ❌ FAIL
- Notes: [Any observations]

### Scenario 2: Call Center Agent
- Status: ✅ PASS / ❌ FAIL
- Notes: [Any observations]

### Scenario 3: Not Punched In
- Status: ✅ PASS / ❌ FAIL
- Notes: [Any observations]

### Scenario 4: Sunday Exclusion
- Status: ✅ PASS / ❌ FAIL
- Notes: [Any observations]

### Scenario 5: Outside Lunch Hours
- Status: ✅ PASS / ❌ FAIL
- Notes: [Any observations]

### Scenario 6: Duplicate Prevention
- Status: ✅ PASS / ❌ FAIL
- Notes: [Any observations]

### Scenario 7: Hour Calculation
- Status: ✅ PASS / ❌ FAIL
- Notes: [Any observations]

## Issues Found

1. [Issue description]
   - Severity: High/Medium/Low
   - Steps to reproduce:
   - Expected result:
   - Actual result:

## Overall Assessment

- Total Tests: [Number]
- Passed: [Number]
- Failed: [Number]
- Pass Rate: [Percentage]

## Recommendation

[ ] ✅ Approve for production
[ ] ⚠️ Approve with minor fixes
[ ] ❌ Reject - major issues found

**Signature:** _______________
**Date:** _______________
```

---

## 🎯 Quick Test Commands

```bash
# Test management command
python manage.py auto_lunch_break

# Check middleware status
python manage.py shell -c "from django.conf import settings; print('crm.middleware.lunch_break_middleware.AutoLunchBreakMiddleware' in settings.MIDDLEWARE)"

# Count today's lunch breaks
python manage.py shell -c "from crm.models import TimeEntry; from django.utils import timezone; print(TimeEntry.objects.filter(timestamp__date=timezone.now().date(), notes__icontains='Automatic lunch break').count())"

# List employees with lunch breaks
python manage.py shell -c "from crm.models import Employee, TimeEntry; from django.utils import timezone; [print(f'{e.user.get_full_name()} ({e.role})') for e in Employee.objects.filter(time_entries__timestamp__date=timezone.now().date(), time_entries__notes__icontains='Automatic lunch break').distinct()]"

# Check for duplicates
python manage.py shell -c "from crm.models import TimeEntry; from django.utils import timezone; from django.db.models import Count; print('Duplicates:', TimeEntry.objects.filter(timestamp__date=timezone.now().date(), notes__icontains='Automatic lunch break').values('employee').annotate(count=Count('id')).filter(count__gt=2).count())"
```

---

**Happy Testing! 🧪**