from django.apps import AppConfig
import os
import sys


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        """Initialize production environment when app is ready"""
        # Only run in production and avoid running during migrations
        is_production = (
            os.environ.get('VERCEL') or 
            os.environ.get('DATABASE_URL') or 
            'vercel.app' in os.environ.get('VERCEL_URL', '')
        )
        
        # Skip during migrations or if not in production
        if not is_production or 'migrate' in sys.argv:
            return
            
        # Import here to avoid circular imports
        try:
            from django.core.management import call_command
            from django.db import connection
            
            # Check if database is accessible
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            
            # Initialize production environment
            call_command('init_production')
            
        except Exception as e:
            # Log error but don't crash the app
            print(f"Warning: Could not initialize production environment: {e}")
