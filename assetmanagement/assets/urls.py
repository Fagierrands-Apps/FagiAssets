from django.urls import path
from . import views

urlpatterns = [
    # Asset URLs
    path('', views.asset_list, name='asset_list'),
    path('<int:asset_id>/', views.asset_detail, name='asset_detail'),
    path('<int:asset_id>/public/', views.asset_public_view, name='asset_public_view'),
    path('add/', views.asset_form, name='asset_add'),
    path('<int:asset_id>/edit/', views.asset_form, name='asset_edit'),
    path('<int:asset_id>/qr-code/', views.asset_qr_code, name='asset_qr_code'),
    path('<int:asset_id>/qr-code.png', views.asset_qr_code_image, name='asset_qr_code_image'),
    path('<int:asset_id>/download-qr/', views.download_asset_qr_code, name='download_asset_qr_code'),
    path('<int:asset_id>/print-labels/', views.asset_label_print, name='asset_label_print'),
    path('bulk-print-labels/', views.bulk_label_print, name='bulk_label_print'),
    path('<int:asset_id>/history/', views.asset_history, name='asset_history'),
    path('<int:asset_id>/maintenance/', views.asset_maintenance, name='asset_maintenance'),
    
    # Asset Actions (AJAX)
    path('<int:asset_id>/assign-user/', views.asset_assign_user, name='asset_assign_user'),
    path('<int:asset_id>/schedule-maintenance/', views.asset_schedule_maintenance, name='asset_schedule_maintenance'),
    path('<int:asset_id>/change-status/', views.asset_change_status, name='asset_change_status'),
    path('generate-asset-tag/', views.generate_asset_tag, name='generate_asset_tag'),
    
    # Maintenance URLs
    path('maintenance/<int:maintenance_id>/update/', views.maintenance_update, name='maintenance_update'),
    path('maintenance/update-status/', views.maintenance_update_status, name='maintenance_update_status'),
    
    # Other views
    path('users/', views.user_assignments, name='user_assignments'),
    path('locations/', views.location_view, name='location_view'),
    path('departments/', views.department_view, name='department_view'),
]