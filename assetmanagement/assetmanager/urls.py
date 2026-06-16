"""
URL configuration for assetmanager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from users.views import RoleBasedLoginView, root_redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication URLs
    path('login/', RoleBasedLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # API URLs
    path('api/', include('assets.api_urls')),
    
    # CRM Integration URLs (legacy)
    path('crm-integration/', include('crm_integration.urls')),
    
    # Unified CRM URLs
    path('crm/', include('crm.urls')),
    
    # Custom Admin Dashboard
    path('admin-dashboard/', include('admin_dashboard.urls')),
    
    # Main application URLs - redirect root to appropriate dashboard
    path('', root_redirect, name='root_redirect'),
    path('assets/', include('assets.urls')),
    path('discovery/', include('discovery.urls')),
    path('users/', include('users.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
