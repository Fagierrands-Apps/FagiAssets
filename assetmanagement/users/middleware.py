"""
Custom middleware for session debugging and reliability
"""
import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)
User = get_user_model()


class SessionDebugMiddleware(MiddlewareMixin):
    """
    Middleware to help debug session issues in production
    """
    
    def process_request(self, request):
        """Log session information for debugging"""
        if settings.DEBUG:
            return None
            
        # Only log for authenticated users having issues
        if hasattr(request, 'user') and request.user.is_authenticated:
            session_key = request.session.session_key
            if session_key:
                logger.info(f"User {request.user.username} session: {session_key[:10]}...")
            else:
                logger.warning(f"User {request.user.username} has no session key")
        
        return None
    
    def process_response(self, request, response):
        """Ensure session is saved properly"""
        if hasattr(request, 'session') and request.session.modified:
            try:
                request.session.save()
            except Exception as e:
                logger.error(f"Failed to save session: {e}")
        
        return response


class SessionReliabilityMiddleware(MiddlewareMixin):
    """
    Middleware to improve session reliability in serverless environments
    """
    
    def process_request(self, request):
        """Ensure session exists and is valid"""
        # Skip for static files and admin
        if request.path.startswith('/static/') or request.path.startswith('/admin/'):
            return None
            
        # Ensure session exists
        if not request.session.session_key:
            request.session.create()
        
        # For authenticated users, verify session is still valid in database
        if hasattr(request, 'user') and request.user.is_authenticated:
            try:
                from django.contrib.sessions.models import Session
                from django.utils import timezone
                
                # Check if session exists and is not expired
                session_obj = Session.objects.get(session_key=request.session.session_key)
                if session_obj.expire_date < timezone.now():
                    # Session expired, create new one
                    request.session.flush()
                    request.session.create()
                    logger.warning(f"Session expired for user {request.user.username}, created new session")
                    
            except Session.DoesNotExist:
                # Session doesn't exist in database, create new one
                request.session.flush()
                request.session.create()
                logger.warning(f"Session not found in database for user {request.user.username}, created new session")
            except Exception as e:
                logger.error(f"Error checking session for user {request.user.username}: {e}")
        
        return None
    
    def process_response(self, request, response):
        """Ensure session is properly saved"""
        if hasattr(request, 'session'):
            # Force session save for authenticated users
            if hasattr(request, 'user') and request.user.is_authenticated:
                request.session.modified = True
                try:
                    request.session.save()
                    # Also update session expiry to extend it
                    from django.conf import settings
                    request.session.set_expiry(settings.SESSION_COOKIE_AGE)
                except Exception as e:
                    logger.error(f"Failed to save session for user {request.user.username}: {e}")
        
        return response