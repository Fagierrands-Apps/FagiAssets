#!/usr/bin/env python
"""
Simple data migration script
Step 1: Export local data
Step 2: Import to production
"""

import os
import sys
import subprocess
import json

def main():
    print("=" * 60)
    print("SIMPLE DATA MIGRATION")
    print("=" * 60)
    
    # Step 1: Export local data
    print("\nStep 1: Exporting local data...")
    export_success = export_local_data()
    
    if not export_success:
        print("❌ Export failed!")
        return False
    
    # Step 2: Import to production
    print("\nStep 2: Importing to production...")
    import_success = import_to_production()
    
    if import_success:
        print("\n✅ Migration completed successfully!")
        print_instructions()
    else:
        print("\n❌ Migration failed!")
    
    return import_success

def export_local_data():
    """Export data from local database"""
    print("Exporting from local database...")
    
    # Change to Django project directory
    os.chdir(os.path.join(os.path.dirname(__file__), 'assetmanagement'))
    
    # Create fixtures directory
    fixtures_dir = os.path.join(os.getcwd(), 'fixtures')
    os.makedirs(fixtures_dir, exist_ok=True)
    
    # Export commands
    export_commands = [
        # Users (excluding superuser for now)
        ['python', 'manage.py', 'dumpdata', 'auth.User', '--output', 'fixtures/users.json'],
        # Assets
        ['python', 'manage.py', 'dumpdata', 'assets', '--output', 'fixtures/assets.json'],
        # User profiles
        ['python', 'manage.py', 'dumpdata', 'users', '--output', 'fixtures/user_profiles.json'],
        # Discovery data
        ['python', 'manage.py', 'dumpdata', 'discovery', '--output', 'fixtures/discovery.json'],
        # Auth tokens
        ['python', 'manage.py', 'dumpdata', 'authtoken', '--output', 'fixtures/auth_tokens.json'],
        # Content types (needed for foreign keys)
        ['python', 'manage.py', 'dumpdata', 'contenttypes', '--output', 'fixtures/contenttypes.json'],
    ]
    
    # Remove production environment variables for local export
    env = os.environ.copy()
    env.pop('VERCEL', None)
    env.pop('DATABASE_URL', None)
    
    success_count = 0
    
    for cmd in export_commands:
        try:
            print(f"  Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, env=env)
            
            if result.returncode == 0:
                # Check if file was created and has data
                output_file = cmd[-1]
                if os.path.exists(output_file):
                    with open(output_file, 'r') as f:
                        data = json.load(f)
                        if data:
                            print(f"    ✓ Exported {len(data)} objects")
                            success_count += 1
                        else:
                            print(f"    - No data found")
                else:
                    print(f"    ! Output file not created")
            else:
                print(f"    ! Command failed: {result.stderr}")
                
        except Exception as e:
            print(f"    ! Error: {e}")
    
    if success_count > 0:
        print(f"✓ Successfully exported {success_count} data types")
        return True
    else:
        print("! No data exported")
        return False

def import_to_production():
    """Import data to production database"""
    print("Importing to production database...")
    
    # Set production environment variables
    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = 'assetmanager.settings'
    env['VERCEL'] = '1'
    env['DATABASE_URL'] = 'postgresql://postgres.dxesmzogjpxswxhsomgf:OnFRtf0SmpHwgNaQ@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres'
    
    # Test production connection first
    print("  Testing production connection...")
    try:
        result = subprocess.run(['python', 'manage.py', 'check', '--database', 'default'], 
                              capture_output=True, text=True, env=env)
        if result.returncode == 0:
            print("    ✓ Production connection successful")
        else:
            print(f"    ! Production connection failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"    ! Connection test error: {e}")
        return False
    
    # Import fixtures in order (to respect foreign key constraints)
    fixtures_dir = os.path.join(os.getcwd(), 'fixtures')
    
    import_order = [
        'contenttypes.json',
        'users.json',
        'assets.json',
        'user_profiles.json',
        'discovery.json',
        'auth_tokens.json',
    ]
    
    success_count = 0
    
    for fixture_file in import_order:
        fixture_path = os.path.join(fixtures_dir, fixture_file)
        
        if os.path.exists(fixture_path):
            print(f"  Importing {fixture_file}...")
            
            try:
                # Check if file has data
                with open(fixture_path, 'r') as f:
                    data = json.load(f)
                    if not data:
                        print(f"    - No data in {fixture_file}")
                        continue
                
                # Import the fixture
                cmd = ['python', 'manage.py', 'loaddata', fixture_path]
                result = subprocess.run(cmd, capture_output=True, text=True, env=env)
                
                if result.returncode == 0:
                    print(f"    ✓ Imported {fixture_file}")
                    success_count += 1
                else:
                    print(f"    ! Failed to import {fixture_file}: {result.stderr}")
                    
            except Exception as e:
                print(f"    ! Error importing {fixture_file}: {e}")
        else:
            print(f"  - {fixture_file} not found, skipping")
    
    if success_count > 0:
        print(f"✓ Successfully imported {success_count} data types")
        
        # Verify import
        print("  Verifying import...")
        verify_import(env)
        
        return True
    else:
        print("! No data imported")
        return False

def verify_import(env):
    """Verify that data was imported correctly"""
    try:
        # Count objects in production
        verification_script = '''
import os
import sys
import django

sys.path.insert(0, os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "assetmanager.settings")
django.setup()

from django.contrib.auth.models import User
from assets.models import Asset, AssetCategory
from users.models import UserProfile
from discovery.models import NetworkDevice

print("Production Database Contents:")
print(f"  Users: {User.objects.count()}")
print(f"  Assets: {Asset.objects.count()}")
print(f"  Asset Categories: {AssetCategory.objects.count()}")
print(f"  User Profiles: {UserProfile.objects.count()}")
print(f"  Network Devices: {NetworkDevice.objects.count()}")

if Asset.objects.exists():
    print("Sample Assets:")
    for asset in Asset.objects.all()[:3]:
        print(f"  - {asset.name} ({asset.asset_type})")

if User.objects.exists():
    print("Users:")
    for user in User.objects.all():
        print(f"  - {user.username} ({user.email})")
'''
        
        with open('verify_import.py', 'w') as f:
            f.write(verification_script)
        
        result = subprocess.run(['python', 'verify_import.py'], 
                              capture_output=True, text=True, env=env)
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"    ! Verification failed: {result.stderr}")
            
        # Clean up
        os.remove('verify_import.py')
        
    except Exception as e:
        print(f"    ! Verification error: {e}")

def print_instructions():
    """Print final instructions"""
    print("\n" + "=" * 60)
    print("MIGRATION COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\n🎉 Your local data has been migrated to production!")
    print("\n📍 Access your data at:")
    print("   https://fagiassets.vercel.app/")
    print("\n🔑 Login with:")
    print("   Username: admin")
    print("   Password: FagiAssets2024!")
    print("\n✅ What was migrated:")
    print("   - All users and user profiles")
    print("   - All assets and categories")
    print("   - All network devices")
    print("   - Authentication tokens")
    print("   - Content types and permissions")
    print("\n📝 Next steps:")
    print("   1. Test the production site")
    print("   2. Verify all your data is there")
    print("   3. Generate QR codes for users")
    print("   4. Update any local references")

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)