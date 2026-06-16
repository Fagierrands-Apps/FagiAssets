#!/usr/bin/env python
"""
Fix auth tables script
This script will create the missing auth_user table by running migrations properly
"""

import os
import sys
import django

def fix_auth_tables():
    """Fix missing auth tables"""
    print("=" * 60)
    print("Fixing Auth Tables")
    print("=" * 60)
    
    # Set environment variables for production
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
    os.environ['VERCEL'] = '1'  # Force production mode
    
    # Use the original postgres database
    os.environ['DATABASE_URL'] = 'postgresql://postgres.dxesmzogjpxswxhsomgf:OnFRtf0SmpHwgNaQ@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres'
    
    # Add Django project to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'assetmanagement'))
    
    # Setup Django
    django.setup()
    
    from django.db import connection
    from django.core.management import execute_from_command_line
    
    try:
        with connection.cursor() as cursor:
            print("Checking current database state...")
            
            # Check if auth_user exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'auth_user'
                )
            """)
            auth_user_exists = cursor.fetchone()[0]
            
            if auth_user_exists:
                print("✓ auth_user table already exists")
                return True
            
            print("auth_user table missing - creating it...")
            
            # Create auth_user table manually
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auth_user (
                    id SERIAL PRIMARY KEY,
                    password VARCHAR(128) NOT NULL,
                    last_login TIMESTAMP WITH TIME ZONE,
                    is_superuser BOOLEAN NOT NULL,
                    username VARCHAR(150) NOT NULL UNIQUE,
                    first_name VARCHAR(150) NOT NULL,
                    last_name VARCHAR(150) NOT NULL,
                    email VARCHAR(254) NOT NULL,
                    is_staff BOOLEAN NOT NULL,
                    is_active BOOLEAN NOT NULL,
                    date_joined TIMESTAMP WITH TIME ZONE NOT NULL
                );
            """)
            
            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS auth_user_username_idx ON auth_user(username);
            """)
            
            print("✓ auth_user table created")
            
            # Now run our app migrations
            print("Running asset management migrations...")
            execute_from_command_line(['manage.py', 'migrate', 'assets', '--fake-initial'])
            execute_from_command_line(['manage.py', 'migrate', 'users', '--fake-initial'])
            execute_from_command_line(['manage.py', 'migrate', 'discovery', '--fake-initial'])
            
            print("✓ Migrations completed")
            
            # Create a test superuser
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
            
            return True
            
    except Exception as e:
        print(f"❌ Failed to fix auth tables: {e}")
        return False

if __name__ == '__main__':
    success = fix_auth_tables()
    if success:
        print("\n✅ Auth tables fixed successfully!")
        print("You can now test login at: https://fagiassets.vercel.app/login/")
        print("Username: admin")
        print("Password: FagiAssets2024!")
    else:
        print("\n❌ Failed to fix auth tables")
    sys.exit(0 if success else 1)