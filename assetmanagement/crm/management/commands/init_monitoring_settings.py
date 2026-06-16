"""
Management command to initialize monitoring settings for all employees.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from crm.models import Employee, MonitoringSettings


class Command(BaseCommand):
    help = 'Initialize monitoring settings for all employees who do not have settings yet'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset settings for all employees (use with caution)',
        )
        parser.add_argument(
            '--idle-threshold',
            type=int,
            default=5,
            help='Idle threshold in minutes (default: 5)',
        )
        parser.add_argument(
            '--extended-idle-threshold',
            type=int,
            default=15,
            help='Extended idle threshold in minutes (default: 15)',
        )
        parser.add_argument(
            '--heartbeat-interval',
            type=int,
            default=60,
            help='Heartbeat interval in seconds (default: 60)',
        )

    def handle(self, *args, **options):
        reset = options['reset']
        idle_threshold = options['idle_threshold']
        extended_idle_threshold = options['extended_idle_threshold']
        heartbeat_interval = options['heartbeat_interval']

        self.stdout.write(self.style.NOTICE('Initializing monitoring settings...'))

        employees = Employee.objects.all()
        total_employees = employees.count()

        if total_employees == 0:
            self.stdout.write(self.style.WARNING('No employees found in the system.'))
            return

        created_count = 0
        updated_count = 0
        skipped_count = 0

        with transaction.atomic():
            for employee in employees:
                try:
                    settings, created = MonitoringSettings.objects.get_or_create(
                        employee=employee,
                        defaults={
                            'idle_threshold': idle_threshold * 60,  # Convert minutes to seconds
                            'extended_idle_threshold': extended_idle_threshold * 60,  # Convert minutes to seconds
                            'heartbeat_interval': heartbeat_interval,
                            'enable_monitoring': True,
                        }
                    )

                    if created:
                        created_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ Created settings for {employee.full_name} '
                                f'(ID: {employee.employee_id})'
                            )
                        )
                    elif reset:
                        settings.idle_threshold = idle_threshold * 60  # Convert minutes to seconds
                        settings.extended_idle_threshold = extended_idle_threshold * 60  # Convert minutes to seconds
                        settings.heartbeat_interval = heartbeat_interval
                        settings.enable_monitoring = True
                        settings.save()
                        updated_count += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f'↻ Reset settings for {employee.full_name} '
                                f'(ID: {employee.employee_id})'
                            )
                        )
                    else:
                        skipped_count += 1
                        self.stdout.write(
                            self.style.NOTICE(
                                f'- Skipped {employee.full_name} '
                                f'(ID: {employee.employee_id}) - settings already exist'
                            )
                        )

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'✗ Error processing {employee.full_name}: {str(e)}'
                        )
                    )

        # Summary
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('SUMMARY'))
        self.stdout.write('=' * 60)
        self.stdout.write(f'Total employees: {total_employees}')
        self.stdout.write(self.style.SUCCESS(f'Created: {created_count}'))
        if reset:
            self.stdout.write(self.style.WARNING(f'Updated: {updated_count}'))
        self.stdout.write(self.style.NOTICE(f'Skipped: {skipped_count}'))
        self.stdout.write('=' * 60)

        if created_count > 0 or updated_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Successfully initialized monitoring settings!'
                )
            )
        else:
            self.stdout.write(
                self.style.NOTICE(
                    '\nAll employees already have monitoring settings configured.'
                )
            )