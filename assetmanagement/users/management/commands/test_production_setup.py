"""
Management command to test production setup locally
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse


class Command(BaseCommand):
    help = 'Test production setup locally by simulating production environment'

    def add_arguments(self, parser):
        parser.add_argument(
            '--simulate-production',
            action='store_true',
            help='Simulate production environment variables',
        )

    def handle(self, *args, **options):
        self.stdout.write('Testing production setup...')
        
        if options['simulate_production']:
            # Temporarily set production environment variables
            os.environ['VERCEL'] = '1'
            os.environ['ADMIN_USERNAME'] = 'admin'
            os.environ['ADMIN_PASSWORD'] = 'FagiAssets2024!'
            os.environ['ADMIN_EMAIL'] = 'admin@fagiassets.com'
            
            self.stdout.write('Simulating production environment...')
        
        try:
            # Test admin user creation
            from django.core.management import call_command
            call_command('init_production')
            
            # Verify admin user exists
            try:
                admin_user = User.objects.get(username='admin')
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Admin user exists: {admin_user.username}')
                )
                self.stdout.write(f'  - Email: {admin_user.email}')
                self.stdout.write(f'  - Is superuser: {admin_user.is_superuser}')
                self.stdout.write(f'  - Is active: {admin_user.is_active}')
                
                # Test password
                if admin_user.check_password('FagiAssets2024!'):
                    self.stdout.write(
                        self.style.SUCCESS('✓ Admin password is correct')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR('✗ Admin password is incorrect')
                    )
                    
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR('✗ Admin user does not exist')
                )
                return
            
            # Test health check endpoint
            client = Client()
            try:
                response = client.get('/users/health/')
                if response.status_code == 200:
                    self.stdout.write(
                        self.style.SUCCESS('✓ Health check endpoint working')
                    )
                    data = response.json()
                    self.stdout.write(f'  - Status: {data.get("status")}')
                    self.stdout.write(f'  - Environment: {data.get("environment")}')
                    self.stdout.write(f'  - Admin user: {data.get("admin_user")}')
                else:
                    self.stdout.write(
                        self.style.ERROR(f'✗ Health check failed: {response.status_code}')
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Health check error: {e}')
                )
            
            # Test login functionality
            try:
                response = client.get('/login/')
                if response.status_code == 200:
                    self.stdout.write(
                        self.style.SUCCESS('✓ Login page accessible')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'✗ Login page error: {response.status_code}')
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Login page error: {e}')
                )
            
            self.stdout.write('\n' + '='*50)
            self.stdout.write(
                self.style.SUCCESS('Production setup test completed!')
            )
            self.stdout.write('\nLogin credentials:')
            self.stdout.write('Username: admin')
            self.stdout.write('Password: FagiAssets2024!')
            self.stdout.write('Email: admin@fagiassets.com')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during production setup test: {e}')
            )
        
        finally:
            # Clean up environment variables if we set them
            if options['simulate_production']:
                os.environ.pop('VERCEL', None)
                os.environ.pop('ADMIN_USERNAME', None)
                os.environ.pop('ADMIN_PASSWORD', None)
                os.environ.pop('ADMIN_EMAIL', None)