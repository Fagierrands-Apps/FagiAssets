import os
import django
import sys

sys.path.insert(0, '/home/fagitone/Documents/GitHub/FagiAssets/assetmanagement')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
django.setup()

from assets.models import Asset, AssetCategory, Manufacturer, AssetModel
from crm.models import Employee, Department
from django.contrib.auth.models import User

print("=" * 60)
print("ADDING EQUIPMENT & EMPLOYEES")
print("=" * 60)

# ========== ADD EQUIPMENT ==========
print("\n📦 Adding Equipment...\n")

# Ring Light
lighting_cat, _ = AssetCategory.objects.get_or_create(
    name='Lighting',
    defaults={'description': 'Photography and video lighting equipment'}
)
print(f"✅ Category: {lighting_cat.name}")

generic_mfr, _ = Manufacturer.objects.get_or_create(
    name='Generic',
    defaults={'website': ''}
)

ringlight_model, _ = AssetModel.objects.get_or_create(
    name='Ring Light White',
    manufacturer=generic_mfr,
    category=lighting_cat,
    defaults={'model_number': 'RL-WHT', 'description': 'White Ring Light'}
)

ringlight, created = Asset.objects.get_or_create(
    serial_number='RING-LIGHT-001',
    defaults={
        'name': 'Ring Light (White)',
        'model': ringlight_model,
        'category': lighting_cat,
        'status': 'active'
    }
)
print(f"{'✅ Created' if created else '⚠️  Exists'}: {ringlight.name} (Tag: {ringlight.asset_tag})")

# Y88 Bluetooth Microphones
audio_cat, _ = AssetCategory.objects.get_or_create(
    name='Audio Equipment',
    defaults={'description': 'Microphones and audio devices'}
)
print(f"✅ Category: {audio_cat.name}")

y88_mfr, _ = Manufacturer.objects.get_or_create(
    name='Y88',
    defaults={'website': ''}
)

y88_model, _ = AssetModel.objects.get_or_create(
    name='Y88 Bluetooth Microphone',
    manufacturer=y88_mfr,
    category=audio_cat,
    defaults={'model_number': 'Y88-BT', 'description': 'Y88 Brand Bluetooth Microphone'}
)

for i in range(1, 3):  # 2 microphones
    mic, created = Asset.objects.get_or_create(
        serial_number=f'Y88-MIC-00{i}',
        defaults={
            'name': f'Y88 Bluetooth Microphone #{i}',
            'model': y88_model,
            'category': audio_cat,
            'status': 'active'
        }
    )
    print(f"{'✅ Created' if created else '⚠️  Exists'}: {mic.name} (Tag: {mic.asset_tag})")

# ========== ADD EMPLOYEES ==========
print("\n👥 Adding Employees...\n")

# Get or create default department
dept, _ = Department.objects.get_or_create(
    name='General',
    defaults={'description': 'General staff department'}
)

employees = [
    {'first': 'Kelvin', 'last': 'Ndungu', 'email': 'kelvin.ndungu@company.com'},
    {'first': 'Harriet', 'last': 'Smith', 'email': 'harriet.smith@company.com'},
    {'first': 'Wendy', 'last': 'Johnson', 'email': 'wendy.johnson@company.com'},
    {'first': 'Joe', 'last': 'Owiti', 'email': 'joe.owiti@company.com'},
]

for emp_data in employees:
    username = f"{emp_data['first'].lower()}.{emp_data['last'].lower()}"
    
    # Create User
    user, user_created = User.objects.get_or_create(
        username=username,
        defaults={
            'first_name': emp_data['first'],
            'last_name': emp_data['last'],
            'email': emp_data['email']
        }
    )
    
    if user_created:
        user.set_password('employee123')
        user.save()
    
    # Create Employee
    from datetime import date
    employee, emp_created = Employee.objects.get_or_create(
        user=user,
        defaults={
            'department': dept,
            'position': 'Staff Member',
            'employment_status': 'active',
            'employment_type': 'full_time',
            'phone': '+254700000000',
            'hire_date': date.today()
        }
    )
    
    status = '✅ Created' if emp_created else '⚠️  Exists'
    print(f"{status}: {emp_data['first']} {emp_data['last']} (Username: {username})")

print("\n" + "=" * 60)
print("🎉 DONE! All equipment and employees added successfully!")
print("=" * 60)
print("\nEquipment Summary:")
print("  • 1 White Ring Light")
print("  • 2 Y88 Bluetooth Microphones")
print("\nEmployees Summary:")
print("  • Kelvin Ndungu")
print("  • Harriet Smith")
print("  • Wendy Johnson")
print("  • Joe Owiti")
print("\nDefault password for all employees: employee123")
