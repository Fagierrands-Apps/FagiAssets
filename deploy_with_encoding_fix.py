#!/usr/bin/env python
"""
Deployment script with encoding fix
This script will deploy the application with the correct database settings
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def deploy_with_encoding_fix():
    """Deploy application with encoding fix"""
    print("=" * 60)
    print("Deploying with Encoding Fix")
    print("=" * 60)
    
    # Set environment variables for production
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
    os.environ['VERCEL'] = '1'  # Force production mode
    
    # Use the original postgres database with proper encoding
    os.environ['DATABASE_URL'] = 'postgresql://postgres.dxesmzogjpxswxhsomgf:OnFRtf0SmpHwgNaQ@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres?sslmode=require&options=-c%20default_transaction_isolation%3Dread_committed'
    
    # Add Django project to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'assetmanagement'))
    
    # Setup Django
    django.setup()
    
    print("Running deployment steps...")
    
    try:
        # Step 1: Run migrations
        print("1. Running migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("✓ Migrations completed")
        
        # Step 2: Collect static files
        print("2. Collecting static files...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("✓ Static files collected")
        
        # Step 3: Create superuser if needed
        print("3. Checking superuser...")
        from django.contrib.auth.models import User
        
        if not User.objects.filter(username='admin').exists():
            user = User.objects.create_superuser(
                username='admin',
                email='admin@fagiassets.com',
                password='FagiAssets2024!'
            )
            print(f"✓ Superuser created: {user.username}")
        else:
            print("✓ Superuser already exists")
        
        # Step 4: Test login functionality
        print("4. Testing login functionality...")
        from django.contrib.auth import authenticate
        
        user = authenticate(username='admin', password='FagiAssets2024!')
        if user:
            print("✓ Login test successful")
        else:
            print("✗ Login test failed")
            return False
        
        # Step 5: Test database connection
        print("5. Testing database connection...")
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            print(f"✓ Database: {version.split()[0]} {version.split()[1]}")
            
            cursor.execute("SELECT COUNT(*) FROM auth_user")
            user_count = cursor.fetchone()[0]
            print(f"✓ Users in database: {user_count}")
        
        print("\n✅ Deployment completed successfully!")
        
        print("\nDeployment Summary:")
        print("- Database: PostgreSQL with encoding fix")
        print("- Migrations: Applied")
        print("- Static files: Collected")
        print("- Superuser: Created/Verified")
        print("- Login: Tested and working")
        
        print("\nEnvironment Variables for Vercel:")
        print("DJANGO_SETTINGS_MODULE=assetmanager.settings")
        print("VERCEL=1")
        print("DATABASE_URL=postgresql://postgres.dxesmzogjpxswxhsomgf:OnFRtf0SmpHwgNaQ@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres?sslmode=require&options=-c%20default_transaction_isolation%3Dread_committed")
        
        print("\nLogin Credentials:")
        print("Username: admin")
        print("Password: FagiAssets2024!")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False

if __name__ == '__main__':
    success = deploy_with_encoding_fix()
    sys.exit(0 if success else 1)