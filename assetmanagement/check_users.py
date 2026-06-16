#!/usr/bin/env python
"""
Check existing users and their employee IDs
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile

def check_users():
    """Check all existing users and their employee IDs"""
    print("Current Users and Employee IDs:")
    print("=" * 50)
    
    users = User.objects.all()
    print(f"Total users: {users.count()}")
    
    for user in users:
        try:
            profile = user.profile
            employee_id = profile.employee_id
            print(f"User: {user.username:<15} | Employee ID: {employee_id:<20} | Name: {user.get_full_name()}")
        except UserProfile.DoesNotExist:
            print(f"User: {user.username:<15} | Employee ID: {'No profile':<20} | Name: {user.get_full_name()}")
    
    # Check for any existing FGE employee IDs
    fge_profiles = UserProfile.objects.filter(employee_id__startswith='FGE')
    print(f"\nExisting FGE employee IDs: {fge_profiles.count()}")
    for profile in fge_profiles:
        print(f"  - {profile.employee_id} ({profile.user.username})")

if __name__ == "__main__":
    check_users()