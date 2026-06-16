from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from crm.models import Employee


class Command(BaseCommand):
    help = 'Check user details'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to check')

    def handle(self, *args, **options):
        username = options['username']
        
        user = User.objects.filter(username=username).first()
        self.stdout.write(f'User exists: {user is not None}')
        
        if user:
            self.stdout.write(f'Username: {user.username}')
            self.stdout.write(f'Email: {user.email}')
            self.stdout.write(f'Is staff: {user.is_staff}')
            self.stdout.write(f'Is superuser: {user.is_superuser}')
            
            emp = Employee.objects.filter(user=user).first()
            self.stdout.write(f'Has employee profile: {emp is not None}')
            if emp:
                self.stdout.write(f'Role: {emp.role}')
                self.stdout.write(f'Position: {emp.position}')
                self.stdout.write(f'Department: {emp.department}')
                self.stdout.write(f'Employment Status: {emp.employment_status}')
        else:
            self.stdout.write(self.style.WARNING(f'User "{username}" does not exist'))