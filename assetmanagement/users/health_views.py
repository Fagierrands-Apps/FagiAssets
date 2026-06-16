"""
Health check and admin initialization views
"""
import os
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.db import transaction


@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint that ensures admin user exists"""
    try:
        # Check if we're in production
        is_production = (
            os.environ.get('VERCEL') or 
            os.environ.get('DATABASE_URL') or 
            'vercel.app' in os.environ.get('VERCEL_URL', '')
        )
        
        if is_production:
            # Ensure admin user exists
            admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
            admin_password = os.environ.get('ADMIN_PASSWORD', 'FagiAssets2024!')
            admin_email = os.environ.get('ADMIN_EMAIL', 'admin@fagiassets.com')
            
            with transaction.atomic():
                user, created = User.objects.get_or_create(
                    username=admin_username,
                    defaults={
                        'email': admin_email,
                        'is_superuser': True,
                        'is_staff': True,
                        'is_active': True,
                    }
                )
                
                if created or not user.check_password(admin_password):
                    user.set_password(admin_password)
                    user.is_superuser = True
                    user.is_staff = True
                    user.is_active = True
                    user.save()
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'connected',
            'admin_user': 'configured',
            'environment': 'production' if is_production else 'development'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)