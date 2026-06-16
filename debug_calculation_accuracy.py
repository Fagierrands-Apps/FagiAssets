#!/usr/bin/env python
"""Debug script to check calculation accuracy in summary reports"""
import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
sys.path.insert(0, 'c:\\Users\\a\\Documents\\GitHub\\fagiassets\\assetmanagement')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
django.setup()

from crm.models import WorkSession
from crm.models import Employee
from django.utils import timezone

# Check a specific employee
print("=" * 80)
print("ACCURACY CHECK: Diana Riziki (EMP0024)")
print("=" * 80)

try:
    diana = Employee.objects.get(employee_id='EMP0024')
    diana_sessions = WorkSession.objects.filter(employee=diana).order_by('date', 'punch_in')
    
    print(f"\nTotal sessions: {diana_sessions.count()}")
    print(f"Date range: {diana_sessions.first().date} to {diana_sessions.last().date}")
    
    total_hours = 0
    total_days = set()
    
    for session in diana_sessions:
        total_days.add(session.date)
        
        if session.is_complete or session.punch_out:
            hours = float(session.worked_hours or 0)
        else:
            # In-progress calculation
            if session.punch_in:
                current_time = timezone.now()
                total_time = current_time - session.punch_in
                total_seconds = total_time.total_seconds()
                hours = total_seconds / 3600
                break_hours = float(session.break_hours or 0)
                hours = max(0, hours - break_hours)
            else:
                hours = 0
        
        total_hours += hours
        
        status = 'Complete' if (session.is_complete or session.punch_out) else 'In-Progress'
        print(f"  {session.date} | {session.punch_in.time() if session.punch_in else 'N/A':>8} - {session.punch_out.time() if session.punch_out else 'N/A':>8} | Break: {float(session.break_hours or 0):.1f}h | Worked: {hours:.1f}h | {status}")
    
    print(f"\nCalculation Summary:")
    print(f"  Total hours: {total_hours:.1f}")
    print(f"  Days worked: {len(total_days)}")
    print(f"  Avg hours/day: {total_hours / len(total_days) if total_days else 0:.1f}")
    print(f"  Report shows: 1155.4 hours in 22 days = 52.5 avg/day")
    print(f"  Status: {'✓ CORRECT' if abs(total_hours - 1155.4) < 1 else '✗ INCORRECT'}")
    
except Employee.DoesNotExist:
    print("Employee not found")

print("\n" + "=" * 80)
print("ACCURACY CHECK: Cyrus Mweu (EMP0026)")
print("=" * 80)

try:
    cyrus = Employee.objects.get(employee_id='EMP0026')
    cyrus_sessions = WorkSession.objects.filter(employee=cyrus).order_by('date', 'punch_in')
    
    print(f"\nTotal sessions: {cyrus_sessions.count()}")
    print(f"Date range: {cyrus_sessions.first().date} to {cyrus_sessions.last().date}")
    
    total_hours = 0
    total_days = set()
    
    for session in cyrus_sessions:
        total_days.add(session.date)
        
        if session.is_complete or session.punch_out:
            hours = float(session.worked_hours or 0)
        else:
            if session.punch_in:
                current_time = timezone.now()
                total_time = current_time - session.punch_in
                total_seconds = total_time.total_seconds()
                hours = total_seconds / 3600
                break_hours = float(session.break_hours or 0)
                hours = max(0, hours - break_hours)
            else:
                hours = 0
        
        total_hours += hours
        
        status = 'Complete' if (session.is_complete or session.punch_out) else 'In-Progress'
        print(f"  {session.date} | {session.punch_in.time() if session.punch_in else 'N/A':>8} - {session.punch_out.time() if session.punch_out else 'N/A':>8} | Break: {float(session.break_hours or 0):.1f}h | Worked: {hours:.1f}h | {status}")
    
    print(f"\nCalculation Summary:")
    print(f"  Total hours: {total_hours:.1f}")
    print(f"  Days worked: {len(total_days)}")
    print(f"  Avg hours/day: {total_hours / len(total_days) if total_days else 0:.1f}")
    print(f"  Report shows: 665.1 hours in 21 days = 31.7 avg/day")
    print(f"  Status: {'✓ CORRECT' if abs(total_hours - 665.1) < 1 else '✗ INCORRECT'}")
    
except Employee.DoesNotExist:
    print("Employee not found")

print("\n" + "=" * 80)
print("ACCURACY CHECK: Colsman (EMP0033)")
print("=" * 80)

try:
    colsman = Employee.objects.get(employee_id='EMP0033')
    colsman_sessions = WorkSession.objects.filter(employee=colsman).order_by('date', 'punch_in')
    
    print(f"\nTotal sessions: {colsman_sessions.count()}")
    if colsman_sessions.exists():
        print(f"Date range: {colsman_sessions.first().date} to {colsman_sessions.last().date}")
        
        total_hours = 0
        total_days = set()
        
        for session in colsman_sessions:
            total_days.add(session.date)
            
            if session.is_complete or session.punch_out:
                hours = float(session.worked_hours or 0)
            else:
                if session.punch_in:
                    current_time = timezone.now()
                    total_time = current_time - session.punch_in
                    total_seconds = total_time.total_seconds()
                    hours = total_seconds / 3600
                    break_hours = float(session.break_hours or 0)
                    hours = max(0, hours - break_hours)
                else:
                    hours = 0
            
            total_hours += hours
            
            status = 'Complete' if (session.is_complete or session.punch_out) else 'In-Progress'
            print(f"  {session.date} | {session.punch_in.time() if session.punch_in else 'N/A':>8} - {session.punch_out.time() if session.punch_out else 'N/A':>8} | Break: {float(session.break_hours or 0):.1f}h | Worked: {hours:.1f}h | {status}")
        
        print(f"\nCalculation Summary:")
        print(f"  Total hours: {total_hours:.1f}")
        print(f"  Days worked: {len(total_days)}")
        print(f"  Avg hours/day: {total_hours / len(total_days) if total_days else 0:.1f}")
        print(f"  Report shows: 623.0 hours in 1 day")
        print(f"  Status: {'✓ CORRECT' if abs(total_hours - 623.0) < 1 else '✗ INCORRECT'}")
    else:
        print("No sessions found for this employee")
    
except Employee.DoesNotExist:
    print("Employee not found")

print("\n" + "=" * 80)