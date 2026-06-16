#!/usr/bin/env python3

import requests
import json
from pprint import pprint

# Test API endpoints
BASE_URL = 'http://localhost:8000/api'

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f'{BASE_URL}/health/')
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print("✅ Health check passed")
            pprint(response.json())
        else:
            print("❌ Health check failed")
    except Exception as e:
        print(f"❌ Health check error: {e}")

def test_dashboard_stats():
    """Test dashboard stats endpoint"""
    try:
        response = requests.get(f'{BASE_URL}/dashboard/stats/')
        print(f"\nDashboard stats: {response.status_code}")
        if response.status_code == 200:
            print("✅ Dashboard stats passed")
            pprint(response.json())
        else:
            print("❌ Dashboard stats failed")
    except Exception as e:
        print(f"❌ Dashboard stats error: {e}")

def test_assets():
    """Test assets endpoint"""
    try:
        response = requests.get(f'{BASE_URL}/assets/')
        print(f"\nAssets: {response.status_code}")
        if response.status_code == 200:
            print("✅ Assets endpoint passed")
            data = response.json()
            print(f"Total assets: {len(data.get('results', data))}")
            if data.get('results'):
                print("First asset:")
                pprint(data['results'][0])
            elif isinstance(data, list) and data:
                print("First asset:")
                pprint(data[0])
        else:
            print("❌ Assets endpoint failed")
    except Exception as e:
        print(f"❌ Assets error: {e}")

def test_asset_distribution():
    """Test asset distribution endpoint"""
    try:
        response = requests.get(f'{BASE_URL}/dashboard/asset-distribution/')
        print(f"\nAsset distribution: {response.status_code}")
        if response.status_code == 200:
            print("✅ Asset distribution passed")
            pprint(response.json())
        else:
            print("❌ Asset distribution failed")
    except Exception as e:
        print(f"❌ Asset distribution error: {e}")

def test_recent_activity():
    """Test recent activity endpoint"""
    try:
        response = requests.get(f'{BASE_URL}/dashboard/recent-activity/')
        print(f"\nRecent activity: {response.status_code}")
        if response.status_code == 200:
            print("✅ Recent activity passed")
            pprint(response.json())
        else:
            print("❌ Recent activity failed")
    except Exception as e:
        print(f"❌ Recent activity error: {e}")

if __name__ == '__main__':
    print("Testing Asset Management API...")
    test_health()
    test_dashboard_stats()
    test_assets()
    test_asset_distribution()
    test_recent_activity()
    print("\nAPI testing completed!")