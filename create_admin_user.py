#!/usr/bin/env python
"""
Create admin user for production
"""

import os
import sys
import django

def create_admin_user():
    """Create admin user in production database"""
    print("=" * 60)
    print("Creating Admin User for Production")
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
        # Check if admin user already exists
        try:
            admin_user = User.objects.get(username='admin')
            print(f"✓ Admin user already exists: {admin_user.username}")
            print(f"  Email: {admin_user.email}")
            print(f"  Is staff: {admin_user.is_staff}")
            print(f"  Is superuser: {admin_user.is_superuser}")
            print(f"  Is active: {admin_user.is_active}")
            
            # Test password
            if admin_user.check_password('FagiAssets2024!'):
                print("✓ Password is correct")
            else:
                print("✗ Password is incorrect - updating password")
                admin_user.set_password('FagiAssets2024!')
                admin_user.save()
                print("✓ Password updated")
            
        except User.DoesNotExist:
            print("Creating new admin user...")
            
            # Create admin user
            admin_user = User.objects.create_user(
                username='admin',
                email='admin@fagiassets.com',
                password='FagiAssets2024!',
                first_name='System',
                last_name='Administrator'
            )
            
            # Make user staff and superuser
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.is_active = True
            admin_user.save()
            
            print("✓ Admin user created successfully")
            print(f"  Username: {admin_user.username}")
            print(f"  Email: {admin_user.email}")
            print(f"  Is staff: {admin_user.is_staff}")
            print(f"  Is superuser: {admin_user.is_superuser}")
            print(f"  Is active: {admin_user.is_active}")
        
        # Ensure user profile exists
        try:
            profile = admin_user.profile
            print(f"✓ User profile exists: Employee ID {profile.employee_id}")
        except UserProfile.DoesNotExist:
            print("Creating user profile...")
            profile = UserProfile.objects.create(
                user=admin_user,
                job_title='System Administrator',
                employee_id='FGE001'  # First employee ID
            )
            print(f"✓ User profile created: Employee ID {profile.employee_id}")
        
        # Test authentication
        from django.contrib.auth import authenticate
        
        user = authenticate(username='admin', password='FagiAssets2024!')
        if user:
            print("✓ Authentication test successful")
        else:
            print("✗ Authentication test failed")
            return False
        
        print("\n" + "=" * 60)
        print("Admin user is ready!")
        print("=" * 60)
        print("Login credentials for https://fagiassets.vercel.app/login/:")
        print("Username: admin")
        print("Password: FagiAssets2024!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = create_admin_user()
    sys.exit(0 if success else 1)