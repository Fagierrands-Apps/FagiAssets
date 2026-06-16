#!/usr/bin/env python
"""
Test Django Admin Access
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse

def test_admin_access():
    """Test admin access"""
    
    print("🧪 Testing Django Admin Access...")
    print("=" * 50)
    
    # Create a test client
    client = Client()
    
    # Test admin login page
    try:
        response = client.get('/admin/')
        print(f"Admin page status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Admin login page accessible")
        elif response.status_code == 302:
            print("✅ Admin redirects to login (normal behavior)")
        else:
            print(f"❌ Admin page returned status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error accessing admin: {e}")
    
    # Test admin with authenticated user
    try:
        # Get admin user
        admin_user = User.objects.get(username='admin')
        
        # Login as admin
        client.force_login(admin_user)
        
        # Access admin dashboard
        response = client.get('/admin/')
        print(f"Admin dashboard status (authenticated): {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Admin dashboard accessible when logged in")
        else:
            print(f"❌ Admin dashboard returned status {response.status_code}")
            print(f"Response content: {response.content.decode()[:500]}")
            
    except User.DoesNotExist:
        print("❌ Admin user not found")
    except Exception as e:
        print(f"❌ Error accessing admin with authentication: {e}")
        import traceback
        traceback.print_exc()

def test_user_profiles():
    """Test user profiles functionality"""
    
    print("\n🧪 Testing User Profiles...")
    print("=" * 50)
    
    try:
        # Check all users have profiles
        users = User.objects.all()
        print(f"Total users: {users.count()}")
        
        for user in users:
            try:
                profile = user.profile
                print(f"✅ User {user.username}: Profile exists, Employee ID: {profile.employee_id}")
            except Exception as e:
                print(f"❌ User {user.username}: Profile error - {e}")
                
    except Exception as e:
        print(f"❌ Error checking user profiles: {e}")

if __name__ == "__main__":
    test_admin_access()
    test_user_profiles()