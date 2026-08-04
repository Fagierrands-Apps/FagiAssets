#!/usr/bin/env python
"""Run this to update existing EMP rider IDs to FGR"""
import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import django; django.setup()

from users.models import Rider

updated = 0
for rider in Rider.objects.filter(rider_id__startswith='EMP'):
    old = rider.rider_id
    rider.rider_id = 'FGR' + old[3:]
    rider.save()
    print(f"{old} -> {rider.rider_id}")
    updated += 1

print(f"\nUpdated {updated} rider(s).")
