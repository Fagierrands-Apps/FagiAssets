#!/usr/bin/env python
"""
Test FGE Employee ID Generation
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile

def test_fge_employee_id_generation():
    """Test that new users get FGE employee IDs"""
    
    print("🧪 Testing FGE Employee ID Generation...")
    print("=" * 50)
    
    # Check current users
    print("Current users:")
    for user in User.objects.all():
        try:
            profile = user.profile
            print(f"  - {user.username}: {profile.employee_id}")
        except UserProfile.DoesNotExist:
            print(f"  - {user.username}: No profile")
    
    # Test creating a new user
    print("\n🔬 Testing new user creation...")
    
    # Create a test user
    test_username = "testuser_fge"
    
    # Clean up any existing test user
    try:
        existing_user = User.objects.get(username=test_username)
        existing_user.delete()
        print(f"  Cleaned up existing test user: {test_username}")
    except User.DoesNotExist:
        pass
    
    # Create new user
    new_user = User.objects.create_user(
        username=test_username,
        email='test@example.com',
        first_name='Test',
        last_name='User'
    )
    
    # Check the employee ID
    try:
        profile = new_user.profile
        print(f"  ✅ New user created: {new_user.username}")
        print(f"  📋 Employee ID: {profile.employee_id}")
        
        # Verify it follows FGE format
        if profile.employee_id.startswith('FGE') and len(profile.employee_id) == 6:
            print(f"  ✅ Employee ID format is correct: {profile.employee_id}")
            
            # Extract number part
            number_part = profile.employee_id[3:]
            if number_part.isdigit():
                number = int(number_part)
                print(f"  ✅ Employee number: {number}")
                
                # Should be FGE005 (next after FGE004)
                if number == 5:
                    print("  ✅ Employee ID sequence is correct (FGE005)")
                else:
                    print(f"  ⚠️  Expected FGE005, got {profile.employee_id}")
            else:
                print(f"  ❌ Invalid number format in employee ID: {profile.employee_id}")
        else:
            print(f"  ❌ Invalid employee ID format: {profile.employee_id}")
            
    except UserProfile.DoesNotExist:
        print(f"  ❌ Profile not created for user: {new_user.username}")
    
    # Clean up test user
    new_user.delete()
    print(f"  🧹 Cleaned up test user: {test_username}")
    
    print("\n" + "=" * 50)
    print("Final user list:")
    for user in User.objects.all():
        try:
            profile = user.profile
            print(f"  - {user.username}: {profile.employee_id}")
        except UserProfile.DoesNotExist:
            print(f"  - {user.username}: No profile")

def test_employee_id_uniqueness():
    """Test that employee IDs are unique"""
    
    print("\n🧪 Testing Employee ID Uniqueness...")
    print("=" * 50)
    
    # Get all employee IDs
    employee_ids = UserProfile.objects.values_list('employee_id', flat=True)
    
    print(f"Total profiles: {len(employee_ids)}")
    print(f"Unique employee IDs: {len(set(employee_ids))}")
    
    if len(employee_ids) == len(set(employee_ids)):
        print("✅ All employee IDs are unique")
    else:
        print("❌ Duplicate employee IDs found!")
        
        # Find duplicates
        seen = set()
        duplicates = set()
        for emp_id in employee_ids:
            if emp_id in seen:
                duplicates.add(emp_id)
            else:
                seen.add(emp_id)
        
        print(f"Duplicate IDs: {duplicates}")

if __name__ == "__main__":
    test_fge_employee_id_generation()
    test_employee_id_uniqueness()