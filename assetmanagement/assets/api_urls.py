from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'assets', api_views.AssetViewSet)
router.register(r'models', api_views.AssetModelViewSet)
router.register(r'categories', api_views.AssetCategoryViewSet)
router.register(r'manufacturers', api_views.ManufacturerViewSet)
router.register(r'locations', api_views.LocationViewSet)
router.register(r'departments', api_views.DepartmentViewSet)
router.register(r'users', api_views.UserViewSet)
router.register(r'maintenance', api_views.MaintenanceRecordViewSet)

# API URL patterns
urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # Health check
    path('health/', api_views.health_check, name='api_health'),
    
    # Dashboard APIs
    path('dashboard/stats/', api_views.dashboard_stats, name='dashboard_stats'),
    path('dashboard/asset-distribution/', api_views.asset_distribution, name='asset_distribution'),
    path('dashboard/trends/', api_views.asset_trends, name='asset_trends'),
    path('dashboard/recent-activity/', api_views.recent_activity, name='recent_activity'),
    
    # Report APIs
    path('reports/<str:report_type>/', api_views.generate_report, name='generate_report'),
    
    # Discovery APIs
    path('discovery/start/', api_views.start_network_discovery, name='start_discovery'),
    path('discovery/devices/', api_views.get_discovered_devices, name='discovered_devices'),
]