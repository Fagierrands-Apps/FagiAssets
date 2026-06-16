#!/usr/bin/env python
"""
Production database setup script
Run this script to set up the production database with all necessary tables
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def setup_production_database():
    """Set up production database"""
    print("=" * 60)
    print("Production Database Setup")
    print("=" * 60)
    
    # Set environment variables for production
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
    os.environ['VERCEL'] = '1'  # Force production mode
    
    # Ensure DATABASE_URL is set
    if not os.environ.get('DATABASE_URL'):
        os.environ['DATABASE_URL'] = 'postgresql://postgres.dxesmzogjpxswxhsomgf:OnFRtf0SmpHwgNaQ@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres'
        print("Using default DATABASE_URL")
    
    # Add Django project to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'assetmanagement'))
    
    # Setup Django
    django.setup()
    
    print("Setting up production database...")
    
    # Run the setup command
    try:
        execute_from_command_line([
            'manage.py', 
            'setup_production_db', 
            '--create-superuser',
            '--superuser-username=admin',
            '--superuser-email=admin@fagiassets.com',
            '--superuser-password=FagiAssets2024!'
        ])
        
        print("\n" + "=" * 60)
        print("✅ Production database setup completed!")
        print("\nLogin credentials:")
        print("Username: admin")
        print("Password: FagiAssets2024!")
        print("\n⚠️  Please change the password after first login!")
        print("\nYou can now test login at: https://fagiassets.vercel.app/login/")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check that DATABASE_URL is correct")
        print("2. Ensure PostgreSQL database is accessible")
        print("3. Verify network connectivity")
        return False
    
    return True

if __name__ == '__main__':
    success = setup_production_database()
    sys.exit(0 if success else 1)