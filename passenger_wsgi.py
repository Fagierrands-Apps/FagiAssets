"""
WSGI config for cPanel deployment using Passenger.
This file is used by cPanel's Python application hosting.
"""

import os
import sys
from pathlib import Path

# Add your project directory to the sys.path
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Add the fagicrm directory to sys.path
fagicrm_path = os.path.join(project_home, 'fagicrm')
if fagicrm_path not in sys.path:
    sys.path.insert(0, fagicrm_path)

# Load environment variables from .env file
env_file = Path(fagicrm_path) / '.env.production'
if not env_file.exists():
    env_file = Path(project_home) / '.env'

if env_file.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(env_file)
        print(f"Loaded environment variables from {env_file}")
    except ImportError:
        print("Warning: python-dotenv not installed")
else:
    print(f"Warning: .env file not found")

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fagicrm.settings_production')
os.environ['DEBUG'] = 'False'

# Import Django's WSGI handler
try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    print("Django application (fagicrm) loaded successfully")
except Exception as e:
    print(f"Error loading Django application: {e}")
    import traceback
    traceback.print_exc()
    raise