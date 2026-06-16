"""
Management command to automatically create lunch break entries at 1 PM
for all employees except call center agents (Monday-Saturday)
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from crm.models import Employee, TimeEntry
from datetime import datetime, time
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Automatically create lunch break entries at 1 PM for non-call-center employees'

    def handle(self, *args, **options):
        now = timezone.now()
        current_time = now.time()
        current_day = now.weekday()  # 0=Monday, 6=Sunday
        
        # Only run Monday-Saturday (0-5)
        if current_day == 6:  # Sunday
            self.stdout.write(self.style.WARNING('Skipping: Today is Sunday'))
            return
        
        # Check if it's 1 PM (13:00)
        lunch_start_time = time(13, 0)
        lunch_end_time = time(14, 0)
        
        # Only run between 13:00 and 13:05 to avoid multiple executions
        if not (lunch_start_time <= current_time < time(13, 5)):
            self.stdout.write(self.style.WARNING(f'Skipping: Current time {current_time} is not lunch time'))
            return
        
        # Get all active employees who are currently punched in
        employees = Employee.objects.filter(
            employment_status='active'
        ).exclude(
            role='call_center'  # Exclude call center agents
        )
        
        processed_count = 0
        skipped_count = 0
        
        for employee in employees:
            try:
                # Check if employee is currently punched in
                current_status = employee.get_current_status()
                
                if current_status not in ['punched_in', 'working']:
                    skipped_count += 1
                    continue
                
                # Check if lunch break already created today
                today_lunch_break = TimeEntry.objects.filter(
                    employee=employee,
                    entry_type='break_start',
                    timestamp__date=now.date(),
                    timestamp__hour=13,
                    notes__contains='Automatic lunch break'
                ).exists()
                
                if today_lunch_break:
                    skipped_count += 1
                    continue
                
                # Create break_start entry at 1 PM
                break_start = TimeEntry.objects.create(
                    employee=employee,
                    entry_type='break_start',
                    timestamp=now.replace(hour=13, minute=0, second=0, microsecond=0),
                    notes='Automatic lunch break (1 PM - 2 PM)',
                    ip_address=None
                )
                
                # Create break_end entry at 2 PM
                break_end = TimeEntry.objects.create(
                    employee=employee,
                    entry_type='break_end',
                    timestamp=now.replace(hour=14, minute=0, second=0, microsecond=0),
                    notes='Automatic lunch break end',
                    ip_address=None
                )
                
                processed_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Created lunch break for {employee.full_name}'
                    )
                )
                
            except Exception as e:
                logger.error(f'Error creating lunch break for {employee.full_name}: {str(e)}')
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Error for {employee.full_name}: {str(e)}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Processed: {processed_count} employees'
            )
        )
        self.stdout.write(
            self.style.WARNING(
                f'⊘ Skipped: {skipped_count} employees (not punched in or already on break)'
            )
        )