"""
Setup Script - Creates directory structure and files for database sync
Run this from cPanel's Python app interface or via web upload
"""
import os
from pathlib import Path

# Get the base directory (where this script is located)
BASE_DIR = Path(__file__).resolve().parent
ASSET_MGMT = BASE_DIR / 'assetmanagement'

print("Creating directory structure...")

# Create management command directories
dirs_to_create = [
    ASSET_MGMT / 'assets' / 'management',
    ASSET_MGMT / 'assets' / 'management' / 'commands',
]

for dir_path in dirs_to_create:
    dir_path.mkdir(parents=True, exist_ok=True)
    print(f"✓ Created: {dir_path}")
    
    # Create __init__.py files
    init_file = dir_path / '__init__.py'
    if not init_file.exists():
        init_file.touch()
        print(f"✓ Created: {init_file}")

# Create sync_to_backup.py command
sync_command = ASSET_MGMT / 'assets' / 'management' / 'commands' / 'sync_to_backup.py'

sync_code = '''from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import connections, transaction
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Sync data from primary (cPanel) to backup (Supabase)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be synced without actually syncing",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes"))
        
        self.stdout.write("Starting database sync...")
        total_synced = 0
        
        for model in apps.get_models():
            model_name = f"{model._meta.app_label}.{model.__name__}"
            
            try:
                primary_count = model.objects.using("default").count()
                backup_count = model.objects.using("backup").count()
                
                self.stdout.write(f"\\n{model_name}:")
                self.stdout.write(f"  Primary: {primary_count} records")
                self.stdout.write(f"  Backup:  {backup_count} records")
                
                if dry_run:
                    continue
                
                objects = list(model.objects.using("default").all())
                
                if not objects:
                    self.stdout.write(self.style.WARNING("  ⊘ No data"))
                    continue
                
                with transaction.atomic(using="backup"):
                    model.objects.using("backup").all().delete()
                    
                    batch_size = 100
                    for i in range(0, len(objects), batch_size):
                        batch = objects[i:i + batch_size]
                        model.objects.using("backup").bulk_create(
                            batch, ignore_conflicts=True
                        )
                
                new_count = model.objects.using("backup").count()
                total_synced += new_count
                
                self.stdout.write(
                    self.style.SUCCESS(f"  ✓ Synced {new_count} records")
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  ✗ Error: {str(e)}")
                )
                logger.error(f"Sync error for {model_name}: {e}", exc_info=True)
        
        self.stdout.write("\\n" + "="*50)
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN COMPLETE"))
        else:
            self.stdout.write(
                self.style.SUCCESS(f"✓ Sync complete! Total: {total_synced}")
            )
'''

with open(sync_command, 'w') as f:
    f.write(sync_code)
print(f"✓ Created: {sync_command}")

print("\n" + "="*60)
print("✓ Setup complete!")
print("\nNext steps:")
print("1. Update your .env file with database credentials")
print("2. Run: python manage.py migrate")
print("3. Run: python manage.py sync_to_backup --dry-run")
print("="*60)
