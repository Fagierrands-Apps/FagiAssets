#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
sys.path.insert(0, 'assetmanagement')
django.setup()

from django.contrib.auth.models import User
from users.views import RoleBasedLoginView

def test_login_redirect():
    # Create a mock view instance
    view = RoleBasedLoginView()

    # Test with a superuser
    superuser = User.objects.filter(is_superuser=True).first()
    if superuser:
        # Mock the request object
        class MockRequest:
            def __init__(self, user):
                self.user = user
                self.GET = {}
                self.POST = {}

        view.request = MockRequest(superuser)
        redirect_url = view.get_success_url()
        print(f'Superuser redirect: {redirect_url}')
    else:
        print('No superuser found')

    # Test with an admin employee
    try:
        from crm.models import Employee
        admin_employee = Employee.objects.filter(role='admin').first()
        if admin_employee:
            view.request = MockRequest(admin_employee.user)
            redirect_url = view.get_success_url()
            print(f'Admin employee redirect: {redirect_url}')
        else:
            print('No admin employee found')
    except Exception as e:
        print(f'Error testing admin employee: {e}')

    # Test with a staff user without employee profile
    staff_user = User.objects.filter(is_staff=True, is_superuser=False).first()
    if staff_user:
        view.request = MockRequest(staff_user)
        redirect_url = view.get_success_url()
        print(f'Staff user redirect: {redirect_url}')
    else:
        print('No staff user found')

if __name__ == '__main__':
    test_login_redirect()
