from django import template
from django.contrib.auth.models import User

register = template.Library()

@register.filter
def unread_notifications_count(user):
    """Get count of unread, non-dismissed notifications for a user"""
    if not user.is_authenticated:
        return 0
    
    try:
        return user.notifications.filter(is_read=False, is_dismissed=False).count()
    except Exception:
        return 0

@register.filter
def has_unread_notifications(user):
    """Check if user has unread notifications"""
    return unread_notifications_count(user) > 0

@register.filter
def safe_employee_profile(user):
    """Safely fetch user's employee_profile without crashing if table is missing"""
    try:
        return getattr(user, 'employee_profile', None)
    except Exception:
        # Covers cases like ProgrammingError when the crm_employee table doesn't exist yet
        return None

@register.filter
def div(value, arg):
    """Divide the value by the argument"""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError, TypeError):
        return 0