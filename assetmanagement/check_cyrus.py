import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanagement.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile
from crm.models import Employee

user = User.objects.filter(first_name='Cyrus', last_name='Mweu').first()
if user:
    profile = getattr(user, 'profile', None)
    employee = getattr(user, 'employee_profile', None)
    
    print(f"User: {user.get_full_name()}")
    print(f"UserProfile job_title: {profile.job_title if profile else 'N/A'}")
    print(f"UserProfile department: {profile.department if profile else 'N/A'}")
    print(f"Employee position: {employee.position if employee else 'N/A'}")
    print(f"Employee department: {employee.department if employee else 'N/A'}")
