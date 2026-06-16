#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanagement.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile

user = User.objects.filter(first_name='Cyrus', last_name='Mweu').first()

if user:
    print(f"Found user: {user.get_full_name()}")
    profile, created = UserProfile.objects.get_or_create(user=user)
    old_title = profile.job_title
    profile.job_title = 'Accountant'
    profile.save()
    print(f"Updated job title from '{old_title}' to '{profile.job_title}'")
else:
    print("User 'Cyrus Mweu' not found")
    print("\nAvailable users:")
    for u in User.objects.all()[:20]:
        profile = getattr(u, 'profile', None)
        job_title = profile.job_title if profile else 'N/A'
        print(f"  - {u.get_full_name() or u.username} (Job Title: {job_title})")
