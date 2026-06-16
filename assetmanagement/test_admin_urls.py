#!/usr/bin/env python
"""
Test Admin URL Configuration
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
django.setup()

from django.urls import reverse, resolve
from django.contrib import admin

def test_admin_urls():
    """Test admin URL configuration"""
    
    print("🧪 Testing Admin URL Configuration...")
    print("=" * 50)
    
    try:
        # Test admin URL resolution
        admin_url = reverse('admin:index')
        print(f"✅ Admin URL: {admin_url}")
        
        # Test URL resolution
        resolved = resolve('/admin/')
        print(f"✅ Admin URL resolves to: {resolved.func}")
        
        # Test admin site
        print(f"✅ Admin site: {admin.site}")
        
        # Check registered models
        print(f"✅ Registered models: {len(admin.site._registry)}")
        
        for model, admin_class in admin.site._registry.items():
            print(f"  - {model.__name__}: {admin_class.__class__.__name__}")
            
    except Exception as e:
        print(f"❌ Error with admin URLs: {e}")
        import traceback
        traceback.print_exc()

def test_admin_templates():
    """Test admin template configuration"""
    
    print("\n🧪 Testing Admin Templates...")
    print("=" * 50)
    
    from django.conf import settings
    
    print(f"Template directories: {settings.TEMPLATES[0]['DIRS']}")
    print(f"Template loaders: {settings.TEMPLATES[0]['OPTIONS']}")
    
    # Test if admin templates are accessible
    try:
        from django.template.loader import get_template
        
        templates_to_test = [
            'admin/base.html',
            'admin/index.html',
            'admin/login.html',
        ]
        
        for template_name in templates_to_test:
            try:
                template = get_template(template_name)
                print(f"✅ Template found: {template_name}")
            except Exception as e:
                print(f"❌ Template missing: {template_name} - {e}")
                
    except Exception as e:
        print(f"❌ Error testing templates: {e}")

if __name__ == "__main__":
    test_admin_urls()
    test_admin_templates()