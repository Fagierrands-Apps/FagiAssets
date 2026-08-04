#!/usr/bin/env python
"""Delete all existing riders and seed new ones"""
import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import django; django.setup()

from django.db import connection
from users.models import Rider

# Fix id_number constraint to allow nulls if migration not yet applied
with connection.cursor() as cursor:
    try:
        cursor.execute("ALTER TABLE users_rider DROP CONSTRAINT IF EXISTS users_rider_id_number_key")
        cursor.execute("ALTER TABLE users_rider ALTER COLUMN id_number DROP NOT NULL")
        print("Fixed column constraints.")
    except Exception as e:
        print(f"Constraint fix skipped: {e}")

deleted, _ = Rider.objects.all().delete()
print(f"Deleted {deleted} existing rider(s).")

riders = [
    {'name': 'Johnsone Wawire',  'plate_number': 'KMGF 272N', 'phone': '0710101014'},
    {'name': 'Shadrack Atito',   'plate_number': 'KMGU 296E', 'phone': '0721925666'},
    {'name': 'Cyrus Ambani',     'plate_number': 'KMFV 307D', 'phone': '0742334074'},
    {'name': 'Willy Masinde',    'plate_number': 'KMGL 349M', 'phone': '0725575674'},
    {'name': 'Daniel Nyakundi',  'plate_number': 'KMGW 951L', 'phone': '0714457094'},
    {'name': 'Tony Sangura',     'plate_number': 'KMFB 367K', 'phone': '0724960875'},
]

for r in riders:
    rider = Rider(**r)
    rider.save()
    print(f"Created: {rider.rider_id} - {rider.name}")

print(f"\nSeeded {len(riders)} rider(s).")

# Rename EMP -> FGR
for rider in Rider.objects.filter(rider_id__startswith='EMP'):
    old = rider.rider_id
    rider.rider_id = 'FGR' + old[3:]
    rider.save()
    print(f"Renamed: {old} -> {rider.rider_id}")
