"""
Management command to sync punch_out TimeEntry records to WorkSession
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from crm.models import WorkSession, TimeEntry


class Command(BaseCommand):
    help = 'Sync punch_out TimeEntry records to WorkSession table'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without actually updating',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Find all punch_out time entries
        punch_out_entries = TimeEntry.objects.filter(
            entry_type='punch_out'
        ).order_by('timestamp')
        
        if punch_out_entries.count() == 0:
            self.stdout.write(self.style.SUCCESS('No punch_out entries found!'))
            return
        
        self.stdout.write(f'Found {punch_out_entries.count()} punch_out entries...')
        
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        for entry in punch_out_entries:
            try:
                # Get the work session for this employee and date
                work_session = WorkSession.objects.get(
                    employee=entry.employee,
                    date=entry.timestamp.date()
                )
                
                # Check if punch_out is already set
                if work_session.punch_out:
                    self.stdout.write(
                        self.style.WARNING(
                            f'  ⊘ Skipped {entry.employee.full_name} on {entry.timestamp.date()}: '
                            f'Already has punch_out at {work_session.punch_out.strftime("%H:%M")}'
                        )
                    )
                    skipped_count += 1
                    continue
                
                if dry_run:
                    self.stdout.write(
                        self.style.WARNING(
                            f'  [DRY RUN] Would update {entry.employee.full_name} on {entry.timestamp.date()}: '
                            f'Set punch_out to {entry.timestamp.strftime("%H:%M")}'
                        )
                    )
                else:
                    # Update the work session
                    work_session.punch_out = entry.timestamp
                    work_session.calculate_hours()
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ Updated {entry.employee.full_name} on {entry.timestamp.date()}: '
                            f'Punch out at {entry.timestamp.strftime("%H:%M")}, '
                            f'Worked {work_session.worked_hours}h'
                        )
                    )
                    updated_count += 1
                    
            except WorkSession.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f'  ✗ No work session found for {entry.employee.full_name} on {entry.timestamp.date()}'
                    )
                )
                error_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'  ✗ Error processing {entry.employee.full_name} on {entry.timestamp.date()}: {str(e)}'
                    )
                )
                error_count += 1
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'\nDRY RUN - No changes were made')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nSummary:'
                    f'\n  - Updated: {updated_count}'
                    f'\n  - Skipped: {skipped_count}'
                    f'\n  - Errors: {error_count}'
                )
            )