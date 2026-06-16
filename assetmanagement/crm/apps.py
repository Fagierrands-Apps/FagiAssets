"""
CRM App Configuration
"""
from django.apps import AppConfig


class CrmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crm'
    verbose_name = 'Customer Relationship Management'

    def ready(self):
        """Import signal handlers when the app is ready"""
        import crm.signals  # noqa