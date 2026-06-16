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
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware

def test_login_redirect():
    # Create a test request
    factory = RequestFactory()
    request = factory.get('/login/')

    # Add session middleware
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()

    # Test with a superuser
    superuser = User.objects.filter(is_superuser=True).first()
    if superuser:
        request.user = superuser
        view = RoleBasedLoginView()
        view.request = request
        redirect_url = view.get_success_url()
        print(f'Superuser redirect: {redirect_url}')
    else:
        print('No superuser found')

    # Test with an admin employee
    try:
        from crm.models import Employee
        admin_employee = Employee.objects.filter(role='admin').first()
        if admin_employee:
            request.user = admin_employee.user
            view = RoleBasedLoginView()
            view.request = request
            redirect_url = view.get_success_url()
            print(f'Admin employee redirect: {redirect_url}')
        else:
            print('No admin employee found')
    except Exception as e:
        print(f'Error testing admin employee: {e}')

if __name__ == '__main__':
    test_login_redirect()
