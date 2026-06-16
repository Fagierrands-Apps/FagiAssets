"""
Test script to verify role-based login redirects work correctly.

Run this script from the assetmanagement directory:
    python test_login_redirect.py
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
django.setup()

from django.contrib.auth.models import User
from crm.models import Employee
from django.test import RequestFactory
from users.views import RoleBasedLoginView


def test_login_redirects():
    """Test that users are redirected to the correct dashboard based on their role"""
    
    print("=" * 70)
    print("Testing Role-Based Login Redirects")
    print("=" * 70)
    
    # Create a mock request factory
    factory = RequestFactory()
    
    # Test cases
    test_cases = []
    
    # Get all users with employee profiles
    employees = Employee.objects.select_related('user').all()
    
    for employee in employees:
        user = employee.user
        role = employee.role
        
        # Create a mock request
        request = factory.get('/login/')
        request.user = user
        
        # Create login view instance
        view = RoleBasedLoginView()
        view.request = request
        
        # Get the redirect URL
        try:
            redirect_url = view.get_success_url()
            expected_url = '/assets/' if role == 'admin' or user.is_superuser else '/crm/employee/'
            status = "✅ PASS" if redirect_url == expected_url else "❌ FAIL"
            
            test_cases.append({
                'username': user.username,
                'role': role,
                'is_superuser': user.is_superuser,
                'expected': expected_url,
                'actual': redirect_url,
                'status': status
            })
        except Exception as e:
            test_cases.append({
                'username': user.username,
                'role': role,
                'is_superuser': user.is_superuser,
                'expected': 'N/A',
                'actual': f'ERROR: {str(e)}',
                'status': "❌ ERROR"
            })
    
    # Print results
    print("\nTest Results:")
    print("-" * 70)
    print(f"{'Username':<20} {'Role':<15} {'Super':<8} {'Expected':<20} {'Status':<10}")
    print("-" * 70)
    
    for test in test_cases:
        print(f"{test['username']:<20} {test['role']:<15} {str(test['is_superuser']):<8} {test['expected']:<20} {test['status']:<10}")
    
    print("-" * 70)
    
    # Summary
    passed = sum(1 for t in test_cases if t['status'] == "✅ PASS")
    failed = sum(1 for t in test_cases if t['status'] in ["❌ FAIL", "❌ ERROR"])
    
    print(f"\nSummary: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 70)
    
    return passed == len(test_cases)


if __name__ == '__main__':
    try:
        success = test_login_redirects()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test script failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)