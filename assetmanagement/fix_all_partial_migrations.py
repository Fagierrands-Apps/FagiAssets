#!/usr/bin/env python
"""
Comprehensive fix for partial migration states across all apps.

This script:
1. Checks which migrations are applied
2. Checks which tables/columns exist
3. Marks migrations as applied if their changes exist in the database
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
from django.apps import apps

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

def get_applied_migrations(app_name=None):
    """Get list of applied migrations."""
    recorder = MigrationRecorder(connection)
    applied = recorder.applied_migrations()
    if app_name:
        return [name for app, name in applied if app == app_name]
    return applied

def mark_migration_as_applied(app_name, migration_name):
    """Mark a specific migration as applied."""
    recorder = MigrationRecorder(connection)
    recorder.record_applied(app_name, migration_name)

def main():
    print("=" * 70)
    print("Comprehensive Migration State Fix")
    print("=" * 70)
    print()
    
    print("This script will:")
    print("  1. Check all installed apps")
    print("  2. Verify which migrations are applied")
    print("  3. Check if database tables/columns exist")
    print("  4. Fix migration state mismatches")
    print()
    
    # Get all installed apps
    installed_apps = [
        'admin',
        'auth',
        'contenttypes',
        'sessions',
        'authtoken',
        'assets',
        'discovery',
        'users',
        'admin_dashboard',
        'crm_integration',
        'crm',
    ]
    
    print("Checking migration state for all apps...")
    print("-" * 70)
    
    issues_found = []
    
    for app_name in installed_apps:
        print(f"\n{app_name}:")
        
        try:
            # Get applied migrations for this app
            applied = get_applied_migrations(app_name)
            
            # Get app config
            try:
                app_config = apps.get_app_config(app_name)
                
                # Check if app has models
                if app_config.models:
                    # Check if tables exist
                    tables_exist = []
                    for model in app_config.get_models():
                        table_name = model._meta.db_table
                        exists = check_table_exists(table_name)
                        tables_exist.append(exists)
                        status = "✓" if exists else "✗"
                        print(f"  {status} Table: {table_name}")
                    
                    # If tables exist but no migrations applied, there's an issue
                    if any(tables_exist) and len(applied) == 0:
                        print(f"  ⚠ WARNING: Tables exist but no migrations marked as applied!")
                        issues_found.append((app_name, 'tables_exist_no_migrations'))
                    elif all(tables_exist) and len(applied) > 0:
                        print(f"  ✓ {len(applied)} migrations applied, tables exist")
                    
            except LookupError:
                print(f"  ℹ App not found in installed apps")
                
        except Exception as e:
            print(f"  ✗ Error checking {app_name}: {str(e)}")
    
    print()
    print("=" * 70)
    
    if issues_found:
        print(f"\nFound {len(issues_found)} apps with migration issues:")
        for app_name, issue_type in issues_found:
            print(f"  - {app_name}: {issue_type}")
        print()
        
        response = input("Do you want to fake all migrations for these apps? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Operation cancelled.")
            print()
            print("You can manually fix each app with:")
            print("  python manage.py migrate <app_name> --fake")
            return 0
        
        print()
        print("Faking migrations for apps with issues...")
        print("-" * 70)
        
        for app_name, _ in issues_found:
            try:
                print(f"\nFaking migrations for {app_name}...")
                call_command('migrate', app_name, '--fake', verbosity=1)
                print(f"  ✓ {app_name} migrations faked successfully")
            except Exception as e:
                print(f"  ✗ Error faking {app_name}: {str(e)}")
        
        print()
        print("✓ Completed faking migrations for problematic apps")
    
    else:
        print("\nNo obvious migration issues found.")
        print("Attempting to apply all migrations normally...")
        print()
    
    # Now try to migrate everything
    print()
    print("=" * 70)
    print("Attempting to migrate all apps...")
    print("=" * 70)
    print()
    
    try:
        call_command('migrate', verbosity=2)
        print()
        print("✓ All migrations applied successfully!")
        
    except Exception as e:
        error_msg = str(e)
        print()
        print("✗ Migration failed with error:")
        print(f"  {error_msg}")
        print()
        
        # Check for specific error patterns
        if "already exists" in error_msg:
            print("DIAGNOSIS: Column or table already exists")
            print()
            
            # Try to extract app and migration from error
            if "assets" in error_msg.lower():
                print("The issue is with the 'assets' app.")
                print()
                print("SOLUTION:")
                print("  Run this command to fake the specific migration:")
                print("  python manage.py migrate assets 0002 --fake")
                print()
                print("  Or run:")
                print("  python fix_partial_migrations.py")
                
            else:
                print("SOLUTION:")
                print("  Try faking the problematic migration:")
                print("  python manage.py migrate <app_name> <migration_number> --fake")
        
        return 1
    
    print()
    print("=" * 70)
    print("VERIFICATION")
    print("=" * 70)
    print()
    print("Showing migration status for all apps:")
    print()
    
    try:
        call_command('showmigrations', verbosity=1)
    except Exception as e:
        print(f"Error showing migrations: {str(e)}")
    
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print("✓ Migration state fix completed!")
    print()
    print("Next steps:")
    print("  1. Verify your application works correctly")
    print("  2. Test database operations")
    print("  3. For future migrations, use:")
    print("     python manage.py makemigrations")
    print("     python manage.py migrate")
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