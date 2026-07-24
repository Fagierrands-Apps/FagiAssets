from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    # Main admin dashboard - now unified
    path('', views.unified_dashboard, name='dashboard'),
    path('unified/', views.unified_dashboard, name='unified_dashboard'),
    
    # User Management
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.user_create, name='user_create'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('users/<int:user_id>/toggle-active/', views.user_toggle_active, name='user_toggle_active'),
    
    # User QR Code Management
    path('users/<int:user_id>/qr-code/', views.user_qr_code, name='user_qr_code'),
    path('users/<int:user_id>/qr-details/', views.user_qr_details, name='user_qr_details'),
    path('users/bulk-qr-codes/', views.bulk_user_qr_codes, name='bulk_user_qr_codes'),
    
    # Asset Management
    path('assets/', views.asset_admin_list, name='asset_list'),
    path('assets/add/', views.asset_create, name='asset_create'),
    path('assets/<int:asset_id>/', views.asset_admin_detail, name='asset_detail'),
    path('assets/<int:asset_id>/edit/', views.asset_edit, name='asset_edit'),
    path('assets/<int:asset_id>/delete/', views.asset_delete, name='asset_delete'),
    
    # Asset Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_create, name='category_create'),
    path('categories/<int:category_id>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:category_id>/delete/', views.category_delete, name='category_delete'),
    
    # Manufacturers
    path('manufacturers/', views.manufacturer_list, name='manufacturer_list'),
    path('manufacturers/add/', views.manufacturer_create, name='manufacturer_create'),
    path('manufacturers/<int:manufacturer_id>/edit/', views.manufacturer_edit, name='manufacturer_edit'),
    path('manufacturers/<int:manufacturer_id>/delete/', views.manufacturer_delete, name='manufacturer_delete'),
    
    # Asset Models
    path('asset-models/', views.asset_model_list, name='asset_model_list'),
    path('asset-models/add/', views.asset_model_create, name='asset_model_create'),
    path('asset-models/<int:model_id>/edit/', views.asset_model_edit, name='asset_model_edit'),
    path('asset-models/<int:model_id>/delete/', views.asset_model_delete, name='asset_model_delete'),
    
    # Locations
    path('locations/', views.location_list, name='location_list'),
    path('locations/add/', views.location_create, name='location_create'),
    path('locations/<int:location_id>/edit/', views.location_edit, name='location_edit'),
    path('locations/<int:location_id>/delete/', views.location_delete, name='location_delete'),
    
    # Departments
    path('departments/', views.department_list, name='department_list'),
    path('departments/add/', views.department_create, name='department_create'),
    path('departments/<int:department_id>/edit/', views.department_edit, name='department_edit'),
    path('departments/<int:department_id>/delete/', views.department_delete, name='department_delete'),
    
    # Discovery Management
    path('discovery/', views.discovery_admin, name='discovery_admin'),
    path('discovery/network-ranges/', views.network_range_list, name='network_range_list'),
    path('discovery/network-ranges/add/', views.network_range_create, name='network_range_create'),
    path('discovery/network-ranges/<int:range_id>/edit/', views.network_range_edit, name='network_range_edit'),
    path('discovery/network-ranges/<int:range_id>/delete/', views.network_range_delete, name='network_range_delete'),
    
    # System Settings
    path('settings/', views.system_settings, name='system_settings'),
    path('settings/backup/', views.system_backup, name='system_backup'),
    path('settings/logs/', views.system_logs, name='system_logs'),
    
    # Employee Management
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/<int:employee_id>/', views.employee_detail, name='employee_detail'),
    
    # Task Management
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/assign/', views.task_assign, name='task_assign'),
    
    # Time Tracking
    path('time-tracking/', views.time_tracking_overview, name='time_tracking_overview'),
    path('time-tracking/download/', views.download_time_tracking_report, name='download_time_tracking_report'),
    
    # Reports
    path('reports/', views.admin_reports, name='reports'),

    # Leave Requests shortcut
    path('leave-requests/', views.admin_leave_redirect, name='leave_requests'),

    # Rider Management
    path('riders/', views.rider_list, name='rider_list'),
    path('riders/add/', views.rider_create, name='rider_create'),
    path('riders/<int:rider_id>/edit/', views.rider_edit, name='rider_edit'),
    path('riders/<int:rider_id>/delete/', views.rider_delete, name='rider_delete'),

    # AJAX endpoints
    path('ajax/user-search/', views.ajax_user_search, name='ajax_user_search'),
    path('ajax/asset-search/', views.ajax_asset_search, name='ajax_asset_search'),
]