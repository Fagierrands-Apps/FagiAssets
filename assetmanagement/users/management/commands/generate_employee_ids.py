from django.core.management.base import BaseCommand
from django.db import transaction
from users.models import UserProfile


class Command(BaseCommand):
    help = 'Generate employee IDs for existing user profiles that don\'t have them'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually doing it',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Find profiles without employee IDs
        profiles_without_ids = UserProfile.objects.filter(employee_id__in=['', None])
        
        if not profiles_without_ids.exists():
            self.stdout.write(
                self.style.SUCCESS('All user profiles already have employee IDs.')
            )
            return
        
        self.stdout.write(
            f'Found {profiles_without_ids.count()} user profiles without employee IDs.'
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN: Would generate employee IDs for:')
            )
            for profile in profiles_without_ids:
                self.stdout.write(f'  - {profile.user.get_full_name() or profile.user.username}')
            return
        
        # Generate employee IDs
        updated_count = 0
        with transaction.atomic():
            for profile in profiles_without_ids:
                try:
                    # The save method will automatically generate the employee ID
                    profile.save()
                    updated_count += 1
                    self.stdout.write(
                        f'Generated employee ID {profile.employee_id} for {profile.user.get_full_name() or profile.user.username}'
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to generate employee ID for {profile.user.username}: {str(e)}')
                    )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully generated employee IDs for {updated_count} user profiles.')
        )