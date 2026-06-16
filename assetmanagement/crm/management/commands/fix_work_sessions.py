"""
Management command to fix work sessions that have punch_out but is_complete is False
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from crm.models import WorkSession


class Command(BaseCommand):
    help = 'Fix work sessions that have punch_out but is_complete is False'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without actually updating',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Find work sessions that have punch_out but is_complete is False
        incomplete_sessions = WorkSession.objects.filter(
            punch_out__isnull=False,
            is_complete=False
        )
        
        count = incomplete_sessions.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No work sessions need fixing!'))
            return
        
        self.stdout.write(f'Found {count} work sessions that need fixing...')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes will be made'))
            for session in incomplete_sessions:
                self.stdout.write(
                    f'  - {session.employee.full_name} on {session.date}: '
                    f'Punch In: {session.punch_in.strftime("%H:%M")}, '
                    f'Punch Out: {session.punch_out.strftime("%H:%M")}'
                )
        else:
            fixed_count = 0
            for session in incomplete_sessions:
                try:
                    session.calculate_hours()
                    fixed_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ Fixed {session.employee.full_name} on {session.date}: '
                            f'{session.worked_hours}h worked'
                        )
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'  ✗ Error fixing {session.employee.full_name} on {session.date}: {str(e)}'
                        )
                    )
            
            self.stdout.write(
                self.style.SUCCESS(f'\nSuccessfully fixed {fixed_count} out of {count} work sessions!')
            )