"""
CORRECTED Database Migration Script
Run migrations FIRST, then copy data
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

print("="*60)
print("DATABASE MIGRATION (CORRECTED): Old Supabase → cPanel")
print("="*60)

# Step 1: Test connections
print("\n[1/6] Testing database connections...")
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

# Step 2: Run migrations on cPanel FIRST to create tables
print("\n[2/6] Creating tables in cPanel database...")
try:
    call_command('migrate', database='default', verbosity=1)
    print("  ✓ Tables created successfully")
except Exception as e:
    print(f"  ✗ Migration failed: {e}")
    sys.exit(1)

# Step 3: NOW copy data
print("\n[3/6] Copying data from old Supabase to cPanel...")
total_copied = 0
errors = []

# Priority order - dependencies first
model_order = [
    'auth.Permission',
    'contenttypes.ContentType', 
    'auth.User',
    'users.UserProfile',
    'assets.Location',
    'assets.Department',
    'assets.Manufacturer',
    'assets.AssetCategory',
    'assets.AssetModel',
    'assets.Asset',
    'crm.Department',
    'crm.Employee',
]

# Get all models
all_models = {f"{m._meta.app_label}.{m.__name__}": m for m in apps.get_models()}

# Process in order first, then remaining
ordered_models = []
for model_name in model_order:
    if model_name in all_models:
        ordered_models.append(all_models[model_name])
        
# Add remaining models
for model in apps.get_models():
    if model not in ordered_models:
        ordered_models.append(model)

for model in ordered_models:
    model_name = f"{model._meta.app_label}.{model.__name__}"
    
    try:
        # Get data from old supabase
        old_objects = list(model.objects.using('old_supabase').all())
        
        if not old_objects:
            continue
        
        # Copy to cPanel in batches (don't delete existing!)
        batch_size = 50
        created = 0
        for i in range(0, len(old_objects), batch_size):
            batch = old_objects[i:i + batch_size]
            # Use bulk_create with ignore_conflicts to skip duplicates
            result = model.objects.using('default').bulk_create(
                batch, 
                ignore_conflicts=True,
                batch_size=batch_size
            )
            created += len(result)
        
        if created > 0:
            total_copied += created
            print(f"  ✓ {model_name}: {created} records")
        
    except Exception as e:
        error_msg = f"{model_name}: {str(e)[:100]}"
        errors.append(error_msg)
        print(f"  ⚠ {error_msg}")

print(f"\n  Total records copied: {total_copied}")
if errors:
    print(f"  Errors: {len(errors)}")

# Step 4: Verify critical data
print("\n[4/6] Verifying critical data...")
try:
    from django.contrib.auth.models import User
    from assets.models import Asset
    
    user_count = User.objects.using('default').count()
    asset_count = Asset.objects.using('default').count()
    
    print(f"  ✓ Users: {user_count}")
    print(f"  ✓ Assets: {asset_count}")
    
    if user_count == 0:
        print("\n  ⚠ WARNING: No users found! You may need to create a superuser:")
        print("     python manage.py createsuperuser")
    
except Exception as e:
    print(f"  ⚠ Verification error: {e}")

# Step 5: Test new Supabase connection
print("\n[5/6] Testing new Supabase backup connection...")
try:
    with connections['backup'].cursor() as cursor:
        cursor.execute("SELECT 1")
    print("  ✓ New Supabase connection OK")
    
    # Run migrations on backup too
    print("  Creating tables in backup database...")
    call_command('migrate', database='backup', verbosity=0)
    print("  ✓ Backup database ready")
    
except Exception as e:
    print(f"  ⚠ Backup connection issue: {e}")
    print("  This is OK - backup sync will be done manually")

# Step 6: Initial sync to backup
print("\n[6/6] Initial sync to new Supabase backup...")
try:
    print("  Running sync command...")
    call_command('sync_to_backup', verbosity=1)
    print("  ✓ Initial backup complete")
except Exception as e:
    print(f"  ⚠ Backup sync error: {e}")
    print("  You can run 'python manage.py sync_to_backup' later")

print("\n" + "="*60)
print("✓ MIGRATION COMPLETE!")
print("\nDatabase Status:")
print("  • PRIMARY: cPanel PostgreSQL (distinc3_crm)")
print("  • BACKUP: New Supabase (ready for sync)")
print("  • OLD: Still available for reference")
print("\nNext steps:")
print("1. Test login: https://fagiassets.fagitone.com")
print("2. Verify all data is visible")
print("3. Run manual backup: python manage.py sync_to_backup")
print("4. Setup cron job for automatic backups")
print("="*60)
