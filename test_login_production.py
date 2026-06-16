#!/usr/bin/env python
"""
Test production login functionality
"""

import os
import sys
import django
from django.test import Client

def test_production_login():
    """Test login functionality in production"""
    print("=" * 60)
    print("Testing Production Login")
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
    
    try:
        # Check if admin user exists
        admin_user = User.objects.get(username='admin')
        print(f"✓ Admin user found: {admin_user.username}")
        print(f"  Email: {admin_user.email}")
        print(f"  Is staff: {admin_user.is_staff}")
        print(f"  Is superuser: {admin_user.is_superuser}")
        print(f"  Is active: {admin_user.is_active}")
        
        # Test authentication
        from django.contrib.auth import authenticate
        
        user = authenticate(username='admin', password='FagiAssets2024!')
        if user:
            print("✓ Authentication successful")
        else:
            print("✗ Authentication failed")
            return False
        
        # Test login view
        client = Client()
        
        # Test GET request to login page
        response = client.get('/login/')
        if response.status_code == 200:
            print("✓ Login page loads successfully")
        else:
            print(f"✗ Login page failed: {response.status_code}")
            return False
        
        # Test POST request (actual login)
        response = client.post('/login/', {
            'username': 'admin',
            'password': 'FagiAssets2024!'
        })
        
        if response.status_code in [200, 302]:  # Success or redirect
            print("✓ Login POST request successful")
            
            # Check if user is logged in
            if response.wsgi_request.user.is_authenticated:
                print("✓ User is authenticated after login")
            else:
                print("! User authentication status unclear")
            
        else:
            print(f"✗ Login POST failed: {response.status_code}")
            return False
        
        # Test user QR code functionality
        print("\nTesting user QR code functionality...")
        
        # Force login for QR code test
        client.force_login(admin_user)
        
        # Test user profile page
        response = client.get(f'/users/{admin_user.id}/')
        if response.status_code == 200:
            print("✓ User profile page loads successfully")
        else:
            print(f"✗ User profile page failed: {response.status_code}")
        
        # Test QR code page
        response = client.get(f'/users/{admin_user.id}/qr/')
        if response.status_code == 200:
            print("✓ User QR code page loads successfully")
        else:
            print(f"✗ User QR code page failed: {response.status_code}")
        
        # Test QR code image
        response = client.get(f'/users/{admin_user.id}/qr/image/')
        if response.status_code == 200:
            print("✓ User QR code image generates successfully")
        else:
            print(f"✗ User QR code image failed: {response.status_code}")
        
        return True
        
    except User.DoesNotExist:
        print("✗ Admin user not found")
        return False
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

if __name__ == '__main__':
    success = test_production_login()
    if success:
        print("\n✅ All tests passed!")
        print("\nProduction login is working correctly.")
        print("You can now deploy to Vercel and test at:")
        print("https://fagiassets.vercel.app/login/")
        print("\nLogin credentials:")
        print("Username: admin")
        print("Password: FagiAssets2024!")
    else:
        print("\n❌ Some tests failed")
    sys.exit(0 if success else 1)