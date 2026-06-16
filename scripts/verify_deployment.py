#!/usr/bin/env python
"""
Deployment verification script
Tests that the production environment is properly configured
"""
import requests
import json
import sys
from urllib.parse import urljoin

def test_endpoint(base_url, endpoint, expected_status=200):
    """Test an endpoint and return the response"""
    url = urljoin(base_url, endpoint)
    try:
        response = requests.get(url, timeout=30)
        print(f"✓ {endpoint}: {response.status_code}")
        if response.status_code == expected_status:
            return response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        else:
            print(f"  ⚠ Expected {expected_status}, got {response.status_code}")
            return None
    except Exception as e:
        print(f"✗ {endpoint}: Error - {e}")
        return None

def test_login(base_url, username, password):
    """Test admin login"""
    login_url = urljoin(base_url, '/login/')
    session = requests.Session()
    
    try:
        # Get login page to get CSRF token
        response = session.get(login_url)
        if 'csrfmiddlewaretoken' in response.text:
            # Extract CSRF token (simple extraction)
            csrf_start = response.text.find('name="csrfmiddlewaretoken" value="') + 34
            csrf_end = response.text.find('"', csrf_start)
            csrf_token = response.text[csrf_start:csrf_end]
            
            # Attempt login
            login_data = {
                'username': username,
                'password': password,
                'csrfmiddlewaretoken': csrf_token
            }
            
            response = session.post(login_url, data=login_data)
            if response.status_code == 302 or 'logout' in response.text.lower():
                print(f"✓ Login successful for {username}")
                return True
            else:
                print(f"✗ Login failed for {username}")
                return False
        else:
            print("✗ Could not find CSRF token on login page")
            return False
            
    except Exception as e:
        print(f"✗ Login test error: {e}")
        return False

def main():
    """Main verification function"""
    base_url = sys.argv[1] if len(sys.argv) > 1 else 'https://fagiassets.vercel.app'
    
    print(f"🔍 Verifying deployment at: {base_url}")
    print("=" * 50)
    
    # Test health check
    print("\n📊 Testing Health Check:")
    health_data = test_endpoint(base_url, '/users/health/')
    if health_data:
        print(f"  Environment: {health_data.get('environment', 'unknown')}")
        print(f"  Database: {health_data.get('database', 'unknown')}")
        print(f"  Admin User: {health_data.get('admin_user', 'unknown')}")
    
    # Test main endpoints
    print("\n🌐 Testing Main Endpoints:")
    test_endpoint(base_url, '/')
    test_endpoint(base_url, '/login/')
    test_endpoint(base_url, '/admin/')
    
    # Test admin login
    print("\n🔐 Testing Admin Login:")
    login_success = test_login(base_url, 'admin', 'FagiAssets2024!')
    
    # Test API endpoints
    print("\n🔌 Testing API Endpoints:")
    test_endpoint(base_url, '/api/assets/')
    test_endpoint(base_url, '/api/users/')
    
    # Summary
    print("\n" + "=" * 50)
    if health_data and health_data.get('status') == 'healthy' and login_success:
        print("✅ Deployment verification PASSED")
        print("\n🎉 Production environment is ready!")
        print(f"   Login at: {base_url}/login/")
        print("   Username: admin")
        print("   Password: FagiAssets2024!")
        return 0
    else:
        print("❌ Deployment verification FAILED")
        print("\n🔧 Check the following:")
        print("   - Database connectivity")
        print("   - Environment variables")
        print("   - Admin user creation")
        return 1

if __name__ == '__main__':
    sys.exit(main())