"""
Public views for users (accessible without login via QR codes)
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods


def user_public_view(request, user_id):
    """Public view for user information (accessible via QR code without login)"""
    user = get_object_or_404(User, id=user_id)
    
    # Get user profile if it exists
    profile = getattr(user, 'profile', None)
    
    # Get assigned assets (public information only)
    assigned_assets = []
    if hasattr(user, 'assigned_assets'):
        for asset in user.assigned_assets.filter(status__in=['active', 'assigned']):
            assigned_assets.append({
                'asset_tag': asset.asset_tag,
                'name': asset.name,
                'category': asset.category.name if asset.category else None,
                'status': asset.status,
            })
    
    context = {
        'profile_user': user,
        'profile': profile,
        'assigned_assets': assigned_assets,
        'is_public_view': True,
    }
    
    return render(request, 'users/user_public_view.html', context)


@require_http_methods(["GET"])
def user_public_data_json(request, user_id):
    """Public JSON endpoint for user data (accessible via QR code without login)"""
    user = get_object_or_404(User, id=user_id)
    
    # Get user profile if it exists
    profile = getattr(user, 'profile', None)
    
    # Get assigned assets (public information only)
    assigned_assets = []
    if hasattr(user, 'assigned_assets'):
        for asset in user.assigned_assets.filter(status__in=['active', 'assigned']):
            assigned_assets.append({
                'asset_tag': asset.asset_tag,
                'name': asset.name,
                'category': asset.category.name if asset.category else None,
                'status': asset.status,
            })
    
    # Build public user data (safe information only)
    user_data = {
        'user_id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'is_active': user.is_active,
        'assigned_assets': assigned_assets,
    }
    
    # Add safe profile data if available
    if profile:
        user_data.update({
            'employee_id': profile.employee_id,
            'phone': profile.phone,
            'job_title': profile.job_title,
            'department': profile.department.name if profile.department else None,
            'location': profile.location.name if profile.location else None,
        })
    
    return JsonResponse(user_data, json_dumps_params={'indent': 2})


def user_public_profile(request, qr_token):
    """Public profile via QR token — no login required."""
    from users.models import UserProfile
    from django.conf import settings
    from types import SimpleNamespace

    up   = get_object_or_404(UserProfile, qr_token=qr_token)
    user = up.user
    emp  = getattr(user, 'employee_profile', None)

    # Merge: prefer employee_profile data, fall back to UserProfile
    profile = SimpleNamespace(
        employee_id = (emp.employee_id if emp else None) or up.employee_id or "N/A",
        job_title   = (emp.position    if emp else None) or up.job_title   or "N/A",
        department  = SimpleNamespace(name=str(emp.department)) if emp and emp.department else (
                      up.department if up.department else None),
        phone       = (emp.phone       if emp else None) or up.phone or up.mobile or "N/A",
        avatar      = up.avatar if up.avatar else None,
    )

    context = {
        'profile_user': user,
        'profile': profile,
        'company_name': getattr(settings, 'COMPANY_NAME', 'Fagi Errands Services Limited'),
        'company_website': getattr(settings, 'COMPANY_WEBSITE', 'fagierrands.com'),
    }
    return render(request, 'users/user_public_profile.html', context)
