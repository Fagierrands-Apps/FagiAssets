#!/usr/bin/env python
"""
Debug Admin 500 Error
"""

import os
import sys
import django
from django.test import Client

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
django.setup()

def debug_admin_500():
    """Debug the admin 500 error"""
    
    print("🐛 Debugging Admin 500 Error...")
    print("=" * 50)
    
    from django.contrib.auth.models import User
    
    # Create a test client
    client = Client()
    
    # Test various admin URLs
    test_urls = [
        '/admin/',
        '/admin/login/',
        '/admin/auth/user/',
        '/admin/users/userprofile/',
        '/admin/assets/asset/',
    ]
    
    for url in test_urls:
        try:
            print(f"\n🔍 Testing URL: {url}")
            response = client.get(url)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 500:
                print("   ❌ 500 Error detected!")
                print(f"   Content: {response.content.decode()[:200]}...")
            elif response.status_code == 302:
                print("   ✅ Redirect (normal for unauthenticated)")
            elif response.status_code == 200:
                print("   ✅ Success")
            else:
                print(f"   ⚠️  Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # Test with authentication
    print(f"\n🔑 Testing with authentication...")
    try:
        admin_user = User.objects.get(username='admin')
        client.force_login(admin_user)
        
        for url in test_urls:
            try:
                print(f"\n🔍 Testing URL (authenticated): {url}")
                response = client.get(url)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 500:
                    print("   ❌ 500 Error detected!")
                    print(f"   Content: {response.content.decode()[:500]}...")
                elif response.status_code == 200:
                    print("   ✅ Success")
                else:
                    print(f"   ⚠️  Status: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Exception: {e}")
                
    except User.DoesNotExist:
        print("   ❌ Admin user not found")
    except Exception as e:
        print(f"   ❌ Authentication error: {e}")

def check_debug_settings():
    """Check debug settings"""
    
    print(f"\n⚙️  Debug Settings...")
    print("=" * 50)
    
    from django.conf import settings
    
    print(f"DEBUG: {settings.DEBUG}")
    print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"INSTALLED_APPS: {len(settings.INSTALLED_APPS)} apps")
    
    # Check for admin app
    if 'django.contrib.admin' in settings.INSTALLED_APPS:
        print("✅ Admin app installed")
    else:
        print("❌ Admin app NOT installed")
    
    # Check middleware
    admin_middleware = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    ]
    
    print(f"\nMiddleware check:")
    for middleware in admin_middleware:
        if middleware in settings.MIDDLEWARE:
            print(f"✅ {middleware}")
        else:
            print(f"❌ {middleware} - MISSING")

if __name__ == "__main__":
    debug_admin_500()
    check_debug_settings()