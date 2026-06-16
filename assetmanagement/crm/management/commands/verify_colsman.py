from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from crm.models import Employee


class Command(BaseCommand):
    help = 'Verify colsman user and employee profile'

    def handle(self, *args, **options):
        username = 'colsman'
        
        try:
            user = User.objects.get(username=username)
            self.stdout.write(self.style.SUCCESS(f'✓ User found: {username}'))
            self.stdout.write(f'  - Email: {user.email}')
            self.stdout.write(f'  - Full Name: {user.get_full_name()}')
            self.stdout.write(f'  - Is Staff: {user.is_staff}')
            self.stdout.write(f'  - Is Active: {user.is_active}')
            
            try:
                employee = Employee.objects.get(user=user)
                self.stdout.write(self.style.SUCCESS(f'\n✓ Employee profile found'))
                self.stdout.write(f'  - Employee ID: {employee.employee_id}')
                self.stdout.write(f'  - Position: {employee.position}')
                self.stdout.write(f'  - Role: {employee.get_role_display()}')
                self.stdout.write(f'  - Department: {employee.department.name if employee.department else "None"}')
                self.stdout.write(f'  - Is Manager: {employee.is_manager}')
                self.stdout.write(f'  - Employment Status: {employee.get_employment_status_display()}')
                self.stdout.write(f'  - Hire Date: {employee.hire_date}')
                
                if employee.is_manager:
                    self.stdout.write(self.style.SUCCESS(f'\n✓ User has manager privileges!'))
                    self.stdout.write(f'\nAccess URLs:')
                    self.stdout.write(f'  - Employee Dashboard: /crm/employee/')
                    self.stdout.write(f'  - Manage Tasks: /crm/manager/tasks/')
                    self.stdout.write(f'  - Create Task: /crm/manager/tasks/create/')
                else:
                    self.stdout.write(self.style.WARNING(f'\n⚠ User does NOT have manager privileges'))
                    
            except Employee.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'✗ Employee profile NOT found'))
                
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'✗ User "{username}" does not exist'))