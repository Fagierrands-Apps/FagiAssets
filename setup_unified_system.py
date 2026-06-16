#!/usr/bin/env python
"""
Setup script for Unified Asset Management & CRM System

This script helps you set up the unified system with both asset management
and CRM functionality in one application.
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
from django.db import transaction
from crm.models import Department, Employee, Customer, Lead
from assets.models import Asset, AssetModel, AssetCategory, Manufacturer


def create_sample_data():
    """Create sample data for testing the unified system"""
    print("🎯 Creating sample data...")
    
    with transaction.atomic():
        # Create departments
        print("  Creating departments...")
        sales_dept, _ = Department.objects.get_or_create(
            name='Sales',
            defaults={'description': 'Sales and customer relations'}
        )
        
        it_dept, _ = Department.objects.get_or_create(
            name='IT',
            defaults={'description': 'Information Technology'}
        )
        
        # Create users and employees
        print("  Creating employees...")
        
        # Sales Manager
        sales_user, created = User.objects.get_or_create(
            username='john.sales',
            defaults={
                'first_name': 'John',
                'last_name': 'Smith',
                'email': 'john.smith@company.com',
                'is_staff': True
            }
        )
        
        sales_employee, _ = Employee.objects.get_or_create(
            user=sales_user,
            defaults={
                'employee_id': 'EMP001',
                'department': sales_dept,
                'position': 'Sales Manager',
                'phone': '+1-555-0101',
                'employment_status': 'active',
                'hire_date': '2023-01-15',
                'is_manager': True
            }
        )
        
        # IT Specialist
        it_user, created = User.objects.get_or_create(
            username='jane.tech',
            defaults={
                'first_name': 'Jane',
                'last_name': 'Doe',
                'email': 'jane.doe@company.com',
                'is_staff': True
            }
        )
        
        it_employee, _ = Employee.objects.get_or_create(
            user=it_user,
            defaults={
                'employee_id': 'EMP002',
                'department': it_dept,
                'position': 'IT Specialist',
                'phone': '+1-555-0102',
                'employment_status': 'active',
                'hire_date': '2023-02-01'
            }
        )
        
        # Create sample customers
        print("  Creating customers...")
        
        customer1, _ = Customer.objects.get_or_create(
            email='alice.johnson@techcorp.com',
            defaults={
                'first_name': 'Alice',
                'last_name': 'Johnson',
                'company_name': 'TechCorp Solutions',
                'customer_type': 'business',
                'phone': '+1-555-0201',
                'address_line1': '123 Business Ave',
                'city': 'New York',
                'state': 'NY',
                'postal_code': '10001',
                'assigned_employee': sales_employee,
                'status': 'active'
            }
        )
        
        customer2, _ = Customer.objects.get_or_create(
            email='bob.wilson@email.com',
            defaults={
                'first_name': 'Bob',
                'last_name': 'Wilson',
                'customer_type': 'individual',
                'phone': '+1-555-0202',
                'address_line1': '456 Home Street',
                'city': 'Los Angeles',
                'state': 'CA',
                'postal_code': '90001',
                'assigned_employee': sales_employee,
                'status': 'active'
            }
        )
        
        # Create sample leads
        print("  Creating leads...")
        
        lead1, _ = Lead.objects.get_or_create(
            email='sarah.brown@startup.com',
            defaults={
                'first_name': 'Sarah',
                'last_name': 'Brown',
                'company_name': 'Startup Inc',
                'title': 'CTO',
                'status': 'qualified',
                'source': 'website',
                'assigned_employee': sales_employee,
                'estimated_value': 50000,
                'notes': 'Interested in enterprise asset management solution'
            }
        )
        
        # Create sample assets (if not exist)
        print("  Creating sample assets...")
        
        # Create manufacturer
        manufacturer, _ = Manufacturer.objects.get_or_create(
            name='Dell Technologies',
            defaults={'website': 'https://dell.com'}
        )
        
        # Create category
        category, _ = AssetCategory.objects.get_or_create(
            name='Laptops',
            defaults={'description': 'Laptop computers'}
        )
        
        # Create model
        model, _ = AssetModel.objects.get_or_create(
            name='Latitude 5520',
            manufacturer=manufacturer,
            category=category,
            defaults={'description': 'Business laptop'}
        )
        
        # Create assets
        for i in range(1, 4):
            asset, created = Asset.objects.get_or_create(
                name=f'Dell Laptop {i}',
                model=model,
                defaults={
                    'status': 'active',
                    'serial_number': f'DL{i:03d}2024',
                    'purchase_date': '2024-01-15',
                    'purchase_cost': 1200.00,
                    'assigned_to': it_user if i == 1 else None
                }
            )
            if created:
                print(f"    Created asset: {asset.asset_tag}")
        
        print("✅ Sample data created successfully!")
        
        return {
            'departments': [sales_dept, it_dept],
            'employees': [sales_employee, it_employee],
            'customers': [customer1, customer2],
            'leads': [lead1],
        }


def setup_unified_system():
    """Setup the unified asset management and CRM system"""
    print("🏢 Unified Asset Management & CRM System Setup")
    print("=" * 60)
    
    # Check if we have a superuser
    if not User.objects.filter(is_superuser=True).exists():
        print("⚠️  No superuser found. Creating admin user...")
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@company.com',
            password='admin123',
            first_name='System',
            last_name='Administrator'
        )
        print(f"✅ Created admin user: {admin_user.username} (password: admin123)")
    else:
        print("✅ Superuser already exists")
    
    # Create sample data
    create_sample = input("\nCreate sample data for testing? (y/N): ").strip().lower()
    if create_sample in ['y', 'yes']:
        sample_data = create_sample_data()
        
        print("\n📊 Sample Data Summary:")
        print(f"  • Departments: {len(sample_data['departments'])}")
        print(f"  • Employees: {len(sample_data['employees'])}")
        print(f"  • Customers: {len(sample_data['customers'])}")
        print(f"  • Leads: {len(sample_data['leads'])}")
        print(f"  • Assets: {Asset.objects.count()}")
    
    print("\n" + "=" * 60)
    print("🚀 Setup Complete!")
    print("\nYour unified system is ready!")
    print("\n📍 Access Points:")
    print("  • Main Dashboard: http://localhost:8000/")
    print("  • Asset Management: http://localhost:8000/assets/")
    print("  • CRM Dashboard: http://localhost:8000/crm/")
    print("  • Admin Interface: http://localhost:8000/admin/")
    
    print("\n🔑 Features Available:")
    print("  ✅ Asset Management")
    print("  ✅ Customer Relationship Management")
    print("  ✅ Employee Management")
    print("  ✅ Lead Tracking")
    print("  ✅ Asset-Customer Assignments")
    print("  ✅ Unified User Interface")
    print("  ✅ Integrated Notifications")
    
    print("\n🎯 Next Steps:")
    print("1. Start the server: python manage.py runserver")
    print("2. Login with your admin credentials")
    print("3. Explore the CRM features at /crm/")
    print("4. Create asset-customer assignments")
    print("5. Manage leads and convert them to customers")
    
    return True


if __name__ == "__main__":
    try:
        setup_unified_system()
        print("\n✨ Setup completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)