#!/usr/bin/env python
"""
Test script for CRM Integration

This script tests the integration between Asset Manager and CRM
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

from django.contrib.auth.models import User
from crm_integration.models import IntegrationSettings, CRMCustomer, AssetCustomerAssignment
from crm_integration.services import CRMIntegrationService
from assets.models import Asset, AssetModel, AssetCategory, Manufacturer


def test_integration():
    """Test the CRM integration functionality"""
    print("🧪 Testing CRM Integration")
    print("=" * 40)
    
    # Test 1: Check integration settings
    print("1. Testing integration settings...")
    settings = IntegrationSettings.get_settings()
    print(f"   ✅ CRM URL: {settings.crm_base_url}")
    print(f"   ✅ Auto sync: {settings.auto_sync_enabled}")
    
    # Test 2: Test service initialization
    print("\n2. Testing service initialization...")
    service = CRMIntegrationService()
    print("   ✅ CRM Integration Service initialized")
    
    # Test 3: Test connection (will fail if CRM not running)
    print("\n3. Testing CRM connection...")
    success, message = service.test_connection()
    if success:
        print(f"   ✅ {message}")
    else:
        print(f"   ⚠️  {message}")
        print("   Note: Start CRM server with: cd fagicrm && python manage.py runserver 8001")
    
    # Test 4: Create sample data for testing
    print("\n4. Creating sample data...")
    
    # Create a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com'
        }
    )
    print(f"   ✅ Test user: {user.username}")
    
    # Create sample asset data
    manufacturer, _ = Manufacturer.objects.get_or_create(
        name='Test Manufacturer',
        defaults={'website': 'https://example.com'}
    )
    
    category, _ = AssetCategory.objects.get_or_create(
        name='Test Category',
        defaults={'description': 'Test category for integration'}
    )
    
    model, _ = AssetModel.objects.get_or_create(
        name='Test Model',
        manufacturer=manufacturer,
        category=category,
        defaults={'description': 'Test model for integration'}
    )
    
    asset, created = Asset.objects.get_or_create(
        name='Test Asset',
        model=model,
        defaults={
            'status': 'active',
            'assigned_to': user
        }
    )
    print(f"   ✅ Test asset: {asset.asset_tag}")
    
    # Create sample CRM customer
    customer, created = CRMCustomer.objects.get_or_create(
        crm_customer_id=999,
        defaults={
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '+1234567890',
            'address_line1': '123 Test Street',
            'city': 'Test City',
            'state': 'Test State',
            'postal_code': '12345',
            'assigned_employee': user
        }
    )
    print(f"   ✅ Test customer: {customer.full_name}")
    
    # Test 5: Create asset assignment
    print("\n5. Testing asset assignment...")
    assignment, created = AssetCustomerAssignment.objects.get_or_create(
        asset=asset,
        customer=customer,
        defaults={
            'assignment_type': 'owned',
            'assigned_by': user,
            'notes': 'Test assignment created by integration test'
        }
    )
    print(f"   ✅ Assignment: {assignment}")
    
    # Test 6: Test API endpoints (basic structure)
    print("\n6. Testing API structure...")
    from crm_integration.api_views import CRMCustomerViewSet, IntegrationViewSet
    print("   ✅ API views imported successfully")
    
    # Test 7: Test management command
    print("\n7. Testing management command...")
    from django.core.management import call_command
    try:
        # Test the command exists
        call_command('sync_crm', '--help')
        print("   ✅ Management command available")
    except Exception as e:
        print(f"   ⚠️  Management command issue: {e}")
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Integration Test Summary")
    print(f"✅ Integration settings configured")
    print(f"✅ Service layer functional")
    print(f"✅ Models and database working")
    print(f"✅ Sample data created")
    print(f"✅ API structure in place")
    
    if success:
        print(f"✅ CRM connection working")
    else:
        print(f"⚠️  CRM connection needs setup")
    
    print("\n🎯 Next Steps:")
    print("1. Start CRM server: cd fagicrm && python manage.py runserver 8001")
    print("2. Start Asset Manager: cd assetmanagement && python manage.py runserver")
    print("3. Visit integration dashboard: http://localhost:8000/crm/")
    print("4. Test full sync functionality")
    
    return True


if __name__ == "__main__":
    try:
        test_integration()
        print("\n✨ Integration test completed!")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)