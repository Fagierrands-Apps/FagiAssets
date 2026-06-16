"""
Management command to initialize production environment
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from django.conf import settings


class Command(BaseCommand):
    help = 'Initialize production environment with admin user and required data'

    def handle(self, *args, **options):
        self.stdout.write('Initializing production environment...')
        
        # Check if we're in production
        is_production = (
            os.environ.get('VERCEL') or 
            os.environ.get('DATABASE_URL') or 
            'vercel.app' in os.environ.get('VERCEL_URL', '')
        )
        
        if not is_production:
            self.stdout.write(
                self.style.WARNING('Not in production environment, skipping initialization')
            )
            return
        
        try:
            with transaction.atomic():
                # Create admin user if it doesn't exist
                admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
                admin_password = os.environ.get('ADMIN_PASSWORD', 'FagiAssets2024!')
                admin_email = os.environ.get('ADMIN_EMAIL', 'admin@fagiassets.com')
                
                user, created = User.objects.get_or_create(
                    username=admin_username,
                    defaults={
                        'email': admin_email,
                        'is_superuser': True,
                        'is_staff': True,
                        'is_active': True,
                    }
                )
                
                if created:
                    user.set_password(admin_password)
                    user.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'Created admin user: {admin_username}')
                    )
                else:
                    # Update existing user to ensure it's properly configured
                    user.email = admin_email
                    user.is_superuser = True
                    user.is_staff = True
                    user.is_active = True
                    user.set_password(admin_password)
                    user.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'Updated admin user: {admin_username}')
                    )
                
                # Ensure required departments exist
                from assets.models import Department
                Department.objects.get_or_create(name='Call Center', defaults={'description': 'Call Center Department'})

                # Run migrations to ensure database is up to date
                from django.core.management import call_command
                self.stdout.write('Running migrations...')
                call_command('migrate', verbosity=0)
                
                # Collect static files
                self.stdout.write('Collecting static files...')
                call_command('collectstatic', verbosity=0, interactive=False)
                
                self.stdout.write(
                    self.style.SUCCESS('Production initialization completed successfully!')
                )
                
                # Display credentials (only in logs, not in response)
                self.stdout.write('\n' + '='*50)
                self.stdout.write('PRODUCTION ADMIN CREDENTIALS:')
                self.stdout.write(f'Username: {admin_username}')
                self.stdout.write(f'Password: {admin_password}')
                self.stdout.write(f'Email: {admin_email}')
                self.stdout.write('='*50)
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error initializing production environment: {e}')
            )
            raise