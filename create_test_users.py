#!/usr/bin/env python
"""
Create test users with different roles for the CRM system
"""

import os
import sys
import django
from datetime import date

def create_test_users():
    """Create test users with different roles"""
    print("=" * 60)
    print("Creating Test Users for CRM System")
    print("=" * 60)

    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')

    # Add Django project to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'assetmanagement'))

    # Setup Django
    django.setup()

    from django.contrib.auth.models import User
    from crm.models import Employee, Department

    try:
        # Create or get department
        dept, created = Department.objects.get_or_create(
            name='Test Department',
            defaults={'description': 'Department for testing'}
        )
        if created:
            print(f"✓ Created department: {dept.name}")
        else:
            print(f"✓ Department already exists: {dept.name}")

        # Create test users with different roles
        roles = ['admin', 'sales', 'call_center', 'user']
        users_data = [
            {'username': 'admin_test', 'email': 'admin@test.com', 'first_name': 'Admin', 'last_name': 'User', 'role': 'admin'},
            {'username': 'sales_test', 'email': 'sales@test.com', 'first_name': 'Sales', 'last_name': 'User', 'role': 'sales'},
            {'username': 'callcenter_test', 'email': 'callcenter@test.com', 'first_name': 'Call Center', 'last_name': 'User', 'role': 'call_center'},
            {'username': 'user_test', 'email': 'user@test.com', 'first_name': 'Regular', 'last_name': 'User', 'role': 'user'},
        ]

        for user_data in users_data:
            # Create user
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                }
            )

            if created:
                user.set_password('testpass123')
                user.save()
                print(f'✓ Created user: {user.username}')
            else:
                print(f'✓ User {user.username} already exists')

            # Create or update employee profile
            employee, emp_created = Employee.objects.get_or_create(
                user=user,
                defaults={
                    'department': dept,
                    'role': user_data['role'],
                    'employee_id': f'EMP{user.id:03d}',
                    'position': f'{user_data["role"].replace("_", " ").title()} Position',
                    'employment_status': 'active',
                    'employment_type': 'full_time',
                    'hire_date': date.today(),  # Required field
                }
            )

            if emp_created:
                print(f'✓ Created employee profile for {user.username} with role {user_data["role"]}')
            else:
                employee.role = user_data['role']
                employee.save()
                print(f'✓ Updated employee profile for {user.username} with role {user_data["role"]}')

        print('\n✓ Test users created successfully!')
        print('Login credentials:')
        print('Username: admin_test, Password: testpass123, Role: admin')
        print('Username: sales_test, Password: testpass123, Role: sales')
        print('Username: callcenter_test, Password: testpass123, Role: call_center')
        print('Username: user_test, Password: testpass123, Role: user')
        print("=" * 60)

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = create_test_users()
    sys.exit(0 if success else 1)
