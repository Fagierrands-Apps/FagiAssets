#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
sys.path.insert(0, 'c:\\Users\\a\\Documents\\GitHub\\fagiassets\\assetmanagement')

django.setup()

from crm.models import WorkSession
from django.utils import timezone

# Check overall WorkSession data
print("=" * 80)
print("WORKSESSION TABLE DEBUG")
print("=" * 80)

total_sessions = WorkSession.objects.count()
print(f"\nTotal WorkSession records: {total_sessions}")

if total_sessions == 0:
    print("❌ NO WORK SESSIONS FOUND IN DATABASE")
else:
    print(f"✓ Found {total_sessions} work sessions")
    
    # Get date range
    oldest = WorkSession.objects.order_by('date').first()
    newest = WorkSession.objects.order_by('-date').first()
    print(f"Date range: {oldest.date} to {newest.date}")
    
    # Get current month
    today = timezone.now().date()
    month_start = today.replace(day=1)
    
    current_month_sessions = WorkSession.objects.filter(date__gte=month_start)
    print(f"\nCurrent month sessions: {current_month_sessions.count()}")
    
    # Check for zero hours
    zero_hours = WorkSession.objects.filter(worked_hours=0)
    print(f"Sessions with 0 hours: {zero_hours.count()}")
    
    # Sample data
    print("\n" + "=" * 80)
    print("SAMPLE WORKSESSION RECORDS (Last 10):")
    print("=" * 80)
    
    for session in WorkSession.objects.order_by('-date')[:10]:
        print(f"\nEmployee: {session.employee.user.get_full_name()} ({session.employee.employee_id})")
        print(f"  Date: {session.date}")
        print(f"  Punch In: {session.punch_in}")
        print(f"  Punch Out: {session.punch_out}")
        print(f"  Total Hours: {session.total_hours}")
        print(f"  Break Hours: {session.break_hours}")
        print(f"  Worked Hours: {session.worked_hours} 🔴" if session.worked_hours == 0 else f"  Worked Hours: {session.worked_hours} ✓")
        print(f"  Productive Hours: {session.productive_hours}")
        print(f"  Idle Hours: {session.idle_hours}")
        print(f"  Is Complete: {session.is_complete}")
    
    # Check unique employees
    unique_employees = WorkSession.objects.values('employee').distinct().count()
    print(f"\n\nUnique employees with sessions: {unique_employees}")
    
    # Group by employee and show summary
    print("\n" + "=" * 80)
    print("EMPLOYEE SUMMARY:")
    print("=" * 80)
    
    from django.db.models import Sum, Count, Q
    
    employee_summary = (
        WorkSession.objects
        .values('employee__user__first_name', 'employee__user__last_name', 'employee__employee_id')
        .annotate(
            total_sessions=Count('id'),
            total_hours=Sum('worked_hours'),
        )
        .order_by('-total_hours')
    )
    
    for emp in employee_summary:
        name = f"{emp['employee__user__first_name']} {emp['employee__user__last_name']}"
        emp_id = emp['employee__employee_id']
        sessions = emp['total_sessions']
        total_hours = emp['total_hours'] or 0
        avg_hours = float(total_hours) / sessions if sessions > 0 else 0
        
        status = "✓" if total_hours > 0 else "🔴"
        print(f"{name:30} ({emp_id:8}) | Sessions: {sessions:3} | Total: {total_hours:7.2f}h | Avg: {avg_hours:6.2f}h {status}")
    
    # Check completed vs incomplete sessions
    print(f"\n\nCompleted sessions (punch_out set): {WorkSession.objects.filter(is_complete=True).count()}")
    print(f"Incomplete sessions (no punch_out): {WorkSession.objects.filter(is_complete=False).count()}")
    
    # Check for October specifically
    oct_start = datetime(2025, 10, 1).date()
    oct_end = datetime(2025, 10, 31).date()
    oct_sessions = WorkSession.objects.filter(date__gte=oct_start, date__lte=oct_end)
    
    print(f"\nOctober sessions: {oct_sessions.count()}")
    print(f"October sessions with hours: {oct_sessions.filter(worked_hours__gt=0).count()}")
    print(f"October total hours: {sum(float(s.worked_hours or 0) for s in oct_sessions):.2f}")

print("\n" + "=" * 80)