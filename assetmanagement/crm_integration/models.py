from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import uuid


class CRMCustomer(models.Model):
    """Mirror of CRM Customer data for integration"""
    # CRM Customer ID for reference
    crm_customer_id = models.IntegerField(unique=True, help_text="ID from CRM system")
    
    # Basic Information (synced from CRM)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=17)
    
    # Address Information
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='USA')
    
    # Business Information
    status = models.CharField(max_length=20, default='active')
    customer_type = models.CharField(max_length=20, default='individual')
    
    # Asset Management specific fields
    assigned_employee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='crm_customers')
    
    # Sync metadata
    last_synced = models.DateTimeField(auto_now=True)
    sync_status = models.CharField(max_length=20, choices=[
        ('synced', 'Synced'),
        ('pending', 'Pending Sync'),
        ('error', 'Sync Error'),
    ], default='synced')
    sync_error = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['crm_customer_id']),
            models.Index(fields=['email']),
            models.Index(fields=['assigned_employee']),
        ]
    
    def __str__(self):
        if self.company_name:
            return f"{self.company_name} ({self.first_name} {self.last_name})"
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class AssetCustomerAssignment(models.Model):
    """Link assets to CRM customers for ownership tracking"""
    asset = models.ForeignKey('assets.Asset', on_delete=models.CASCADE, related_name='customer_assignments')
    customer = models.ForeignKey(CRMCustomer, on_delete=models.CASCADE, related_name='asset_assignments')
    
    # Assignment details
    assigned_date = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    
    # Assignment type
    ASSIGNMENT_TYPES = [
        ('owned', 'Owned by Customer'),
        ('leased', 'Leased to Customer'),
        ('serviced', 'Under Service Contract'),
        ('temporary', 'Temporary Assignment'),
    ]
    assignment_type = models.CharField(max_length=20, choices=ASSIGNMENT_TYPES, default='owned')
    
    # Contract details
    contract_number = models.CharField(max_length=100, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    
    # Financial information
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-assigned_date']
        indexes = [
            models.Index(fields=['asset', 'is_active']),
            models.Index(fields=['customer', 'is_active']),
            models.Index(fields=['assignment_type']),
        ]
    
    def __str__(self):
        return f"{self.asset.asset_tag} → {self.customer.full_name} ({self.assignment_type})"


class SyncLog(models.Model):
    """Log synchronization activities between Asset Manager and CRM"""
    SYNC_TYPES = [
        ('customer_to_asset', 'Customer → Asset Manager'),
        ('asset_to_crm', 'Asset Manager → CRM'),
        ('employee_sync', 'Employee Synchronization'),
        ('assignment_sync', 'Assignment Synchronization'),
    ]
    
    SYNC_ACTIONS = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('sync', 'Full Sync'),
    ]
    
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('error', 'Error'),
        ('partial', 'Partial Success'),
        ('pending', 'Pending'),
    ]
    
    # Sync details
    sync_type = models.CharField(max_length=30, choices=SYNC_TYPES)
    sync_action = models.CharField(max_length=20, choices=SYNC_ACTIONS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    # Related object tracking
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Sync metadata
    records_processed = models.IntegerField(default=0)
    records_success = models.IntegerField(default=0)
    records_error = models.IntegerField(default=0)
    
    # Error details
    error_message = models.TextField(blank=True, null=True)
    error_details = models.JSONField(default=dict, blank=True)
    
    # Request details
    initiated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    sync_id = models.UUIDField(default=uuid.uuid4, unique=True)
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.FloatField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['sync_type', 'status']),
            models.Index(fields=['started_at']),
            models.Index(fields=['sync_id']),
        ]
    
    def __str__(self):
        return f"{self.sync_type} - {self.sync_action} ({self.status})"


class IntegrationSettings(models.Model):
    """Configuration settings for CRM integration"""
    # CRM Connection Settings
    crm_base_url = models.URLField(default='http://localhost:8001', help_text="Base URL of CRM system")
    crm_api_key = models.CharField(max_length=255, blank=True, help_text="API key for CRM authentication")
    
    # Sync Settings
    auto_sync_enabled = models.BooleanField(default=True, help_text="Enable automatic synchronization")
    sync_interval_minutes = models.IntegerField(default=30, help_text="Sync interval in minutes")
    
    # Sync Direction Settings
    sync_customers_to_assets = models.BooleanField(default=True, help_text="Sync CRM customers to Asset Manager")
    sync_assets_to_crm = models.BooleanField(default=True, help_text="Sync Asset assignments to CRM")
    sync_employees = models.BooleanField(default=True, help_text="Sync employee data between systems")
    
    # Field Mapping Settings
    customer_assignment_field_mapping = models.JSONField(default=dict, blank=True, help_text="Field mapping configuration")
    
    # Notification Settings
    notify_on_sync_error = models.BooleanField(default=True)
    notification_email = models.EmailField(blank=True, help_text="Email for sync notifications")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Integration Settings"
        verbose_name_plural = "Integration Settings"
    
    def __str__(self):
        return f"CRM Integration Settings (Updated: {self.updated_at.strftime('%Y-%m-%d %H:%M')})"
    
    def save(self, *args, **kwargs):
        # Ensure only one settings instance exists
        if not self.pk and IntegrationSettings.objects.exists():
            raise ValueError("Only one IntegrationSettings instance is allowed")
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create the integration settings instance"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings