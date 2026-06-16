#!/usr/bin/env python
"""
Verify that the django_admin_log fix is working correctly
"""

import os
import sys
import django

def verify_admin_log_fix():
    """Verify the django_admin_log fix"""
    print("Verifying django_admin_log fix...")
    
    # Set environment variables
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
    
    # Add Django project to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'assetmanagement'))
    
    # Setup Django
    django.setup()
    
    from django.db import connection
    
    with connection.cursor() as cursor:
        print("\n✓ Verification Results:")
        print("=" * 60)
        
        # 1. Check constraint
        print("\n1. Foreign Key Constraint:")
        cursor.execute("""
            SELECT
                tc.constraint_name,
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
            AND tc.constraint_name LIKE '%user_id%'
        """)
        constraint = cursor.fetchone()
        if constraint and constraint[2] == 'auth_user':
            print(f"   ✓ Correct: {constraint[1]} -> {constraint[2]}.{constraint[3]}")
        else:
            print(f"   ✗ Incorrect or missing constraint")
            if constraint:
                print(f"     Found: {constraint[1]} -> {constraint[2]}.{constraint[3]}")
        
        # 2. Check for orphaned entries
        print("\n2. Orphaned Entries:")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM django_admin_log 
            WHERE user_id NOT IN (SELECT id FROM auth_user)
        """)
        orphaned = cursor.fetchone()[0]
        if orphaned == 0:
            print(f"   ✓ No orphaned entries (count: {orphaned})")
        else:
            print(f"   ✗ Found {orphaned} orphaned entries")
        
        # 3. Check admin log entries
        print("\n3. Admin Log Entries:")
        cursor.execute("SELECT COUNT(*) FROM django_admin_log")
        total = cursor.fetchone()[0]
        print(f"   Total entries: {total}")
        
        # 4. Check user tables
        print("\n4. User Tables:")
        cursor.execute("SELECT COUNT(*) FROM auth_user")
        auth_count = cursor.fetchone()[0]
        print(f"   auth_user: {auth_count} users")
        
        cursor.execute("SELECT COUNT(*) FROM accounts_user")
        accounts_count = cursor.fetchone()[0]
        print(f"   accounts_user: {accounts_count} users")
        
        # 5. Test query that was failing
        print("\n5. Test Query (simulating admin action):")
        try:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM django_admin_log dal
                INNER JOIN auth_user au ON dal.user_id = au.id
                WHERE au.id = 17
            """)
            count = cursor.fetchone()[0]
            print(f"   ✓ Query successful (found {count} log entries for user 17)")
        except Exception as e:
            print(f"   ✗ Query failed: {e}")
        
        print("\n" + "=" * 60)
        print("\n✅ Verification complete!")
        
        if constraint and constraint[2] == 'auth_user' and orphaned == 0:
            print("\n🎉 All checks passed! The admin panel should work correctly.")
        else:
            print("\n⚠️  Some issues found. Please review the results above.")

if __name__ == '__main__':
    verify_admin_log_fix()