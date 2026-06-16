#!/usr/bin/env python
"""
Check all users in production database
"""

import os
import sys
import django

def check_production_users():
    """Check all users in production database"""
    print("=" * 60)
    print("Checking Production Database Users")
    print("=" * 60)
    
    # Set environment variables for production
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
    os.environ['VERCEL'] = '1'  # Force production mode
    os.environ['DATABASE_URL'] = 'postgresql://postgres.dxesmzogjpxswxhsomgf:OnFRtf0SmpHwgNaQ@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres'
    
    # Add Django project to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'assetmanagement'))
    
    # Setup Django
    django.setup()
    
    from django.contrib.auth.models import User
    from users.models import UserProfile
    
    try:
        users = User.objects.all()
        print(f"Total users in production database: {users.count()}")
        print()
        
        if users.count() == 0:
            print("No users found in database.")
            return
        
        print("User Details:")
        print("-" * 80)
        print(f"{'Username':<15} {'Email':<25} {'Name':<20} {'Staff':<6} {'Super':<6} {'Active':<6} {'Employee ID':<12}")
        print("-" * 80)
        
        for user in users:
            try:
                profile = user.profile
                employee_id = profile.employee_id or 'N/A'
            except UserProfile.DoesNotExist:
                employee_id = 'No Profile'
            
            full_name = user.get_full_name() or 'N/A'
            
            print(f"{user.username:<15} {user.email:<25} {full_name:<20} {user.is_staff:<6} {user.is_superuser:<6} {user.is_active:<6} {employee_id:<12}")
        
        print("-" * 80)
        
        # Check for profiles without users (shouldn't happen but good to check)
        orphaned_profiles = UserProfile.objects.filter(user__isnull=True)
        if orphaned_profiles.exists():
            print(f"\nWarning: Found {orphaned_profiles.count()} orphaned profiles")
        
        # Check for users without profiles
        users_without_profiles = User.objects.filter(profile__isnull=True)
        if users_without_profiles.exists():
            print(f"\nWarning: Found {users_without_profiles.count()} users without profiles:")
            for user in users_without_profiles:
                print(f"  - {user.username}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = check_production_users()
    sys.exit(0 if success else 1)