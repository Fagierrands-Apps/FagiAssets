"""
Production settings for cPanel deployment.
Import this in your settings.py or use as DJANGO_SETTINGS_MODULE.
"""

import os
from pathlib import Path

# Build paths
BASE_DIR = Path(__file__).resolve().parent / 'assetmanagement'

# SECURITY WARNING: Change this in production!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-)uydf_yg5c=z5^)xi+&$1@y$7w@)lboa2l#eom$!4uk1l!22u0')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Add your domain here
ALLOWED_HOSTS = [
    'yourdomain.com',
    'www.yourdomain.com',
    'subdomain.yourdomain.com',
    'localhost',
    '127.0.0.1',
]

# Database configuration for cPanel PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'fagiassets_db'),
        'USER': os.environ.get('DB_USER', 'fagiassets_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'your_password_here'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 30,
        },
        'CONN_MAX_AGE': 600,
    }
}

# Static files configuration for cPanel
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_SSL_REDIRECT = True  # Enable if you have SSL
SESSION_COOKIE_SECURE = True  # Enable if you have SSL
CSRF_COOKIE_SECURE = True  # Enable if you have SSL

# CORS settings - adjust based on your needs
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'django_errors.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}