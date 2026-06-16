from celery import shared_task
from django.utils import timezone
from .services import NetworkDiscoveryService, AssetMatchingService
from .models import NetworkRange, ScanJob
import logging

logger = logging.getLogger(__name__)


@shared_task
def scan_network_range_task(network_range_id, scan_type='discovery', scan_options=None):
    """Celery task to scan a network range"""
    try:
        network_range = NetworkRange.objects.get(id=network_range_id)
        discovery_service = NetworkDiscoveryService()
        
        scan_job = discovery_service.scan_network_range(
            network_range=network_range,
            scan_type=scan_type,
            scan_options=scan_options or {}
        )
        
        return {
            'success': True,
            'scan_job_id': scan_job.id,
            'devices_found': scan_job.devices_found,
            'new_devices': scan_job.new_devices,
            'updated_devices': scan_job.updated_devices
        }
        
    except NetworkRange.DoesNotExist:
        logger.error(f"Network range with ID {network_range_id} not found")
        return {'success': False, 'error': 'Network range not found'}
    
    except Exception as e:
        logger.error(f"Error scanning network range {network_range_id}: {str(e)}")
        return {'success': False, 'error': str(e)}


@shared_task
def scan_all_active_ranges_task():
    """Celery task to scan all active network ranges"""
    try:
        discovery_service = NetworkDiscoveryService()
        discovery_service.scan_all_active_ranges()
        
        return {'success': True, 'message': 'All active ranges scanned'}
        
    except Exception as e:
        logger.error(f"Error scanning all active ranges: {str(e)}")
        return {'success': False, 'error': str(e)}


@shared_task
def match_discovered_devices_task():
    """Celery task to match discovered devices with assets"""
    try:
        matching_service = AssetMatchingService()
        matching_service.match_discovered_devices()
        
        return {'success': True, 'message': 'Device matching completed'}
        
    except Exception as e:
        logger.error(f"Error matching discovered devices: {str(e)}")
        return {'success': False, 'error': str(e)}


