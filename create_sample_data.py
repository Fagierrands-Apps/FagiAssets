#!/usr/bin/env python
"""
Create sample data for production
Since the models have changed, we'll create sample data that matches the new structure
"""

import os
import sys
import django
from django.db import transaction

def create_sample_data():
    """Create sample data for the new model structure"""
    print("=" * 70)
    print("CREATING SAMPLE DATA FOR NEW MODEL STRUCTURE")
    print("=" * 70)
    
    # Setup Django with production settings
    os.environ['DJANGO_SETTINGS_MODULE'] = 'assetmanager.settings'
    os.environ['VERCEL'] = '1'
    os.environ['DATABASE_URL'] = 'postgresql://postgres.dxesmzogjpxswxhsomgf:OnFRtf0SmpHwgNaQ@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres'
    
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'assetmanagement'))
    django.setup()
    
    from django.contrib.auth.models import User
    from assets.models import Location, Department, Manufacturer, AssetCategory, AssetModel, Asset
    from users.models import UserProfile
    
    try:
        with transaction.atomic():
            print("Step 1: Creating basic lookup data...")
            
            # Create locations
            locations = [
                {'name': 'Main Office', 'address': '123 Main St', 'description': 'Main office building'},
                {'name': 'Branch Office', 'address': '456 Branch Ave', 'description': 'Branch office'},
                {'name': 'Warehouse', 'address': '789 Storage Rd', 'description': 'Main warehouse'},
                {'name': 'Remote', 'address': '', 'description': 'Remote/Home office'},
            ]
            
            for loc_data in locations:
                location, created = Location.objects.get_or_create(
                    name=loc_data['name'],
                    defaults={
                        'address': loc_data['address'],
                        'description': loc_data['description']
                    }
                )
                if created:
                    print(f"  ✓ Created location: {location.name}")
            
            # Create departments
            departments = [
                {'name': 'IT', 'description': 'Information Technology'},
                {'name': 'HR', 'description': 'Human Resources'},
                {'name': 'Finance', 'description': 'Finance and Accounting'},
                {'name': 'Operations', 'description': 'Operations and Management'},
                {'name': 'Sales', 'description': 'Sales and Marketing'},
            ]
            
            for dept_data in departments:
                department, created = Department.objects.get_or_create(
                    name=dept_data['name'],
                    defaults={'description': dept_data['description']}
                )
                if created:
                    print(f"  ✓ Created department: {department.name}")
            
            # Create manufacturers
            manufacturers = [
                {'name': 'Dell', 'website': 'https://www.dell.com'},
                {'name': 'HP', 'website': 'https://www.hp.com'},
                {'name': 'Lenovo', 'website': 'https://www.lenovo.com'},
                {'name': 'Apple', 'website': 'https://www.apple.com'},
                {'name': 'Microsoft', 'website': 'https://www.microsoft.com'},
                {'name': 'Cisco', 'website': 'https://www.cisco.com'},
            ]
            
            for mfg_data in manufacturers:
                manufacturer, created = Manufacturer.objects.get_or_create(
                    name=mfg_data['name'],
                    defaults={'website': mfg_data['website']}
                )
                if created:
                    print(f"  ✓ Created manufacturer: {manufacturer.name}")
            
            # Create asset categories
            categories = [
                {'name': 'Computer', 'description': 'Desktop and laptop computers'},
                {'name': 'Mobile Device', 'description': 'Smartphones and tablets'},
                {'name': 'Network Equipment', 'description': 'Routers, switches, and networking gear'},
                {'name': 'Printer', 'description': 'Printers and printing equipment'},
                {'name': 'Monitor', 'description': 'Computer monitors and displays'},
                {'name': 'Server', 'description': 'Server hardware'},
            ]
            
            for cat_data in categories:
                category, created = AssetCategory.objects.get_or_create(
                    name=cat_data['name'],
                    defaults={'description': cat_data['description']}
                )
                if created:
                    print(f"  ✓ Created category: {category.name}")
            
            print("\nStep 2: Creating asset models...")
            
            # Create some asset models
            models_data = [
                {'name': 'OptiPlex 7090', 'manufacturer': 'Dell', 'category': 'Computer'},
                {'name': 'EliteBook 840', 'manufacturer': 'HP', 'category': 'Computer'},
                {'name': 'ThinkPad T14', 'manufacturer': 'Lenovo', 'category': 'Computer'},
                {'name': 'MacBook Pro 14"', 'manufacturer': 'Apple', 'category': 'Computer'},
                {'name': 'iPhone 13', 'manufacturer': 'Apple', 'category': 'Mobile Device'},
                {'name': 'Catalyst 2960', 'manufacturer': 'Cisco', 'category': 'Network Equipment'},
            ]
            
            for model_data in models_data:
                manufacturer = Manufacturer.objects.get(name=model_data['manufacturer'])
                category = AssetCategory.objects.get(name=model_data['category'])
                
                asset_model, created = AssetModel.objects.get_or_create(
                    name=model_data['name'],
                    manufacturer=manufacturer,
                    defaults={'category': category}
                )
                if created:
                    print(f"  ✓ Created model: {manufacturer.name} {asset_model.name}")
            
            print("\nStep 3: Creating sample users...")
            
            # Create sample users from the migrated data
            users_data = [
                {'username': 'admin1', 'email': 'wayneryan@gmail.com', 'first_name': 'Wayne', 'last_name': 'Ryan'},
                {'username': 'WendyWhiteny', 'email': 'hr@fagitone.com', 'first_name': 'Wendy', 'last_name': 'Whiteny'},
                {'username': 'SharonNjeri', 'email': 'njeri.sharon@fagitone.com', 'first_name': 'Sharon', 'last_name': 'Njeri'},
                {'username': 'testuser', 'email': 'test@example.com', 'first_name': 'Test', 'last_name': 'User'},
            ]
            
            for user_data in users_data:
                user, created = User.objects.get_or_create(
                    username=user_data['username'],
                    defaults={
                        'email': user_data['email'],
                        'first_name': user_data['first_name'],
                        'last_name': user_data['last_name'],
                        'is_active': True
                    }
                )
                if created:
                    user.set_password('password123')  # Set a default password
                    user.save()
                    print(f"  ✓ Created user: {user.username}")
                
                # Update user profile
                if hasattr(user, 'profile'):
                    profile = user.profile
                    profile.department = Department.objects.get(name='IT')
                    profile.location = Location.objects.get(name='Main Office')
                    profile.job_title = 'Employee'
                    profile.save()
                    print(f"    ✓ Updated profile for: {user.username}")
            
            print("\nStep 4: Creating sample assets...")
            
            # Create some sample assets
            assets_data = [
                {'name': 'DESKTOP-001', 'model': 'OptiPlex 7090', 'manufacturer': 'Dell', 'assigned_to': 'admin1'},
                {'name': 'LAPTOP-001', 'model': 'EliteBook 840', 'manufacturer': 'HP', 'assigned_to': 'WendyWhiteny'},
                {'name': 'LAPTOP-002', 'model': 'ThinkPad T14', 'manufacturer': 'Lenovo', 'assigned_to': 'SharonNjeri'},
                {'name': 'PHONE-001', 'model': 'iPhone 13', 'manufacturer': 'Apple', 'assigned_to': 'testuser'},
            ]
            
            for asset_data in assets_data:
                try:
                    model = AssetModel.objects.get(
                        name=asset_data['model'],
                        manufacturer__name=asset_data['manufacturer']
                    )
                    
                    assigned_to = User.objects.get(username=asset_data['assigned_to'])
                    
                    asset, created = Asset.objects.get_or_create(
                        name=asset_data['name'],
                        defaults={
                            'model': model,
                            'assigned_to': assigned_to,
                            'department': Department.objects.get(name='IT'),
                            'location': Location.objects.get(name='Main Office'),
                            'status': 'active'
                        }
                    )
                    if created:
                        print(f"  ✓ Created asset: {asset.name} → {assigned_to.username}")
                except Exception as e:
                    print(f"  ! Error creating asset {asset_data['name']}: {e}")
            
            print("\nStep 5: Verifying created data...")
            
            # Verify counts
            counts = {
                'Users': User.objects.count(),
                'Assets': Asset.objects.count(),
                'Asset Models': AssetModel.objects.count(),
                'Asset Categories': AssetCategory.objects.count(),
                'Departments': Department.objects.count(),
                'Locations': Location.objects.count(),
                'Manufacturers': Manufacturer.objects.count(),
                'User Profiles': UserProfile.objects.count(),
            }
            
            print("\nProduction Database Contents:")
            for item, count in counts.items():
                print(f"  {item}: {count}")
            
            print("\nSample Assets:")
            for asset in Asset.objects.all():
                assigned = f" → {asset.assigned_to.username}" if asset.assigned_to else ""
                print(f"  - {asset.name} ({asset.model}){assigned}")
            
            print("\nSample Users:")
            for user in User.objects.all():
                dept = user.profile.department.name if hasattr(user, 'profile') and user.profile.department else "No dept"
                print(f"  - {user.username} ({user.email}) - {dept}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        return False

def print_final_summary():
    """Print final summary"""
    print("\n" + "=" * 70)
    print("SAMPLE DATA CREATION COMPLETED!")
    print("=" * 70)
    print("\n🎉 Your production database now has sample data!")
    print("\n📍 Access your data at:")
    print("   https://fagiassets.vercel.app/")
    print("\n🔑 Login credentials:")
    print("   Username: admin")
    print("   Password: FagiAssets2024!")
    print("\n👥 Sample users created (password: password123):")
    print("   - admin1 (wayneryan@gmail.com)")
    print("   - WendyWhiteny (hr@fagitone.com)")
    print("   - SharonNjeri (njeri.sharon@fagitone.com)")
    print("   - testuser (test@example.com)")
    print("\n📦 Sample assets created:")
    print("   - Desktop computers")
    print("   - Laptops")
    print("   - Mobile devices")
    print("   - All assigned to users")
    print("\n🏢 Organizational structure:")
    print("   - Multiple departments")
    print("   - Multiple locations")
    print("   - Asset manufacturers")
    print("   - Asset categories")
    print("\n📝 Next steps:")
    print("   1. Login and explore the system")
    print("   2. Generate QR codes for users")
    print("   3. Add more assets as needed")
    print("   4. Customize departments and locations")
    print("\n🌟 Your asset management system is fully operational!")

if __name__ == '__main__':
    success = create_sample_data()
    if success:
        print_final_summary()
    sys.exit(0 if success else 1)