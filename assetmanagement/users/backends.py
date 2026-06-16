"""
Custom authentication backends for handling user sessions and activity tracking
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db import transaction
from django.conf import settings
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class SafeModelBackend(ModelBackend):
    """
    Custom authentication backend that safely handles user session tracking
    without failing if database writes are not possible (e.g., in read-only environments)
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """Authenticate user with safe session tracking"""
        user = super().authenticate(request, username, password, **kwargs)
        
        if user and user.is_authenticated and request:
            try:
                # Ensure session is created and saved
                if hasattr(request, 'session'):
                    if not request.session.session_key:
                        request.session.create()
                        logger.info(f"Created new session for user {user.username}: {request.session.session_key}")
                    else:
                        logger.info(f"Using existing session for user {user.username}: {request.session.session_key}")
                    
                    # Force session save
                    request.session.modified = True
                    request.session.save()
                    
                    # Try to create session tracking, but don't fail if it doesn't work
                    self._safe_create_user_session(request, user)
                    self._safe_log_user_activity(request, user, 'login')
            except Exception as e:
                logger.warning(f"Error in session handling: {e}")
        
        return user
    
    def get_user(self, user_id):
        """Get user by ID with error handling"""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        except Exception as e:
            logger.warning(f"Error getting user {user_id}: {e}")
            return None
    
    def _safe_create_user_session(self, request, user):
        """Safely create user session tracking"""
        try:
            from .models import UserSession
            
            # Only create session tracking if we can write to database
            with transaction.atomic():
                session_key = request.session.session_key
                if session_key:
                    ip_address = self._get_client_ip(request)
                    user_agent = request.META.get('HTTP_USER_AGENT', '')
                    
                    # Create or update session
                    UserSession.objects.update_or_create(
                        session_key=session_key,
                        defaults={
                            'user': user,
                            'ip_address': ip_address,
                            'user_agent': user_agent,
                            'is_active': True,
                        }
                    )
        except Exception as e:
            # Log the error but don't fail authentication
            logger.warning(f"Could not create user session tracking: {e}")
    
    def _safe_log_user_activity(self, request, user, action):
        """Safely log user activity"""
        try:
            from .models import UserActivity
            
            with transaction.atomic():
                ip_address = self._get_client_ip(request)
                user_agent = request.META.get('HTTP_USER_AGENT', '')
                
                UserActivity.objects.create(
                    user=user,
                    action=action,
                    description=f"User {action}",
                    ip_address=ip_address,
                    user_agent=user_agent,
                )
        except Exception as e:
            # Log the error but don't fail authentication
            logger.warning(f"Could not log user activity: {e}")
    
    def _get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip