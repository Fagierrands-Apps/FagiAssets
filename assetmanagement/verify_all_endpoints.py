#!/usr/bin/env python3

import requests
import json

BASE_URL = 'http://localhost:8000/api'

def test_endpoint(endpoint, name):
    """Test a single endpoint"""
    try:
        response = requests.get(f'{BASE_URL}{endpoint}')
        status = "✅ PASS" if response.status_code == 200 else "❌ FAIL"
        print(f"{status} {name}: {response.status_code}")
        if response.status_code != 200:
            print(f"    Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ FAIL {name}: {e}")
        return False

def main():
    """Test all API endpoints"""
    print("Testing all Asset Management API endpoints...")
    print("=" * 50)
    
    endpoints = [
        ('/health/', 'Health Check'),
        ('/assets/', 'Assets'),
        ('/categories/', 'Asset Categories'),
        ('/manufacturers/', 'Manufacturers'),
        ('/locations/', 'Locations'),
        ('/departments/', 'Departments'),
        ('/users/', 'Users'),
        ('/models/', 'Asset Models'),
        ('/maintenance/', 'Maintenance Records'),
        ('/dashboard/stats/', 'Dashboard Stats'),
        ('/dashboard/asset-distribution/', 'Asset Distribution'),
        ('/dashboard/trends/', 'Asset Trends'),
        ('/dashboard/recent-activity/', 'Recent Activity'),
        ('/reports/asset-summary/', 'Asset Summary Report'),
        ('/reports/maintenance-schedule/', 'Maintenance Schedule Report'),
        ('/reports/financial-report/', 'Financial Report'),
        ('/reports/assignment-report/', 'Assignment Report'),
    ]
    
    passed = 0
    total = len(endpoints)
    
    for endpoint, name in endpoints:
        if test_endpoint(endpoint, name):
            passed += 1
    
    print("=" * 50)
    print(f"Results: {passed}/{total} endpoints working")
    
    if passed == total:
        print("🎉 All endpoints are working correctly!")
        print("Your desktop app should now be able to display real data.")
    else:
        print("⚠️  Some endpoints are failing. Check the errors above.")

if __name__ == '__main__':
    main()