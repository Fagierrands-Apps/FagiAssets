#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append('c:/Users/a/Documents/GitHub/fagiassets/assetmanagement')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from crm.models import Employee

# Test the employee dashboard
client = Client()

# Get the test employee user
try:
    user = User.objects.get(username='test.sales')
    print(f"Found user: {user.username}")
    
    # Login
    login_success = client.login(username='test.sales', password='employee123')
    print(f"Login successful: {login_success}")
    
    if login_success:
        # Test employee dashboard
        response = client.get('/crm/employee/')
        print(f"Employee dashboard status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Employee dashboard loads successfully!")
        else:
            print(f"❌ Employee dashboard failed with status: {response.status_code}")
            if hasattr(response, 'content'):
                print("Response content:", response.content.decode()[:500])
    else:
        print("❌ Login failed")
        
except User.DoesNotExist:
    print("❌ User 'test.sales' not found")
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()