import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanagement.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile
from assets.models import Department

user = User.objects.filter(first_name='Cyrus', last_name='Mweu').first()
if user:
    profile = getattr(user, 'profile', None)
    if profile:
        accounts_dept, created = Department.objects.get_or_create(
            name='Accounts',
            defaults={'description': 'Accounts Department'}
        )
        old_dept = profile.department
        profile.department = accounts_dept
        profile.save()
        print(f"Updated {user.get_full_name()}'s department from '{old_dept}' to '{profile.department}'")
    else:
        print("Profile not found")
else:
    print("User not found")
