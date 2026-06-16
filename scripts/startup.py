#!/usr/bin/env python
"""
Startup script for production deployment
This script runs after deployment to initialize the production environment
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_root = Path(__file__).parent.parent / 'assetmanagement'
sys.path.insert(0, str(project_root))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')

# Setup Django
django.setup()

from django.core.management import execute_from_command_line

def main():
    """Run startup commands"""
    print("Starting production initialization...")
    
    try:
        # Run migrations
        print("Running migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        
        # Initialize production environment
        print("Initializing production environment...")
        execute_from_command_line(['manage.py', 'init_production'])
        
        print("Production initialization completed successfully!")
        
    except Exception as e:
        print(f"Error during startup: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()