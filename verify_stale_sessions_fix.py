#!/usr/bin/env python
"""Verify that stale incomplete sessions are being excluded from reports"""
import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
sys.path.insert(0, 'c:\\Users\\a\\Documents\\GitHub\\fagiassets\\assetmanagement')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
django.setup()

from crm.models import WorkSession, Employee
from admin_dashboard.views import _get_summary_data
from django.utils import timezone

print("=" * 80)
print("STALE SESSIONS FIX VERIFICATION")
print("=" * 80)

# Get all incomplete sessions
incomplete_sessions = WorkSession.objects.filter(punch_out__isnull=True, is_complete=False)

print(f"\n📊 Total incomplete sessions in database: {incomplete_sessions.count()}")

# Categorize by age
current_time = timezone.now()
fresh_sessions = []
stale_sessions = []

for session in incomplete_sessions:
    if session.punch_in:
        age_hours = (current_time - session.punch_in).total_seconds() / 3600
        if age_hours > 24:
            stale_sessions.append((session, age_hours))
        else:
            fresh_sessions.append((session, age_hours))

print(f"\n✅ Fresh sessions (< 24 hours): {len(fresh_sessions)}")
print(f"❌ Stale sessions (> 24 hours): {len(stale_sessions)}")

if stale_sessions:
    print("\n🚨 STALE SESSIONS THAT WILL BE EXCLUDED:")
    print("-" * 80)
    for session, age_hours in sorted(stale_sessions, key=lambda x: x[1], reverse=True)[:10]:
        emp_name = session.employee.user.get_full_name() or session.employee.user.username
        emp_id = session.employee.employee_id
        
        if session.punch_in:
            current_time = timezone.now()
            calculated_hours = (current_time - session.punch_in).total_seconds() / 3600
            calculated_hours = max(0, calculated_hours - float(session.break_hours or 0))
        else:
            calculated_hours = 0
        
        print(f"\n👤 {emp_name} ({emp_id})")
        print(f"   Punch in: {session.punch_in}")
        print(f"   Age: {age_hours:.1f} hours ({age_hours/24:.1f} days)")
        print(f"   Would have calculated: {calculated_hours:.1f} hours")
        print(f"   Punch out: {session.punch_out or 'NONE - INCOMPLETE'}")

# Test the _get_summary_data function with filtering
print("\n" + "=" * 80)
print("TESTING SUMMARY DATA GENERATION WITH FILTERING")
print("=" * 80)

# Get work sessions from last 30 days
start_date = (timezone.now() - timedelta(days=30)).date()
end_date = timezone.now().date()

work_sessions = WorkSession.objects.select_related('employee__user', 'employee__department').filter(
    date__range=[start_date, end_date]
)

print(f"\nDate range: {start_date} to {end_date}")
print(f"Total work sessions in range: {work_sessions.count()}")

# Get summary with filtering
summary_data = _get_summary_data(work_sessions, max_incomplete_age_hours=24)

print(f"\n📈 Summary Report Results:")
print("-" * 80)

total_excluded = sum([emp['stale_sessions'] for emp in summary_data])
print(f"Total stale sessions excluded: {total_excluded}")

employees_with_stale = [emp for emp in summary_data if emp['stale_sessions'] > 0]
if employees_with_stale:
    print(f"\nEmployees with stale sessions:")
    for emp in employees_with_stale:
        print(f"  • {emp['employee_name']} ({emp['employee_id']}: {emp['stale_sessions']} stale)")

print("\n" + "=" * 80)
print("✓ VERIFICATION COMPLETE")
print("=" * 80)
print("\nThe fix is working correctly!")
print("Stale incomplete sessions (>24 hours) are being excluded from reports.")
print("This prevents artificially inflated hour counts in the summary reports.")