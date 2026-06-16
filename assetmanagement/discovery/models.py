from django.db import models
from django.contrib.auth.models import User
from django.core.validators import validate_ipv4_address
import json


class NetworkRange(models.Model):
    """Network ranges to scan for assets"""
    name = models.CharField(max_length=100)
    network = models.CharField(max_length=18, help_text="CIDR notation (e.g., 192.168.1.0/24)")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    scan_frequency = models.IntegerField(default=3600, help_text="Scan frequency in seconds")
    last_scan = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.network})"

    class Meta:
        ordering = ['name']


class DiscoveryRule(models.Model):
    """Rules for automatic asset discovery and classification"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0, help_text="Higher numbers have higher priority")
    
    # Conditions (JSON format)
    conditions = models.JSONField(default=dict, help_text="JSON conditions for matching")
    
    # Actions (JSON format)
    actions = models.JSONField(default=dict, help_text="JSON actions to perform when matched")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-priority', 'name']


class DiscoveredDevice(models.Model):
    """Devices discovered during network scans"""
    STATUS_CHOICES = [
        ('new', 'New'),
        ('matched', 'Matched to Asset'),
        ('ignored', 'Ignored'),
        ('pending', 'Pending Review'),
    ]

    ip_address = models.GenericIPAddressField(validators=[validate_ipv4_address])
    mac_address = models.CharField(max_length=17, blank=True, help_text="Format: XX:XX:XX:XX:XX:XX")
    hostname = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    
    # Network information
    network_range = models.ForeignKey(NetworkRange, on_delete=models.CASCADE, related_name='discovered_devices')
    ports_open = models.JSONField(default=list, blank=True)
    services = models.JSONField(default=dict, blank=True)
    
    # Device information
    os_info = models.JSONField(default=dict, blank=True)
    hardware_info = models.JSONField(default=dict, blank=True)
    software_info = models.JSONField(default=dict, blank=True)
    
    # Discovery metadata
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    scan_count = models.IntegerField(default=1)
    
    # Asset matching
    matched_asset = models.ForeignKey('assets.Asset', on_delete=models.SET_NULL, null=True, blank=True)
    confidence_score = models.FloatField(default=0.0, help_text="Confidence in asset matching (0-1)")
    
    # Additional data
    raw_data = models.JSONField(default=dict, blank=True, help_text="Raw scan data")
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.ip_address} ({self.hostname or 'Unknown'})"

    class Meta:
        ordering = ['-last_seen']
        unique_together = ['ip_address', 'network_range']


class ScanJob(models.Model):
    """Track network scan jobs"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    SCAN_TYPES = [
        ('discovery', 'Network Discovery'),
        ('port_scan', 'Port Scan'),
        ('service_scan', 'Service Detection'),
        ('os_detection', 'OS Detection'),
        ('full_scan', 'Full Scan'),
    ]

    name = models.CharField(max_length=200)
    scan_type = models.CharField(max_length=20, choices=SCAN_TYPES, default='discovery')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    network_ranges = models.ManyToManyField(NetworkRange)
    
    # Scan parameters
    scan_options = models.JSONField(default=dict, blank=True)
    
    # Execution details
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Results
    devices_found = models.IntegerField(default=0)
    new_devices = models.IntegerField(default=0)
    updated_devices = models.IntegerField(default=0)
    errors = models.JSONField(default=list, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.status}"

    class Meta:
        ordering = ['-created_at']


class ScanResult(models.Model):
    """Individual scan results for devices"""
    scan_job = models.ForeignKey(ScanJob, on_delete=models.CASCADE, related_name='results')
    discovered_device = models.ForeignKey(DiscoveredDevice, on_delete=models.CASCADE, related_name='scan_results')
    
    # Scan details
    scan_timestamp = models.DateTimeField(auto_now_add=True)
    response_time = models.FloatField(null=True, blank=True, help_text="Response time in milliseconds")
    
    # Results data
    ports_scanned = models.JSONField(default=list, blank=True)
    ports_open = models.JSONField(default=list, blank=True)
    services_detected = models.JSONField(default=dict, blank=True)
    os_fingerprint = models.JSONField(default=dict, blank=True)
    
    # Status
    is_alive = models.BooleanField(default=True)
    scan_successful = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)

    def __str__(self):
        return f"{self.discovered_device.ip_address} - {self.scan_timestamp}"

    class Meta:
        ordering = ['-scan_timestamp']


class AssetDiscoveryLog(models.Model):
    """Log of asset discovery activities"""
    LOG_LEVELS = [
        ('debug', 'Debug'),
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]

    level = models.CharField(max_length=10, choices=LOG_LEVELS, default='info')
    message = models.TextField()
    details = models.JSONField(default=dict, blank=True)
    
    # Related objects
    scan_job = models.ForeignKey(ScanJob, on_delete=models.CASCADE, null=True, blank=True, related_name='logs')
    discovered_device = models.ForeignKey(DiscoveredDevice, on_delete=models.CASCADE, null=True, blank=True, related_name='logs')
    
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.level.upper()}: {self.message[:100]}"

    class Meta:
        ordering = ['-timestamp']
