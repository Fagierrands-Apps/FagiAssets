#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
sys.path.insert(0, 'assetmanagement')
django.setup()

from django.contrib.auth.models import User
from crm.models import Employee

def check_users():
    print('Users:')
    for u in User.objects.all():
        print(f'{u.username}: superuser={u.is_superuser}, staff={u.is_staff}')

    print('\nEmployees:')
    for e in Employee.objects.all():
        print(f'{e.user.username}: role={e.role}')

if __name__ == '__main__':
    check_users()
