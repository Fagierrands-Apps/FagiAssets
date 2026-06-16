#!/usr/bin/env python
"""
Test migration fix without making changes.

This script checks what would happen if you fake the migrations,
without actually making any changes to the database.
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
django.setup()

from django.db import connection
from django.db.migrations.recorder import MigrationRecorder

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

def get_applied_migrations(app_name):
    """Get list of applied migrations for an app."""
    recorder = MigrationRecorder(connection)
    applied = recorder.applied_migrations()
    return [name for app, name in applied if app == app_name]

def main():
    print("=" * 70)
    print("Migration Fix Test - No Changes Will Be Made")
    print("=" * 70)
    print()
    
    print("This script will analyze your database and tell you what needs to be fixed.")
    print("NO CHANGES will be made to your database.")
    print()
    
    # Check assets app specifically
    print("Analyzing 'assets' app...")
    print("-" * 70)
    
    # Check if assets_asset table exists
    table_exists = check_table_exists('assets_asset')
    print(f"\nTable 'assets_asset': {'✓ EXISTS' if table_exists else '✗ MISSING'}")
    
    if not table_exists:
        print("\n⚠ WARNING: assets_asset table doesn't exist!")
        print("You should run migrations normally, not fake them.")
        return 1
    
    # Check columns from migration 0002
    print("\nColumns from migration 0002:")
    columns_0002 = [
        'device_id',
        'device_name',
        'installed_ram',
        'processor',
        'product_id',
        'system_type',
    ]
    
    columns_exist = {}
    for column in columns_0002:
        exists = check_column_exists('assets_asset', column)
        columns_exist[column] = exists
        status = "✓ EXISTS" if exists else "✗ MISSING"
        print(f"  {status}: {column}")
    
    # Check applied migrations
    print("\nApplied migrations for 'assets':")
    applied = get_applied_migrations('assets')
    
    if not applied:
        print("  ✗ No migrations marked as applied")
    else:
        for migration in applied:
            print(f"  ✓ {migration}")
    
    # Analyze and provide recommendation
    print()
    print("=" * 70)
    print("ANALYSIS")
    print("=" * 70)
    print()
    
    all_columns_exist = all(columns_exist.values())
    migration_0002_applied = '0002_asset_device_id_asset_device_name_and_more' in applied
    
    if all_columns_exist and not migration_0002_applied:
        print("✓ DIAGNOSIS:")
        print("  - All columns from migration 0002 exist in the database")
        print("  - Migration 0002 is NOT marked as applied")
        print("  - This WILL cause 'column already exists' errors")
        print()
        print("✓ RECOMMENDATION:")
        print("  Run this command to fix:")
        print()
        print("    python manage.py migrate assets 0002 --fake")
        print()
        print("  Or use the fix script:")
        print()
        print("    python fix_partial_migrations.py")
        print()
        print("✓ EXPECTED RESULT:")
        print("  - Migration 0002 will be marked as applied")
        print("  - No database changes will be made")
        print("  - Subsequent migrations can proceed normally")
        
    elif all_columns_exist and migration_0002_applied:
        print("✓ DIAGNOSIS:")
        print("  - All columns exist")
        print("  - Migration 0002 is already marked as applied")
        print("  - No fix needed for migration 0002")
        print()
        print("✓ RECOMMENDATION:")
        print("  Try running migrations normally:")
        print()
        print("    python manage.py migrate")
        print()
        print("  If you still get errors, the issue is with a different migration.")
        
    elif not all_columns_exist and not migration_0002_applied:
        print("⚠ DIAGNOSIS:")
        print("  - Some columns are missing")
        print("  - Migration 0002 is not applied")
        print("  - This is the expected state")
        print()
        print("✓ RECOMMENDATION:")
        print("  Run migrations normally (don't fake):")
        print()
        print("    python manage.py migrate")
        print()
        print("  This will add the missing columns.")
        
    else:  # Some columns exist, migration is applied
        print("⚠ DIAGNOSIS:")
        print("  - Some columns exist, some don't")
        print("  - Migration 0002 is marked as applied")
        print("  - Database state is inconsistent")
        print()
        print("⚠ RECOMMENDATION:")
        print("  This is a complex situation. You may need to:")
        print("  1. Manually add missing columns, OR")
        print("  2. Restore from a backup, OR")
        print("  3. Contact a database administrator")
        print()
        print("  Missing columns:")
        for column, exists in columns_exist.items():
            if not exists:
                print(f"    - {column}")
    
    # Check other apps
    print()
    print("=" * 70)
    print("CHECKING OTHER APPS")
    print("=" * 70)
    
    other_apps = [
        ('admin', 'django_admin_log'),
        ('auth', 'auth_user'),
        ('contenttypes', 'django_content_type'),
        ('sessions', 'django_session'),
        ('authtoken', 'authtoken_token'),
    ]
    
    issues = []
    
    for app_name, table_name in other_apps:
        table_exists = check_table_exists(table_name)
        applied = get_applied_migrations(app_name)
        
        status = "✓" if table_exists else "✗"
        print(f"\n{app_name}:")
        print(f"  {status} Table: {table_name}")
        print(f"  Migrations applied: {len(applied)}")
        
        if table_exists and len(applied) == 0:
            print(f"  ⚠ WARNING: Table exists but no migrations marked as applied!")
            issues.append(app_name)
    
    if issues:
        print()
        print("=" * 70)
        print("ADDITIONAL ISSUES FOUND")
        print("=" * 70)
        print()
        print(f"The following apps have tables but no migrations marked as applied:")
        for app in issues:
            print(f"  - {app}")
        print()
        print("RECOMMENDATION:")
        print("  Run the comprehensive fix:")
        print()
        print("    python fix_all_partial_migrations.py")
        print()
        print("  Or fake migrations for each app:")
        for app in issues:
            print(f"    python manage.py migrate {app} --fake")
    
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print("✓ Analysis complete - no changes were made to your database")
    print()
    print("Next steps:")
    print("  1. Review the recommendations above")
    print("  2. Choose the appropriate fix command")
    print("  3. Run the fix on your production server")
    print("  4. Verify with: python manage.py showmigrations")
    print()
    
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        print()
        print("This might be a connection issue. Check your database settings.")
        sys.exit(1)