#!/usr/bin/env python
"""
Test script to verify login functionality works with the new authentication backend
"""

import os
import sys
import django
from django.conf import settings
from django.test import Client, RequestFactory

# Add the project directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'assetmanagement'))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from users.backends import SafeModelBackend

def test_authentication_backend():
    """Test the SafeModelBackend authentication"""
    print("Testing SafeModelBackend authentication...")
    
    # Create test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
        }
    )
    
    if created:
        user.set_password('testpassword')
        user.save()
        print(f"✓ Created test user: {user.username}")
    else:
        print(f"✓ Using existing user: {user.username}")
    
    # Test authentication
    try:
        # Create request factory
        factory = RequestFactory()
        request = factory.post('/login/')
        request.session = {}
        
        # Test authentication backend
        backend = SafeModelBackend()
        authenticated_user = backend.authenticate(
            request, 
            username='testuser', 
            password='testpassword'
        )
        
        if authenticated_user:
            print("✓ Authentication successful")
            print(f"  User: {authenticated_user.username}")
            print(f"  Email: {authenticated_user.email}")
            return True
        else:
            print("✗ Authentication failed")
            return False
            
    except Exception as e:
        print(f"✗ Authentication error: {e}")
        return False

def test_login_view():
    """Test login view functionality"""
    print("\nTesting login view...")
    
    try:
        client = Client()
        
        # Test GET request to login page
        response = client.get('/login/')
        if response.status_code == 200:
            print("✓ Login page loads successfully")
        else:
            print(f"✗ Login page failed: {response.status_code}")
            return False
        
        # Test POST request (login attempt)
        response = client.post('/login/', {
            'username': 'testuser',
            'password': 'testpassword'
        })
        
        if response.status_code in [200, 302]:  # Success or redirect
            print("✓ Login POST request successful")
            return True
        else:
            print(f"✗ Login POST failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Login view error: {e}")
        return False

def test_user_qr_code():
    """Test user QR code functionality"""
    print("\nTesting user QR code functionality...")
    
    try:
        # Get test user
        user = User.objects.get(username='testuser')
        
        # Create authenticated client
        client = Client()
        client.force_login(user)
        
        # Test user profile page
        response = client.get(f'/users/{user.id}/')
        if response.status_code == 200:
            print("✓ User profile page loads successfully")
        else:
            print(f"✗ User profile page failed: {response.status_code}")
            return False
        
        # Test QR code page
        response = client.get(f'/users/{user.id}/qr/')
        if response.status_code == 200:
            print("✓ User QR code page loads successfully")
        else:
            print(f"✗ User QR code page failed: {response.status_code}")
            return False
        
        # Test QR code image
        response = client.get(f'/users/{user.id}/qr/image/')
        if response.status_code == 200:
            print("✓ User QR code image generates successfully")
        else:
            print(f"✗ User QR code image failed: {response.status_code}")
            return False
        
        # Test JSON data
        response = client.get(f'/users/{user.id}/qr/data.json')
        if response.status_code == 200:
            print("✓ User QR code JSON data loads successfully")
        else:
            print(f"✗ User QR code JSON data failed: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ User QR code error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Login and User QR Code System Test")
    print("=" * 60)
    
    # Test authentication backend
    auth_ok = test_authentication_backend()
    
    # Test login view
    login_ok = test_login_view()
    
    # Test user QR code functionality
    qr_ok = test_user_qr_code()
    
    print("\n" + "=" * 60)
    if auth_ok and login_ok and qr_ok:
        print("✓ All tests passed! The system is working correctly.")
        print("\nReady for deployment:")
        print("1. Set environment variables in Vercel")
        print("2. Deploy with: vercel --prod")
        print("3. Run migrations in production")
    else:
        print("✗ Some tests failed. Please check the errors above.")
        
    print("=" * 60)

if __name__ == '__main__':
    main()