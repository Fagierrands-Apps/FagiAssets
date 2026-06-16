#!/bin/bash
# Vercel build script
# This script runs during Vercel deployment to set up the database

echo "Starting Vercel build process..."

# Set environment variables
export DJANGO_SETTINGS_MODULE=assetmanager.settings
export VERCEL=1

# Change to Django project directory
cd assetmanagement

# Install Python dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Initialize production environment (create admin user, etc.)
echo "Initializing production environment..."
python manage.py init_production

echo "Build completed successfully!"