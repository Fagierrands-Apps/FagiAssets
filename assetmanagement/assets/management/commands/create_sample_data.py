from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from assets.models import (
    Location, Department, Manufacturer, AssetCategory, AssetModel, Asset
)
from discovery.models import NetworkRange
from datetime import date, datetime
import random


class Command(BaseCommand):
    help = 'Create sample data for the asset management system'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create locations
        locations = [
            {'name': 'Main Office', 'address': '123 Business St, City, State 12345'},
            {'name': 'Data Center', 'address': '456 Server Ave, City, State 12345'},
            {'name': 'Branch Office', 'address': '789 Remote Rd, City, State 12345'},
            {'name': 'Warehouse', 'address': '321 Storage Blvd, City, State 12345'},
        ]
        
        for loc_data in locations:
            location, created = Location.objects.get_or_create(
                name=loc_data['name'],
                defaults={'address': loc_data['address']}
            )
            if created:
                self.stdout.write(f'Created location: {location.name}')

        # Create departments
        departments = [
            {'name': 'IT Department', 'description': 'Information Technology'},
            {'name': 'Finance', 'description': 'Financial Operations'},
            {'name': 'HR', 'description': 'Human Resources'},
            {'name': 'Operations', 'description': 'Daily Operations'},
            {'name': 'Marketing', 'description': 'Marketing and Sales'},
        ]
        
        for dept_data in departments:
            department, created = Department.objects.get_or_create(
                name=dept_data['name'],
                defaults={'description': dept_data['description']}
            )
            if created:
                self.stdout.write(f'Created department: {department.name}')

        # Create manufacturers
        manufacturers = [
            {'name': 'Dell', 'website': 'https://www.dell.com'},
            {'name': 'HP', 'website': 'https://www.hp.com'},
            {'name': 'Lenovo', 'website': 'https://www.lenovo.com'},
            {'name': 'Apple', 'website': 'https://www.apple.com'},
            {'name': 'Cisco', 'website': 'https://www.cisco.com'},
            {'name': 'Microsoft', 'website': 'https://www.microsoft.com'},
        ]
        
        for mfg_data in manufacturers:
            manufacturer, created = Manufacturer.objects.get_or_create(
                name=mfg_data['name'],
                defaults={'website': mfg_data['website']}
            )
            if created:
                self.stdout.write(f'Created manufacturer: {manufacturer.name}')

        # Create asset categories
        categories = [
            {'name': 'Desktop Computer', 'description': 'Desktop workstations'},
            {'name': 'Laptop', 'description': 'Portable computers'},
            {'name': 'Server', 'description': 'Server hardware'},
            {'name': 'Network Equipment', 'description': 'Switches, routers, etc.'},
            {'name': 'Printer', 'description': 'Printing devices'},
            {'name': 'Monitor', 'description': 'Display devices'},
            {'name': 'Mobile Device', 'description': 'Phones and tablets'},
        ]
        
        for cat_data in categories:
            category, created = AssetCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Create asset models
        models_data = [
            {'name': 'OptiPlex 7090', 'manufacturer': 'Dell', 'category': 'Desktop Computer'},
            {'name': 'Latitude 5520', 'manufacturer': 'Dell', 'category': 'Laptop'},
            {'name': 'PowerEdge R740', 'manufacturer': 'Dell', 'category': 'Server'},
            {'name': 'EliteBook 850', 'manufacturer': 'HP', 'category': 'Laptop'},
            {'name': 'ProDesk 600', 'manufacturer': 'HP', 'category': 'Desktop Computer'},
            {'name': 'ThinkPad X1 Carbon', 'manufacturer': 'Lenovo', 'category': 'Laptop'},
            {'name': 'MacBook Pro', 'manufacturer': 'Apple', 'category': 'Laptop'},
            {'name': 'iMac', 'manufacturer': 'Apple', 'category': 'Desktop Computer'},
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
                self.stdout.write(f'Created model: {asset_model}')

        # Create some users for assignment
        users_data = [
            {'username': 'john.doe', 'first_name': 'John', 'last_name': 'Doe', 'email': 'john.doe@company.com'},
            {'username': 'jane.smith', 'first_name': 'Jane', 'last_name': 'Smith', 'email': 'jane.smith@company.com'},
            {'username': 'bob.johnson', 'first_name': 'Bob', 'last_name': 'Johnson', 'email': 'bob.johnson@company.com'},
            {'username': 'alice.brown', 'first_name': 'Alice', 'last_name': 'Brown', 'email': 'alice.brown@company.com'},
        ]
        
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'email': user_data['email'],
                    'is_active': True,
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'Created user: {user.get_full_name()}')

        # Create sample assets
        locations_list = list(Location.objects.all())
        departments_list = list(Department.objects.all())
        models_list = list(AssetModel.objects.all())
        users_list = list(User.objects.filter(is_superuser=False))
        
        statuses = ['active', 'inactive', 'maintenance']
        
        for i in range(1, 51):  # Create 50 assets
            asset_tag = f'AST-{i:04d}'
            model = random.choice(models_list)
            
            asset_data = {
                'asset_tag': asset_tag,
                'name': f'{model.manufacturer.name} {model.name} #{i}',
                'model': model,
                'serial_number': f'SN{random.randint(100000, 999999)}',
                'status': random.choice(statuses),
                'location': random.choice(locations_list),
                'department': random.choice(departments_list),
                'purchase_date': date(2023, random.randint(1, 12), random.randint(1, 28)),
                'purchase_cost': random.randint(500, 5000),
            }
            
            # Randomly assign some assets to users
            if random.choice([True, False]) and users_list:
                asset_data['assigned_to'] = random.choice(users_list)
            
            # Add IP addresses for network equipment and computers
            if model.category.name in ['Desktop Computer', 'Laptop', 'Server', 'Network Equipment']:
                asset_data['ip_address'] = f'192.168.1.{random.randint(10, 250)}'
                asset_data['hostname'] = f'{model.name.lower().replace(" ", "-")}-{i:02d}'
            
            asset, created = Asset.objects.get_or_create(
                asset_tag=asset_tag,
                defaults=asset_data
            )
            
            if created:
                self.stdout.write(f'Created asset: {asset.asset_tag}')

        # Create network ranges for discovery
        network_ranges = [
            {'name': 'Main Office Network', 'network': '192.168.1.0/24', 'description': 'Primary office network'},
            {'name': 'Server Network', 'network': '10.0.1.0/24', 'description': 'Server subnet'},
            {'name': 'Guest Network', 'network': '192.168.100.0/24', 'description': 'Guest WiFi network'},
        ]
        
        for range_data in network_ranges:
            network_range, created = NetworkRange.objects.get_or_create(
                name=range_data['name'],
                defaults={
                    'network': range_data['network'],
                    'description': range_data['description'],
                    'is_active': True,
                    'scan_frequency': 3600,
                }
            )
            if created:
                self.stdout.write(f'Created network range: {network_range.name}')

        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )