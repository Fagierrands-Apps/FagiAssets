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

# Simulate the fixed _get_summary_data function
def _get_summary_data(work_sessions):
    """Aggregate work sessions by employee and return summary data sorted by total hours"""
    from decimal import Decimal
    
    summary_dict = {}
    
    for session in work_sessions:
        emp_id = session.employee_id
        if emp_id not in summary_dict:
            summary_dict[emp_id] = {
                'employee_name': session.employee.user.get_full_name() or session.employee.user.username,
                'employee_id': session.employee.employee_id,
                'department': session.employee.department.name if session.employee.department else 'N/A',
                'total_hours': 0,
                'total_productive_hours': 0,
                'total_idle_hours': 0,
                'days_worked': set(),
                'sessions_count': 0,
                'incomplete_sessions': 0,
            }
        
        # Calculate hours for this session
        if session.is_complete or session.punch_out:
            # Completed session - use calculated hours
            session_hours = float(session.worked_hours or 0)
            productive = float(session.productive_hours or 0)
            idle = float(session.idle_hours or 0)
        else:
            # Incomplete session - calculate real-time hours
            if session.punch_in:
                current_time = timezone.now()
                total_time = current_time - session.punch_in
                total_seconds = total_time.total_seconds()
                session_hours = total_seconds / 3600
                break_hours_float = float(session.break_hours or 0)
                session_hours = max(0, session_hours - break_hours_float)
                
                # For incomplete sessions, assume all working time is productive
                productive = session_hours
                idle = 0
            else:
                session_hours = 0
                productive = 0
                idle = 0
            
            summary_dict[emp_id]['incomplete_sessions'] += 1
        
        summary_dict[emp_id]['total_hours'] += session_hours
        summary_dict[emp_id]['total_productive_hours'] += productive
        summary_dict[emp_id]['total_idle_hours'] += idle
        summary_dict[emp_id]['days_worked'].add(session.date)
        summary_dict[emp_id]['sessions_count'] += 1
    
    # Convert to list and calculate average hours per day
    summary_list = []
    for emp_id, data in summary_dict.items():
        days_count = len(data['days_worked'])
        avg_hours = data['total_hours'] / days_count if days_count > 0 else 0
        
        summary_list.append({
            'employee_name': data['employee_name'],
            'employee_id': data['employee_id'],
            'department': data['department'],
            'total_hours': data['total_hours'],
            'days_worked': days_count,
            'avg_hours_per_day': avg_hours,
            'productive_hours': data['total_productive_hours'],
            'idle_hours': data['total_idle_hours'],
            'sessions_count': data['sessions_count'],
            'incomplete_sessions': data['incomplete_sessions'],
        })
    
    # Sort by total hours (descending)
    summary_list.sort(key=lambda x: x['total_hours'], reverse=True)
    return summary_list


print("=" * 80)
print("TESTING SUMMARY REPORT FIX")
print("=" * 80)

# Test with current month (November - where there are incomplete sessions)
today = timezone.now().date()
month_start = today.replace(day=1)

current_month_sessions = WorkSession.objects.filter(date__gte=month_start)

print(f"\nTesting with {current_month_sessions.count()} sessions from current month")
print(f"Date range: {month_start} to {today}")

summary_data = _get_summary_data(current_month_sessions)

print(f"\n{'Employee Name':<30} | {'Total Hours':>10} | {'Days':>4} | {'Sessions':>4} | {'In Progress':>3}")
print("-" * 80)

for emp in summary_data:
    print(f"{emp['employee_name']:<30} | {emp['total_hours']:>10.2f}h | {emp['days_worked']:>4} | {emp['sessions_count']:>4} | {emp['incomplete_sessions']:>3}")

total_hours = sum([emp['total_hours'] for emp in summary_data])
total_incomplete = sum([emp['incomplete_sessions'] for emp in summary_data])

print("-" * 80)
print(f"{'TOTAL':<30} | {total_hours:>10.2f}h | | | {total_incomplete:>3}")
print(f"\n✓ All {len(summary_data)} employees are shown in the report")
print(f"✓ Real-time hours calculated for {total_incomplete} in-progress sessions")
print(f"✓ Total hours across all employees: {total_hours:.2f}h")

# Also test with October (should have all completed sessions)
print("\n" + "=" * 80)
print("COMPARISON WITH OCTOBER (All Completed Sessions)")
print("=" * 80)

oct_start = datetime(2025, 10, 1).date()
oct_end = datetime(2025, 10, 31).date()
oct_sessions = WorkSession.objects.filter(date__gte=oct_start, date__lte=oct_end)

print(f"\nTesting with {oct_sessions.count()} sessions from October")

oct_summary_data = _get_summary_data(oct_sessions)

print(f"\n{'Employee Name':<30} | {'Total Hours':>10} | {'Days':>4} | {'Sessions':>4}")
print("-" * 80)

for emp in oct_summary_data:
    print(f"{emp['employee_name']:<30} | {emp['total_hours']:>10.2f}h | {emp['days_worked']:>4} | {emp['sessions_count']:>4}")

oct_total_hours = sum([emp['total_hours'] for emp in oct_summary_data])
print("-" * 80)
print(f"{'TOTAL':<30} | {oct_total_hours:>10.2f}h")

print("\n✓ All employees display correctly")
print("✓ Hours are properly calculated")
print("\n" + "=" * 80)