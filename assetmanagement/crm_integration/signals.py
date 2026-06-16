from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from assets.models import Asset
from .models import AssetCustomerAssignment, SyncLog
from .services import CRMIntegrationService
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Asset)
def asset_assignment_changed(sender, instance, created, **kwargs):
    """Handle asset assignment changes"""
    if not created and instance.assigned_to:
        # Check if this asset has customer assignments that need updating
        try:
            service = CRMIntegrationService()
            settings = service.settings
            
            if settings.auto_sync_enabled and settings.sync_assets_to_crm:
                # Get active assignments for this asset
                assignments = AssetCustomerAssignment.objects.filter(
                    asset=instance,
                    is_active=True
                )
                
                # Sync each assignment to CRM
                for assignment in assignments:
                    try:
                        service._sync_assignment_to_crm(assignment)
                        logger.info(f"Synced asset assignment {assignment.id} to CRM")
                    except Exception as e:
                        logger.error(f"Failed to sync assignment {assignment.id}: {e}")
                        
                        # Log the sync error
                        SyncLog.objects.create(
                            sync_type='asset_to_crm',
                            sync_action='update',
                            status='error',
                            error_message=str(e),
                            records_processed=1,
                            records_error=1,
                            content_object=assignment
                        )
        
        except Exception as e:
            logger.error(f"Error in asset assignment sync signal: {e}")


@receiver(post_save, sender=AssetCustomerAssignment)
def assignment_created_or_updated(sender, instance, created, **kwargs):
    """Handle new or updated asset-customer assignments"""
    try:
        service = CRMIntegrationService()
        settings = service.settings
        
        if settings.auto_sync_enabled and settings.sync_assets_to_crm:
            try:
                service._sync_assignment_to_crm(instance)
                action = 'create' if created else 'update'
                logger.info(f"Synced asset assignment {instance.id} to CRM ({action})")
                
                # Log successful sync
                SyncLog.objects.create(
                    sync_type='asset_to_crm',
                    sync_action=action,
                    status='success',
                    records_processed=1,
                    records_success=1,
                    content_object=instance
                )
                
            except Exception as e:
                logger.error(f"Failed to sync assignment {instance.id}: {e}")
                
                # Log the sync error
                SyncLog.objects.create(
                    sync_type='asset_to_crm',
                    sync_action='create' if created else 'update',
                    status='error',
                    error_message=str(e),
                    records_processed=1,
                    records_error=1,
                    content_object=instance
                )
    
    except Exception as e:
        logger.error(f"Error in assignment sync signal: {e}")


@receiver(post_delete, sender=AssetCustomerAssignment)
def assignment_deleted(sender, instance, **kwargs):
    """Handle deleted asset-customer assignments"""
    try:
        service = CRMIntegrationService()
        settings = service.settings
        
        if settings.auto_sync_enabled and settings.sync_assets_to_crm:
            # Note: In a real implementation, you might want to notify the CRM
            # about the deletion or mark the assignment as inactive
            logger.info(f"Asset assignment {instance.id} deleted - CRM sync may be needed")
            
            # Log the deletion
            SyncLog.objects.create(
                sync_type='asset_to_crm',
                sync_action='delete',
                status='success',
                records_processed=1,
                records_success=1,
                error_message=f"Assignment deleted: Asset {instance.asset.asset_tag} from Customer {instance.customer.full_name}"
            )
    
    except Exception as e:
        logger.error(f"Error in assignment deletion sync signal: {e}")


@receiver(post_save, sender=User)
def user_profile_sync(sender, instance, created, **kwargs):
    """Sync user profile changes to CRM if needed"""
    if not created:  # Only for updates, not new users
        try:
            service = CRMIntegrationService()
            settings = service.settings
            
            if settings.auto_sync_enabled and settings.sync_employees:
                # Check if this user has an employee profile that should be synced
                if hasattr(instance, 'profile') and instance.profile.employee_id:
                    logger.info(f"User {instance.username} updated - employee sync may be needed")
                    
                    # In a full implementation, you might want to sync the user data back to CRM
                    # For now, we just log it
                    SyncLog.objects.create(
                        sync_type='employee_sync',
                        sync_action='update',
                        status='pending',
                        records_processed=1,
                        error_message=f"User {instance.username} updated - manual sync recommended"
                    )
        
        except Exception as e:
            logger.error(f"Error in user profile sync signal: {e}")