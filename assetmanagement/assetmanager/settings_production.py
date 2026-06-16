"""
Production settings for Vercel deployment
"""

from .settings import *
import os
import dj_database_url

# Force production environment detection
DEBUG = False

# Ensure VERCEL environment is detected
VERCEL_ENV = os.environ.get('VERCEL', False) or os.environ.get('VERCEL_ENV', False)

# Database configuration - Force PostgreSQL in production
if VERCEL_ENV or os.environ.get('DATABASE_URL'):
    # Production database configuration
    DATABASE_URL = os.environ.get('DATABASE_URL', 
        'postgresql://postgres.dxesmzogjpxswxhsomgf:OnFRtf0SmpHwgNaQ@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres'
    )
    
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
    
    # Ensure we're using PostgreSQL
    if 'sqlite' in DATABASES['default']['ENGINE']:
        raise ValueError("SQLite detected in production environment. This will cause readonly database errors.")
    
    print(f"Using database engine: {DATABASES['default']['ENGINE']}")
    print(f"Database host: {DATABASES['default']['HOST']}")

# Static files settings for Vercel
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files settings for Vercel
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security settings for production
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_TZ = True

# Session settings for production
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Allow Vercel hosts
ALLOWED_HOSTS = [
    'fagiassets.vercel.app',
    '.vercel.app',
    '127.0.0.1',
    'localhost'
]

# CORS settings for production
CORS_ALLOWED_ORIGINS = [
    "https://fagiassets.vercel.app",
]

# Logging configuration for production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'users.backends': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}