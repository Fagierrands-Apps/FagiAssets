from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import connections, transaction
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Sync data from primary (cPanel) to backup (Supabase)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be synced without actually syncing',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        self.stdout.write('Starting database sync...')
        total_synced = 0
        
        # Get all models
        for model in apps.get_models():
            model_name = f"{model._meta.app_label}.{model.__name__}"
            
            try:
                # Get count from primary
                primary_count = model.objects.using('default').count()
                backup_count = model.objects.using('backup').count()
                
                self.stdout.write(f'\n{model_name}:')
                self.stdout.write(f'  Primary: {primary_count} records')
                self.stdout.write(f'  Backup:  {backup_count} records')
                
                if dry_run:
                    continue
                
                # Get all objects from primary
                objects = list(model.objects.using('default').all())
                
                if not objects:
                    self.stdout.write(self.style.WARNING('  ⊘ No data to sync'))
                    continue
                
                # Clear backup and bulk insert
                with transaction.atomic(using='backup'):
                    model.objects.using('backup').all().delete()
                    
                    # Bulk create in batches
                    batch_size = 100
                    for i in range(0, len(objects), batch_size):
                        batch = objects[i:i + batch_size]
                        model.objects.using('backup').bulk_create(
                            batch, 
                            ignore_conflicts=True
                        )
                
                new_backup_count = model.objects.using('backup').count()
                total_synced += new_backup_count
                
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ Synced {new_backup_count} records')
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ✗ Error: {str(e)}')
                )
                logger.error(f"Sync error for {model_name}: {e}", exc_info=True)
        
        self.stdout.write('\n' + '='*50)
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN COMPLETE'))
        else:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Sync complete! Total records: {total_synced}')
            )
