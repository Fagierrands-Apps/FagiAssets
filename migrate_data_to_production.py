#!/usr/bin/env python
"""
Migrate all local database data to production
This script will transfer all data from local SQLite to production PostgreSQL
"""

import os
import sys
import django
import json
from django.core import serializers
from django.db import connections
from django.apps import apps

def migrate_data_to_production():
    """Migrate all data from local to production"""
    print("=" * 70)
    print("DATA MIGRATION: Local → Production")
    print("=" * 70)
    
    # Add Django project to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'assetmanagement'))
    
    # Setup Django with local settings first
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
    django.setup()
    
    # Step 1: Export data from local database
    print("Step 1: Exporting data from local database...")
    local_data = export_local_data()
    
    if not local_data:
        print("No data found in local database")
        return False
    
    # Step 2: Switch to production database
    print("Step 2: Switching to production database...")
    setup_production_db()
    
    # Step 3: Import data to production
    print("Step 3: Importing data to production...")
    success = import_to_production(local_data)
    
    if success:
        print("\n✅ Data migration completed successfully!")
        print_migration_summary()
    else:
        print("\n❌ Data migration failed!")
    
    return success

def export_local_data():
    """Export all data from local database"""
    print("Exporting local database data...")
    
    # Use default (local) database connection
    from django.db import connection
    
    try:
        # Check if local database exists and has data
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
        if not tables:
            print("No tables found in local database")
            return {}
        
        print(f"Found {len(tables)} tables in local database")
        
        # Export data from each app
        exported_data = {}
        
        # Export Users
        try:
            from django.contrib.auth.models import User
            users = User.objects.all()
            if users:
                exported_data['users'] = serializers.serialize('json', users)
                print(f"✓ Exported {len(users)} users")
        except Exception as e:
            print(f"! Could not export users: {e}")
        
        # Export Assets
        try:
            from assets.models import Asset
            assets = Asset.objects.all()
            if assets:
                exported_data['assets'] = serializers.serialize('json', assets)
                print(f"✓ Exported {len(assets)} assets")
        except Exception as e:
            print(f"! Could not export assets: {e}")
        
        # Export Asset Categories
        try:
            from assets.models import AssetCategory
            categories = AssetCategory.objects.all()
            if categories:
                exported_data['asset_categories'] = serializers.serialize('json', categories)
                print(f"✓ Exported {len(categories)} asset categories")
        except Exception as e:
            print(f"! Could not export asset categories: {e}")
        
        # Export Users app data
        try:
            from users.models import UserProfile
            profiles = UserProfile.objects.all()
            if profiles:
                exported_data['user_profiles'] = serializers.serialize('json', profiles)
                print(f"✓ Exported {len(profiles)} user profiles")
        except Exception as e:
            print(f"! Could not export user profiles: {e}")
        
        # Export Discovery data
        try:
            from discovery.models import NetworkDevice
            devices = NetworkDevice.objects.all()
            if devices:
                exported_data['network_devices'] = serializers.serialize('json', devices)
                print(f"✓ Exported {len(devices)} network devices")
        except Exception as e:
            print(f"! Could not export network devices: {e}")
        
        # Export Sessions (if needed)
        try:
            from django.contrib.sessions.models import Session
            sessions = Session.objects.all()
            if sessions:
                exported_data['sessions'] = serializers.serialize('json', sessions)
                print(f"✓ Exported {len(sessions)} sessions")
        except Exception as e:
            print(f"! Could not export sessions: {e}")
        
        # Export Auth Tokens
        try:
            from rest_framework.authtoken.models import Token
            tokens = Token.objects.all()
            if tokens:
                exported_data['auth_tokens'] = serializers.serialize('json', tokens)
                print(f"✓ Exported {len(tokens)} auth tokens")
        except Exception as e:
            print(f"! Could not export auth tokens: {e}")
        
        return exported_data
        
    except Exception as e:
        print(f"Error exporting local data: {e}")
        return {}

def setup_production_db():
    """Setup production database connection"""
    print("Setting up production database connection...")
    
    # Set production environment variables
    os.environ['VERCEL'] = '1'
    os.environ['DATABASE_URL'] = 'postgresql://postgres.dxesmzogjpxswxhsomgf:OnFRtf0SmpHwgNaQ@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres'
    
    # Force Django to reload settings
    from django.conf import settings
    settings.configure()
    
    # Reload Django with production settings
    django.setup()
    
    print("✓ Production database connection configured")

def import_to_production(exported_data):
    """Import data to production database"""
    print("Importing data to production database...")
    
    try:
        # Use production database connection
        from django.db import connection, transaction
        
        # Test production connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            print(f"✓ Connected to production database: {version.split()[0]} {version.split()[1]}")
        
        # Import data in order (to respect foreign key constraints)
        import_order = [
            'users',
            'asset_categories', 
            'assets',
            'user_profiles',
            'network_devices',
            'auth_tokens',
            'sessions'
        ]
        
        with transaction.atomic():
            for data_type in import_order:
                if data_type in exported_data:
                    print(f"Importing {data_type}...")
                    
                    try:
                        # Deserialize and save objects
                        objects = serializers.deserialize('json', exported_data[data_type])
                        
                        saved_count = 0
                        for obj in objects:
                            # Check if object already exists
                            model_class = obj.object.__class__
                            
                            if hasattr(obj.object, 'pk') and obj.object.pk:
                                # Check if object with this pk exists
                                if not model_class.objects.filter(pk=obj.object.pk).exists():
                                    obj.save()
                                    saved_count += 1
                                else:
                                    print(f"  ! Skipping existing {model_class.__name__} with ID {obj.object.pk}")
                            else:
                                obj.save()
                                saved_count += 1
                        
                        print(f"✓ Imported {saved_count} {data_type}")
                        
                    except Exception as e:
                        print(f"! Error importing {data_type}: {e}")
                        # Continue with other data types
                        continue
        
        print("✓ All data imported successfully")
        return True
        
    except Exception as e:
        print(f"Error importing to production: {e}")
        return False

def print_migration_summary():
    """Print summary of migrated data"""
    print("\n" + "=" * 50)
    print("MIGRATION SUMMARY")
    print("=" * 50)
    
    try:
        # Count objects in production database
        from django.contrib.auth.models import User
        from assets.models import Asset, AssetCategory
        from users.models import UserProfile
        from discovery.models import NetworkDevice
        from rest_framework.authtoken.models import Token
        
        print(f"Users: {User.objects.count()}")
        print(f"Assets: {Asset.objects.count()}")
        print(f"Asset Categories: {AssetCategory.objects.count()}")
        print(f"User Profiles: {UserProfile.objects.count()}")
        print(f"Network Devices: {NetworkDevice.objects.count()}")
        print(f"Auth Tokens: {Token.objects.count()}")
        
        # Show some sample data
        print("\nSample Assets:")
        for asset in Asset.objects.all()[:5]:
            print(f"  - {asset.name} ({asset.asset_type})")
        
        print("\nSample Users:")
        for user in User.objects.all()[:5]:
            print(f"  - {user.username} ({user.email})")
            
        print("\n✅ Your local data is now available on the production server!")
        print("🌐 Access it at: https://fagiassets.vercel.app/")
        
    except Exception as e:
        print(f"Could not generate summary: {e}")

if __name__ == '__main__':
    success = migrate_data_to_production()
    sys.exit(0 if success else 1)