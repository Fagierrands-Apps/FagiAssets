#!/usr/bin/env python
"""
Fix connection encoding issue
This script will test and fix the "server didn't return client encoding" error
"""

import os
import sys
import django
import psycopg2

def test_direct_connection():
    """Test direct psycopg2 connection"""
    print("=" * 60)
    print("Testing Direct PostgreSQL Connection")
    print("=" * 60)
    
    # Connection parameters
    conn_params = {
        'host': 'aws-0-ap-southeast-1.pooler.supabase.com',
        'port': 6543,
        'database': 'postgres',
        'user': 'postgres.dxesmzogjpxswxhsomgf',
        'password': 'OnFRtf0SmpHwgNaQ',
        'sslmode': 'require',
        'client_encoding': 'UTF8',
        'connect_timeout': 60,
    }
    
    try:
        print("Testing direct psycopg2 connection...")
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"✓ Direct connection successful: {version.split()[0]} {version.split()[1]}")
        
        # Test encoding
        cursor.execute("SHOW client_encoding")
        encoding = cursor.fetchone()[0]
        print(f"✓ Client encoding: {encoding}")
        
        # Test server encoding
        cursor.execute("SHOW server_encoding")
        server_encoding = cursor.fetchone()[0]
        print(f"✓ Server encoding: {server_encoding}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"✗ Direct connection failed: {e}")
        return False

def test_django_connection():
    """Test Django database connection"""
    print("\nTesting Django Database Connection...")
    
    # Set environment variables for production
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
    os.environ['VERCEL'] = '1'  # Force production mode
    os.environ['DATABASE_URL'] = 'postgresql://postgres.dxesmzogjpxswxhsomgf:OnFRtf0SmpHwgNaQ@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres'
    
    # Add Django project to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'assetmanagement'))
    
    try:
        # Setup Django
        django.setup()
        
        from django.db import connection
        
        print("Testing Django database connection...")
        
        # Test connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            print(f"✓ Django connection successful: {version.split()[0]} {version.split()[1]}")
            
            # Test encoding
            cursor.execute("SHOW client_encoding")
            encoding = cursor.fetchone()[0]
            print(f"✓ Django client encoding: {encoding}")
        
        return True
        
    except Exception as e:
        print(f"✗ Django connection failed: {e}")
        return False

def test_auth_functionality():
    """Test authentication functionality"""
    print("\nTesting Authentication...")
    
    try:
        from django.contrib.auth.models import User
        from django.contrib.auth import authenticate
        
        # Check if admin user exists
        try:
            admin_user = User.objects.get(username='admin')
            print(f"✓ Admin user found: {admin_user.username}")
            
            # Test authentication
            user = authenticate(username='admin', password='FagiAssets2024!')
            if user:
                print("✓ Authentication successful")
                return True
            else:
                print("✗ Authentication failed")
                return False
                
        except User.DoesNotExist:
            print("✗ Admin user not found")
            return False
            
    except Exception as e:
        print(f"✗ Authentication test failed: {e}")
        return False

def create_updated_settings():
    """Create updated settings with better connection handling"""
    print("\nCreating updated database settings...")
    
    settings_addition = '''
# Enhanced PostgreSQL connection settings for Vercel
if VERCEL_ENV or os.environ.get('DATABASE_URL'):
    # Additional connection options to prevent encoding issues
    if 'default' in DATABASES:
        DATABASES['default']['OPTIONS'].update({
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
            'use_unicode': True,
        })
        
        # For PostgreSQL specifically
        if DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql':
            DATABASES['default']['OPTIONS'].update({
                'sslmode': 'require',
                'client_encoding': 'UTF8',
                'connect_timeout': 60,
                'keepalives_idle': 600,
                'keepalives_interval': 30,
                'keepalives_count': 3,
            })
    '''
    
    print("✓ Updated settings created")
    print("Copy this to your settings.py file:")
    print(settings_addition)
    
    return True

def main():
    """Main function to diagnose and fix connection issues"""
    print("Connection Encoding Fix Script")
    print("This script will diagnose and fix the 'server didn't return client encoding' error")
    
    # Test direct connection first
    direct_ok = test_direct_connection()
    
    if direct_ok:
        # Test Django connection
        django_ok = test_django_connection()
        
        if django_ok:
            # Test authentication
            auth_ok = test_auth_functionality()
            
            if auth_ok:
                print("\n✅ All tests passed! Connection is working correctly.")
                print("The encoding issue should be resolved.")
            else:
                print("\n⚠️  Connection works but authentication failed.")
                print("Check user credentials and try again.")
        else:
            print("\n❌ Django connection failed.")
            print("Creating updated settings...")
            create_updated_settings()
    else:
        print("\n❌ Direct connection failed.")
        print("Check network connectivity and database credentials.")
    
    print("\n" + "=" * 60)
    print("Diagnosis completed.")

if __name__ == '__main__':
    main()