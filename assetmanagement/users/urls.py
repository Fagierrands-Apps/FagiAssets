"""
URL configuration for users app
"""
from django.urls import path
from . import views
from . import health_views
from . import public_views

app_name = 'users'

urlpatterns = [
    # Public views (no login required - for QR code scanning)
    path('<int:user_id>/public/', public_views.user_public_view, name='user_public_view'),
    path('<int:user_id>/public/data.json', public_views.user_public_data_json, name='user_public_data_json'),
    path('public/<uuid:qr_token>/', public_views.user_public_profile, name='user_public_profile'),

    # User profile (login required)
    path('<int:user_id>/', views.user_profile, name='profile'),

    # User QR code views (login required)
    path('<int:user_id>/qr/', views.user_qr_code, name='qr_code'),
    path('<int:user_id>/qr/image/', views.user_qr_code_image, name='qr_code_image'),
    path('<int:user_id>/qr/download/', views.download_user_qr_code, name='download_qr_code'),
    path('<int:user_id>/qr/data.json', views.user_qr_data_json, name='qr_data_json'),

    # Name tag download (login required)
    path('<int:user_id>/nametag/', views.download_nametag_pdf, name='download_nametag'),
    path('nametag/bulk/', views.bulk_nametag_pdf, name='bulk_nametag'),

    # Debug views
    path('session-status/', views.session_status, name='session_status'),
    path('health/', health_views.health_check, name='health_check'),
]