"""
Signal handlers for CRM app
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Employee, MonitoringSettings


@receiver(post_save, sender=Employee)
def create_monitoring_settings(sender, instance, created, **kwargs):
    """
    Automatically create monitoring settings when a new employee is created
    """
    if created:
        MonitoringSettings.objects.get_or_create(
            employee=instance,
            defaults={
                'idle_threshold': 300,  # 5 minutes in seconds
                'extended_idle_threshold': 900,  # 15 minutes in seconds
                'heartbeat_interval': 60,  # 60 seconds
                'enable_monitoring': True,
                'enable_idle_alerts': True,
                'enable_screenshots': False,
            }
        )