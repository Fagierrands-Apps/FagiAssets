"""
Quick test script to verify Activity Monitoring System
Run this after starting the development server
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
django.setup()

from django.utils import timezone
from crm.models import (
    Employee, WorkSession, MonitoringSettings, 
    ActivityLog, IdlePeriod, ActivitySession
)

def test_monitoring_system():
    """Test the activity monitoring system"""
    print("=" * 60)
    print("ACTIVITY MONITORING SYSTEM - VERIFICATION TEST")
    print("=" * 60)
    
    # Test 1: Check if models are accessible
    print("\n✓ Test 1: Database Models")
    print(f"  - MonitoringSettings model: OK")
    print(f"  - ActivityLog model: OK")
    print(f"  - IdlePeriod model: OK")
    print(f"  - ActivitySession model: OK")
    
    # Test 2: Check monitoring settings
    print("\n✓ Test 2: Monitoring Settings")
    settings_count = MonitoringSettings.objects.count()
    print(f"  - Total monitoring settings: {settings_count}")
    
    if settings_count > 0:
        sample_setting = MonitoringSettings.objects.first()
        print(f"  - Sample employee: {sample_setting.employee.full_name}")
        print(f"  - Idle threshold: {sample_setting.idle_threshold}s ({sample_setting.idle_threshold/60}min)")
        print(f"  - Extended idle: {sample_setting.extended_idle_threshold}s ({sample_setting.extended_idle_threshold/60}min)")
        print(f"  - Heartbeat interval: {sample_setting.heartbeat_interval}s")
        print(f"  - Monitoring enabled: {sample_setting.enable_monitoring}")
    
    # Test 3: Check employees without settings
    print("\n✓ Test 3: Employee Coverage")
    total_employees = Employee.objects.count()
    employees_with_settings = Employee.objects.filter(
        monitoring_settings__isnull=False
    ).count()
    print(f"  - Total employees: {total_employees}")
    print(f"  - Employees with settings: {employees_with_settings}")
    
    if total_employees != employees_with_settings:
        print(f"  ⚠ WARNING: {total_employees - employees_with_settings} employees without settings!")
        print("  Run: python manage.py init_monitoring_settings")
    else:
        print("  ✓ All employees have monitoring settings!")
    
    # Test 4: Check activity logs
    print("\n✓ Test 4: Activity Logs")
    activity_count = ActivityLog.objects.count()
    print(f"  - Total activity logs: {activity_count}")
    
    if activity_count > 0:
        recent_activity = ActivityLog.objects.order_by('-timestamp').first()
        print(f"  - Most recent activity: {recent_activity.activity_type}")
        print(f"  - Employee: {recent_activity.employee.full_name}")
        print(f"  - Timestamp: {recent_activity.timestamp}")
    else:
        print("  - No activities logged yet (expected if just set up)")
    
    # Test 5: Check idle periods
    print("\n✓ Test 5: Idle Periods")
    idle_count = IdlePeriod.objects.count()
    print(f"  - Total idle periods: {idle_count}")
    
    if idle_count > 0:
        recent_idle = IdlePeriod.objects.order_by('-start_time').first()
        print(f"  - Most recent idle period: {recent_idle.duration_seconds}s")
        print(f"  - Employee: {recent_idle.employee.full_name}")
    else:
        print("  - No idle periods detected yet (expected if just set up)")
    
    # Test 6: Check activity sessions
    print("\n✓ Test 6: Activity Sessions")
    session_count = ActivitySession.objects.count()
    print(f"  - Total activity sessions: {session_count}")
    
    if session_count > 0:
        recent_session = ActivitySession.objects.order_by('-created_at').first()
        print(f"  - Most recent session productivity: {recent_session.productivity_score}")
        print(f"  - Active time: {recent_session.active_time_seconds}s")
        print(f"  - Idle time: {recent_session.idle_time_seconds}s")
    else:
        print("  - No activity sessions yet (expected if just set up)")
    
    # Test 7: Check work sessions with new fields
    print("\n✓ Test 7: Enhanced Work Sessions")
    work_sessions = WorkSession.objects.filter(
        productive_hours__isnull=False
    ).count()
    print(f"  - Work sessions with productivity data: {work_sessions}")
    
    if work_sessions > 0:
        recent_ws = WorkSession.objects.filter(
            productive_hours__isnull=False
        ).order_by('-punch_in').first()
        print(f"  - Sample session:")
        print(f"    - Employee: {recent_ws.employee.full_name}")
        print(f"    - Productive hours: {recent_ws.productive_hours}")
        print(f"    - Idle hours: {recent_ws.idle_hours}")
    
    # Test 8: Check active work sessions
    print("\n✓ Test 8: Active Work Sessions")
    active_sessions = WorkSession.objects.filter(punch_out__isnull=True).count()
    print(f"  - Currently active sessions: {active_sessions}")
    
    if active_sessions > 0:
        print("  - Employees currently punched in:")
        for ws in WorkSession.objects.filter(punch_out__isnull=True):
            print(f"    - {ws.employee.full_name} (since {ws.punch_in.strftime('%H:%M')})")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_good = True
    
    if settings_count == 0:
        print("❌ No monitoring settings found!")
        print("   Run: python manage.py init_monitoring_settings")
        all_good = False
    elif total_employees != employees_with_settings:
        print("⚠ Some employees missing monitoring settings")
        print("   Run: python manage.py init_monitoring_settings")
        all_good = False
    else:
        print("✅ All employees have monitoring settings")
    
    if all_good:
        print("✅ System is ready for use!")
        print("\nNext steps:")
        print("1. Start the development server: python manage.py runserver")
        print("2. Login as an employee")
        print("3. Punch in to start a work session")
        print("4. Open browser console (F12) to see activity tracker logs")
        print("5. Interact with the page and watch activities being logged")
    
    print("=" * 60)

if __name__ == '__main__':
    try:
        test_monitoring_system()
    except Exception as e:
        print(f"\n❌ Error running tests: {str(e)}")
        import traceback
        traceback.print_exc()