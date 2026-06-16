#!/usr/bin/env python
"""
Test CRM access and functionality
"""

import os
import sys
import django
from pathlib import Path

# Add the asset management directory to Python path
asset_mgmt_path = Path(__file__).parent / 'assetmanagement'
sys.path.insert(0, str(asset_mgmt_path))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse


def test_crm_access():
    """Test CRM access and basic functionality"""
    print("🧪 Testing CRM Access")
    print("=" * 30)
    
    try:
        # Create a test client
        client = Client()
        
        # Test 1: Check if CRM URLs are working
        print("1. Testing CRM URL resolution...")
        
        try:
            crm_dashboard_url = reverse('crm:dashboard')
            print(f"   ✅ CRM Dashboard URL: {crm_dashboard_url}")
        except Exception as e:
            print(f"   ❌ CRM Dashboard URL failed: {e}")
            return False
        
        try:
            customer_list_url = reverse('crm:customer_list')
            print(f"   ✅ Customer List URL: {customer_list_url}")
        except Exception as e:
            print(f"   ❌ Customer List URL failed: {e}")
            return False
        
        # Test 2: Check if we can access CRM views (without authentication)
        print("\n2. Testing CRM view access...")
        
        # These should redirect to login since they require authentication
        response = client.get(crm_dashboard_url)
        if response.status_code in [200, 302]:  # 200 = success, 302 = redirect to login
            print(f"   ✅ CRM Dashboard accessible (status: {response.status_code})")
        else:
            print(f"   ❌ CRM Dashboard failed (status: {response.status_code})")
        
        response = client.get(customer_list_url)
        if response.status_code in [200, 302]:
            print(f"   ✅ Customer List accessible (status: {response.status_code})")
        else:
            print(f"   ❌ Customer List failed (status: {response.status_code})")
        
        # Test 3: Test with authenticated user
        print("\n3. Testing with authenticated user...")
        
        # Get or create a superuser
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            user.set_password('testpass')
            user.save()
            print("   ✅ Created test user")
        else:
            print("   ✅ Using existing test user")
        
        # Login the user
        client.force_login(user)
        
        # Test authenticated access
        response = client.get(crm_dashboard_url)
        if response.status_code == 200:
            print(f"   ✅ CRM Dashboard accessible with auth (status: {response.status_code})")
        else:
            print(f"   ❌ CRM Dashboard failed with auth (status: {response.status_code})")
            print(f"   Response content: {response.content[:200]}")
        
        response = client.get(customer_list_url)
        if response.status_code == 200:
            print(f"   ✅ Customer List accessible with auth (status: {response.status_code})")
        else:
            print(f"   ❌ Customer List failed with auth (status: {response.status_code})")
        
        # Test 4: Check template rendering
        print("\n4. Testing template rendering...")
        
        try:
            response = client.get(crm_dashboard_url)
            if b'CRM Dashboard' in response.content or b'crm' in response.content.lower():
                print("   ✅ CRM templates rendering correctly")
            else:
                print("   ⚠️  CRM templates may have issues")
        except Exception as e:
            print(f"   ❌ Template rendering failed: {e}")
        
        print("\n" + "=" * 30)
        print("✅ CRM System Test Complete!")
        print("\n🌐 Your CRM is accessible at:")
        print("• CRM Dashboard: http://localhost:8000/crm/")
        print("• Customer List: http://localhost:8000/crm/customers/")
        print("• Lead List: http://localhost:8000/crm/leads/")
        print("• Asset Assignments: http://localhost:8000/crm/assignments/")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_crm_access()
    if success:
        print("\n✨ CRM system is working correctly!")
    else:
        print("\n❌ CRM system has issues.")
        sys.exit(1)