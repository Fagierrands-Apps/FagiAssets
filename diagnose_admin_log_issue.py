#!/usr/bin/env python
"""
Diagnose the django_admin_log foreign key constraint issue
"""

import os
import sys
import django

def diagnose_admin_log():
    """Check the admin log table and its constraints"""
    print("Diagnosing django_admin_log issue...")
    
    # Set environment variables
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
    
    # Add Django project to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'assetmanagement'))
    
    # Setup Django
    django.setup()
    
    from django.db import connection
    
    with connection.cursor() as cursor:
        # Check what tables exist
        print("\n1. Checking user-related tables:")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%user%'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        for table in tables:
            print(f"   - {table[0]}")
        
        # Check django_admin_log structure
        print("\n2. Checking django_admin_log structure:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'django_admin_log'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        for col in columns:
            print(f"   - {col[0]}: {col[1]} (nullable: {col[2]})")
        
        # Check foreign key constraints on django_admin_log
        print("\n3. Checking foreign key constraints on django_admin_log:")
        cursor.execute("""
            SELECT
                tc.constraint_name,
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_name = 'django_admin_log'
        """)
        constraints = cursor.fetchall()
        for constraint in constraints:
            print(f"   - {constraint[0]}: {constraint[1]}.{constraint[2]} -> {constraint[3]}.{constraint[4]}")
        
        # Check if accounts_user table exists
        print("\n4. Checking if accounts_user table exists:")
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'accounts_user'
            )
        """)
        exists = cursor.fetchone()[0]
        print(f"   accounts_user exists: {exists}")
        
        # Check if auth_user table exists and count users
        print("\n5. Checking auth_user table:")
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'auth_user'
            )
        """)
        exists = cursor.fetchone()[0]
        print(f"   auth_user exists: {exists}")
        
        if exists:
            cursor.execute("SELECT COUNT(*) FROM auth_user")
            count = cursor.fetchone()[0]
            print(f"   auth_user count: {count}")
            
            # Check if user 17 exists
            cursor.execute("SELECT id, username FROM auth_user WHERE id = 17")
            user = cursor.fetchone()
            if user:
                print(f"   User 17 exists: {user[1]}")
            else:
                print(f"   User 17 does NOT exist in auth_user")
        
        # Check django_admin_log entries
        print("\n6. Checking django_admin_log entries:")
        cursor.execute("SELECT COUNT(*) FROM django_admin_log")
        count = cursor.fetchone()[0]
        print(f"   Total admin log entries: {count}")
        
        # Check for orphaned user_ids in admin log
        print("\n7. Checking for orphaned user_ids in django_admin_log:")
        cursor.execute("""
            SELECT DISTINCT user_id 
            FROM django_admin_log 
            WHERE user_id NOT IN (SELECT id FROM auth_user)
            LIMIT 10
        """)
        orphaned = cursor.fetchall()
        if orphaned:
            print(f"   Found {len(orphaned)} orphaned user_ids:")
            for user_id in orphaned:
                print(f"      - user_id: {user_id[0]}")
        else:
            print("   No orphaned user_ids found")
        
        # Check current user (who is logged in)
        print("\n8. Checking who is trying to perform the action:")
        print("   (This would be user_id 17 based on the error)")

if __name__ == '__main__':
    diagnose_admin_log()
    print("\n✅ Diagnosis complete!")