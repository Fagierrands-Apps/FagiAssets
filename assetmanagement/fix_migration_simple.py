#!/usr/bin/env python
"""
Simple fix for Django migration state when tables already exist.

This uses Django's --fake-initial flag which automatically detects
existing tables and marks only the initial migrations as applied.
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

def main():
    print("=" * 70)
    print("Django Migration State Fix - Simple Method")
    print("=" * 70)
    print()
    print("This will use Django's --fake-initial flag to automatically")
    print("detect existing tables and mark initial migrations as applied.")
    print()
    
    response = input("Continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Operation cancelled.")
        return
    
    print()
    print("Running: python manage.py migrate --fake-initial")
    print("-" * 70)
    
    try:
        call_command('migrate', '--fake-initial', verbosity=2)
        
        print("-" * 70)
        print()
        print("✓ SUCCESS!")
        print()
        print("Migration state has been synchronized.")
        print()
        print("You can now run:")
        print("  python manage.py makemigrations")
        print("  python manage.py migrate")
        
    except Exception as e:
        print()
        print("✗ ERROR occurred:")
        print(f"  {str(e)}")
        print()
        print("If this doesn't work, you may need to:")
        print("  1. Check your database connection")
        print("  2. Ensure all tables are properly created")
        print("  3. Try the manual approach with --fake flag")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())