#!/usr/bin/env python
"""
Check the accounts_user table contents
"""

import os
import sys
import django

def check_accounts_user():
    """Check what's in the accounts_user table"""
    print("Checking accounts_user table...")
    
    # Set environment variables
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
    
    # Add Django project to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'assetmanagement'))
    
    # Setup Django
    django.setup()
    
    from django.db import connection
    
    with connection.cursor() as cursor:
        # Check accounts_user structure
        print("\n1. accounts_user table structure:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'accounts_user'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        for col in columns:
            print(f"   - {col[0]}: {col[1]} (nullable: {col[2]})")
        
        # Count users in accounts_user
        print("\n2. Users in accounts_user:")
        cursor.execute("SELECT COUNT(*) FROM accounts_user")
        count = cursor.fetchone()[0]
        print(f"   Total: {count}")
        
        if count > 0:
            cursor.execute("SELECT id, username, email, is_active, is_staff, is_superuser FROM accounts_user ORDER BY id LIMIT 20")
            users = cursor.fetchall()
            print("\n   Users:")
            for user in users:
                print(f"      ID {user[0]}: {user[1]} ({user[2]}) - Active: {user[3]}, Staff: {user[4]}, Super: {user[5]}")
        
        # Count users in auth_user
        print("\n3. Users in auth_user:")
        cursor.execute("SELECT COUNT(*) FROM auth_user")
        count = cursor.fetchone()[0]
        print(f"   Total: {count}")
        
        cursor.execute("SELECT id, username, email, is_active, is_staff, is_superuser FROM auth_user ORDER BY id LIMIT 20")
        users = cursor.fetchall()
        print("\n   Users:")
        for user in users:
            print(f"      ID {user[0]}: {user[1]} ({user[2]}) - Active: {user[3]}, Staff: {user[4]}, Super: {user[5]}")
        
        # Check which app is referenced in migrations
        print("\n4. Checking migrations for user model references:")
        cursor.execute("""
            SELECT app, name 
            FROM django_migrations 
            WHERE app IN ('auth', 'accounts', 'users')
            ORDER BY app, name
        """)
        migrations = cursor.fetchall()
        for mig in migrations:
            print(f"   - {mig[0]}.{mig[1]}")

if __name__ == '__main__':
    check_accounts_user()
    print("\n✅ Check complete!")