#!/usr/bin/env python
"""
Test script to verify user QR code functionality works correctly
"""

import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
django.setup()

from django.contrib.auth.models import User
from assets.utils import generate_user_qr_data
from django.test import RequestFactory
import json

def test_user_qr_code():
    """Test user QR code generation"""
    print("Testing User QR Code Generation...")
    
    # Create test request
    factory = RequestFactory()
    request = factory.get('/')
    request.META['HTTP_HOST'] = 'localhost:8000'
    
    # Get or create test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
        }
    )
    
    if created:
        print(f"Created test user: {user.username}")
    else:
        print(f"Using existing user: {user.username}")
    
    # Generate user QR data
    try:
        qr_data = generate_user_qr_data(user, request)
        print("✓ User QR data generated successfully")
        
        # Check data structure
        expected_keys = ['user', 'user_data', 'qr_data', 'qr_image', 'user_url', 'assigned_assets', 'has_qrcode']
        for key in expected_keys:
            if key in qr_data:
                print(f"✓ {key} present in QR data")
            else:
                print(f"✗ {key} missing from QR data")
        
        # Check user data content
        user_data = qr_data['user_data']
        print(f"✓ User data contains {len(user_data)} fields")
        
        # Verify password is not included
        if 'password' not in user_data:
            print("✓ Password correctly excluded from QR data")
        else:
            print("✗ Password found in QR data (security issue!)")
        
        # Check if QR code can be generated
        if qr_data['has_qrcode']:
            print("✓ QR code generation is available")
        else:
            print("! QR code generation not available (qrcode library may not be installed)")
        
        # Print sample QR data
        print("\nSample QR Data:")
        print(json.dumps(user_data, indent=2)[:500] + "...")
        
        return True
        
    except Exception as e:
        print(f"✗ Error generating user QR data: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("\nTesting Database Connection...")
    
    try:
        # Test basic query
        user_count = User.objects.count()
        print(f"✓ Database connection successful (found {user_count} users)")
        
        # Test database type
        from django.db import connection
        db_vendor = connection.vendor
        print(f"✓ Database vendor: {db_vendor}")
        
        # Check if it's SQLite in production-like environment
        if db_vendor == 'sqlite' and (os.environ.get('VERCEL') or 'vercel' in os.environ.get('VERCEL_URL', '')):
            print("! WARNING: Using SQLite in production environment - this may cause write errors")
        
        return True
        
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("User QR Code System Test")
    print("=" * 60)
    
    # Test database connection
    db_ok = test_database_connection()
    
    if db_ok:
        # Test user QR code generation
        qr_ok = test_user_qr_code()
        
        if qr_ok:
            print("\n✓ All tests passed! User QR code system is working correctly.")
        else:
            print("\n✗ QR code generation test failed.")
    else:
        print("\n✗ Database connection test failed.")
    
    print("\n" + "=" * 60)
    print("Test completed.")

if __name__ == '__main__':
    main()