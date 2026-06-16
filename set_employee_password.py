#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append('c:/Users/a/Documents/GitHub/fagiassets/assetmanagement')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
django.setup()

from django.contrib.auth.models import User

# Set password for the test.sales user
try:
    user = User.objects.get(username='test.sales')
    user.set_password('employee123')
    user.save()
    print(f"Password set for user: {user.username}")
    print(f"New password: employee123")
except User.DoesNotExist:
    print("User test.sales not found")

# Also create another employee user for testing
test_user, created = User.objects.get_or_create(
    username='employee1',
    defaults={
        'email': 'employee1@company.com',
        'first_name': 'John',
        'last_name': 'Smith',
        'is_staff': False,
        'is_active': True
    }
)

if created:
    test_user.set_password('employee123')
    test_user.save()
    print(f"Created additional user: {test_user.username}")
    print(f"Password: employee123")
else:
    # Update password for existing user
    test_user.set_password('employee123')
    test_user.save()
    print(f"Updated password for existing user: {test_user.username}")
    print(f"Password: employee123")