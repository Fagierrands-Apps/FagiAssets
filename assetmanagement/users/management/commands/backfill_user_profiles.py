from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone


class Command(BaseCommand):
    help = 'Create missing UserProfile and Employee records for existing users'

    def handle(self, *args, **kwargs):
        from users.models import UserProfile
        from crm.models import Employee

        users = User.objects.all()
        created_profiles = 0
        created_employees = 0

        for user in users:
            # Backfill UserProfile
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={'employee_id': ''}
            )
            if created:
                if not profile.employee_id:
                    profile.save()  # triggers employee_id generation
                created_profiles += 1

            # Backfill Employee
            employee, created = Employee.objects.get_or_create(
                user=user,
                defaults={
                    'employee_id': profile.employee_id or '',
                    'position': profile.job_title or 'User',
                    'employment_status': 'active',
                    'employment_type': 'full_time',
                    'role': 'user',
                    'hire_date': timezone.now().date(),
                }
            )
            if created:
                created_employees += 1

        self.stdout.write(self.style.SUCCESS(
            f'Done. Created {created_profiles} UserProfile(s) and {created_employees} Employee record(s).'
        ))
