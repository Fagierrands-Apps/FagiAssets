#!/usr/bin/env python
"""
Improved data migration script
This script exports data from local database and imports to production
"""

import os
import sys
import django
import json
from django.core.management import call_command
from io import StringIO

def migrate_data_improved():
    """Improved data migration process"""
    print("=" * 70)
    print("IMPROVED DATA MIGRATION: Local → Production")
    print("=" * 70)
    
    # Add Django project to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'assetmanagement'))
    
    # Step 1: Export data from local database
    print("Step 1: Exporting data from local database...")
    if not export_local_data():
        return False
    
    # Step 2: Import data to production
    print("Step 2: Importing data to production...")
    if not import_to_production():
        return False
    
    # Step 3: Verify migration
    print("Step 3: Verifying migration...")
    verify_migration()
    
    print("\n✅ Data migration completed successfully!")
    return True

def export_local_data():
    """Export data from local database using dumpdata"""
    print("Exporting local database data...")
    
    # Setup Django with local settings (development)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
    # Ensure we're using local database
    if 'VERCEL' in os.environ:
        del os.environ['VERCEL']
    if 'DATABASE_URL' in os.environ:
        del os.environ['DATABASE_URL']
    
    django.setup()
    
    try:
        # Create data directory
        data_dir = os.path.join(os.path.dirname(__file__), 'migration_data')
        os.makedirs(data_dir, exist_ok=True)
        
        # Export each app's data
        apps_to_export = [
            'auth.User',
            'assets.AssetCategory',
            'assets.Asset', 
            'users.UserProfile',
            'discovery.NetworkDevice',
            'authtoken.Token',
            'contenttypes.ContentType',
        ]
        
        for app_model in apps_to_export:
            try:
                output_file = os.path.join(data_dir, f'{app_model.replace(".", "_")}.json')
                
                # Use dumpdata to export
                with open(output_file, 'w') as f:
                    call_command('dumpdata', app_model, 
                               format='json', 
                               indent=2, 
                               stdout=f,
                               verbosity=0)
                
                # Check if file has data
                with open(output_file, 'r') as f:
                    data = json.load(f)
                    if data:
                        print(f"✓ Exported {len(data)} {app_model} objects")
                    else:
                        print(f"- No {app_model} data found")
                        
            except Exception as e:
                print(f"! Could not export {app_model}: {e}")
                continue
        
        print(f"✓ Data exported to {data_dir}")
        return True
        
    except Exception as e:
        print(f"Error exporting data: {e}")
        return False

def import_to_production():
    """Import data to production database"""
    print("Importing data to production database...")
    
    # Setup Django with production settings
    os.environ['DJANGO_SETTINGS_MODULE'] = 'assetmanager.settings'
    os.environ['VERCEL'] = '1'
    os.environ['DATABASE_URL'] = 'postgresql://postgres.dxesmzogjpxswxhsomgf:OnFRtf0SmpHwgNaQ@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres'
    
    # Clear Django setup and reinitialize
    from django.apps import apps
    apps.populated = False
    django.setup()
    
    try:
        # Test production connection
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            print(f"✓ Connected to production: {version.split()[0]} {version.split()[1]}")
        
        # Import data files in order
        data_dir = os.path.join(os.path.dirname(__file__), 'migration_data')
        
        # Order matters for foreign key constraints
        import_order = [
            'contenttypes_ContentType.json',
            'auth_User.json',
            'assets_AssetCategory.json',
            'assets_Asset.json',
            'users_UserProfile.json',
            'discovery_NetworkDevice.json',
            'authtoken_Token.json',
        ]
        
        for filename in import_order:
            filepath = os.path.join(data_dir, filename)
            
            if os.path.exists(filepath):
                print(f"Importing {filename}...")
                
                try:
                    # Check if file has data
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        if not data:
                            print(f"  - No data in {filename}")
                            continue
                    
                    # Use loaddata to import
                    call_command('loaddata', filepath, verbosity=1)
                    print(f"✓ Imported {filename}")
                    
                except Exception as e:
                    print(f"! Error importing {filename}: {e}")
                    # Continue with other files
                    continue
            else:
                print(f"  - {filename} not found, skipping")
        
        print("✓ Data import completed")
        return True
        
    except Exception as e:
        print(f"Error importing to production: {e}")
        return False

def verify_migration():
    """Verify that migration was successful"""
    print("Verifying migration...")
    
    try:
        from django.contrib.auth.models import User
        from assets.models import Asset, AssetCategory
        from users.models import UserProfile
        from discovery.models import NetworkDevice
        from rest_framework.authtoken.models import Token
        
        # Count objects
        counts = {
            'Users': User.objects.count(),
            'Assets': Asset.objects.count(),
            'Asset Categories': AssetCategory.objects.count(),
            'User Profiles': UserProfile.objects.count(),
            'Network Devices': NetworkDevice.objects.count(),
            'Auth Tokens': Token.objects.count(),
        }
        
        print("\nProduction Database Contents:")
        for item, count in counts.items():
            print(f"  {item}: {count}")
        
        # Show sample data
        if Asset.objects.exists():
            print("\nSample Assets:")
            for asset in Asset.objects.all()[:3]:
                print(f"  - {asset.name} ({asset.asset_type})")
        
        if User.objects.exists():
            print("\nUsers:")
            for user in User.objects.all():
                print(f"  - {user.username} ({user.email})")
        
        print("\n✅ Migration verification completed!")
        print("🌐 Your data is now available at: https://fagiassets.vercel.app/")
        
    except Exception as e:
        print(f"Verification failed: {e}")

if __name__ == '__main__':
    success = migrate_data_improved()
    sys.exit(0 if success else 1)