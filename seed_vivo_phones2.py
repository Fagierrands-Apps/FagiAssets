import os
import django
import sys

sys.path.insert(0, '/home/fagitone/Documents/GitHub/FagiAssets/assetmanagement')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
django.setup()

from assets.models import Asset, AssetCategory, Manufacturer, AssetModel

# Create or get Vivo manufacturer
manufacturer, created = Manufacturer.objects.get_or_create(
    name='Vivo',
    defaults={'website': 'https://www.vivo.com'}
)
print(f"✅ Manufacturer: {manufacturer.name} ({'created' if created else 'exists'})")

# Create or get Phone category
category, created = AssetCategory.objects.get_or_create(
    name='Phone',
    defaults={'description': 'Mobile phones and smartphones'}
)
print(f"✅ Category: {category.name} ({'created' if created else 'exists'})")

# Create AssetModels for different variants
model_8gb, created = AssetModel.objects.get_or_create(
    name='Y04 8GB/256GB',
    manufacturer=manufacturer,
    category=category,
    defaults={'model_number': 'Y04-8256', 'description': '8GB RAM, 256GB Storage'}
)
print(f"✅ Model: {model_8gb} ({'created' if created else 'exists'})")

model_5gb, created = AssetModel.objects.get_or_create(
    name='Y04 5GB/128GB',
    manufacturer=manufacturer,
    category=category,
    defaults={'model_number': 'Y04-5128', 'description': '5GB RAM, 128GB Storage'}
)
print(f"✅ Model: {model_5gb} ({'created' if created else 'exists'})")

# Add 4 Vivo Y04 phones
phones = [
    {
        'name': 'Vivo Y04 (8GB/256GB)',
        'model': model_8gb,
        'serial_number': 'VIVO-Y04-001',
        'status': 'active'
    },
    {
        'name': 'Vivo Y04 (5GB/128GB)',
        'model': model_5gb,
        'serial_number': 'VIVO-Y04-002',
        'status': 'active'
    },
    {
        'name': 'Vivo Y04 (5GB/128GB)',
        'model': model_5gb,
        'serial_number': 'VIVO-Y04-003',
        'status': 'active'
    },
    {
        'name': 'Vivo Y04 (5GB/128GB)',
        'model': model_5gb,
        'serial_number': 'VIVO-Y04-004',
        'status': 'active'
    }
]

print("\n📱 Adding Vivo Y04 phones...\n")
for phone_data in phones:
    asset, created = Asset.objects.get_or_create(
        serial_number=phone_data['serial_number'],
        defaults={
            'name': phone_data['name'],
            'model': phone_data['model'],
            'category': category,
            'status': phone_data['status']
        }
    )
    status = '✅ Created' if created else '⚠️  Already exists'
    print(f"{status}: {asset.name} (SN: {asset.serial_number}, Tag: {asset.asset_tag})")

print(f"\n🎉 Done! Added 4 Vivo Y04 phones to database.")
