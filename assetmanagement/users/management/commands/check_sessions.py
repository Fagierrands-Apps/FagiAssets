"""
Management command to check and clean up sessions
"""
from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.utils import timezone
from users.models import UserSession
import json


class Command(BaseCommand):
    help = 'Check and clean up user sessions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Clean up expired sessions',
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Check sessions for specific user',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Checking user sessions...'))
        
        # Check Django sessions
        total_sessions = Session.objects.count()
        expired_sessions = Session.objects.filter(expire_date__lt=timezone.now()).count()
        active_sessions = total_sessions - expired_sessions
        
        self.stdout.write(f"Django Sessions:")
        self.stdout.write(f"  Total: {total_sessions}")
        self.stdout.write(f"  Active: {active_sessions}")
        self.stdout.write(f"  Expired: {expired_sessions}")
        
        # Check UserSession tracking
        try:
            total_user_sessions = UserSession.objects.count()
            active_user_sessions = UserSession.objects.filter(is_active=True).count()
            
            self.stdout.write(f"\nUser Session Tracking:")
            self.stdout.write(f"  Total: {total_user_sessions}")
            self.stdout.write(f"  Active: {active_user_sessions}")
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Could not check UserSession: {e}"))
        
        # Check specific user if requested
        if options['user']:
            try:
                user = User.objects.get(username=options['user'])
                user_sessions = Session.objects.filter(
                    expire_date__gte=timezone.now()
                )
                
                active_user_sessions = []
                for session in user_sessions:
                    session_data = session.get_decoded()
                    if session_data.get('_auth_user_id') == str(user.id):
                        active_user_sessions.append(session)
                
                self.stdout.write(f"\nSessions for user '{user.username}':")
                self.stdout.write(f"  Active sessions: {len(active_user_sessions)}")
                
                for session in active_user_sessions:
                    self.stdout.write(f"    Session: {session.session_key[:10]}...")
                    self.stdout.write(f"    Expires: {session.expire_date}")
                    
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"User '{options['user']}' not found"))
        
        # Cleanup if requested
        if options['cleanup']:
            self.stdout.write(self.style.WARNING('\nCleaning up expired sessions...'))
            
            # Clean Django sessions
            deleted_sessions = Session.objects.filter(expire_date__lt=timezone.now()).delete()
            self.stdout.write(f"Deleted {deleted_sessions[0]} expired Django sessions")
            
            # Clean UserSession tracking
            try:
                # Mark sessions as inactive if they don't exist in Django sessions
                existing_session_keys = set(Session.objects.values_list('session_key', flat=True))
                inactive_count = UserSession.objects.exclude(
                    session_key__in=existing_session_keys
                ).update(is_active=False)
                
                self.stdout.write(f"Marked {inactive_count} UserSessions as inactive")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Could not clean UserSession: {e}"))
        
        self.stdout.write(self.style.SUCCESS('\nSession check complete!'))