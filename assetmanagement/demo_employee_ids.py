#!/usr/bin/env python
"""
Demo script to show automatic employee ID generation
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile

def demo_employee_id_generation():
    print("=== Employee ID Generation Demo ===\n")
    
    # Show existing users with employee IDs
    print("Existing users with employee IDs:")
    existing_profiles = UserProfile.objects.all().order_by('employee_id')
    for profile in existing_profiles:
        print(f"  {profile.user.username}: {profile.employee_id}")
    
    if not existing_profiles:
        print("  No existing users found")
    
    print("\n" + "="*50 + "\n")
    
    # Create a few test users to demonstrate automatic ID generation
    print("Creating new users to demonstrate automatic employee ID generation:")
    
    test_users = [
        {'username': 'john_doe', 'first_name': 'John', 'last_name': 'Doe', 'email': 'john@example.com'},
        {'username': 'jane_smith', 'first_name': 'Jane', 'last_name': 'Smith', 'email': 'jane@example.com'},
        {'username': 'bob_johnson', 'first_name': 'Bob', 'last_name': 'Johnson', 'email': 'bob@example.com'},
    ]
    
    for user_data in test_users:
        # Check if user already exists
        if User.objects.filter(username=user_data['username']).exists():
            print(f"  User {user_data['username']} already exists, skipping...")
            continue
        
        # Create new user
        user = User.objects.create_user(**user_data)
        
        # Display the automatically generated employee ID
        print(f"  Created user: {user.username}")
        print(f"  Full name: {user.get_full_name()}")
        print(f"  Employee ID: {user.profile.employee_id}")
        print()
    
    print("=" * 50)
    print("\nAll users with employee IDs (after demo):")
    all_profiles = UserProfile.objects.all().order_by('employee_id')
    for profile in all_profiles:
        print(f"  {profile.user.get_full_name() or profile.user.username}: {profile.employee_id}")

if __name__ == "__main__":
    demo_employee_id_generation()