#!/usr/bin/env python
"""
Restore auth migration records and create missing tables
"""

import os
import sys
import django

def restore_auth_migrations():
    """Restore the auth migration records and create missing tables"""
    print("Restoring auth migration records and tables...")

    # Set environment variables
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')

    # Add Django project to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'assetmanagement'))

    # Setup Django
    django.setup()

    from django.db import connection

    with connection.cursor() as cursor:
        # First, create missing auth_user_user_permissions table if needed
        print("Checking for missing auth tables...")
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'auth_user_user_permissions'
            )
        """)
        exists = cursor.fetchone()[0]
        
        if not exists:
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
        else:
            print("✓ auth_user_user_permissions table already exists")

        # Now restore migration records
        migrations = [
            ('auth', '0001_initial'),
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
            ('auth', '0012_alter_user_first_name_max_length'),
            ('contenttypes', '0001_initial'),
            ('contenttypes', '0002_remove_content_type_name')
        ]

        for app, name in migrations:
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

        print("✓ Auth migration records restored")

if __name__ == '__main__':
    restore_auth_migrations()
    print("✅ Auth migrations restored successfully!")
