import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanagement.settings')
django.setup()

from django.contrib.auth.models import User
from crm.models import Employee

user = User.objects.filter(username='colsman').first()
print(f'User exists: {user is not None}')
if user:
    print(f'Username: {user.username}')
    print(f'Email: {user.email}')
    print(f'Is staff: {user.is_staff}')
    print(f'Is superuser: {user.is_superuser}')
    
    emp = Employee.objects.filter(user=user).first()
    print(f'Has employee profile: {emp is not None}')
    if emp:
        print(f'Role: {emp.role}')
        print(f'Position: {emp.position}')
        print(f'Department: {emp.department}')
        print(f'Employment Status: {emp.employment_status}')
else:
    print('User "colsman" does not exist')