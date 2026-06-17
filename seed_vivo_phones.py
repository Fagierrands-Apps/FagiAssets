import os
import django
import sys

sys.path.insert(0, '/home/fagitone/Documents/GitHub/FagiAssets/assetmanagement')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
django.setup()

from assets.models import Asset, AssetCategory, Manufacturer

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

# Add 4 Vivo Y04 phones
phones = [
    {
        'name': 'Vivo Y04',
        'model': 'Y04 8GB/256GB',
        'serial_number': 'VIVO-Y04-001',
        'specifications': '8GB RAM, 256GB Storage',
        'status': 'available',
        'condition': 'new'
    },
    {
        'name': 'Vivo Y04',
        'model': 'Y04 5GB/128GB',
        'serial_number': 'VIVO-Y04-002',
        'specifications': '5GB RAM, 128GB Storage',
        'status': 'available',
        'condition': 'new'
    },
    {
        'name': 'Vivo Y04',
        'model': 'Y04 5GB/128GB',
        'serial_number': 'VIVO-Y04-003',
        'specifications': '5GB RAM, 128GB Storage',
        'status': 'available',
        'condition': 'new'
    },
    {
        'name': 'Vivo Y04',
        'model': 'Y04 5GB/128GB',
        'serial_number': 'VIVO-Y04-004',
        'specifications': '5GB RAM, 128GB Storage',
        'status': 'available',
        'condition': 'new'
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
            'manufacturer': manufacturer,
            'specifications': phone_data['specifications'],
            'status': phone_data['status'],
            'condition': phone_data['condition']
        }
    )
    status = '✅ Created' if created else '⚠️  Already exists'
    print(f"{status}: {asset.name} {asset.model} (SN: {asset.serial_number})")

print(f"\n🎉 Done! Added 4 Vivo Y04 phones to database.")
