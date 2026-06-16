#!/usr/bin/env python
import os
import sys
import django

# Setup Django first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
sys.path.insert(0, 'assetmanagement')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_login_redirect():
    """Test the full login redirect process"""
    client = Client()

    # Get the admin user
    try:
        admin_user = User.objects.get(username='admin')
        print(f"Found admin user: {admin_user.username}, superuser={admin_user.is_superuser}, staff={admin_user.is_staff}")
    except User.DoesNotExist:
        print("Admin user not found")
        return

    # Test login with a simple password check first
    from django.contrib.auth import authenticate
    user = authenticate(username='admin', password='admin123')
    if user:
        print("Authentication successful with admin123")
    else:
        print("Authentication failed - trying different passwords")
        # Try common passwords
        for password in ['admin', 'password', '123456', 'admin123']:
            user = authenticate(username='admin', password=password)
            if user:
                print(f"Authentication successful with password: {password}")
                break
        else:
            print("Could not authenticate admin user")
            return

    # Now test the login process
    response = client.post('/login/', {
        'username': 'admin',
        'password': 'admin123'
    })

    print(f"Login response status: {response.status_code}")
    print(f"Login response redirect: {response.get('Location', 'No redirect header')}")

    # Check if user is authenticated
    if response.status_code == 302:  # Redirect
        redirect_url = response.get('Location', '')
        print(f"Redirected to: {redirect_url}")

        # Check if we're on the admin dashboard
        if '/admin-dashboard/' in redirect_url:
            print("SUCCESS: Redirected to admin dashboard")
        else:
            print("ISSUE: Not redirected to admin dashboard")
    else:
        print("Login failed or no redirect")
        if response.status_code == 200:
            print("Login form returned - authentication failed")

if __name__ == '__main__':
    test_login_redirect()
