#!/usr/bin/env python3
"""
This script updates your settings.py to work with cPanel deployment
It adds support for environment variables while keeping existing functionality
"""

import os
import shutil
from datetime import datetime

def backup_settings():
    """Create a backup of the current settings.py"""
    settings_path = 'assetmanagement/assetmanager/settings.py'
    backup_path = f'assetmanagement/assetmanager/settings.py.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    
    if os.path.exists(settings_path):
        shutil.copy2(settings_path, backup_path)
        print(f"✓ Backup created: {backup_path}")
        return True
    else:
        print(f"✗ Settings file not found: {settings_path}")
        return False

def update_settings():
    """Update settings.py with environment variable support"""
    settings_path = 'assetmanagement/assetmanager/settings.py'
    
    # Read current settings
    with open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already updated
    if 'from decouple import config' in content or 'os.environ.get' in content:
        print("⚠ Settings.py already appears to be configured for environment variables")
        proceed = input("Do you want to continue anyway? (y/n): ").strip().lower()
        if proceed != 'y':
            print("Aborted.")
            return False
    
    # Add imports at the top if not present
    if 'from decouple import config' not in content:
        # Find the imports section
        import_section = "from pathlib import Path\nimport os"
        if import_section in content:
            new_imports = import_section + "\nfrom decouple import config, Csv"
            content = content.replace(import_section, new_imports)
            print("✓ Added decouple imports")
    
    # Update SECRET_KEY
    if "SECRET_KEY = 'django-insecure-" in content:
        old_secret = "SECRET_KEY = 'django-insecure-)uydf_yg5c=z5^)xi+&$1@y$7w@)lboa2l#eom$!4uk1l!22u0'"
        new_secret = "SECRET_KEY = config('SECRET_KEY', default='django-insecure-)uydf_yg5c=z5^)xi+&$1@y$7w@)lboa2l#eom$!4uk1l!22u0')"
        content = content.replace(old_secret, new_secret)
        print("✓ Updated SECRET_KEY to use environment variable")
    
    # Update DEBUG
    if "DEBUG = os.environ.get('DEBUG'" not in content:
        old_debug = "DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'"
        new_debug = "DEBUG = config('DEBUG', default=True, cast=bool)"
        if old_debug in content:
            content = content.replace(old_debug, new_debug)
            print("✓ Updated DEBUG to use environment variable")
    
    # Update ALLOWED_HOSTS
    if "ALLOWED_HOSTS = [" in content and "config('ALLOWED_HOSTS'" not in content:
        # Find the ALLOWED_HOSTS line
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('ALLOWED_HOSTS = ['):
                # Find the closing bracket
                j = i
                while j < len(lines) and ']' not in lines[j]:
                    j += 1
                
                # Replace with environment variable version
                new_allowed_hosts = "ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,testserver,10.246.23.10,fagiassets.vercel.app,*.vercel.app', cast=Csv())"
                lines[i:j+1] = [new_allowed_hosts]
                content = '\n'.join(lines)
                print("✓ Updated ALLOWED_HOSTS to use environment variable")
                break
    
    # Update DATABASES - make it flexible for both Supabase and cPanel
    database_config = """
# Database Configuration
# Supports both Supabase (default) and cPanel PostgreSQL
if config('USE_CPANEL_DB', default=False, cast=bool):
    # cPanel PostgreSQL Configuration
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', default='fagiassets_db'),
            'USER': config('DB_USER', default='fagiassets_user'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
            'OPTIONS': {
                'connect_timeout': 30,
            },
            'CONN_MAX_AGE': 600,
        }
    }
else:
    # Supabase PostgreSQL Configuration (default)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', default='postgres'),
            'USER': config('DB_USER', default='postgres.dxesmzogjpxswxhsomgf'),
            'PASSWORD': config('DB_PASSWORD', default='OnFRtf0SmpHwgNaQ'),
            'HOST': config('DB_HOST', default='aws-0-ap-southeast-1.pooler.supabase.com'),
            'PORT': config('DB_PORT', default='6543'),
            'OPTIONS': {
                'sslmode': 'require',
                'connect_timeout': 30,
                'options': '-c client_encoding=UTF8'
            },
            'CONN_MAX_AGE': 0,
            'DISABLE_SERVER_SIDE_CURSORS': True,
        }
    }
"""
    
    # Find and replace DATABASES section
    if 'DATABASES = {' in content:
        lines = content.split('\n')
        start_idx = None
        end_idx = None
        brace_count = 0
        
        for i, line in enumerate(lines):
            if 'DATABASES = {' in line:
                start_idx = i
                brace_count = line.count('{') - line.count('}')
            elif start_idx is not None:
                brace_count += line.count('{') - line.count('}')
                if brace_count == 0:
                    end_idx = i
                    break
        
        if start_idx is not None and end_idx is not None:
            lines[start_idx:end_idx+1] = database_config.strip().split('\n')
            content = '\n'.join(lines)
            print("✓ Updated DATABASES to support both Supabase and cPanel")
    
    # Write updated settings
    with open(settings_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Settings.py updated successfully")
    return True

def create_env_template():
    """Create a .env.template file"""
    template_content = """# Django Settings
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,localhost,127.0.0.1

# Database Settings
# Set USE_CPANEL_DB=True to use cPanel database, False for Supabase
USE_CPANEL_DB=True

# cPanel PostgreSQL Database
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432

# Application Settings
DJANGO_SETTINGS_MODULE=assetmanager.settings
"""
    
    with open('.env.template', 'w') as f:
        f.write(template_content)
    
    print("✓ Created .env.template file")

def main():
    print("=" * 60)
    print("Update Settings for cPanel Deployment")
    print("=" * 60)
    print()
    print("This script will:")
    print("1. Backup your current settings.py")
    print("2. Update settings.py to use environment variables")
    print("3. Create a .env.template file")
    print()
    
    proceed = input("Do you want to continue? (y/n): ").strip().lower()
    if proceed != 'y':
        print("Aborted.")
        return
    
    print()
    print("Starting update...")
    print()
    
    # Backup settings
    if not backup_settings():
        return
    
    # Update settings
    if not update_settings():
        return
    
    # Create template
    create_env_template()
    
    print()
    print("=" * 60)
    print("✓ Update completed successfully!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Review the changes in settings.py")
    print("2. Copy .env.template to .env")
    print("3. Update .env with your actual credentials")
    print("4. Install python-decouple: pip install python-decouple")
    print("5. Test locally before deploying")
    print()
    print("To restore original settings:")
    print("  Use the backup file created in assetmanagement/assetmanager/")
    print()

if __name__ == '__main__':
    main()