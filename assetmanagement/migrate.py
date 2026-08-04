#!/usr/bin/env python
"""
Run this on cPanel terminal to apply all migrations and post-deploy steps.
Usage: python migrate.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')

# Ensure we're in the right directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.core.management import call_command

print("=== Running migrations ===")
call_command('migrate', '--run-syncdb')

print("\n=== Backfilling missing user profiles ===")
call_command('backfill_user_profiles')

print("\n=== Collecting static files ===")
call_command('collectstatic', '--noinput')

print("\nDone. Restart the app (touch passenger_wsgi.py).")

# Seed riders
print("\n=== Seeding riders ===")
exec(open(os.path.join(os.path.dirname(__file__), 'seed_riders.py')).read())
