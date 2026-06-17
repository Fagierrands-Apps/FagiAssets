"""
Database Migration Script - Migrate from OLD Supabase to cPanel PostgreSQL
Run this via Python App interface or upload and execute via web
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'assetmanagement'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
django.setup()

from django.core.management import call_command
from django.db import connections
from django.apps import apps
import subprocess

print("="*60)
print("DATABASE MIGRATION: Old Supabase → cPanel PostgreSQL")
print("="*60)

# Step 1: Test connections
print("\n[1/5] Testing database connections...")
try:
    with connections['old_supabase'].cursor() as cursor:
        cursor.execute("SELECT 1")
    print("  ✓ Old Supabase connection OK")
except Exception as e:
    print(f"  ✗ Old Supabase connection failed: {e}")
    sys.exit(1)

try:
    with connections['default'].cursor() as cursor:
        cursor.execute("SELECT 1")
    print("  ✓ cPanel PostgreSQL connection OK")
except Exception as e:
    print(f"  ✗ cPanel connection failed: {e}")
    sys.exit(1)

# Step 2: Copy data model by model
print("\n[2/5] Copying data from old Supabase to cPanel...")
total_copied = 0

for model in apps.get_models():
    model_name = f"{model._meta.app_label}.{model.__name__}"
    
    try:
        # Get data from old supabase
        old_objects = list(model.objects.using('old_supabase').all())
        
        if not old_objects:
            print(f"  ⊘ {model_name}: No data")
            continue
        
        # Clear existing data in cPanel (optional - comment out if you want to merge)
        model.objects.using('default').all().delete()
        
        # Copy to cPanel in batches
        batch_size = 100
        for i in range(0, len(old_objects), batch_size):
            batch = old_objects[i:i + batch_size]
            model.objects.using('default').bulk_create(batch, ignore_conflicts=True)
        
        count = model.objects.using('default').count()
        total_copied += count
        print(f"  ✓ {model_name}: {count} records")
        
    except Exception as e:
        print(f"  ✗ {model_name}: Error - {e}")

print(f"\n  Total records copied: {total_copied}")

# Step 3: Run migrations on cPanel
print("\n[3/5] Running migrations on cPanel database...")
try:
    call_command('migrate', database='default', verbosity=0)
    print("  ✓ Migrations complete")
except Exception as e:
    print(f"  ✗ Migration failed: {e}")

# Step 4: Verify data
print("\n[4/5] Verifying data...")
try:
    from django.contrib.auth.models import User
    from assets.models import Asset
    
    user_count = User.objects.using('default').count()
    asset_count = Asset.objects.using('default').count()
    
    print(f"  ✓ Users: {user_count}")
    print(f"  ✓ Assets: {asset_count}")
except Exception as e:
    print(f"  ⚠ Verification warning: {e}")

# Step 5: Initial backup to new Supabase
print("\n[5/5] Initial backup to new Supabase...")
try:
    with connections['backup'].cursor() as cursor:
        cursor.execute("SELECT 1")
    print("  ✓ New Supabase connection OK")
    
    # Run initial sync
    print("  Running initial sync...")
    call_command('sync_to_backup', verbosity=1)
    
except Exception as e:
    print(f"  ⚠ Backup sync error: {e}")
    print("  You can run 'python manage.py sync_to_backup' manually later")

print("\n" + "="*60)
print("✓ MIGRATION COMPLETE!")
print("\nNext steps:")
print("1. Test your application thoroughly")
print("2. Verify all data is accessible")
print("3. Setup cron job for automatic backups")
print("4. After 1 week, delete old Supabase project")
print("="*60)
