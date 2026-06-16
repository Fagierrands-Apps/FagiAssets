#!/usr/bin/env python
"""
Database diagnostic script
Check what tables exist in the production database
"""

import os
import sys
import django

def diagnose_database():
    """Diagnose database issues"""
    print("=" * 60)
    print("Database Diagnostic")
    print("=" * 60)
    
    # Set environment variables for production
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
    os.environ['VERCEL'] = '1'  # Force production mode
    
    # Ensure DATABASE_URL is set
    if not os.environ.get('DATABASE_URL'):
        os.environ['DATABASE_URL'] = 'postgresql://postgres.dxesmzogjpxswxhsomgf:OnFRtf0SmpHwgNaQ@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres'
    
    # Add Django project to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'assetmanagement'))
    
    # Setup Django
    django.setup()
    
    from django.db import connection
    
    try:
        with connection.cursor() as cursor:
            # Check database version
            cursor.execute("SELECT version()")
            db_version = cursor.fetchone()[0]
            print(f"Database: {db_version}")
            
            # Check current schema
            cursor.execute("SELECT current_schema()")
            current_schema = cursor.fetchone()[0]
            print(f"Current schema: {current_schema}")
            
            # List all schemas
            cursor.execute("SELECT schema_name FROM information_schema.schemata ORDER BY schema_name")
            schemas = [row[0] for row in cursor.fetchall()]
            print(f"Available schemas: {', '.join(schemas)}")
            
            # Check tables in public schema
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """)
            public_tables = [row[0] for row in cursor.fetchall()]
            print(f"\nTables in public schema ({len(public_tables)}):")
            for table in public_tables[:20]:  # Show first 20
                print(f"  - {table}")
            if len(public_tables) > 20:
                print(f"  ... and {len(public_tables) - 20} more")
            
            # Check specifically for auth tables
            auth_tables = [t for t in public_tables if t.startswith('auth_')]
            print(f"\nAuth tables found: {auth_tables}")
            
            # Check Django migrations table
            django_migrations = [t for t in public_tables if 'django_migrations' in t]
            print(f"Django migrations table: {django_migrations}")
            
            if 'django_migrations' in public_tables:
                cursor.execute("SELECT app, name FROM django_migrations ORDER BY app, name")
                migrations = cursor.fetchall()
                print(f"\nApplied migrations ({len(migrations)}):")
                for app, name in migrations[:10]:  # Show first 10
                    print(f"  - {app}: {name}")
                if len(migrations) > 10:
                    print(f"  ... and {len(migrations) - 10} more")
            
            # Check if auth_user exists in any schema
            cursor.execute("""
                SELECT table_schema, table_name 
                FROM information_schema.tables 
                WHERE table_name = 'auth_user'
            """)
            auth_user_locations = cursor.fetchall()
            print(f"\nauth_user table locations: {auth_user_locations}")
            
            # Try to describe auth_user if it exists
            if auth_user_locations:
                schema, table = auth_user_locations[0]
                cursor.execute(f"""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_schema = '{schema}' AND table_name = '{table}'
                    ORDER BY ordinal_position
                """)
                columns = cursor.fetchall()
                print(f"\nauth_user columns:")
                for col_name, col_type in columns:
                    print(f"  - {col_name}: {col_type}")
            
            # Check if we can access auth_user directly
            try:
                cursor.execute("SELECT COUNT(*) FROM auth_user")
                user_count = cursor.fetchone()[0]
                print(f"\nUsers in auth_user: {user_count}")
            except Exception as e:
                print(f"\nCannot access auth_user: {e}")
            
            # Check accounts_user table instead
            if 'accounts_user' in public_tables:
                try:
                    cursor.execute("SELECT COUNT(*) FROM accounts_user")
                    user_count = cursor.fetchone()[0]
                    print(f"\nUsers in accounts_user: {user_count}")
                    
                    # Show structure of accounts_user
                    cursor.execute("""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_schema = 'public' AND table_name = 'accounts_user'
                        ORDER BY ordinal_position
                    """)
                    columns = cursor.fetchall()
                    print(f"\naccounts_user columns:")
                    for col_name, col_type in columns:
                        print(f"  - {col_name}: {col_type}")
                        
                except Exception as e:
                    print(f"\nCannot access accounts_user: {e}")
            
            # Check what Django apps are in migrations
            if 'django_migrations' in public_tables:
                cursor.execute("SELECT DISTINCT app FROM django_migrations ORDER BY app")
                apps = [row[0] for row in cursor.fetchall()]
                print(f"\nDjango apps in database: {', '.join(apps)}")
                
                # Check if our apps are there
                our_apps = ['assets', 'users', 'discovery']
                missing_apps = [app for app in our_apps if app not in apps]
                if missing_apps:
                    print(f"Missing our apps: {', '.join(missing_apps)}")
                else:
                    print("All our apps are present in migrations")
            
    except Exception as e:
        print(f"Database diagnostic failed: {e}")
        return False
    
    return True

if __name__ == '__main__':
    success = diagnose_database()
    sys.exit(0 if success else 1)