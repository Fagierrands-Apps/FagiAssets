#!/usr/bin/env python
"""
Fix partial migration state - when columns/tables exist but migrations aren't marked as applied.

This script checks which columns exist and marks the appropriate migrations as applied.
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
django.setup()

from django.core.management import call_command
from django.db import connection
from django.db.migrations.recorder import MigrationRecorder

def check_column_exists(table_name, column_name):
    """Check if a column exists in a table."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = %s 
                AND column_name = %s
            );
        """, [table_name, column_name])
        return cursor.fetchone()[0]

def check_table_exists(table_name):
    """Check if a table exists in the database."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            );
        """, [table_name])
        return cursor.fetchone()[0]

def get_applied_migrations(app_name):
    """Get list of applied migrations for an app."""
    recorder = MigrationRecorder(connection)
    applied = recorder.applied_migrations()
    return [name for app, name in applied if app == app_name]

def mark_migration_as_applied(app_name, migration_name):
    """Mark a specific migration as applied."""
    recorder = MigrationRecorder(connection)
    recorder.record_applied(app_name, migration_name)
    print(f"  ✓ Marked {app_name}.{migration_name} as applied")

def main():
    print("=" * 70)
    print("Django Partial Migration State Fix")
    print("=" * 70)
    print()
    
    # Check the specific issue: assets.0002 migration
    print("Checking assets app migration state...")
    print("-" * 70)
    
    # Check if the problematic columns exist
    columns_to_check = [
        ('assets_asset', 'device_id'),
        ('assets_asset', 'device_name'),
        ('assets_asset', 'installed_ram'),
        ('assets_asset', 'processor'),
        ('assets_asset', 'product_id'),
        ('assets_asset', 'system_type'),
    ]
    
    print("\nChecking columns from migration 0002:")
    all_exist = True
    for table, column in columns_to_check:
        exists = check_column_exists(table, column)
        status = "✓ EXISTS" if exists else "✗ MISSING"
        print(f"  {status}: {table}.{column}")
        if not exists:
            all_exist = False
    
    print()
    
    # Check current migration state
    applied_migrations = get_applied_migrations('assets')
    print(f"Currently applied migrations for 'assets': {len(applied_migrations)}")
    for migration in applied_migrations:
        print(f"  ✓ {migration}")
    
    print()
    
    # Determine what to do
    if all_exist and '0002_asset_device_id_asset_device_name_and_more' not in applied_migrations:
        print("DIAGNOSIS:")
        print("  - All columns from migration 0002 exist in the database")
        print("  - But migration 0002 is not marked as applied")
        print("  - This will cause 'column already exists' errors")
        print()
        
        response = input("Mark migration 0002 as applied? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Operation cancelled.")
            return 0
        
        print()
        print("Marking migration as applied...")
        try:
            mark_migration_as_applied('assets', '0002_asset_device_id_asset_device_name_and_more')
            print()
            print("✓ SUCCESS!")
            print()
            print("Now checking if there are more migrations to apply...")
            print()
            
            # Try to apply remaining migrations
            call_command('migrate', 'assets', verbosity=1)
            
        except Exception as e:
            print(f"\n✗ Error: {str(e)}")
            return 1
    
    elif not all_exist:
        print("DIAGNOSIS:")
        print("  - Some columns are missing from the database")
        print("  - The database state is inconsistent")
        print()
        print("RECOMMENDATION:")
        print("  This is a more complex issue. You may need to:")
        print("  1. Manually add the missing columns, OR")
        print("  2. Restore from a backup, OR")
        print("  3. Recreate the database")
        return 1
    
    else:
        print("DIAGNOSIS:")
        print("  - Migration 0002 is already marked as applied")
        print("  - No action needed for this migration")
        print()
        print("Checking for other migration issues...")
        print()
        
        # Try to migrate normally
        try:
            call_command('showmigrations', 'assets', verbosity=1)
            print()
            call_command('migrate', 'assets', verbosity=1)
        except Exception as e:
            print(f"\n✗ Error: {str(e)}")
            return 1
    
    print()
    print("=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print()
    print("1. Verify all migrations are applied:")
    print("   python manage.py showmigrations")
    print()
    print("2. Try migrating all apps:")
    print("   python manage.py migrate")
    print()
    print("3. If you still have issues, try:")
    print("   python fix_all_partial_migrations.py")
    print()
    
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)