@shared_task
def cleanup_old_scan_results_task(days_to_keep=30):
    """Celery task to cleanup old scan results"""
    try:
        cutoff_date = timezone.now() - timezone.timedelta(days=days_to_keep)
        
        # Delete old scan jobs and their results
        old_scan_jobs = ScanJob.objects.filter(created_at__lt=cutoff_date)
        deleted_count = old_scan_jobs.count()
        old_scan_jobs.delete()
        
        return {
            'success': True, 
            'message': f'Cleaned up {deleted_count} old scan jobs'
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up old scan results: {str(e)}")
        return {'success': False, 'error': str(e)}


@shared_task
def periodic_network_discovery():
    """Periodic task for network discovery - runs every hour"""
    try:
        # Scan all active ranges
        scan_result = scan_all_active_ranges_task.delay()
        
        # Match discovered devices
        match_result = match_discovered_devices_task.delay()
        
        return {
            'success': True,
            'scan_task_id': scan_result.id,
            'match_task_id': match_result.id
        }
        
    except Exception as e:
        logger.error(f"Error in periodic network discovery: {str(e)}")
        return {'success': False, 'error': str(e)}from celery import shared_task
from django.utils import timezone
from .services import NetworkDiscoveryService, AssetMatchingService
from .models import NetworkRange, ScanJob
import logging

logger = logging.getLogger(__name__)


@shared_task
def scan_network_range_task(network_range_id, scan_type='discovery', scan_options=None):
    """Celery task to scan a network range"""
    try:
        network_range = NetworkRange.objects.get(id=network_range_id)
        discovery_service = NetworkDiscoveryService()
        
        scan_job = discovery_service.scan_network_range(
            network_range=network_range,
            scan_type=scan_type,
            scan_options=scan_options or {}
        )
        
        return {
            'success': True,
            'scan_job_id': scan_job.id,
            'devices_found': scan_job.devices_found,
            'new_devices': scan_job.new_devices,
            'updated_devices': scan_job.updated_devices
        }
        
    except NetworkRange.DoesNotExist:
        logger.error(f"Network range with ID {network_range_id} not found")
        return {'success': False, 'error': 'Network range not found'}
    
    except Exception as e:
        logger.error(f"Error scanning network range {network_range_id}: {str(e)}")
        return {'success': False, 'error': str(e)}


@shared_task
def scan_all_active_ranges_task():
    """Celery task to scan all active network ranges"""
    try:
        discovery_service = NetworkDiscoveryService()
        discovery_service.scan_all_active_ranges()
        
        return {'success': True, 'message': 'All active ranges scanned'}
        
    except Exception as e:
        logger.error(f"Error scanning all active ranges: {str(e)}")
        return {'success': False, 'error': str(e)}


@shared_task
def match_discovered_devices_task():
    """Celery task to match discovered devices with assets"""
    try:
        matching_service = AssetMatchingService()
        matching_service.match_discovered_devices()
        
        return {'success': True, 'message': 'Device matching completed'}
        
    except Exception as e:
        logger.error(f"Error matching discovered devices: {str(e)}")
        return {'success': False, 'error': str(e)}


@shared_task
def cleanup_old_scan_results_task(days_to_keep=30):
    """Celery task to cleanup old scan results"""
    try:
        cutoff_date = timezone.now() - timezone.timedelta(days=days_to_keep)
        
        # Delete old scan jobs and their results
        old_scan_jobs = ScanJob.objects.filter(created_at__lt=cutoff_date)
        deleted_count = old_scan_jobs.count()
        old_scan_jobs.delete()
        
        return {
            'success': True, 
            'message': f'Cleaned up {deleted_count} old scan jobs'
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up old scan results: {str(e)}")
        return {'success': False, 'error': str(e)}


@shared_task
def periodic_network_discovery():
    """Periodic task for network discovery - runs every hour"""
    try:
        # Scan all active ranges
        scan_result = scan_all_active_ranges_task.delay()
        
        # Match discovered devices
        match_result = match_discovered_devices_task.delay()
        
        return {
            'success': True,
            'scan_task_id': scan_result.id,
            'match_task_id': match_result.id
        }
        
    except Exception as e:
        logger.error(f"Error in periodic network discovery: {str(e)}")
        return {'success': False, 'error': str(e)}from celery import shared_task
from django.utils import timezone
from .services import NetworkDiscoveryService, AssetMatchingService
from .models import NetworkRange, ScanJob
import logging

logger = logging.getLogger(__name__)


@shared_task
def scan_network_range_task(network_range_id, scan_type='discovery', scan_options=None):
    """Celery task to scan a network range"""
    try:
        network_range = NetworkRange.objects.get(id=network_range_id)
        discovery_service = NetworkDiscoveryService()
        
        scan_job = discovery_service.scan_network_range(
            network_range=network_range,
            scan_type=scan_type,
            scan_options=scan_options or {}
        )
        
        return {
            'success': True,
            'scan_job_id': scan_job.id,
            'devices_found': scan_job.devices_found,
            'new_devices': scan_job.new_devices,
            'updated_devices': scan_job.updated_devices
        }
        
    except NetworkRange.DoesNotExist:
        logger.error(f"Network range with ID {network_range_id} not found")
        return {'success': False, 'error': 'Network range not found'}
    
    except Exception as e:
        logger.error(f"Error scanning network range {network_range_id}: {str(e)}")
        return {'success': False, 'error': str(e)}


@shared_task
def scan_all_active_ranges_task():
    """Celery task to scan all active network ranges"""
    try:
        discovery_service = NetworkDiscoveryService()
        discovery_service.scan_all_active_ranges()
        
        return {'success': True, 'message': 'All active ranges scanned'}
        
    except Exception as e:
        logger.error(f"Error scanning all active ranges: {str(e)}")
        return {'success': False, 'error': str(e)}


@shared_task
def match_discovered_devices_task():
    """Celery task to match discovered devices with assets"""
    try:
        matching_service = AssetMatchingService()
        matching_service.match_discovered_devices()
        
        return {'success': True, 'message': 'Device matching completed'}
        
    except Exception as e:
        logger.error(f"Error matching discovered devices: {str(e)}")
        return {'success': False, 'error': str(e)}


@shared_task
def cleanup_old_scan_results_task(days_to_keep=30):
    """Celery task to cleanup old scan results"""
    try:
        cutoff_date = timezone.now() - timezone.timedelta(days=days_to_keep)
        
        # Delete old scan jobs and their results
        old_scan_jobs = ScanJob.objects.filter(created_at__lt=cutoff_date)
        deleted_count = old_scan_jobs.count()
        old_scan_jobs.delete()
        
        return {
            'success': True, 
            'message': f'Cleaned up {deleted_count} old scan jobs'
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up old scan results: {str(e)}")
        return {'success': False, 'error': str(e)}


@shared_task
def periodic_network_discovery():
    """Periodic task for network discovery - runs every hour"""
    try:
        # Scan all active ranges
        scan_result = scan_all_active_ranges_task.delay()
        
        # Match discovered devices
        match_result = match_discovered_devices_task.delay()
        
        return {
            'success': True,
            'scan_task_id': scan_result.id,
            'match_task_id': match_result.id
        }
        
    except Exception as e:
        logger.error(f"Error in periodic network discovery: {str(e)}")
        return {'success': False, 'error': str(e)}from celery import shared_task
from django.utils import timezone
from .services import NetworkDiscoveryService, AssetMatchingService
from .models import NetworkRange, ScanJob
import logging

logger = logging.getLogger(__name__)


@shared_task
def scan_network_range_task(network_range_id, scan_type='discovery', scan_options=None):
    """Celery task to scan a network range"""
    try:
        network_range = NetworkRange.objects.get(id=network_range_id)
        discovery_service = NetworkDiscoveryService()
        
        scan_job = discovery_service.scan_network_range(
            network_range=network_range,
            scan_type=scan_type,
            scan_options=scan_options or {}
        )
        
        return {
            'success': True,
            'scan_job_id': scan_job.id,
            'devices_found': scan_job.devices_found,
            'new_devices': scan_job.new_devices,
            'updated_devices': scan_job.updated_devices
        }
        
    except NetworkRange.DoesNotExist:
        logger.error(f"Network range with ID {network_range_id} not found")
        return {'success': False, 'error': 'Network range not found'}
    
    except Exception as e:
        logger.error(f"Error scanning network range {network_range_id}: {str(e)}")
        return {'success': False, 'error': str(e)}


@shared_task
def scan_all_active_ranges_task():
    """Celery task to scan all active network ranges"""
    try:
        discovery_service = NetworkDiscoveryService()
        discovery_service.scan_all_active_ranges()
        
        return {'success': True, 'message': 'All active ranges scanned'}
        
    except Exception as e:
        logger.error(f"Error scanning all active ranges: {str(e)}")
        return {'success': False, 'error': str(e)}


@shared_task
def match_discovered_devices_task():
    """Celery task to match discovered devices with assets"""
    try:
        matching_service = AssetMatchingService()
        matching_service.match_discovered_devices()
        
        return {'success': True, 'message': 'Device matching completed'}
        
    except Exception as e:
        logger.error(f"Error matching discovered devices: {str(e)}")
        return {'success': False, 'error': str(e)}


@shared_task
def cleanup_old_scan_results_task(days_to_keep=30):
    """Celery task to cleanup old scan results"""
    try:
        cutoff_date = timezone.now() - timezone.timedelta(days=days_to_keep)
        
        # Delete old scan jobs and their results
        old_scan_jobs = ScanJob.objects.filter(created_at__lt=cutoff_date)
        deleted_count = old_scan_jobs.count()
        old_scan_jobs.delete()
        
        return {
            'success': True, 
            'message': f'Cleaned up {deleted_count} old scan jobs'
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up old scan results: {str(e)}")
        return {'success': False, 'error': str(e)}


@shared_task
def periodic_network_discovery():
    """Periodic task for network discovery - runs every hour"""
    try:
        # Scan all active ranges
        scan_result = scan_all_active_ranges_task.delay()
        
        # Match discovered devices
        match_result = match_discovered_devices_task.delay()
        
        return {
            'success': True,
            'scan_task_id': scan_result.id,
            'match_task_id': match_result.id
        }
        
    except Exception as e:
        logger.error(f"Error in periodic network discovery: {str(e)}")
        return {'success': False, 'error': str(e)}