#!/usr/bin/env python
"""
Check all auth tables and create any missing ones
"""

import os
import sys
import django

def check_all_auth_tables():
    """Check and create all required auth tables"""
    print("=" * 60)
    print("Checking All Auth Tables")
    print("=" * 60)
    
    # Set environment variables for production
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
    os.environ['VERCEL'] = '1'  # Force production mode
    
    # Add Django project to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'assetmanagement'))
    
    # Setup Django
    django.setup()
    
    from django.db import connection
    
    required_tables = {
        'auth_user': True,
        'auth_group': True,
        'auth_permission': True,
        'auth_user_groups': False,
        'auth_user_user_permissions': False,
        'auth_group_permissions': True,
        'django_content_type': True,
    }
    
    try:
        with connection.cursor() as cursor:
            print("\nChecking required auth tables...")
            
            missing_tables = []
            for table_name, should_exist in required_tables.items():
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    )
                """, [table_name])
                exists = cursor.fetchone()[0]
                
                status = "✓" if exists else "❌"
                print(f"{status} {table_name}: {'exists' if exists else 'MISSING'}")
                
                if not exists:
                    missing_tables.append(table_name)
            
            # Create missing tables
            if missing_tables:
                print(f"\nCreating {len(missing_tables)} missing table(s)...")
                
                if 'auth_user_groups' in missing_tables:
                    print("Creating auth_user_groups table...")
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS auth_user_groups (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
                            group_id INTEGER NOT NULL REFERENCES auth_group(id) ON DELETE CASCADE,
                            UNIQUE (user_id, group_id)
                        );
                    """)
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS auth_user_groups_user_id_idx 
                        ON auth_user_groups(user_id);
                    """)
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS auth_user_groups_group_id_idx 
                        ON auth_user_groups(group_id);
                    """)
                    print("✓ auth_user_groups table created")
                
                if 'auth_user_user_permissions' in missing_tables:
                    print("Creating auth_user_user_permissions table...")
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS auth_user_user_permissions (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
                            permission_id INTEGER NOT NULL REFERENCES auth_permission(id) ON DELETE CASCADE,
                            UNIQUE (user_id, permission_id)
                        );
                    """)
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS auth_user_user_permissions_user_id_idx 
                        ON auth_user_user_permissions(user_id);
                    """)
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS auth_user_user_permissions_permission_id_idx 
                        ON auth_user_user_permissions(permission_id);
                    """)
                    print("✓ auth_user_user_permissions table created")
                
                print("\n✓ All missing tables created")
            else:
                print("\n✓ All required tables exist")
            
            # Show table counts
            print("\nTable record counts:")
            for table_name in required_tables.keys():
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    print(f"  {table_name}: {count} records")
                except Exception as e:
                    print(f"  {table_name}: Error - {e}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = check_all_auth_tables()
    if success:
        print("\n✅ All auth tables checked and fixed!")
    else:
        print("\n❌ Failed to check auth tables")
    sys.exit(0 if success else 1)