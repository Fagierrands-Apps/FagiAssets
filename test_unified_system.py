#!/usr/bin/env python3
"""
Test script to verify the unified system is working properly
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_root = Path(__file__).parent / 'assetmanagement'
sys.path.insert(0, str(project_root))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
django.setup()

def test_unified_system():
    """Test the unified system components"""
    print("🔍 Testing Unified Business Management System...")
    print("=" * 60)
    
    # Test 1: Check if templates exist
    print("\n📁 Checking Template Files:")
    template_files = [
        'assetmanagement/templates/base.html',
        'assetmanagement/templates/crm/base.html',
        'assetmanagement/static/css/unified-theme.css'
    ]
    
    for template_file in template_files:
        if os.path.exists(template_file):
            print(f"✅ {template_file}")
        else:
            print(f"❌ {template_file} - MISSING")
    
    # Test 2: Check Django apps
    print("\n🔧 Checking Django Apps:")
    try:
        from django.apps import apps
        app_configs = apps.get_app_configs()
        app_names = [app.name for app in app_configs]
        
        required_apps = ['assets', 'users', 'crm', 'admin_dashboard', 'crm_integration']
        for app in required_apps:
            if app in app_names:
                print(f"✅ {app} app")
            else:
                print(f"❌ {app} app - NOT FOUND")
                
    except Exception as e:
        print(f"❌ Error checking apps: {e}")
    
    # Test 3: Check URL patterns
    print("\n🌐 Checking URL Patterns:")
    try:
        from django.urls import reverse
        
        test_urls = [
            ('dashboard', 'Main Dashboard'),
            ('asset_list', 'Asset List'),
            ('crm:dashboard', 'CRM Dashboard'),
            ('admin_dashboard:dashboard', 'Admin Dashboard')
        ]
        
        for url_name, description in test_urls:
            try:
                url = reverse(url_name)
                print(f"✅ {description}: {url}")
            except Exception as e:
                print(f"❌ {description}: {e}")
                
    except Exception as e:
        print(f"❌ Error checking URLs: {e}")
    
    # Test 4: Check static files
    print("\n🎨 Checking Static Files:")
    static_files = [
        'assetmanagement/static/css/unified-theme.css'
    ]
    
    for static_file in static_files:
        if os.path.exists(static_file):
            file_size = os.path.getsize(static_file)
            print(f"✅ {static_file} ({file_size} bytes)")
        else:
            print(f"❌ {static_file} - MISSING")
    
    # Test 5: Database connectivity
    print("\n💾 Checking Database:")
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✅ Database connection successful")
            
        # Check if tables exist
        from django.db import connection
        table_names = connection.introspection.table_names()
        
        required_tables = ['assets_asset', 'crm_customer', 'crm_lead', 'auth_user']
        for table in required_tables:
            if table in table_names:
                print(f"✅ Table: {table}")
            else:
                print(f"❌ Table: {table} - NOT FOUND")
                
    except Exception as e:
        print(f"❌ Database error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Unified System Test Complete!")
    print("\n💡 Next Steps:")
    print("1. Start the server: python manage.py runserver")
    print("2. Visit: http://localhost:8000/")
    print("3. Test navigation between Asset Management and CRM")
    print("4. Verify consistent styling across all pages")

if __name__ == "__main__":
    test_unified_system()