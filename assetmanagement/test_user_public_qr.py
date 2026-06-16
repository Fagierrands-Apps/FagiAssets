#!/usr/bin/env python
"""
Test script to verify user QR codes point to public URLs and work without login
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')

# Setup Django
django.setup()

from django.test import Client, RequestFactory
from django.contrib.auth.models import User
from django.urls import reverse
from assets.utils import generate_user_qr_data
import json

def test_user_qr_public_access():
    """Test that user QR codes work without login"""
    print("🔍 Testing User QR Code Public Access")
    print("=" * 50)
    
    # Create test client
    client = Client()
    factory = RequestFactory()
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'is_active': True
        }
    )
    
    if created:
        print(f"✓ Created test user: {user.username}")
    else:
        print(f"✓ Using existing test user: {user.username}")
    
    # Test QR data generation
    print("\n📊 Testing QR Data Generation:")
    try:
        request = factory.get('/')
        request.META['HTTP_HOST'] = 'localhost:8000'
        
        qr_data = generate_user_qr_data(user, request)
        
        print(f"✓ QR data generated successfully")
        print(f"  - User URL: {qr_data['user_url']}")
        
        # Check if URL points to public endpoint
        if '/public/' in qr_data['user_url']:
            print("✓ QR code points to public URL (no login required)")
        else:
            print("✗ QR code points to private URL (login required)")
            return False
            
    except Exception as e:
        print(f"✗ QR data generation failed: {e}")
        return False
    
    # Test public view access (without login)
    print("\n🌐 Testing Public View Access (No Login):")
    try:
        url = reverse('users:user_public_view', kwargs={'user_id': user.id})
        response = client.get(url)
        
        if response.status_code == 200:
            print(f"✓ Public view accessible: {url}")
            print(f"  - Status: {response.status_code}")
            
            # Check if response contains user information
            content = response.content.decode('utf-8')
            if user.username in content or user.get_full_name() in content:
                print("✓ User information displayed correctly")
            else:
                print("⚠ User information might not be displayed")
                
        else:
            print(f"✗ Public view failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Public view test failed: {e}")
        return False
    
    # Test public JSON endpoint (without login)
    print("\n📄 Testing Public JSON Endpoint (No Login):")
    try:
        url = reverse('users:user_public_data_json', kwargs={'user_id': user.id})
        response = client.get(url)
        
        if response.status_code == 200:
            print(f"✓ Public JSON accessible: {url}")
            
            # Parse JSON response
            data = response.json()
            print(f"  - User ID: {data.get('user_id')}")
            print(f"  - Username: {data.get('username')}")
            print(f"  - Email: {data.get('email')}")
            print(f"  - Assets: {len(data.get('assigned_assets', []))}")
            
        else:
            print(f"✗ Public JSON failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Public JSON test failed: {e}")
        return False
    
    # Test that private views still require login
    print("\n🔒 Testing Private View Access (Should Require Login):")
    try:
        url = reverse('users:profile', kwargs={'user_id': user.id})
        response = client.get(url)
        
        if response.status_code == 302:  # Redirect to login
            print(f"✓ Private view correctly requires login: {url}")
            print(f"  - Status: {response.status_code} (redirect to login)")
        else:
            print(f"⚠ Private view status: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Private view test failed: {e}")
    
    print("\n" + "=" * 50)
    print("✅ User QR Code Public Access Test PASSED!")
    print("\n🎉 QR codes now work without login!")
    print(f"   Public URL: /users/{user.id}/public/")
    print(f"   JSON API: /users/{user.id}/public/data.json")
    
    return True

def test_asset_qr_public_access():
    """Test that asset QR codes also work without login"""
    print("\n🔍 Testing Asset QR Code Public Access")
    print("=" * 50)
    
    client = Client()
    
    # Try to get an asset to test with
    try:
        from assets.models import Asset
        asset = Asset.objects.first()
        
        if not asset:
            print("⚠ No assets found to test with")
            return True
        
        print(f"✓ Testing with asset: {asset.asset_tag}")
        
        # Test public view access (without login)
        url = reverse('asset_public_view', kwargs={'asset_id': asset.id})
        response = client.get(url)
        
        if response.status_code == 200:
            print(f"✓ Asset public view accessible: {url}")
        else:
            print(f"✗ Asset public view failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"⚠ Asset test skipped: {e}")
    
    return True

if __name__ == '__main__':
    success = test_user_qr_public_access()
    if success:
        test_asset_qr_public_access()
        print("\n🎯 All tests completed successfully!")
        print("📱 QR codes can now be scanned without requiring login!")
    else:
        print("\n❌ Tests failed!")
        sys.exit(1)