from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    CRMCustomerViewSet, AssetCustomerAssignmentViewSet, 
    SyncLogViewSet, IntegrationViewSet
)
from . import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r'customers', CRMCustomerViewSet)
router.register(r'assignments', AssetCustomerAssignmentViewSet)
router.register(r'sync-logs', SyncLogViewSet)
router.register(r'integration', IntegrationViewSet, basename='integration')

app_name = 'crm_integration'

urlpatterns = [
    # Web interface URLs
    path('', views.integration_dashboard, name='dashboard'),
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/<int:customer_id>/', views.customer_detail, name='customer_detail'),
    path('assignments/', views.assignment_list, name='assignment_list'),
    path('assignments/create/', views.create_assignment, name='create_assignment'),
    path('sync-logs/', views.sync_logs, name='sync_logs'),
    path('sync/', views.sync_action, name='sync_action'),
    path('settings/', views.settings_view, name='settings'),
    
    # API URLs
    path('api/', include(router.urls)),
]