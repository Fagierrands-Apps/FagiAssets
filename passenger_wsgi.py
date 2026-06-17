"""
WSGI config for cPanel deployment using Passenger.
This file is used by cPanel's Python application hosting.
"""

import os
import sys
from pathlib import Path

# Add your project directories to sys.path
project_home = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(project_home, 'assetmanagement')

if project_home not in sys.path:
    sys.path.insert(0, project_home)
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Load environment variables from .env file
env_file = Path(project_home) / '.env.cpanel'
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
    print(f"Warning: .env file not found at {env_file}")

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
os.environ['DEBUG'] = 'False'

# Import Django's WSGI handler
try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    print("Django application loaded successfully")
except Exception as e:
    print(f"Error loading Django application: {e}")
    import traceback
    traceback.print_exc()
    raise