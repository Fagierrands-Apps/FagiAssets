#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
sys.path.append('assetmanagement')
django.setup()

from django.contrib.auth.models import User
from assets.models import Asset

def check_asset_counts():
    try:
        user = User.objects.get(id=24)
        print(f'User: {user.username}')
        print(f'Legacy assigned_assets count: {user.assigned_assets.count()}')
        print(f'New assets count: {user.assets.count()}')
        print(f'Total assets in system: {Asset.objects.count()}')
        print(f'Assets with assigned_to: {Asset.objects.filter(assigned_to__isnull=False).count()}')
        print(f'Assets with assigned_users: {Asset.objects.filter(assigned_users__isnull=False).count()}')

        # Check specific assets assigned to this user
        legacy_assets = Asset.objects.filter(assigned_to=user)
        new_assets = Asset.objects.filter(assigned_users=user)

        print(f'\nLegacy assigned_to assets for user {user.username}:')
        for asset in legacy_assets[:5]:  # Show first 5
            print(f'  - {asset.asset_tag}: {asset.name}')

        print(f'\nNew assigned_users assets for user {user.username}:')
        for asset in new_assets[:5]:  # Show first 5
            print(f'  - {asset.asset_tag}: {asset.name}')

    except User.DoesNotExist:
        print("User with id 24 not found")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check_asset_counts()
