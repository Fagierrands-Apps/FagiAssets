# Generated migration to update employee IDs to FGE format

from django.db import migrations
from django.contrib.auth.models import User

def migrate_employee_ids_to_fge(apps, schema_editor):
    """
    Migrate existing employee IDs to FGE format (FGE001, FGE002, etc.)
    """
    UserProfile = apps.get_model('users', 'UserProfile')
    
    # Get all users ordered by ID for consistent numbering
    users_with_profiles = UserProfile.objects.all().order_by('user__id')
    
    print(f"Migrating {users_with_profiles.count()} user profiles to FGE format...")
    
    for index, profile in enumerate(users_with_profiles, start=1):
        old_employee_id = profile.employee_id
        new_employee_id = f"FGE{index:03d}"
        
        profile.employee_id = new_employee_id
        profile.save()
        
        print(f"  User: {profile.user.username} | {old_employee_id} -> {new_employee_id}")

def reverse_migrate_employee_ids(apps, schema_editor):
    """
    Reverse migration - restore original employee ID format
    """
    UserProfile = apps.get_model('users', 'UserProfile')
    
    # Get all users with FGE IDs
    fge_profiles = UserProfile.objects.filter(employee_id__startswith='FGE')
    
    print(f"Reversing {fge_profiles.count()} FGE employee IDs...")
    
    from datetime import datetime
    current_year = datetime.now().year
    
    for index, profile in enumerate(fge_profiles, start=1):
        old_employee_id = profile.employee_id
        new_employee_id = f"EMP-{current_year}-{index:04d}"
        
        profile.employee_id = new_employee_id
        profile.save()
        
        print(f"  User: {profile.user.username} | {old_employee_id} -> {new_employee_id}")

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0004_auto_20250711_0858'),
    ]

    operations = [
        migrations.RunPython(
            migrate_employee_ids_to_fge,
            reverse_migrate_employee_ids,
            atomic=True,
        ),
    ]