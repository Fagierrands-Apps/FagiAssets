#!/usr/bin/env python
"""
Complete fix for django_admin_log foreign key constraint
"""

import os
import sys
import django

def complete_admin_log_fix():
    """Fix the foreign key constraint on django_admin_log"""
    print("Fixing django_admin_log foreign key constraint...")
    
    # Set environment variables
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
    
    # Add Django project to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'assetmanagement'))
    
    # Setup Django
    django.setup()
    
    from django.db import connection
    
    with connection.cursor() as cursor:
        print("\n1. Checking current constraint...")
        cursor.execute("""
            SELECT
                tc.constraint_name,
                ccu.table_name AS foreign_table_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_name = 'django_admin_log'
            AND tc.constraint_name LIKE '%user_id%'
        """)
        constraint = cursor.fetchone()
        
        if constraint:
            print(f"   Current constraint: {constraint[0]} -> {constraint[1]}")
            constraint_name = constraint[0]
            
            # Drop the constraint if it exists
            print("\n2. Dropping incorrect foreign key constraint...")
            cursor.execute(f"""
                ALTER TABLE django_admin_log 
                DROP CONSTRAINT IF EXISTS {constraint_name}
            """)
            print(f"   ✓ Dropped constraint: {constraint_name}")
        else:
            print("   No user_id constraint found (may have been dropped already)")
        
        print("\n3. Cleaning up orphaned admin log entries...")
        # Check for orphaned entries
        cursor.execute("""
            SELECT COUNT(*) 
            FROM django_admin_log 
            WHERE user_id NOT IN (SELECT id FROM auth_user)
        """)
        orphaned_count = cursor.fetchone()[0]
        
        if orphaned_count > 0:
            print(f"   Found {orphaned_count} orphaned entries")
            # Show which user_ids are orphaned
            cursor.execute("""
                SELECT DISTINCT user_id 
                FROM django_admin_log 
                WHERE user_id NOT IN (SELECT id FROM auth_user)
            """)
            orphaned_ids = cursor.fetchall()
            print(f"   Orphaned user_ids: {[uid[0] for uid in orphaned_ids]}")
            
            # Delete orphaned entries
            cursor.execute("""
                DELETE FROM django_admin_log 
                WHERE user_id NOT IN (SELECT id FROM auth_user)
            """)
            print(f"   ✓ Deleted {orphaned_count} orphaned entries")
        else:
            print("   No orphaned entries found")
        
        print("\n4. Creating correct foreign key constraint to auth_user...")
        try:
            cursor.execute("""
                ALTER TABLE django_admin_log
                ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_auth_user_id
                FOREIGN KEY (user_id) 
                REFERENCES auth_user(id) 
                ON DELETE CASCADE
                DEFERRABLE INITIALLY DEFERRED
            """)
            print("   ✓ Created new constraint pointing to auth_user")
        except Exception as e:
            if "already exists" in str(e):
                print("   ✓ Constraint already exists")
            else:
                raise
        
        print("\n5. Verifying new constraint...")
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
        new_constraint = cursor.fetchone()
        if new_constraint:
            print(f"   ✓ Constraint: {new_constraint[0]}")
            print(f"     {new_constraint[1]} -> {new_constraint[2]}.{new_constraint[3]}")
        else:
            print("   ✗ No constraint found!")
        
        print("\n6. Verifying no orphaned entries remain...")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM django_admin_log 
            WHERE user_id NOT IN (SELECT id FROM auth_user)
        """)
        orphaned_count = cursor.fetchone()[0]
        print(f"   Orphaned entries: {orphaned_count} (should be 0)")
        
        print("\n7. Testing the fix...")
        # Try to insert a test log entry for user 17
        cursor.execute("""
            SELECT id FROM django_content_type WHERE app_label = 'auth' AND model = 'user' LIMIT 1
        """)
        content_type = cursor.fetchone()
        if content_type:
            content_type_id = content_type[0]
            print(f"   Testing with user_id=17, content_type_id={content_type_id}")
            
            # This should work now
            try:
                cursor.execute("""
                    INSERT INTO django_admin_log 
                    (action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id)
                    VALUES (NOW(), '17', 'Test Entry', 2, '[]', %s, 17)
                    RETURNING id
                """, [content_type_id])
                test_id = cursor.fetchone()[0]
                print(f"   ✓ Successfully inserted test entry (id={test_id})")
                
                # Clean up test entry
                cursor.execute("DELETE FROM django_admin_log WHERE id = %s", [test_id])
                print(f"   ✓ Cleaned up test entry")
            except Exception as e:
                print(f"   ✗ Test failed: {e}")
        else:
            print("   Could not find content type for testing")

if __name__ == '__main__':
    complete_admin_log_fix()
    print("\n✅ Fix complete! The admin panel should now work correctly.")
    print("\nYou can now:")
    print("  - Access /admin/auth/user/21/password/ without errors")
    print("  - Change user passwords in the Django admin")
    print("  - All admin actions will be logged correctly")