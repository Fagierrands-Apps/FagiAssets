#!/usr/bin/env python
"""
Fix missing auth tables by creating them manually
The auth_user_user_permissions table is missing from the database
"""

import os
import sys
import django

def fix_missing_auth_tables():
    """Create missing auth tables"""
    print("=" * 60)
    print("Fixing Missing Auth Tables")
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
            print("Creating missing auth tables...")
            
            # Create auth_user_user_permissions table
            print("Creating auth_user_user_permissions table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auth_user_user_permissions (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
                    permission_id INTEGER NOT NULL REFERENCES auth_permission(id) ON DELETE CASCADE,
                    UNIQUE (user_id, permission_id)
                );
            """)
            
            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS auth_user_user_permissions_user_id_idx 
                ON auth_user_user_permissions(user_id);
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS auth_user_user_permissions_permission_id_idx 
                ON auth_user_user_permissions(permission_id);
            """)
            
            print("✓ auth_user_user_permissions table created")
            
            # Verify the table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'auth_user_user_permissions'
                )
            """)
            exists = cursor.fetchone()[0]
            
            if exists:
                print("✓ Verified: auth_user_user_permissions table exists")
                
                # Update migration records to reflect all auth migrations
                print("\nUpdating migration records...")
                
                auth_migrations = [
                    ('auth', '0002_alter_permission_name_max_length'),
                    ('auth', '0003_alter_user_email_max_length'),
                    ('auth', '0004_alter_user_username_opts'),
                    ('auth', '0005_alter_user_last_login_null'),
                    ('auth', '0006_require_contenttypes_0002'),
                    ('auth', '0007_alter_validators_add_error_messages'),
                    ('auth', '0008_alter_user_username_max_length'),
                    ('auth', '0009_alter_user_last_name_max_length'),
                    ('auth', '0010_alter_group_name_max_length'),
                    ('auth', '0011_update_proxy_permissions'),
                    ('auth', '0012_alter_user_first_name_max_length')
                ]
                
                for app, name in auth_migrations:
                    # Check if migration already exists
                    cursor.execute(
                        'SELECT COUNT(*) FROM django_migrations WHERE app = %s AND name = %s',
                        [app, name]
                    )
                    count = cursor.fetchone()[0]
                    
                    if count == 0:
                        cursor.execute(
                            'INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, NOW())',
                            [app, name]
                        )
                        print(f"  ✓ Added {app}.{name}")
                    else:
                        print(f"  - Already exists: {app}.{name}")
                
                print("\n✓ All auth migration records updated")
                return True
            else:
                print("❌ Failed to create auth_user_user_permissions table")
                return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = fix_missing_auth_tables()
    if success:
        print("\n✅ Auth tables fixed successfully!")
        print("The admin panel should now work correctly.")
    else:
        print("\n❌ Failed to fix auth tables")
    sys.exit(0 if success else 1)