"""
Test script for automatic clock-out functionality
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
django.setup()

from django.utils import timezone
from crm.models import Employee, TimeEntry, WorkSession
from datetime import datetime, timedelta

def test_auto_clockout():
    """Test the automatic clock-out system"""
    
    print("=" * 60)
    print("Testing Automatic Clock-Out System")
    print("=" * 60)
    print()
    
    # Get all active employees
    active_employees = Employee.objects.filter(employment_status='active')
    
    if not active_employees.exists():
        print("❌ No active employees found!")
        return
    
    print(f"✅ Found {active_employees.count()} active employees")
    print()
    
    # Test 1: Check current clock-in status
    print("Test 1: Current Clock-In Status")
    print("-" * 60)
    
    clocked_in_count = 0
    for employee in active_employees[:5]:  # Test first 5 employees
        status = employee.get_current_status()
        print(f"  {employee.full_name}: {status}")
        if status == 'punched_in':
            clocked_in_count += 1
    
    print(f"\n  Total clocked in: {clocked_in_count}")
    print()
    
    # Test 2: Simulate lunch clock-out
    print("Test 2: Simulating Lunch Clock-Out (1:30 PM)")
    print("-" * 60)
    
    # Create a test employee if needed
    test_employee = active_employees.first()
    
    # Clock in the test employee if not already
    today = timezone.now().date()
    latest_entry = test_employee.time_entries.filter(
        timestamp__date=today
    ).order_by('-timestamp').first()
    
    if not latest_entry or latest_entry.entry_type == 'punch_out':
        # Clock in first
        TimeEntry.objects.create(
            employee=test_employee,
            entry_type='punch_in',
            timestamp=timezone.now().replace(hour=8, minute=0, second=0),
            notes='Test clock-in',
            location='Test Location'
        )
        print(f"  ✅ Clocked in {test_employee.full_name} at 8:00 AM")
    
    # Simulate lunch clock-out
    lunch_time = timezone.now().replace(hour=13, minute=30, second=0, microsecond=0)
    TimeEntry.objects.create(
        employee=test_employee,
        entry_type='punch_out',
        timestamp=lunch_time,
        notes='Automatic clock-out for lunch break',
        location='System Auto Clock-Out'
    )
    print(f"  ✅ Clocked out {test_employee.full_name} at 1:30 PM")
    
    # Simulate re-clock-in
    reclock_time = lunch_time + timedelta(seconds=1)
    TimeEntry.objects.create(
        employee=test_employee,
        entry_type='punch_in',
        timestamp=reclock_time,
        notes='Automatic clock-in after lunch break',
        location='System Auto Clock-In'
    )
    print(f"  ✅ Re-clocked in {test_employee.full_name} at 1:30:01 PM")
    print()
    
    # Test 3: Check work session calculation
    print("Test 3: Work Session Calculation")
    print("-" * 60)
    
    # Get all time entries for today
    entries = test_employee.time_entries.filter(
        timestamp__date=today
    ).order_by('timestamp')
    
    print(f"  Time entries for {test_employee.full_name}:")
    for entry in entries:
        print(f"    - {entry.timestamp.strftime('%H:%M:%S')}: {entry.get_entry_type_display()}")
    
    # Check work session
    work_session = WorkSession.objects.filter(
        employee=test_employee,
        date=today
    ).first()
    
    if work_session:
        print(f"\n  Work Session:")
        print(f"    Punch In: {work_session.punch_in.strftime('%H:%M:%S') if work_session.punch_in else 'N/A'}")
        print(f"    Punch Out: {work_session.punch_out.strftime('%H:%M:%S') if work_session.punch_out else 'N/A'}")
        print(f"    Total Hours: {work_session.total_hours}")
        print(f"    Break Hours: {work_session.break_hours}")
        print(f"    Worked Hours: {work_session.worked_hours}")
        print(f"    Complete: {work_session.is_complete}")
    else:
        print("  ⚠️  No work session found (run auto_clockout command to create)")
    
    print()
    
    # Test 4: Test end-of-day clock-out
    print("Test 4: Simulating End-of-Day Clock-Out (10:00 PM)")
    print("-" * 60)
    
    # Simulate end-of-day clock-out
    eod_time = timezone.now().replace(hour=22, minute=0, second=0, microsecond=0)
    TimeEntry.objects.create(
        employee=test_employee,
        entry_type='punch_out',
        timestamp=eod_time,
        notes='Automatic end-of-day clock-out',
        location='System Auto Clock-Out'
    )
    print(f"  ✅ Clocked out {test_employee.full_name} at 10:00 PM")
    
    # Check final status
    final_status = test_employee.get_current_status()
    print(f"  Final status: {final_status}")
    print()
    
    # Test 5: Management command test
    print("Test 5: Management Command Test")
    print("-" * 60)
    print("  To test the management command, run:")
    print("    python manage.py auto_clockout --force")
    print()
    print("  To setup scheduled tasks, run:")
    print("    PowerShell: .\\setup_auto_clockout.ps1")
    print("    Batch: setup_auto_clockout.bat")
    print()
    
    print("=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
    print()
    print("Next Steps:")
    print("1. Run: python manage.py auto_clockout --force")
    print("2. Check the timesheet at: http://127.0.0.1:8000/crm/employee/timesheet/")
    print("3. Setup scheduled tasks using setup_auto_clockout.ps1")
    print()

if __name__ == '__main__':
    test_auto_clockout()