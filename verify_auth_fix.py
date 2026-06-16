#!/usr/bin/env python
"""
Verify that auth tables are fixed
"""

import os
import sys
import django

def verify_auth_fix():
    """Verify auth tables are working"""
    print("=" * 60)
    print("Verifying Auth Tables Fix")
    print("=" * 60)
    
    # Set environment variables for production
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
    os.environ['VERCEL'] = '1'  # Force production mode
    
    # Add Django project to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'assetmanagement'))
    
    # Setup Django
    django.setup()
    
    from django.db import connection
    
    try:
        with connection.cursor() as cursor:
            # Check for auth_user_user_permissions table
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'auth_user_user_permissions'
                )
            """)
            exists = cursor.fetchone()[0]
            
            if exists:
                print("✓ auth_user_user_permissions table exists")
                
                # Check table structure
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_schema = 'public' AND table_name = 'auth_user_user_permissions'
                    ORDER BY ordinal_position
                """)
                columns = cursor.fetchall()
                print("\nTable structure:")
                for col_name, col_type in columns:
                    print(f"  - {col_name}: {col_type}")
                
                # Check auth migrations
                cursor.execute("""
                    SELECT name FROM django_migrations 
                    WHERE app = 'auth' 
                    ORDER BY name
                """)
                migrations = [row[0] for row in cursor.fetchall()]
                print(f"\nAuth migrations applied ({len(migrations)}):")
                for migration in migrations:
                    print(f"  ✓ {migration}")
                
                # Test a query that would have failed before
                print("\nTesting query that previously failed...")
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM auth_permission 
                    INNER JOIN auth_user_user_permissions 
                    ON auth_permission.id = auth_user_user_permissions.permission_id
                """)
                count = cursor.fetchone()[0]
                print(f"✓ Query successful! Found {count} user permissions")
                
                return True
            else:
                print("❌ auth_user_user_permissions table still missing")
                return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = verify_auth_fix()
    if success:
        print("\n✅ All auth tables are working correctly!")
        print("\nYou can now access the admin panel at:")
        print("https://fagiassets.onrender.com/admin/auth/user/21/change/")
    else:
        print("\n❌ Auth tables verification failed")
    sys.exit(0 if success else 1)