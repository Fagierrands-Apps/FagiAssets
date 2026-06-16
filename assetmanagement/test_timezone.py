"""
Test script to verify Kenya timezone configuration
Run with: python manage.py shell < test_timezone.py
Or: python manage.py shell
Then: exec(open('test_timezone.py').read())
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
django.setup()

from django.conf import settings
from django.utils import timezone
from datetime import datetime
import pytz

print("=" * 70)
print("KENYA TIMEZONE CONFIGURATION TEST")
print("=" * 70)

# 1. Check configured timezone
print("\n1. CONFIGURED TIMEZONE")
print(f"   TIME_ZONE setting: {settings.TIME_ZONE}")
print(f"   USE_TZ setting: {settings.USE_TZ}")

# 2. Current time in different formats
print("\n2. CURRENT TIME")
now_utc = timezone.now()
now_local = timezone.localtime(now_utc)

print(f"   UTC time:        {now_utc.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"   Kenya time:      {now_local.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"   Timezone offset: UTC{now_local.strftime('%z')}")

# 3. Verify timezone offset
kenya_tz = pytz.timezone('Africa/Nairobi')
offset = kenya_tz.utcoffset(datetime.now())
hours_offset = offset.total_seconds() / 3600

print(f"\n3. TIMEZONE OFFSET")
print(f"   Expected: +3 hours (UTC+3)")
print(f"   Actual:   {'+' if hours_offset >= 0 else ''}{hours_offset} hours")
print(f"   Status:   {'✅ CORRECT' if hours_offset == 3 else '❌ INCORRECT'}")

# 4. Test date calculation
print(f"\n4. DATE CALCULATION")
today_utc = now_utc.date()
today_local = now_local.date()

print(f"   UTC date:   {today_utc}")
print(f"   Kenya date: {today_local}")
if today_utc != today_local:
    print(f"   Note: Dates differ (normal if near midnight)")

# 5. Test timezone conversion
print(f"\n5. TIMEZONE CONVERSION TEST")
test_time_utc = timezone.now().replace(hour=6, minute=0, second=0, microsecond=0)
test_time_local = timezone.localtime(test_time_utc)

print(f"   06:00 UTC    → {test_time_local.strftime('%H:%M')} Kenya time")
print(f"   Expected:    → 09:00 Kenya time")
print(f"   Status:      → {'✅ CORRECT' if test_time_local.hour == 9 else '❌ INCORRECT'}")

# 6. Check if WorkSession model exists and test
print(f"\n6. DATABASE MODEL TEST")
try:
    from crm.models import WorkSession, TimeEntry
    
    # Count records
    work_sessions = WorkSession.objects.count()
    time_entries = TimeEntry.objects.count()
    
    print(f"   WorkSession records: {work_sessions}")
    print(f"   TimeEntry records:   {time_entries}")
    
    # Get latest entry if exists
    if time_entries > 0:
        latest_entry = TimeEntry.objects.latest('timestamp')
        entry_utc = latest_entry.timestamp
        entry_local = timezone.localtime(entry_utc)
        
        print(f"\n   Latest TimeEntry:")
        print(f"   - Employee:    {latest_entry.employee.full_name}")
        print(f"   - Type:        {latest_entry.get_entry_type_display()}")
        print(f"   - UTC time:    {entry_utc.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   - Kenya time:  {entry_local.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"   Status:      ✅ Models accessible")
    
except ImportError as e:
    print(f"   Status:      ⚠️  CRM models not found: {e}")
except Exception as e:
    print(f"   Status:      ⚠️  Error: {e}")

# 7. Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

all_correct = (
    settings.TIME_ZONE == 'Africa/Nairobi' and
    settings.USE_TZ == True and
    hours_offset == 3
)

if all_correct:
    print("✅ All timezone settings are CORRECT!")
    print("✅ Punch in/out times will display in Kenya local time")
    print("✅ Database stores in UTC, displays in Africa/Nairobi")
else:
    print("❌ Some timezone settings are INCORRECT")
    print("⚠️  Please review the configuration")

print("\nNext steps:")
print("1. Restart Django development server")
print("2. Test punch in/out on employee dashboard")
print("3. Verify times match Kenya local time")
print("4. Check timesheet page for correct display")

print("=" * 70)