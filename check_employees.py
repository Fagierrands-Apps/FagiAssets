#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append('c:/Users/a/Documents/GitHub/fagiassets/assetmanagement')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
django.setup()

from crm.models import Employee
from django.contrib.auth.models import User

print("=== EXISTING USERS ===")
users = User.objects.all()
for user in users:
    print(f"Username: {user.username}")
    print(f"Email: {user.email}")
    print(f"Is Staff: {user.is_staff}")
    print(f"Is Superuser: {user.is_superuser}")
    print("---")

print("\n=== EXISTING EMPLOYEES ===")
employees = Employee.objects.all()
for emp in employees:
    print(f"Employee: {emp.full_name}")
    print(f"Department: {emp.department}")
    if emp.user:
        print(f"Linked User: {emp.user.username}")
    else:
        print("No user account linked")
    print("---")

print("\n=== CREATING TEST EMPLOYEE LOGIN ===")
# Create a test employee user if none exists
if not employees.filter(user__isnull=False).exists():
    # Create user
    test_user, created = User.objects.get_or_create(
        username='employee1',
        defaults={
            'email': 'employee1@company.com',
            'first_name': 'John',
            'last_name': 'Employee',
            'is_staff': False,
            'is_active': True
        }
    )
    
    if created:
        test_user.set_password('employee123')
        test_user.save()
        print(f"Created user: {test_user.username}")
    
    # Link to employee or create employee
    if employees.exists():
        emp = employees.first()
        emp.user = test_user
        emp.save()
        print(f"Linked user to existing employee: {emp.full_name}")
    else:
        # Create new employee
        emp = Employee.objects.create(
            user=test_user,
            employee_id='EMP001',
            first_name='John',
            last_name='Employee',
            email='employee1@company.com',
            phone='555-0123',
            department='Sales',
            position='Sales Representative',
            hire_date='2024-01-01',
            is_active=True
        )
        print(f"Created new employee: {emp.full_name}")

print("\n=== FINAL LOGIN DETAILS ===")
employees = Employee.objects.filter(user__isnull=False)
for emp in employees:
    print(f"Employee: {emp.full_name}")
    print(f"Username: {emp.user.username}")
    print(f"Password: employee123 (if newly created)")
    print(f"Department: {emp.department}")
    print(f"Position: {emp.position}")
    print("---")