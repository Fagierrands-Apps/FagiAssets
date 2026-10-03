from functools import wraps
from django.shortcuts import redirect


def require_manager(view_func):
    """
    Decorator for all manager portal views.

    Allows access only to:
    - Django superusers (is_superuser=True)
    - Django staff users (is_staff=True)
    - Employees whose role is 'admin' or 'project_manager'

    Anyone else is sent back to the manager login page.
    Unauthenticated users are also sent to the manager login page
    (not the general /login/).
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Not logged in at all
        if not request.user.is_authenticated:
            return redirect('manager_portal:login')

        # Django superuser or staff — always allowed
        if request.user.is_superuser or request.user.is_staff:
            return view_func(request, *args, **kwargs)

        # Check employee role
        try:
            employee = request.user.employee_profile
            if employee.role in ('admin', 'project_manager'):
                return view_func(request, *args, **kwargs)
        except AttributeError:
            pass

        # Wrong role — back to manager login with error flag
        return redirect('manager_portal:login')

    return _wrapped_view
