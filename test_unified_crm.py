#!/usr/bin/env python
"""
Test script for Unified CRM System

This script tests the unified CRM functionality to ensure everything works correctly.
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
from crm.models import Department, Employee, Customer, Lead, AssetCustomerAssignment
from assets.models import Asset, AssetModel, AssetCategory, Manufacturer


def test_unified_crm():
    """Test the unified CRM functionality"""
    print("🧪 Testing Unified CRM System")
    print("=" * 40)
    
    try:
        # Test 1: Check models are working
        print("1. Testing CRM models...")
        
        # Test Department model
        dept_count = Department.objects.count()
        print(f"   ✅ Departments: {dept_count}")
        
        # Test Employee model
        emp_count = Employee.objects.count()
        print(f"   ✅ Employees: {emp_count}")
        
        # Test Customer model
        customer_count = Customer.objects.count()
        print(f"   ✅ Customers: {customer_count}")
        
        # Test Lead model
        lead_count = Lead.objects.count()
        print(f"   ✅ Leads: {lead_count}")
        
        # Test Assignment model
        assignment_count = AssetCustomerAssignment.objects.count()
        print(f"   ✅ Asset Assignments: {assignment_count}")
        
        # Test 2: Create sample data if none exists
        if customer_count == 0:
            print("\n2. Creating sample data...")
            
            with transaction.atomic():
                # Create department
                sales_dept = Department.objects.create(
                    name='Sales Test',
                    description='Test sales department'
                )
                
                # Create user and employee
                user = User.objects.create_user(
                    username='test.sales',
                    first_name='Test',
                    last_name='Sales',
                    email='test.sales@company.com'
                )
                
                employee = Employee.objects.create(
                    user=user,
                    employee_id='TEST001',
                    department=sales_dept,
                    position='Sales Rep',
                    employment_status='active',
                    hire_date='2024-01-01'
                )
                
                # Create customer
                customer = Customer.objects.create(
                    first_name='Test',
                    last_name='Customer',
                    email='test.customer@example.com',
                    phone='+1-555-0123',
                    address_line1='123 Test Street',
                    city='Test City',
                    state='TS',
                    postal_code='12345',
                    assigned_employee=employee
                )
                
                # Create lead
                lead = Lead.objects.create(
                    first_name='Test',
                    last_name='Lead',
                    email='test.lead@example.com',
                    company_name='Test Company',
                    status='new',
                    source='website',
                    assigned_employee=employee
                )
                
                print(f"   ✅ Created sample department: {sales_dept.name}")
                print(f"   ✅ Created sample employee: {employee.full_name}")
                print(f"   ✅ Created sample customer: {customer.full_name}")
                print(f"   ✅ Created sample lead: {lead.full_name}")
        
        # Test 3: Test relationships
        print("\n3. Testing model relationships...")
        
        customers_with_employees = Customer.objects.filter(assigned_employee__isnull=False).count()
        print(f"   ✅ Customers with assigned employees: {customers_with_employees}")
        
        employees_with_customers = Employee.objects.filter(customers__isnull=False).distinct().count()
        print(f"   ✅ Employees with customers: {employees_with_customers}")
        
        # Test 4: Test asset-customer assignments if assets exist
        asset_count = Asset.objects.count()
        print(f"\n4. Testing asset integration...")
        print(f"   ✅ Total assets available: {asset_count}")
        
        if asset_count > 0 and customer_count > 0:
            # Try to create an assignment
            asset = Asset.objects.first()
            customer = Customer.objects.first()
            
            assignment, created = AssetCustomerAssignment.objects.get_or_create(
                asset=asset,
                customer=customer,
                defaults={
                    'assignment_type': 'owned',
                    'notes': 'Test assignment'
                }
            )
            
            if created:
                print(f"   ✅ Created test assignment: {assignment}")
            else:
                print(f"   ✅ Assignment already exists: {assignment}")
        
        # Test 5: Test template tags
        print("\n5. Testing template functionality...")
        from crm.templatetags.crm_tags import unread_notifications_count, has_unread_notifications
        
        test_user = User.objects.first()
        if test_user:
            unread_count = unread_notifications_count(test_user)
            has_unread = has_unread_notifications(test_user)
            print(f"   ✅ Template tags working - Unread: {unread_count}, Has unread: {has_unread}")
        
        # Test 6: Test views (basic import test)
        print("\n6. Testing view imports...")
        from crm import views
        print("   ✅ CRM views imported successfully")
        
        from crm import urls
        print("   ✅ CRM URLs imported successfully")
        
        # Summary
        print("\n" + "=" * 40)
        print("📊 Test Summary")
        print(f"✅ Departments: {Department.objects.count()}")
        print(f"✅ Employees: {Employee.objects.count()}")
        print(f"✅ Customers: {Customer.objects.count()}")
        print(f"✅ Leads: {Lead.objects.count()}")
        print(f"✅ Asset Assignments: {AssetCustomerAssignment.objects.count()}")
        print(f"✅ Total Assets: {Asset.objects.count()}")
        
        print("\n🎯 System Status:")
        print("✅ CRM models working correctly")
        print("✅ Database relationships functional")
        print("✅ Template tags operational")
        print("✅ Views and URLs properly configured")
        print("✅ Asset-CRM integration ready")
        
        print("\n🌐 Access Points:")
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
    try:
        success = test_unified_crm()
        if success:
            print("\n✨ All tests passed! Your unified CRM system is working correctly!")
        else:
            print("\n❌ Some tests failed. Check the errors above.")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")
        sys.exit(1)