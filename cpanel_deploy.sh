#!/bin/bash
# cPanel Deployment Script for fagicrm.fagitone.com
# Run this script after uploading your files to cPanel
# Usage: ./cpanel_deploy.sh

echo "=========================================="
echo "Django cPanel Deployment Script"
echo "Domain: fagicrm.fagitone.com"
echo "=========================================="

# Configuration
CPANEL_USER="distinc3"
PYTHON_VERSION="3.11"
PROJECT_ROOT="/home/${CPANEL_USER}/fagiassets"
VENV_PATH="/home/${CPANEL_USER}/virtualenv/fagiassets/${PYTHON_VERSION}"

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Project directory: $SCRIPT_DIR"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠ Warning: .env file not found!"
    echo "Please create .env file with your configuration."
    echo "You can copy from .env.example if available."
    exit 1
fi
echo "✓ .env file found"

# Activate virtual environment
if [ -d "$VENV_PATH" ]; then
    source "$VENV_PATH/bin/activate"
    echo "✓ Virtual environment activated: $VENV_PATH"
elif [ -d "virtualenv" ]; then
    source virtualenv/bin/activate
    echo "✓ Virtual environment activated (local)"
else
    echo "⚠ Warning: Virtual environment not found!"
    echo "Please create Python app in cPanel first."
    echo "Expected path: $VENV_PATH"
    exit 1
fi

# Verify Python version
PYTHON_VER=$(python --version)
echo "Python version: $PYTHON_VER"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip
echo "✓ pip upgraded"

# Install/Update dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "✗ Error installing dependencies"
    exit 1
fi

# Navigate to Django project
cd assetmanagement

# Check database connection
echo ""
echo "Testing database connection..."
python manage.py check --database default
if [ $? -eq 0 ]; then
    echo "✓ Database connection successful"
else
    echo "✗ Database connection failed"
    echo "Please check your database credentials in .env file"
    exit 1
fi

# Run migrations
echo ""
echo "Running database migrations..."
python manage.py migrate --noinput
if [ $? -eq 0 ]; then
    echo "✓ Migrations completed successfully"
else
    echo "✗ Migration failed"
    exit 1
fi

# Create cache table (if using database cache)
echo ""
echo "Creating cache table..."
python manage.py createcachetable 2>/dev/null || echo "Cache table already exists or not needed"

# Collect static files
echo ""
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear
if [ $? -eq 0 ]; then
    echo "✓ Static files collected successfully"
else
    echo "✗ Static files collection failed"
    exit 1
fi

# Create superuser (if needed)
echo ""
echo "Checking for superuser..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@fagicrm.fagitone.com', 'FagiAssets2024!')
    print('✓ Superuser created: admin / FagiAssets2024!')
else:
    print('✓ Superuser already exists')
EOF

# Set proper permissions
echo ""
echo "Setting file permissions..."
cd "$SCRIPT_DIR"

# Set directory permissions (755 = rwxr-xr-x)
find assetmanagement -type d -exec chmod 755 {} \;

# Set file permissions (644 = rw-r--r--)
find assetmanagement -type f -exec chmod 644 {} \;

# Set write permissions for media and logs
chmod -R 775 assetmanagement/media 2>/dev/null || mkdir -p assetmanagement/media && chmod -R 775 assetmanagement/media
chmod -R 775 assetmanagement/staticfiles 2>/dev/null || echo "Staticfiles directory permissions set"

# Make manage.py executable
chmod +x assetmanagement/manage.py

echo "✓ Permissions set successfully"

# Create necessary directories
echo ""
echo "Creating necessary directories..."
mkdir -p assetmanagement/media/qr_codes
mkdir -p assetmanagement/media/employee_ids
mkdir -p assetmanagement/logs
chmod -R 775 assetmanagement/media
chmod -R 775 assetmanagement/logs
echo "✓ Directories created"

# Test Django configuration
echo ""
echo "Testing Django configuration..."
cd assetmanagement
python manage.py check
if [ $? -eq 0 ]; then
    echo "✓ Django configuration is valid"
else
    echo "✗ Django configuration has errors"
    exit 1
fi

echo ""
echo "=========================================="
echo "✓ Deployment completed successfully!"
echo "=========================================="
echo ""
echo "Configuration Summary:"
echo "  Domain: fagicrm.fagitone.com"
echo "  Project: $PROJECT_ROOT"
echo "  Python: $PYTHON_VER"
echo "  Virtual Env: $VENV_PATH"
echo ""
echo "Next steps:"
echo "1. Go to cPanel → Setup Python App"
echo "2. Find your application and click 'Restart'"
echo "3. Visit https://fagicrm.fagitone.com"
echo "4. Login with: admin / FagiAssets2024!"
echo ""
echo "Important files:"
echo "  - .htaccess (configured for Apache)"
echo "  - .env (environment variables)"
echo "  - passenger_wsgi.py (WSGI entry point)"
echo ""
echo "Troubleshooting:"
echo "  - Check logs: tail -f ~/logs/error_log"
echo "  - Check Django logs: tail -f assetmanagement/logs/django.log"
echo "  - Test manually: cd assetmanagement && python manage.py runserver"
echo "=========================================="