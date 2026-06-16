#!/usr/bin/env python
import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth.models import User

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
sys.path.insert(0, 'assetmanagement')
django.setup()

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

    # Test login
    response = client.post('/login/', {
        'username': 'admin',
        'password': 'admin123'  # Assuming default password
    })

    print(f"Login response status: {response.status_code}")
    print(f"Login response redirect: {response.get('Location', 'No redirect header')}")

    # Check if user is authenticated
    if response.status_code == 302:  # Redirect
        redirect_url = response.get('Location', '')
        print(f"Redirected to: {redirect_url}")

        # Follow the redirect
        follow_response = client.get(redirect_url)
        print(f"Follow response status: {follow_response.status_code}")
        print(f"Follow response URL: {follow_response.request['PATH_INFO']}")

        # Check if we're on the admin dashboard
        if '/admin-dashboard/' in redirect_url:
            print("SUCCESS: Redirected to admin dashboard")
        else:
            print("ISSUE: Not redirected to admin dashboard")
    else:
        print("Login failed or no redirect")
        print(f"Response content: {response.content.decode()[:500]}")

if __name__ == '__main__':
    test_login_redirect()
