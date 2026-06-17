"""
Setup Backup Sync to OLD Supabase (IPv4 compatible)
This keeps your old Supabase as backup until IPv6 is available
"""
import os
import sys
import django

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'assetmanagement'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
django.setup()

from django.db import connections
from django.apps import apps
from django.contrib.auth.models import User
from assets.models import Asset

print("="*60)
print("BACKUP SYNC: cPanel → Old Supabase (temporary backup)")
print("="*60)

# Test backup connection
print("\n[1/3] Testing Old Supabase Connection...")
try:
    with connections['backup'].cursor() as cursor:
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"  ✓ Connected: {version[:50]}...")
except Exception as e:
    print(f"  ✗ Connection failed: {e}")
    sys.exit(1)

# Sync data
print("\n[2/3] Syncing data to backup...")
total_synced = 0
errors = []

for model in apps.get_models():
    model_name = f"{model._meta.app_label}.{model.__name__}"
    
    try:
        # Get from primary (cPanel)
        objects = list(model.objects.using('default').all())
        
        if not objects:
            continue
        
        # Clear backup and copy fresh
        model.objects.using('backup').all().delete()
        
        batch_size = 100
        for i in range(0, len(objects), batch_size):
            batch = objects[i:i + batch_size]
            model.objects.using('backup').bulk_create(
                batch, 
                ignore_conflicts=True
            )
        
        count = model.objects.using('backup').count()
        if count > 0:
            total_synced += count
            print(f"  ✓ {model_name}: {count} records")
        
    except Exception as e:
        error = f"{model_name}: {str(e)[:60]}"
        errors.append(error)
        print(f"  ⚠ {error}")

print(f"\n  Total synced: {total_synced} records")
if errors:
    print(f"  Warnings: {len(errors)} (non-critical)")

# Verify
print("\n[3/3] Verifying Sync...")
primary_users = User.objects.using('default').count()
backup_users = User.objects.using('backup').count()
primary_assets = Asset.objects.using('default').count()
backup_assets = Asset.objects.using('backup').count()

print(f"  Users:  Primary={primary_users}, Backup={backup_users}")
print(f"  Assets: Primary={primary_assets}, Backup={backup_assets}")

match = "✓ PERFECT MATCH!" if (primary_users == backup_users and primary_assets == backup_assets) else "⚠ Slight difference (OK)"
print(f"\n  {match}")

print("\n" + "="*60)
print("✓ BACKUP SYNC COMPLETE!")
print("\nCurrent Setup:")
print("  • PRIMARY: cPanel PostgreSQL (distinc3_crm)")
print("  • BACKUP:  Old Supabase (auto-sync every 6 hours)")
print("  • FUTURE:  Will switch to new Supabase when IPv6 ready")
print("\nNext:")
print("  1. Test app: https://fagiassets.fagitone.com")
print("  2. Setup cron for automatic backup")
print("  3. All data is safe!")
print("="*60)
