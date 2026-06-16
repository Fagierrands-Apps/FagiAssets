from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from assets.models import (
    Location, Department, Manufacturer, AssetCategory, 
    AssetModel, Asset, AssetHistory, MaintenanceRecord
)
from datetime import datetime, timedelta
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Populate database with sample data for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate sample data...'))
        
        # Create sample users
        self.create_users()
        
        # Create locations
        self.create_locations()
        
        # Create departments
        self.create_departments()
        
        # Create manufacturers
        self.create_manufacturers()
        
        # Create categories
        self.create_categories()
        
        # Create asset models
        self.create_asset_models()
        
        # Create assets
        self.create_assets()
        
        # Create maintenance records
        self.create_maintenance_records()
        
        # Create asset history
        self.create_asset_history()
        
        self.stdout.write(self.style.SUCCESS('Sample data populated successfully!'))

    def create_users(self):
        """Create sample users"""
        users_data = [
            {'username': 'john.doe', 'first_name': 'John', 'last_name': 'Doe', 'email': 'john.doe@company.com'},
            {'username': 'jane.smith', 'first_name': 'Jane', 'last_name': 'Smith', 'email': 'jane.smith@company.com'},
            {'username': 'bob.johnson', 'first_name': 'Bob', 'last_name': 'Johnson', 'email': 'bob.johnson@company.com'},
            {'username': 'alice.williams', 'first_name': 'Alice', 'last_name': 'Williams', 'email': 'alice.williams@company.com'},
            {'username': 'charlie.brown', 'first_name': 'Charlie', 'last_name': 'Brown', 'email': 'charlie.brown@company.com'},
        ]
        
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults=user_data
            )
            if created:
                self.stdout.write(f'Created user: {user.username}')

    def create_locations(self):
        """Create sample locations"""
        locations_data = [
            {'name': 'Office Building A', 'address': '123 Main St, City, State 12345', 'description': 'Main office building'},
            {'name': 'Office Building B', 'address': '456 Oak Ave, City, State 12345', 'description': 'Secondary office building'},
            {'name': 'Warehouse', 'address': '789 Industrial Blvd, City, State 12345', 'description': 'Storage and distribution center'},
            {'name': 'Data Center', 'address': '321 Tech Park, City, State 12345', 'description': 'Server and network equipment'},
            {'name': 'Remote Office', 'address': '654 Branch St, City, State 12345', 'description': 'Remote branch office'},
        ]
        
        for location_data in locations_data:
            location, created = Location.objects.get_or_create(
                name=location_data['name'],
                defaults=location_data
            )
            if created:
                self.stdout.write(f'Created location: {location.name}')

    def create_departments(self):
        """Create sample departments"""
        departments_data = [
            {'name': 'IT', 'description': 'Information Technology'},
            {'name': 'HR', 'description': 'Human Resources'},
            {'name': 'Finance', 'description': 'Finance and Accounting'},
            {'name': 'Sales', 'description': 'Sales and Marketing'},
            {'name': 'Operations', 'description': 'Operations and Logistics'},
        ]
        
        for dept_data in departments_data:
            department, created = Department.objects.get_or_create(
                name=dept_data['name'],
                defaults=dept_data
            )
            if created:
                self.stdout.write(f'Created department: {department.name}')

    def create_manufacturers(self):
        """Create sample manufacturers"""
        manufacturers_data = [
            {'name': 'Dell', 'website': 'https://www.dell.com', 'support_email': 'support@dell.com'},
            {'name': 'HP', 'website': 'https://www.hp.com', 'support_email': 'support@hp.com'},
            {'name': 'Lenovo', 'website': 'https://www.lenovo.com', 'support_email': 'support@lenovo.com'},
            {'name': 'Apple', 'website': 'https://www.apple.com', 'support_email': 'support@apple.com'},
            {'name': 'Microsoft', 'website': 'https://www.microsoft.com', 'support_email': 'support@microsoft.com'},
            {'name': 'Cisco', 'website': 'https://www.cisco.com', 'support_email': 'support@cisco.com'},
        ]
        
        for mfg_data in manufacturers_data:
            manufacturer, created = Manufacturer.objects.get_or_create(
                name=mfg_data['name'],
                defaults=mfg_data
            )
            if created:
                self.stdout.write(f'Created manufacturer: {manufacturer.name}')

    def create_categories(self):
        """Create sample asset categories"""
        categories_data = [
            {'name': 'Computer', 'description': 'Desktop computers and workstations'},
            {'name': 'Laptop', 'description': 'Portable computers and notebooks'},
            {'name': 'Printer', 'description': 'Printing devices and equipment'},
            {'name': 'Network', 'description': 'Network equipment and infrastructure'},
            {'name': 'Monitor', 'description': 'Display devices and screens'},
            {'name': 'Server', 'description': 'Server hardware and equipment'},
            {'name': 'Mobile', 'description': 'Mobile devices and tablets'},
        ]
        
        for cat_data in categories_data:
            category, created = AssetCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')

    def create_asset_models(self):
        """Create sample asset models"""
        models_data = [
            {'name': 'OptiPlex 7010', 'manufacturer': 'Dell', 'category': 'Computer', 'model_number': 'O7010'},
            {'name': 'ThinkPad X1 Carbon', 'manufacturer': 'Lenovo', 'category': 'Laptop', 'model_number': 'X1C'},
            {'name': 'MacBook Pro 13"', 'manufacturer': 'Apple', 'category': 'Laptop', 'model_number': 'MBP13'},
            {'name': 'LaserJet Pro M404dn', 'manufacturer': 'HP', 'category': 'Printer', 'model_number': 'M404dn'},
            {'name': 'Catalyst 2960-X', 'manufacturer': 'Cisco', 'category': 'Network', 'model_number': 'C2960X'},
            {'name': 'Surface Pro 8', 'manufacturer': 'Microsoft', 'category': 'Mobile', 'model_number': 'SP8'},
            {'name': 'UltraSharp 24"', 'manufacturer': 'Dell', 'category': 'Monitor', 'model_number': 'U2419H'},
            {'name': 'ProLiant DL380', 'manufacturer': 'HP', 'category': 'Server', 'model_number': 'DL380'},
        ]
        
        for model_data in models_data:
            manufacturer = Manufacturer.objects.get(name=model_data['manufacturer'])
            category = AssetCategory.objects.get(name=model_data['category'])
            
            asset_model, created = AssetModel.objects.get_or_create(
                name=model_data['name'],
                manufacturer=manufacturer,
                category=category,
                defaults={'model_number': model_data['model_number']}
            )
            if created:
                self.stdout.write(f'Created model: {asset_model.name}')

    def create_assets(self):
        """Create sample assets"""
        users = list(User.objects.all())
        locations = list(Location.objects.all())
        departments = list(Department.objects.all())
        models = list(AssetModel.objects.all())
        
        statuses = ['active', 'inactive', 'maintenance', 'retired']
        
        for i in range(50):  # Create 50 sample assets
            model = random.choice(models)
            
            # Create asset with random data
            asset = Asset.objects.create(
                name=f"{model.manufacturer.name} {model.name} #{i+1:03d}",
                model=model,
                status=random.choice(statuses),
                assigned_to=random.choice(users + [None]),
                location=random.choice(locations),
                department=random.choice(departments),
                purchase_date=datetime.now().date() - timedelta(days=random.randint(30, 1095)),
                purchase_cost=Decimal(str(random.randint(500, 5000))),
                warranty_expires=datetime.now().date() + timedelta(days=random.randint(30, 730)),
                ip_address=f"192.168.1.{random.randint(10, 250)}",
                mac_address=f"00:1B:44:11:{random.randint(10, 99):02d}:{random.randint(10, 99):02d}",
                hostname=f"PC{i+1:03d}",
                device_name=f"DESKTOP-{random.randint(1000, 9999)}",
                processor=f"Intel Core i{random.choice([3, 5, 7])}-{random.randint(8000, 12000)}",
                installed_ram=f"{random.choice([8, 16, 32])}.0 GB",
                notes=f"Sample asset #{i+1} for testing purposes"
            )
            
            if i % 10 == 0:
                self.stdout.write(f'Created {i+1} assets...')
        
        self.stdout.write(f'Created {Asset.objects.count()} total assets')

    def create_maintenance_records(self):
        """Create sample maintenance records"""
        assets = list(Asset.objects.all())
        users = list(User.objects.all())
        
        maintenance_types = ['preventive', 'corrective', 'emergency', 'upgrade']
        statuses = ['scheduled', 'in_progress', 'completed', 'cancelled']
        
        for i in range(20):  # Create 20 maintenance records
            asset = random.choice(assets)
            
            MaintenanceRecord.objects.create(
                asset=asset,
                maintenance_type=random.choice(maintenance_types),
                status=random.choice(statuses),
                title=f"Maintenance Task #{i+1}",
                description=f"Sample maintenance task for {asset.name}",
                scheduled_date=datetime.now() + timedelta(days=random.randint(-30, 60)),
                performed_by=random.choice(users),
                cost=Decimal(str(random.randint(50, 500))),
                notes=f"Sample maintenance record #{i+1}"
            )
        
        self.stdout.write(f'Created {MaintenanceRecord.objects.count()} maintenance records')

    def create_asset_history(self):
        """Create sample asset history"""
        assets = list(Asset.objects.all())
        users = list(User.objects.all())
        
        actions = ['created', 'updated', 'assigned', 'moved', 'status_changed']
        
        for i in range(100):  # Create 100 history entries
            asset = random.choice(assets)
            
            AssetHistory.objects.create(
                asset=asset,
                action=random.choice(actions),
                description=f"Sample history entry #{i+1} for {asset.name}",
                user=random.choice(users),
                timestamp=datetime.now() - timedelta(days=random.randint(0, 365))
            )
        
        self.stdout.write(f'Created {AssetHistory.objects.count()} history entries')