#!/usr/bin/env python
"""Verify work sessions are properly updated"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanagement.settings')
django.setup()

from crm.models import WorkSession
from django.utils import timezone
from datetime import timedelta

# Get recent sessions
today = timezone.now().date()
start_date = today - timedelta(days=7)
sessions = WorkSession.objects.filter(date__gte=start_date).order_by('-date', 'employee__user__first_name')

print('Recent Work Sessions (Last 7 Days):')
print('=' * 100)
print(f"{'Employee':<20} | {'Date':<12} | {'Punch In':<8} | {'Punch Out':<8} | {'Hours':<6} | {'Status':<12}")
print('-' * 100)

for session in sessions:
    employee_name = session.employee.full_name[:20]
    date_str = str(session.date)
    punch_in = session.punch_in.strftime('%H:%M') if session.punch_in else 'N/A'
    punch_out = session.punch_out.strftime('%H:%M') if session.punch_out else 'N/A'
    hours = f"{session.worked_hours:.1f}" if session.worked_hours else '0.0'
    status = 'Complete' if session.is_complete else 'In Progress'
    
    print(f"{employee_name:<20} | {date_str:<12} | {punch_in:<8} | {punch_out:<8} | {hours:<6} | {status:<12}")

print('-' * 100)
print(f"\nTotal Sessions: {sessions.count()}")
print(f"Complete: {sessions.filter(is_complete=True).count()}")
print(f"In Progress: {sessions.filter(is_complete=False).count()}")