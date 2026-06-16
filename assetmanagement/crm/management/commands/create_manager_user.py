from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from crm.models import Employee, Department
from django.utils import timezone
from datetime import date


class Command(BaseCommand):
    help = 'Create manager user (colsman) with task assignment capabilities'

    def handle(self, *args, **options):
        username = 'colsman'
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'User "{username}" already exists'))
            user = User.objects.get(username=username)
        else:
            # Create user
            user = User.objects.create_user(
                username=username,
                email='colsman@fagicrm.com',
                password='Manager2024!',  # Change this after first login
                first_name='Collins',
                last_name='Manager',
                is_staff=True,  # Allow access to admin if needed
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS(f'Created user: {username}'))
        
        # Get or create a department
        department, created = Department.objects.get_or_create(
            name='Management',
            defaults={'description': 'Management and Administration'}
        )
        
        # Check if employee profile exists
        try:
            employee = Employee.objects.get(user=user)
            self.stdout.write(self.style.WARNING(f'Employee profile already exists for {username}'))
            # Update to manager role
            employee.is_manager = True
            employee.role = 'project_manager'
            employee.position = 'Project Manager'
            employee.department = department
            if not employee.hire_date:
                employee.hire_date = date.today()
            employee.save()
            self.stdout.write(self.style.SUCCESS(f'Updated employee profile to manager role'))
        except Employee.DoesNotExist:
            # Create employee profile
            try:
                employee = Employee.objects.create(
                    user=user,
                    position='Project Manager',
                    department=department,
                    role='project_manager',
                    employment_status='active',
                    employment_type='full_time',
                    hire_date=date.today(),
                    is_manager=True,
                    phone='+254700000000'
                )
                self.stdout.write(self.style.SUCCESS(f'Created employee profile for {username}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating employee profile for user {username}: {str(e)}'))
                raise
        
        # Display credentials
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('Manager User Created Successfully!'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(f'Username: {username}')
        self.stdout.write(f'Password: Manager2024!')
        self.stdout.write(f'Email: {user.email}')
        self.stdout.write(f'Role: {employee.get_role_display()}')
        self.stdout.write(f'Position: {employee.position}')
        self.stdout.write(f'Is Manager: {employee.is_manager}')
        self.stdout.write(f'Employee ID: {employee.employee_id}')
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('⚠️  IMPORTANT: Change the password after first login!'))
        self.stdout.write(self.style.SUCCESS('=' * 60))