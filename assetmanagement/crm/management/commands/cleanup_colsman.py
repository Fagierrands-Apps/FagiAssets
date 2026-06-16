from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from crm.models import Employee


class Command(BaseCommand):
    help = 'Clean up colsman user and employee profile'

    def handle(self, *args, **options):
        username = 'colsman'
        
        # Check and delete employee profile
        try:
            user = User.objects.get(username=username)
            self.stdout.write(f'Found user: {username}')
            
            # Try to get employee profile
            try:
                employee = Employee.objects.get(user=user)
                self.stdout.write(f'Found employee profile: {employee.employee_id}')
                employee.delete()
                self.stdout.write(self.style.SUCCESS('Deleted employee profile'))
            except Employee.DoesNotExist:
                self.stdout.write('No employee profile found')
            
            # Delete user
            user.delete()
            self.stdout.write(self.style.SUCCESS(f'Deleted user: {username}'))
            
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING(f'User "{username}" does not exist'))
        
        self.stdout.write(self.style.SUCCESS('Cleanup complete!'))