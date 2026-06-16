"""
Management command to set up production database
This command will:
1. Run migrations
2. Create superuser if needed
3. Set up initial data
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User
from django.db import transaction
import os


class Command(BaseCommand):
    help = 'Set up production database with migrations and initial data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-superuser',
            action='store_true',
            help='Create a superuser account',
        )
        parser.add_argument(
            '--superuser-username',
            type=str,
            default='admin',
            help='Superuser username (default: admin)',
        )
        parser.add_argument(
            '--superuser-email',
            type=str,
            default='admin@example.com',
            help='Superuser email (default: admin@example.com)',
        )
        parser.add_argument(
            '--superuser-password',
            type=str,
            default='admin123',
            help='Superuser password (default: admin123)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up production database...'))
        
        # Check database connection first
        self.check_database_connection()
        
        # Step 1: Run migrations in order
        self.stdout.write('Running migrations...')
        try:
            # First, run core Django migrations
            self.stdout.write('Running core Django migrations...')
            call_command('migrate', 'contenttypes', verbosity=1, interactive=False)
            call_command('migrate', 'auth', verbosity=1, interactive=False)
            call_command('migrate', 'admin', verbosity=1, interactive=False)
            call_command('migrate', 'sessions', verbosity=1, interactive=False)
            
            # Then run app-specific migrations
            self.stdout.write('Running app migrations...')
            call_command('migrate', verbosity=1, interactive=False)
            
            self.stdout.write(self.style.SUCCESS('✓ Migrations completed'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Migration failed: {e}'))
            # Try to continue anyway
            self.stdout.write('Attempting to continue with remaining setup...')
        
        # Step 2: Create superuser if requested
        if options['create_superuser']:
            self.create_superuser(
                options['superuser_username'],
                options['superuser_email'],
                options['superuser_password']
            )
        
        # Step 3: Check database status
        self.check_database_status()
        
        self.stdout.write(self.style.SUCCESS('Production database setup completed!'))

    def create_superuser(self, username, email, password):
        """Create superuser if it doesn't exist"""
        self.stdout.write(f'Checking for superuser: {username}')
        
        try:
            with transaction.atomic():
                if User.objects.filter(username=username).exists():
                    self.stdout.write(self.style.WARNING(f'Superuser {username} already exists'))
                    return
                
                if User.objects.filter(is_superuser=True).exists():
                    self.stdout.write(self.style.WARNING('A superuser already exists'))
                    return
                
                # Create superuser
                user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                
                self.stdout.write(self.style.SUCCESS(f'✓ Superuser created: {username}'))
                self.stdout.write(self.style.WARNING(f'Password: {password}'))
                self.stdout.write(self.style.WARNING('Please change the password after first login!'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Superuser creation failed: {e}'))

    def check_database_connection(self):
        """Check database connection and show info"""
        self.stdout.write('Checking database connection...')
        
        try:
            from django.db import connection
            
            with connection.cursor() as cursor:
                # Test basic connection
                cursor.execute("SELECT 1")
                self.stdout.write(self.style.SUCCESS('✓ Database connection successful'))
                
                # Check if any tables exist
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                table_count = cursor.fetchone()[0]
                
                if table_count == 0:
                    self.stdout.write('Database is empty - will create all tables')
                else:
                    self.stdout.write(f'Database has {table_count} existing tables')
                
                # Show database info
                cursor.execute("SELECT version()")
                db_version = cursor.fetchone()[0]
                self.stdout.write(f'Database: {db_version.split()[0]} {db_version.split()[1]}')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Database connection failed: {e}'))
            raise

    def check_database_status(self):
        """Check database status and show summary"""
        self.stdout.write('Checking database status...')
        
        try:
            from django.db import connection
            
            # Check database connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT version()")
                db_version = cursor.fetchone()[0]
                self.stdout.write(f'✓ Database: {db_version}')
            
            # Check user count
            user_count = User.objects.count()
            superuser_count = User.objects.filter(is_superuser=True).count()
            
            self.stdout.write(f'✓ Total users: {user_count}')
            self.stdout.write(f'✓ Superusers: {superuser_count}')
            
            # Check if auth tables exist
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE 'auth_%'
                ORDER BY table_name
            """)
            auth_tables = [row[0] for row in cursor.fetchall()]
            
            if auth_tables:
                self.stdout.write(f'✓ Auth tables: {", ".join(auth_tables)}')
            else:
                self.stdout.write(self.style.ERROR('✗ No auth tables found'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Database status check failed: {e}'))