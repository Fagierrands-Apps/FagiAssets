#!/usr/bin/env python
"""
Fix Django migration state when tables already exist in the database.

This script marks all existing migrations as applied without actually running them,
which is useful when the database tables already exist but Django doesn't know about them.
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

def main():
    print("=" * 70)
    print("Django Migration State Fix Tool")
    print("=" * 70)
    print()
    
    # Check if key tables exist
    print("Checking database state...")
    tables_to_check = [
        'django_admin_log',
        'auth_user',
        'auth_group',
        'django_content_type',
        'django_session',
    ]
    
    existing_tables = []
    for table in tables_to_check:
        exists = check_table_exists(table)
        status = "✓ EXISTS" if exists else "✗ MISSING"
        print(f"  {table}: {status}")
        if exists:
            existing_tables.append(table)
    
    print()
    
    if len(existing_tables) == 0:
        print("No tables found. You can run 'python manage.py migrate' normally.")
        return
    
    if len(existing_tables) > 0:
        print(f"Found {len(existing_tables)} existing tables.")
        print("This indicates the database has been partially or fully migrated.")
        print()
        
        response = input("Do you want to mark all migrations as applied? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Operation cancelled.")
            return
        
        print()
        print("Marking migrations as applied (fake)...")
        print("-" * 70)
        
        try:
            # Fake all migrations for all apps
            call_command('migrate', '--fake', verbosity=2)
            
            print("-" * 70)
            print()
            print("✓ SUCCESS!")
            print()
            print("All migrations have been marked as applied.")
            print("Your database state is now synchronized with Django's migration system.")
            print()
            print("Next steps:")
            print("  1. Run 'python manage.py makemigrations' to create any new migrations")
            print("  2. Run 'python manage.py migrate' to apply any new migrations")
            
        except Exception as e:
            print()
            print("✗ ERROR occurred:")
            print(f"  {str(e)}")
            print()
            print("Alternative approach:")
            print("  Try running these commands manually:")
            print("    python manage.py migrate --fake-initial")
            print("  or")
            print("    python manage.py migrate <app_name> --fake")
            return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())