#!/usr/bin/env python
"""
Complete auth fix - add missing contenttypes migration
"""

import os
import sys
import django

def complete_auth_fix():
    """Add missing contenttypes migration"""
    print("=" * 60)
    print("Completing Auth Fix")
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
            print("Adding missing contenttypes migration...")
            
            # Check if migration already exists
            cursor.execute(
                'SELECT COUNT(*) FROM django_migrations WHERE app = %s AND name = %s',
                ['contenttypes', '0002_remove_content_type_name']
            )
            count = cursor.fetchone()[0]
            
            if count == 0:
                cursor.execute(
                    'INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, NOW())',
                    ['contenttypes', '0002_remove_content_type_name']
                )
                print("✓ Added contenttypes.0002_remove_content_type_name")
            else:
                print("- Migration already exists")
            
            # Verify all migrations
            cursor.execute("""
                SELECT app, name FROM django_migrations 
                WHERE app IN ('auth', 'contenttypes')
                ORDER BY app, name
            """)
            migrations = cursor.fetchall()
            print(f"\nAll core migrations ({len(migrations)}):")
            for app, name in migrations:
                print(f"  ✓ {app}.{name}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = complete_auth_fix()
    if success:
        print("\n✅ Auth fix completed successfully!")
    else:
        print("\n❌ Failed to complete auth fix")
    sys.exit(0 if success else 1)