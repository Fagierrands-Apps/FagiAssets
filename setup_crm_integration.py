#!/usr/bin/env python
"""
Setup script for CRM Integration between Asset Manager and FagiCRM

This script helps you set up the seamless integration between your
Asset Management system and CRM system.
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
from crm_integration.models import IntegrationSettings, CRMCustomer
from crm_integration.services import CRMIntegrationService


def setup_integration():
    """Setup the CRM integration"""
    print("🔧 Setting up CRM Integration...")
    print("=" * 50)
    
    # 1. Create or update integration settings
    print("1. Configuring integration settings...")
    settings = IntegrationSettings.get_settings()
    
    # Default CRM URL (assuming CRM runs on port 8001)
    crm_url = input(f"Enter CRM URL (default: http://localhost:8001): ").strip()
    if not crm_url:
        crm_url = "http://localhost:8001"
    
    settings.crm_base_url = crm_url
    
    # API Key (optional for development)
    api_key = input("Enter CRM API key (optional for development): ").strip()
    if api_key:
        settings.crm_api_key = api_key
    else:
        settings.crm_api_key = "dev-api-key-12345"  # Default for development
    
    # Configure sync settings
    settings.auto_sync_enabled = True
    settings.sync_customers_to_assets = True
    settings.sync_assets_to_crm = True
    settings.sync_employees = True
    settings.sync_interval_minutes = 30
    
    settings.save()
    print(f"✅ Integration settings configured for {crm_url}")
    
    # 2. Test connection
    print("\n2. Testing connection to CRM...")
    service = CRMIntegrationService()
    success, message = service.test_connection()
    
    if success:
        print(f"✅ {message}")
    else:
        print(f"⚠️  {message}")
        print("   Note: Make sure your CRM system is running and accessible")
    
    # 3. Initial sync (if connection works)
    if success:
        print("\n3. Performing initial synchronization...")
        
        try:
            # Sync employees first
            print("   Syncing employees...")
            employee_log = service.sync_employee_data()
            print(f"   ✅ Employees: {employee_log.records_success}/{employee_log.records_processed} synced")
            
            # Sync customers
            print("   Syncing customers...")
            customer_log = service.sync_customers_from_crm()
            print(f"   ✅ Customers: {customer_log.records_success}/{customer_log.records_processed} synced")
            
            print("\n🎉 Initial synchronization completed!")
            
        except Exception as e:
            print(f"   ⚠️  Sync failed: {str(e)}")
            print("   You can run sync manually later from the web interface")
    
    # 4. Show next steps
    print("\n" + "=" * 50)
    print("🚀 Setup Complete!")
    print("\nNext steps:")
    print("1. Start your Asset Management server:")
    print("   cd assetmanagement")
    print("   python manage.py runserver")
    print("\n2. Start your CRM server (in another terminal):")
    print("   cd fagicrm")
    print("   python manage.py runserver 8001")
    print("\n3. Access the CRM Integration dashboard:")
    print("   http://localhost:8000/crm/")
    print("\n4. Test the integration:")
    print("   - View synced customers")
    print("   - Create asset assignments")
    print("   - Monitor sync logs")
    
    print("\n📚 Integration Features:")
    print("- Bidirectional customer/employee sync")
    print("- Asset ownership tracking")
    print("- Automatic sync on changes")
    print("- Web interface for management")
    print("- REST API for custom integrations")
    
    return True


def create_sample_data():
    """Create some sample data for testing"""
    print("\n🎯 Creating sample data for testing...")
    
    # This would create sample customers, assets, etc.
    # For now, we'll just show what could be done
    print("Sample data creation is available through Django admin or API")
    print("You can:")
    print("- Add customers in CRM")
    print("- Add assets in Asset Manager")
    print("- Create assignments between them")


if __name__ == "__main__":
    print("🏢 Asset Manager ↔️ CRM Integration Setup")
    print("=" * 50)
    
    try:
        setup_integration()
        
        # Ask if user wants sample data
        create_sample = input("\nCreate sample data for testing? (y/N): ").strip().lower()
        if create_sample in ['y', 'yes']:
            create_sample_data()
        
        print("\n✨ Setup completed successfully!")
        print("Check the integration dashboard at: http://localhost:8000/crm/")
        
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")
        print("\nPlease check:")
        print("1. Django is properly installed")
        print("2. Database migrations are applied")
        print("3. Asset management server can start")
        sys.exit(1)