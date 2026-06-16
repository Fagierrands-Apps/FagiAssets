from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from crm_integration.services import CRMIntegrationService
from crm_integration.models import IntegrationSettings
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Synchronize data between Asset Manager and CRM'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            choices=['customers', 'assignments', 'employees', 'full'],
            default='full',
            help='Type of synchronization to perform'
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Username of the user initiating the sync'
        )
        parser.add_argument(
            '--test-connection',
            action='store_true',
            help='Test connection to CRM system'
        )
        parser.add_argument(
            '--setup',
            action='store_true',
            help='Setup initial integration settings'
        )
        parser.add_argument(
            '--crm-url',
            type=str,
            help='CRM base URL for setup'
        )
        parser.add_argument(
            '--api-key',
            type=str,
            help='CRM API key for setup'
        )
    
    def handle(self, *args, **options):
        # Setup integration settings if requested
        if options['setup']:
            self.setup_integration(options)
            return
        
        # Test connection if requested
        if options['test_connection']:
            self.test_connection()
            return
        
        # Get user if specified
        user = None
        if options['user']:
            try:
                user = User.objects.get(username=options['user'])
            except User.DoesNotExist:
                raise CommandError(f"User '{options['user']}' not found")
        
        # Initialize service
        service = CRMIntegrationService()
        sync_type = options['type']
        
        self.stdout.write(f"Starting {sync_type} synchronization...")
        
        try:
            if sync_type == 'customers':
                sync_log = service.sync_customers_from_crm(user)
                self.report_sync_result('Customer sync', sync_log)
                
            elif sync_type == 'assignments':
                sync_log = service.sync_asset_assignments_to_crm(user)
                self.report_sync_result('Assignment sync', sync_log)
                
            elif sync_type == 'employees':
                sync_log = service.sync_employee_data(user)
                self.report_sync_result('Employee sync', sync_log)
                
            elif sync_type == 'full':
                results = service.full_sync(user)
                self.stdout.write(self.style.SUCCESS("Full synchronization completed:"))
                for sync_name, sync_log in results.items():
                    self.report_sync_result(f"{sync_name.title()} sync", sync_log)
            
        except Exception as e:
            raise CommandError(f"Synchronization failed: {str(e)}")
    
    def setup_integration(self, options):
        """Setup initial integration settings"""
        self.stdout.write("Setting up CRM integration...")
        
        settings = IntegrationSettings.get_settings()
        
        if options['crm_url']:
            settings.crm_base_url = options['crm_url']
            self.stdout.write(f"Set CRM URL to: {options['crm_url']}")
        
        if options['api_key']:
            settings.crm_api_key = options['api_key']
            self.stdout.write("Set CRM API key")
        
        # Set default sync settings
        settings.auto_sync_enabled = True
        settings.sync_customers_to_assets = True
        settings.sync_assets_to_crm = True
        settings.sync_employees = True
        settings.sync_interval_minutes = 30
        
        settings.save()
        
        self.stdout.write(self.style.SUCCESS("Integration settings configured successfully"))
        
        # Test connection
        self.test_connection()
    
    def test_connection(self):
        """Test connection to CRM system"""
        self.stdout.write("Testing connection to CRM...")
        
        service = CRMIntegrationService()
        success, message = service.test_connection()
        
        if success:
            self.stdout.write(self.style.SUCCESS(f"✓ {message}"))
        else:
            self.stdout.write(self.style.ERROR(f"✗ {message}"))
    
    def report_sync_result(self, sync_name, sync_log):
        """Report the result of a sync operation"""
        if sync_log.status == 'success':
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ {sync_name}: {sync_log.records_success}/{sync_log.records_processed} records synced successfully"
                )
            )
        elif sync_log.status == 'partial':
            self.stdout.write(
                self.style.WARNING(
                    f"⚠ {sync_name}: {sync_log.records_success}/{sync_log.records_processed} records synced "
                    f"({sync_log.records_error} errors)"
                )
            )
            if sync_log.error_message:
                self.stdout.write(f"  Errors: {sync_log.error_message}")
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"✗ {sync_name}: Failed - {sync_log.error_message or 'Unknown error'}"
                )
            )
        
        if sync_log.duration_seconds:
            self.stdout.write(f"  Duration: {sync_log.duration_seconds:.2f} seconds")