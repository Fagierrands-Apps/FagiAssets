"""
Management command to fix Vercel database connection issues
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Fix Vercel database connection issues'

    def handle(self, *args, **options):
        self.stdout.write('Fixing Vercel database connection...')
        
        # Update database settings for Vercel
        if os.environ.get('VERCEL'):
            self.stdout.write('Detected Vercel environment')
            
            # Override database settings
            settings.DATABASES['default'].update({
                'ENGINE': 'django.db.backends.postgresql',
                'CONN_MAX_AGE': 0,  # Disable connection pooling
                'OPTIONS': {
                    'sslmode': 'require',
                    'connect_timeout': 30,
                    'options': '-c default_transaction_isolation=read_committed -c client_encoding=UTF8'
                },
                'DISABLE_SERVER_SIDE_CURSORS': True,
            })
            
            self.stdout.write('Database settings updated for Vercel')
        
        # Test connection
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                result = cursor.fetchone()
                if result[0] == 1:
                    self.stdout.write(self.style.SUCCESS('✓ Database connection successful'))
                else:
                    self.stdout.write(self.style.ERROR('✗ Database connection failed'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Database connection error: {e}'))
            
            # Try alternative connection method
            self.stdout.write('Trying alternative connection method...')
            self.try_alternative_connection()
    
    def try_alternative_connection(self):
        """Try alternative connection method"""
        try:
            import psycopg2
            from django.conf import settings
            
            db_settings = settings.DATABASES['default']
            
            # Build connection string manually
            conn_string = f"host={db_settings['HOST']} port={db_settings['PORT']} dbname={db_settings['NAME']} user={db_settings['USER']} password={db_settings['PASSWORD']} sslmode=require"
            
            conn = psycopg2.connect(conn_string)
            cursor = conn.cursor()
            
            # Set encoding explicitly
            cursor.execute("SET client_encoding TO 'UTF8'")
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
            if result[0] == 1:
                self.stdout.write(self.style.SUCCESS('✓ Alternative connection successful'))
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Alternative connection failed: {e}'))