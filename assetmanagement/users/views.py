from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.urls import reverse
from assets.utils import generate_user_qr_data, generate_qr_code_image
import json


def root_redirect(request):
    """
    Redirect root URL to appropriate dashboard based on user authentication and role.
    - Authenticated admin/superuser: redirect to /admin-dashboard/
    - Authenticated employee: redirect to /crm/employee/
    - Not authenticated: redirect to /login/
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Check if user is superuser or staff
    if request.user.is_superuser or request.user.is_staff:
        return redirect('/admin-dashboard/')
    
    # Check if user has an employee profile with a role
    try:
        employee_profile = request.user.employee_profile
        
        # If user is admin role, redirect to admin dashboard
        if employee_profile.role == 'admin':
            return redirect('/admin-dashboard/')
        else:
            # Non-admin users (call_center, sales, user) go to employee portal
            return redirect(reverse('crm:employee_dashboard'))
    
    except AttributeError:
        # No employee profile exists
        # If staff user without employee profile, go to admin dashboard
        if request.user.is_staff:
            return redirect('/admin-dashboard/')
        else:
            # Regular users without employee profile - redirect to assets as fallback
            return redirect('/assets/')


class RoleBasedLoginView(LoginView):
    """
    Custom login view that redirects users based on their role.
    - Admin users: redirected to /admin-dashboard/ (admin dashboard)
    - Non-admin users (call_center, sales, user): redirected to /crm/employee/ (employee portal)
    """
    
    def get_success_url(self):
        """Determine redirect URL based on user role"""
        # Get the next parameter if provided
        next_url = self.request.GET.get('next') or self.request.POST.get('next')

        # Check if user is superuser first (highest priority)
        if self.request.user.is_superuser:
            return next_url if next_url else '/admin-dashboard/'

        # Check if user has an employee profile with a role
        try:
            employee_profile = self.request.user.employee_profile

            # If user is admin role, redirect to admin dashboard
            if employee_profile.role == 'admin':
                return next_url if next_url else '/admin-dashboard/'
            else:
                # Non-admin users (call_center, sales, user) go to employee portal
                return reverse('crm:employee_dashboard')

        except AttributeError:
            # No employee profile exists
            # If staff user without employee profile, go to admin dashboard
            if self.request.user.is_staff:
                return next_url if next_url else '/admin-dashboard/'
            else:
                # Regular users without employee profile - redirect to assets as fallback
                # (they may need to contact admin to set up their employee profile)
                return next_url if next_url else '/assets/'


@login_required
def user_profile(request, user_id):
    """Display user profile with QR code"""
    user = get_object_or_404(User, id=user_id)
    
    # Check if user can view this profile (self or admin)
    if not (request.user == user or request.user.is_staff):
        return render(request, 'users/access_denied.html', status=403)
    
    # Generate user QR data
    qr_data = generate_user_qr_data(user, request)
    
    context = {
        'profile_user': user,
        'qr_data': qr_data,
    }
    
    return render(request, 'users/profile.html', context)


@login_required
def user_qr_code(request, user_id):
    """Display user QR code page"""
    user = get_object_or_404(User, id=user_id)
    
    # Check permissions
    if not (request.user == user or request.user.is_staff):
        return render(request, 'users/access_denied.html', status=403)
    
    # Generate QR data
    qr_data = generate_user_qr_data(user, request)
    
    context = {
        'profile_user': user,
        'qr_data': qr_data,
    }
    
    return render(request, 'users/user_qr_code.html', context)


@login_required
@require_http_methods(["GET"])
def user_qr_code_image(request, user_id):
    """Generate user QR code image"""
    user = get_object_or_404(User, id=user_id)
    
    # Check permissions
    if not (request.user == user or request.user.is_staff):
        return HttpResponse('Access denied', status=403)
    
    # Get size parameter
    size = int(request.GET.get('size', 200))
    size = max(100, min(size, 800))  # Limit size between 100 and 800
    
    # Generate user QR data
    qr_data = generate_user_qr_data(user, request)
    
    # Generate QR code image with user data
    qr_data_url = generate_qr_code_image(qr_data['qr_data'], size=(size, size))
    
    if not qr_data_url:
        return HttpResponse('QR code generation not available', status=500)
    
    # Extract base64 data
    base64_data = qr_data_url.split(',')[1]
    
    # Return image
    import base64
    image_data = base64.b64decode(base64_data)
    
    response = HttpResponse(image_data, content_type='image/png')
    response['Cache-Control'] = 'max-age=3600'  # Cache for 1 hour
    
    return response


@login_required
@require_http_methods(["GET"])
def download_user_qr_code(request, user_id):
    """Download user QR code as PNG file"""
    user = get_object_or_404(User, id=user_id)
    
    # Check permissions
    if not (request.user == user or request.user.is_staff):
        return HttpResponse('Access denied', status=403)
    
    # Get size parameter
    size = int(request.GET.get('size', 300))
    size = max(100, min(size, 800))
    
    # Generate user QR data
    qr_data = generate_user_qr_data(user, request)
    
    # Generate QR code image
    qr_data_url = generate_qr_code_image(qr_data['qr_data'], size=(size, size))
    
    if not qr_data_url:
        return HttpResponse('QR code generation not available', status=500)
    
    # Extract base64 data
    base64_data = qr_data_url.split(',')[1]
    
    # Return as download
    import base64
    image_data = base64.b64decode(base64_data)
    
    response = HttpResponse(image_data, content_type='image/png')
    
    # Set filename
    filename = f"{user.username}_qr_code_{size}x{size}.png"
    if hasattr(user, 'profile') and user.profile.employee_id:
        filename = f"{user.profile.employee_id}_qr_code_{size}x{size}.png"
    
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@login_required
@require_http_methods(["GET"])
def user_qr_data_json(request, user_id):
    """Return user QR data as JSON"""
    user = get_object_or_404(User, id=user_id)
    
    # Check permissions
    if not (request.user == user or request.user.is_staff):
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    # Generate user QR data
    qr_data = generate_user_qr_data(user, request)
    
    return JsonResponse(qr_data['user_data'], json_dumps_params={'indent': 2})


@login_required
@require_http_methods(["GET"])
def session_status(request):
    """Debug view to check session status"""
    session_data = {
        'user': request.user.username,
        'session_key': request.session.session_key,
        'session_age': request.session.get_expiry_age(),
        'session_expires': request.session.get_expiry_date().isoformat() if request.session.get_expiry_date() else None,
        'is_authenticated': request.user.is_authenticated,
        'session_data_keys': list(request.session.keys()),
        'user_id': request.user.id,
    }
    
    # Check if session exists in database
    try:
        session_obj = Session.objects.get(session_key=request.session.session_key)
        session_data['session_in_db'] = True
        session_data['db_expire_date'] = session_obj.expire_date.isoformat()
    except Session.DoesNotExist:
        session_data['session_in_db'] = False
    
    return JsonResponse(session_data, json_dumps_params={'indent': 2})


@login_required
@require_http_methods(["GET"])
def session_status(request):
    """Debug view to check session status"""
    session_data = {
        'user': request.user.username,
        'session_key': request.session.session_key,
        'session_age': request.session.get_expiry_age(),
        'session_expires': request.session.get_expiry_date().isoformat() if request.session.get_expiry_date() else None,
        'is_authenticated': request.user.is_authenticated,
        'session_data_keys': list(request.session.keys()),
        'user_id': request.user.id,
    }
    
    # Check if session exists in database
    try:
        session_obj = Session.objects.get(session_key=request.session.session_key)
        session_data['session_in_db'] = True
        session_data['db_expire_date'] = session_obj.expire_date.isoformat()
    except Session.DoesNotExist:
        session_data['session_in_db'] = False
    
    return JsonResponse(session_data, json_dumps_params={'indent': 2})
