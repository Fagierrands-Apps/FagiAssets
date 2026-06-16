from django.db import models
from django.contrib.auth.models import User
from django.core.validators import validate_ipv4_address
from django.apps import apps
import uuid
import random
import string


def generate_serial_number():
    """Generate a serial number with format FAGI + 7 random characters"""
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
    return f"FAGI{random_chars}"


def generate_asset_tag_for_category(category_name):
    """Generate an asset tag based on category with format CAT-001"""
    from django.db import transaction
    
    # Create category prefix (first 3 letters, uppercase)
    prefix = category_name[:3].upper()
    
    with transaction.atomic():
        # Import here to avoid circular imports during module loading
        Asset = apps.get_model('assets', 'Asset')
        
        # Find the highest existing number for this category prefix
        existing_tags = Asset.objects.filter(
            asset_tag__startswith=f"{prefix}-"
        ).values_list('asset_tag', flat=True)
        
        # Extract numbers from existing tags
        numbers = []
        for tag in existing_tags:
            try:
                # Extract number part after the prefix and dash
                number_part = tag.split('-', 1)[1]
                if number_part.isdigit():
                    numbers.append(int(number_part))
            except (IndexError, ValueError):
                continue
        
        # Get next number
        next_number = max(numbers) + 1 if numbers else 1
        
        # Format with leading zeros (3 digits)
        return f"{prefix}-{next_number:03d}"


class Location(models.Model):
    """Physical locations where assets can be placed"""
    name = models.CharField(max_length=100, unique=True)
    address = models.TextField(blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Department(models.Model):
    """Departments that can own assets"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Manufacturer(models.Model):
    """Asset manufacturers"""
    name = models.CharField(max_length=100, unique=True)
    website = models.URLField(blank=True)
    support_email = models.EmailField(blank=True)
    support_phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class AssetCategory(models.Model):
    """Categories for organizing assets"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Asset Categories"


class AssetModel(models.Model):
    """Asset models from manufacturers"""
    name = models.CharField(max_length=100)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
    category = models.ForeignKey(AssetCategory, on_delete=models.CASCADE)
    model_number = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='asset_models/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.manufacturer.name} {self.name}"

    class Meta:
        ordering = ['manufacturer__name', 'name']
        unique_together = ['manufacturer', 'name']


class Asset(models.Model):
    """Main asset model"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Under Maintenance'),
        ('retired', 'Retired'),
        ('lost', 'Lost'),
        ('stolen', 'Stolen'),
    ]

    # Basic Information
    asset_tag = models.CharField(max_length=50, unique=True, blank=True)
    name = models.CharField(max_length=200)
    model = models.ForeignKey(AssetModel, on_delete=models.CASCADE)
    category = models.ForeignKey(AssetCategory, on_delete=models.SET_NULL, null=True, blank=True)
    serial_number = models.CharField(max_length=100, blank=True, default=generate_serial_number)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Ownership and Location
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_assets')  # legacy single assignment
    assigned_users = models.ManyToManyField(User, blank=True, related_name='assets')  # new: multiple users
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Financial Information
    purchase_date = models.DateField(null=True, blank=True)
    purchase_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    warranty_expires = models.DateField(null=True, blank=True)
    
    # Technical Information
    ip_address = models.GenericIPAddressField(null=True, blank=True, validators=[validate_ipv4_address])
    mac_address = models.CharField(max_length=17, blank=True, help_text="Format: XX:XX:XX:XX:XX:XX")
    hostname = models.CharField(max_length=100, blank=True)
    
    # Device Specifications
    device_name = models.CharField(max_length=100, blank=True, help_text="Device name (e.g., DESKTOP-2ANTBJU)")
    processor = models.CharField(max_length=200, blank=True, help_text="Processor information")
    installed_ram = models.CharField(max_length=50, blank=True, help_text="RAM information (e.g., 16.0 GB)")
    device_id = models.CharField(max_length=100, blank=True, help_text="Device ID")
    product_id = models.CharField(max_length=100, blank=True, help_text="Product ID")
    system_type = models.CharField(max_length=100, blank=True, help_text="System type (e.g., 64-bit operating system)")
    
    # Additional Information
    notes = models.TextField(blank=True)
    image = models.ImageField(upload_to='assets/', blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_seen = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Generate unique serial number if not provided
        if not self.serial_number:
            self.serial_number = self.generate_unique_serial_number()
        
        # Generate unique asset tag if not provided
        if not self.asset_tag:
            self.asset_tag = self.generate_unique_asset_tag()
        
        super().save(*args, **kwargs)
    
    def generate_unique_serial_number(self):
        """Generate a unique serial number"""
        while True:
            serial = generate_serial_number()
            if not Asset.objects.filter(serial_number=serial).exists():
                return serial
    
    def generate_unique_asset_tag(self):
        """Generate a unique asset tag based on category"""
        category_name = self.category.name if self.category else self.model.category.name
        while True:
            asset_tag = generate_asset_tag_for_category(category_name)
            if not Asset.objects.filter(asset_tag=asset_tag).exists():
                return asset_tag

    def __str__(self):
        return f"{self.asset_tag} - {self.name}"

    class Meta:
        ordering = ['asset_tag']


class AssetHistory(models.Model):
    """Track changes to assets"""
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('assigned', 'Assigned'),
        ('unassigned', 'Unassigned'),
        ('moved', 'Moved'),
        ('status_changed', 'Status Changed'),
        ('maintenance', 'Maintenance'),
    ]

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Store previous values for comparison
    previous_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.asset.asset_tag} - {self.action} at {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = "Asset Histories"


class MaintenanceRecord(models.Model):
    """Track maintenance activities"""
    MAINTENANCE_TYPES = [
        ('preventive', 'Preventive'),
        ('corrective', 'Corrective'),
        ('emergency', 'Emergency'),
        ('upgrade', 'Upgrade'),
    ]

    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='maintenance_records')
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    title = models.CharField(max_length=200)
    description = models.TextField()
    scheduled_date = models.DateTimeField()
    completed_date = models.DateTimeField(null=True, blank=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.asset.asset_tag} - {self.title}"

    class Meta:
        ordering = ['-scheduled_date']


class NetworkInterface(models.Model):
    """Network interfaces for assets"""
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='network_interfaces')
    interface_name = models.CharField(max_length=50)  # e.g., eth0, wlan0
    mac_address = models.CharField(max_length=17, help_text="Format: XX:XX:XX:XX:XX:XX")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    subnet_mask = models.GenericIPAddressField(null=True, blank=True)
    gateway = models.GenericIPAddressField(null=True, blank=True)
    dns_servers = models.TextField(blank=True, help_text="Comma-separated DNS servers")
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    speed = models.CharField(max_length=20, blank=True)  # e.g., "1000 Mbps"
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.asset.asset_tag} - {self.interface_name}"

    class Meta:
        ordering = ['asset', 'interface_name']
        unique_together = ['asset', 'interface_name']


class SoftwareInstallation(models.Model):
    """Software installed on assets"""
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='software_installations')
    name = models.CharField(max_length=200)
    version = models.CharField(max_length=100, blank=True)
    publisher = models.CharField(max_length=200, blank=True)
    install_date = models.DateTimeField(null=True, blank=True)
    license_key = models.CharField(max_length=200, blank=True)
    is_licensed = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.asset.asset_tag} - {self.name} {self.version}"

    class Meta:
        ordering = ['asset', 'name']
        unique_together = ['asset', 'name', 'version']
