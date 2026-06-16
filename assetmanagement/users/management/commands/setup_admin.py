"""
Management command to create or reset admin user
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction


class Command(BaseCommand):
    help = 'Create or reset admin user with default credentials'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Admin username (default: admin)',
        )
        parser.add_argument(
            '--password',
            type=str,
            default='FagiAssets2024!',
            help='Admin password (default: FagiAssets2024!)',
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@fagiassets.com',
            help='Admin email (default: admin@fagiassets.com)',
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset password if user already exists',
        )

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']
        reset = options['reset']
        
        try:
            with transaction.atomic():
                # Check if user exists
                try:
                    user = User.objects.get(username=username)
                    if reset:
                        user.set_password(password)
                        user.email = email
                        user.is_superuser = True
                        user.is_staff = True
                        user.is_active = True
                        user.save()
                        self.stdout.write(
                            self.style.SUCCESS(f'Successfully reset admin user: {username}')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'User {username} already exists. Use --reset to update password.')
                        )
                        return
                        
                except User.DoesNotExist:
                    # Create new user
                    user = User.objects.create_superuser(
                        username=username,
                        email=email,
                        password=password
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully created admin user: {username}')
                    )
                
                # Display credentials
                self.stdout.write('\n' + '='*50)
                self.stdout.write('ADMIN CREDENTIALS:')
                self.stdout.write(f'Username: {username}')
                self.stdout.write(f'Password: {password}')
                self.stdout.write(f'Email: {email}')
                self.stdout.write('='*50)
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating/updating admin user: {e}')
            )