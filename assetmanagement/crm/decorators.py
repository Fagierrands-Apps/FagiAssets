from django.http import HttpResponseForbidden
from functools import wraps

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Allow Django staff/superusers to access
            if request.user.is_staff or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Check employee role
            try:
                employee = request.user.employee_profile
            except AttributeError:
                return HttpResponseForbidden("Access denied: No employee profile found.")
            if employee.role not in allowed_roles:
                return HttpResponseForbidden("Access denied: Insufficient permissions.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def admin_required(view_func):
    """
    Decorator that allows access to:
    1. Django staff users (is_staff=True)
    2. Django superusers (is_superuser=True)
    3. Employees with role='admin'
    """
    return role_required(['admin'])(view_func)

def sales_required(view_func):
    return role_required(['sales', 'admin'])(view_func)

def call_center_required(view_func):
    return role_required(['call_center', 'admin'])(view_func)

def user_required(view_func):
    return role_required(['user', 'admin'])(view_func)
