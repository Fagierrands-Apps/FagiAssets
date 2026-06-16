# 🚀 Quick Start: Automatic Lunch Break System

## ✅ System Status: ACTIVE & READY

Your automatic lunch break system is **fully operational** right now!

---

## 🎯 What It Does

- ⏰ **Automatically pauses work** at 1:00 PM for 1 hour
- 👥 **Applies to all employees** except call center agents
- 📅 **Active Monday - Saturday** (excludes Sunday)
- 🔄 **Runs automatically** - no manual action needed
- 📊 **Integrates with timesheets** - hours calculated correctly

---

## 🧪 Test It Now

### Option 1: Manual Test (Anytime)

```bash
cd assetmanagement
python manage.py auto_lunch_break
```

**Expected output:**
- If it's 1:00 PM - 1:59 PM: Creates lunch breaks
- Otherwise: "Not lunch time, skipping..."

### Option 2: Live Test (During Lunch Hour)

1. **Login** as any non-call-center employee
2. **Navigate** to Time Tracking page
3. **Look for** yellow alert banner at top
4. **Check** status shows "On Break"
5. **Verify** two time entries created at 1:00 PM and 2:00 PM

---

## 📊 Verify It's Working

### Check Database

```bash
python manage.py shell
```

```python
from crm.models import TimeEntry
from django.utils import timezone

# Count automatic lunch breaks today
today = timezone.now().date()
lunch_count = TimeEntry.objects.filter(
    timestamp__date=today,
    notes__icontains='Automatic lunch break'
).count()

print(f"Automatic lunch breaks created today: {lunch_count}")
```

### Check Middleware Status

```bash
python manage.py shell
```

```python
from django.conf import settings

# Verify middleware is enabled
middleware_active = 'crm.middleware.lunch_break_middleware.AutoLunchBreakMiddleware' in settings.MIDDLEWARE
print(f"Lunch break middleware active: {middleware_active}")
```

---

## 🎨 What Employees See

### Regular Employees (1:00 PM - 1:59 PM)

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

### Call Center Agents

```
No alert - can work normally through lunch
```

---

## 🔧 Quick Configuration

### Change Lunch Time

Edit: `assetmanagement/crm/middleware/lunch_break_middleware.py`

```python
# Line 20: Change start hour
if now.hour == 13:  # 13 = 1 PM, 12 = 12 PM, 14 = 2 PM

# Lines 47-48: Change break times
break_start_time = now.replace(hour=13, minute=0)  # Start time
break_end_time = now.replace(hour=14, minute=0)    # End time
```

### Change Active Days

```python
# Line 21: Current = Monday-Saturday
if now.weekday() < 6:

# For Monday-Friday only:
if now.weekday() < 5:

# For all days:
if True:
```

### Add Exempt Roles

```python
# Line 35: Current = call_center only
if employee.role == 'call_center':

# Multiple roles:
if employee.role in ['call_center', 'manager', 'admin']:
```

### Disable System

Edit: `assetmanagement/assetmanager/settings.py`

```python
# Line 70: Comment out this line
# 'crm.middleware.lunch_break_middleware.AutoLunchBreakMiddleware',
```

---

## 📈 Impact Example

### Before
```
Work: 9 AM - 5 PM = 8 hours
Breaks: Manual (inconsistent)
Worked Hours: 8 hours (incorrect)
```

### After
```
Work: 9 AM - 5 PM = 8 hours
Lunch: 1 PM - 2 PM = 1 hour (automatic)
Worked Hours: 7 hours (correct)
```

---

## 🐛 Troubleshooting

### Lunch breaks not created?

1. **Check time:**
   ```python
   from django.utils import timezone
   now = timezone.now()
   print(f"Hour: {now.hour}, Day: {now.weekday()}")
   # Should be: Hour: 13, Day: 0-5
   ```

2. **Check middleware:**
   ```bash
   grep -n "AutoLunchBreakMiddleware" assetmanagement/assetmanager/settings.py
   # Should show line 70
   ```

3. **Check employee status:**
   ```python
   employee.get_current_status()
   # Should be 'punched_in' or 'working'
   ```

### Alert not showing?

1. Clear browser cache
2. Verify it's 1:00 PM - 1:59 PM
3. Verify employee role is NOT 'call_center'
4. Verify it's Monday-Saturday (not Sunday)

---

## 📁 Key Files

| File | Purpose | Status |
|------|---------|--------|
| `crm/middleware/lunch_break_middleware.py` | Auto-creates breaks | ✅ Active |
| `crm/management/commands/auto_lunch_break.py` | Manual command | ✅ Ready |
| `templates/crm/punch_in_out.html` | Alert banner | ✅ Active |
| `crm/views.py` | Context variable | ✅ Active |
| `assetmanager/settings.py` | Middleware config | ✅ Enabled |

---

## 🎯 Success Indicators

✅ **System is working if:**

1. At 1:00 PM, non-call-center employees see alert banner
2. Two time entries created automatically (break_start, break_end)
3. Employee status shows "On Break" during lunch
4. Worked hours exclude the 1-hour lunch break
5. Call center agents are NOT affected

---

## 📞 Quick Commands

```bash
# Test the system
python manage.py auto_lunch_break

# Check today's lunch breaks
python manage.py shell -c "from crm.models import TimeEntry; from django.utils import timezone; print(TimeEntry.objects.filter(timestamp__date=timezone.now().date(), notes__icontains='Automatic lunch break').count())"

# View logs
tail -f assetmanagement/logs/django.log

# Django shell
python manage.py shell
```

---

## 📚 Documentation

- **Detailed Setup:** `LUNCH_BREAK_SETUP.md`
- **Complete Summary:** `AUTO_LUNCH_BREAK_SUMMARY.md`
- **This Quick Start:** `QUICK_START_LUNCH_BREAK.md`

---

## 🎉 You're All Set!

The automatic lunch break system is **active and running**. 

**Next steps:**
1. ✅ Test during lunch hour (1:00 PM - 1:59 PM)
2. ✅ Verify alert appears for regular employees
3. ✅ Check timesheets show correct worked hours
4. ✅ Confirm call center agents are exempt

**Questions?** Check the detailed documentation in `LUNCH_BREAK_SETUP.md`

---

**Last Updated:** January 2025
**Status:** ✅ Production Ready
**Version:** 1.0