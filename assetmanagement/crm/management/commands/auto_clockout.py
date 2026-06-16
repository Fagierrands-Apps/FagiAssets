"""
Management command to automatically clock out employees at specific times.

This command should be run periodically (e.g., via cron or Windows Task Scheduler):
- At 1:30 PM: Clock out employees for lunch break
- At 10:00 PM: Clock out all employees still clocked in

Usage:
    python manage.py auto_clockout
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from crm.models import Employee, TimeEntry, WorkSession
from datetime import datetime, time
from decimal import Decimal


class Command(BaseCommand):
    help = 'Automatically clock out employees at scheduled times (1:30 PM and 10:00 PM)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force clock out regardless of time',
        )
        parser.add_argument(
            '--time',
            type=str,
            help='Specific time to check (e.g., "13:30" or "22:00")',
        )

    def handle(self, *args, **options):
        now = timezone.now()
        current_time = now.time()
        force = options.get('force', False)
        specific_time = options.get('time')

        # Determine which clock-out to perform
        should_lunch_clockout = False
        should_end_of_day_clockout = False

        if specific_time:
            # Parse specific time
            hour, minute = map(int, specific_time.split(':'))
            target_time = time(hour, minute)
            
            if target_time == time(13, 30):
                should_lunch_clockout = True
            elif target_time == time(22, 0):
                should_end_of_day_clockout = True
        elif force:
            # Force both if requested
            should_lunch_clockout = True
            should_end_of_day_clockout = True
        else:
            # Check current time
            # Lunch clock-out: 1:30 PM (13:30)
            if current_time.hour == 13 and 30 <= current_time.minute < 35:
                should_lunch_clockout = True
            
            # End of day clock-out: 10:00 PM (22:00)
            if current_time.hour == 22 and 0 <= current_time.minute < 5:
                should_end_of_day_clockout = True

        if not should_lunch_clockout and not should_end_of_day_clockout:
            self.stdout.write(
                self.style.WARNING(
                    f'Not the right time for auto clock-out. Current time: {current_time.strftime("%H:%M")}'
                )
            )
            return

        # Get all active employees
        active_employees = Employee.objects.filter(employment_status='active')
        
        lunch_clockout_count = 0
        end_of_day_clockout_count = 0
        reclock_in_count = 0

        for employee in active_employees:
            # Get today's latest time entry
            today = now.date()
            latest_entry = employee.time_entries.filter(
                timestamp__date=today
            ).order_by('-timestamp').first()

            if not latest_entry:
                continue

            # Check if employee is currently clocked in
            if latest_entry.entry_type in ['punch_in', 'break_end']:
                
                if should_lunch_clockout:
                    # Clock out for lunch at 1:30 PM
                    self.clock_out_employee(
                        employee, 
                        now.replace(hour=13, minute=30, second=0, microsecond=0),
                        'Automatic clock-out for lunch break'
                    )
                    lunch_clockout_count += 1
                    
                    # Immediately clock back in for afternoon shift
                    self.clock_in_employee(
                        employee,
                        now.replace(hour=13, minute=30, second=1, microsecond=0),
                        'Automatic clock-in after lunch break'
                    )
                    reclock_in_count += 1
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Clocked out and back in {employee.full_name} for lunch break'
                        )
                    )

                if should_end_of_day_clockout:
                    # Clock out at end of day (10:00 PM)
                    self.clock_out_employee(
                        employee,
                        now.replace(hour=22, minute=0, second=0, microsecond=0),
                        'Automatic end-of-day clock-out'
                    )
                    end_of_day_clockout_count += 1
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Clocked out {employee.full_name} at end of day'
                        )
                    )

        # Update work sessions
        self.update_work_sessions(now.date())

        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\n=== Auto Clock-Out Summary ==='
            )
        )
        if should_lunch_clockout:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Lunch break clock-outs: {lunch_clockout_count}'
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Lunch break re-clock-ins: {reclock_in_count}'
                )
            )
        if should_end_of_day_clockout:
            self.stdout.write(
                self.style.SUCCESS(
                    f'End-of-day clock-outs: {end_of_day_clockout_count}'
                )
            )

    def clock_out_employee(self, employee, timestamp, notes):
        """Clock out an employee"""
        TimeEntry.objects.create(
            employee=employee,
            entry_type='punch_out',
            timestamp=timestamp,
            notes=notes,
            location='System Auto Clock-Out'
        )

    def clock_in_employee(self, employee, timestamp, notes):
        """Clock in an employee"""
        TimeEntry.objects.create(
            employee=employee,
            entry_type='punch_in',
            timestamp=timestamp,
            notes=notes,
            location='System Auto Clock-In'
        )

    def update_work_sessions(self, date):
        """Update work sessions for the given date"""
        # Get all employees with time entries for this date
        employees_with_entries = Employee.objects.filter(
            time_entries__timestamp__date=date
        ).distinct()

        for employee in employees_with_entries:
            # Get all time entries for this date
            entries = employee.time_entries.filter(
                timestamp__date=date
            ).order_by('timestamp')

            if not entries.exists():
                continue

            # Find first punch_in and last punch_out
            punch_in = None
            punch_out = None
            break_minutes = 0

            for entry in entries:
                if entry.entry_type == 'punch_in' and punch_in is None:
                    punch_in = entry.timestamp
                elif entry.entry_type == 'punch_out':
                    punch_out = entry.timestamp

            # Calculate break time
            break_start = None
            for entry in entries:
                if entry.entry_type == 'break_start':
                    break_start = entry.timestamp
                elif entry.entry_type == 'break_end' and break_start:
                    break_duration = (entry.timestamp - break_start).total_seconds() / 60
                    break_minutes += break_duration
                    break_start = None

            if punch_in:
                # Calculate hours
                if punch_out:
                    total_minutes = (punch_out - punch_in).total_seconds() / 60
                    total_hours = Decimal(str(total_minutes / 60))
                    break_hours = Decimal(str(break_minutes / 60))
                    worked_hours = total_hours - break_hours
                    is_complete = True
                else:
                    # Still clocked in
                    total_hours = Decimal('0')
                    break_hours = Decimal('0')
                    worked_hours = Decimal('0')
                    is_complete = False

                # Update or create work session
                WorkSession.objects.update_or_create(
                    employee=employee,
                    date=date,
                    defaults={
                        'punch_in': punch_in,
                        'punch_out': punch_out,
                        'total_hours': total_hours,
                        'break_hours': break_hours,
                        'worked_hours': worked_hours,
                        'is_complete': is_complete,
                    }
                )