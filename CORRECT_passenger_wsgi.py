"""
WSGI config for FagiAssets - Asset Management System
"""
import os
import sys
from pathlib import Path

# Project root
project_home = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_home)

# Add assetmanagement directory
assetmanagement_path = os.path.join(project_home, 'assetmanagement')
sys.path.insert(0, assetmanagement_path)

# Load .env
env_file = Path(project_home) / '.env'
if env_file.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(env_file)
    except ImportError:
        pass

# Django settings - CORRECT module name
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')

# WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
