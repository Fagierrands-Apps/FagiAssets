#!/usr/bin/env python
"""
Deployment script for Vercel
Ensures database is properly configured and migrations are run
"""

import os
import sys
import subprocess
import django
from django.conf import settings

def setup_django():
    """Set up Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'assetmanagement'))
    django.setup()

def check_database_config():
    """Check that database is properly configured"""
    print("Checking database configuration...")
    
    from django.db import connection
    
    try:
        db_vendor = connection.vendor
        print(f"Database vendor: {db_vendor}")
        
        if db_vendor == 'postgresql':
            print("✓ PostgreSQL detected - good for production")
            return True
        elif db_vendor == 'sqlite':
            print("✗ SQLite detected - this will cause readonly errors in production")
            return False
        else:
            print(f"? Unknown database vendor: {db_vendor}")
            return False
            
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def run_migrations():
    """Run database migrations"""
    print("Running migrations...")
    
    try:
        from django.core.management import execute_from_command_line
        
        # Run migrations
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("✓ Migrations completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        return False

def collect_static():
    """Collect static files"""
    print("Collecting static files...")
    
    try:
        from django.core.management import execute_from_command_line
        
        # Collect static files
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("✓ Static files collected successfully")
        return True
        
    except Exception as e:
        print(f"✗ Static file collection failed: {e}")
        return False

def create_superuser():
    """Create superuser if it doesn't exist"""
    print("Checking for superuser...")
    
    try:
        from django.contrib.auth.models import User
        
        if not User.objects.filter(is_superuser=True).exists():
            print("No superuser found, creating one...")
            
            # Create superuser with default credentials
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'  # Change this in production
            )
            print("✓ Superuser created: admin/admin123")
        else:
            print("✓ Superuser already exists")
            
        return True
        
    except Exception as e:
        print(f"✗ Superuser creation failed: {e}")
        return False

def main():
    """Main deployment function"""
    print("=" * 60)
    print("Django Deployment Script")
    print("=" * 60)
    
    # Setup Django
    setup_django()
    
    # Check database configuration
    if not check_database_config():
        print("\n✗ Database configuration check failed!")
        print("Make sure DATABASE_URL environment variable is set with PostgreSQL connection string")
        sys.exit(1)
    
    # Run migrations
    if not run_migrations():
        print("\n✗ Migration failed!")
        sys.exit(1)
    
    # Collect static files
    if not collect_static():
        print("\n✗ Static file collection failed!")
        sys.exit(1)
    
    # Create superuser if needed
    if not create_superuser():
        print("\n✗ Superuser creation failed!")
        sys.exit(1)
    
    print("\n✓ Deployment completed successfully!")
    print("Your Django app is ready for production.")
    print("\nNext steps:")
    print("1. Deploy to Vercel: vercel --prod")
    print("2. Set environment variables in Vercel dashboard:")
    print("   - DJANGO_SETTINGS_MODULE=assetmanager.settings")
    print("   - DATABASE_URL=postgresql://...")
    print("   - VERCEL=1")
    print("3. Test login functionality")

if __name__ == '__main__':
    main()