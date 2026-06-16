#!/usr/bin/env python
"""
Comprehensive Django migration state fix tool.

Provides multiple methods to fix migration state issues when tables already exist.
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

def check_migration_table():
    """Check if django_migrations table exists and has records."""
    if not check_table_exists('django_migrations'):
        return False, 0
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM django_migrations;")
        count = cursor.fetchone()[0]
        return True, count

def list_apps_and_tables():
    """List all installed apps and their expected tables."""
    print("\nInstalled Django Apps:")
    print("-" * 70)
    
    for app_config in apps.get_app_configs():
        if app_config.models:
            print(f"\n{app_config.label}:")
            for model in app_config.get_models():
                table_name = model._meta.db_table
                exists = check_table_exists(table_name)
                status = "✓" if exists else "✗"
                print(f"  {status} {table_name}")

def method_1_fake_initial():
    """Method 1: Use --fake-initial flag."""
    print("\n" + "=" * 70)
    print("METHOD 1: Fake Initial Migrations")
    print("=" * 70)
    print("\nThis method uses Django's --fake-initial flag.")
    print("It will mark initial migrations as applied if their tables exist.")
    print()
    
    try:
        call_command('migrate', '--fake-initial', verbosity=2)
        print("\n✓ Method 1 completed successfully!")
        return True
    except Exception as e:
        print(f"\n✗ Method 1 failed: {str(e)}")
        return False

def method_2_fake_all():
    """Method 2: Fake all migrations."""
    print("\n" + "=" * 70)
    print("METHOD 2: Fake All Migrations")
    print("=" * 70)
    print("\nThis method marks ALL migrations as applied without running them.")
    print("Use this if Method 1 didn't work and you're sure all tables exist.")
    print()
    
    response = input("Are you sure you want to fake ALL migrations? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Skipped.")
        return False
    
    try:
        call_command('migrate', '--fake', verbosity=2)
        print("\n✓ Method 2 completed successfully!")
        return True
    except Exception as e:
        print(f"\n✗ Method 2 failed: {str(e)}")
        return False

def method_3_fake_per_app():
    """Method 3: Fake migrations per app."""
    print("\n" + "=" * 70)
    print("METHOD 3: Fake Migrations Per App")
    print("=" * 70)
    print("\nThis method allows you to fake migrations for specific apps.")
    print()
    
    # List of apps that typically need migration
    apps_to_migrate = [
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
    
    print("Apps to process:")
    for i, app in enumerate(apps_to_migrate, 1):
        print(f"  {i}. {app}")
    
    print()
    response = input("Fake migrations for these apps? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Skipped.")
        return False
    
    success_count = 0
    fail_count = 0
    
    for app in apps_to_migrate:
        try:
            print(f"\nProcessing {app}...")
            call_command('migrate', app, '--fake', verbosity=1)
            success_count += 1
        except Exception as e:
            print(f"  ✗ Failed: {str(e)}")
            fail_count += 1
    
    print(f"\n✓ Completed: {success_count} succeeded, {fail_count} failed")
    return success_count > 0

def main():
    print("=" * 70)
    print("Django Migration State Fix - Comprehensive Tool")
    print("=" * 70)
    
    # Check database state
    print("\n1. Checking database state...")
    print("-" * 70)
    
    migration_table_exists, migration_count = check_migration_table()
    
    if migration_table_exists:
        print(f"✓ django_migrations table exists with {migration_count} records")
    else:
        print("✗ django_migrations table does not exist")
    
    # Check key tables
    key_tables = ['django_admin_log', 'auth_user', 'auth_group', 'django_content_type']
    existing_count = sum(1 for table in key_tables if check_table_exists(table))
    
    print(f"\nKey tables found: {existing_count}/{len(key_tables)}")
    for table in key_tables:
        exists = check_table_exists(table)
        status = "✓" if exists else "✗"
        print(f"  {status} {table}")
    
    # List all apps and tables
    list_apps_and_tables()
    
    # Provide options
    print("\n" + "=" * 70)
    print("AVAILABLE METHODS")
    print("=" * 70)
    print("\n1. Fake Initial (Recommended) - Marks initial migrations as applied")
    print("2. Fake All - Marks ALL migrations as applied")
    print("3. Fake Per App - Fake migrations for specific apps")
    print("4. Show Migration Status - Just show current status")
    print("5. Exit")
    
    while True:
        print()
        choice = input("Select a method (1-5): ").strip()
        
        if choice == '1':
            if method_1_fake_initial():
                break
        elif choice == '2':
            if method_2_fake_all():
                break
        elif choice == '3':
            if method_3_fake_per_app():
                break
        elif choice == '4':
            print("\nShowing migration status...")
            try:
                call_command('showmigrations', verbosity=2)
            except Exception as e:
                print(f"Error: {str(e)}")
        elif choice == '5':
            print("Exiting...")
            return 0
        else:
            print("Invalid choice. Please select 1-5.")
    
    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("\n1. Verify migration status:")
    print("   python manage.py showmigrations")
    print("\n2. Create new migrations if needed:")
    print("   python manage.py makemigrations")
    print("\n3. Apply new migrations:")
    print("   python manage.py migrate")
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