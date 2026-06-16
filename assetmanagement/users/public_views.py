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