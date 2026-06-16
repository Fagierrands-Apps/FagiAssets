from django.contrib import admin
from django.utils.html import format_html
from .models import (
    NetworkRange, DiscoveryRule, DiscoveredDevice, ScanJob, 
    ScanResult, AssetDiscoveryLog
)


@admin.register(NetworkRange)
class NetworkRangeAdmin(admin.ModelAdmin):
    list_display = ['name', 'network', 'is_active', 'scan_frequency', 'last_scan', 'created_at']
    search_fields = ['name', 'network']
    list_filter = ['is_active', 'created_at']
    readonly_fields = ['last_scan']


@admin.register(DiscoveryRule)
class DiscoveryRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'priority', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['is_active', 'priority', 'created_at']


@admin.register(DiscoveredDevice)
class DiscoveredDeviceAdmin(admin.ModelAdmin):
    list_display = [
        'ip_address', 'hostname', 'mac_address', 'status', 
        'network_range', 'matched_asset', 'confidence_score', 
        'first_seen', 'last_seen', 'scan_count'
    ]
    search_fields = ['ip_address', 'hostname', 'mac_address']
    list_filter = ['status', 'network_range', 'first_seen', 'last_seen']
    raw_id_fields = ['network_range', 'matched_asset']
    readonly_fields = ['first_seen', 'last_seen', 'scan_count']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'network_range', 'matched_asset'
        )


class ScanResultInline(admin.TabularInline):
    model = ScanResult
    extra = 0
    readonly_fields = ['scan_timestamp']


@admin.register(ScanJob)
class ScanJobAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'scan_type', 'status', 'devices_found', 
        'new_devices', 'created_by', 'started_at', 'completed_at'
    ]
    search_fields = ['name']
    list_filter = ['scan_type', 'status', 'created_at']
    raw_id_fields = ['created_by']
    readonly_fields = ['started_at', 'completed_at', 'devices_found', 'new_devices', 'updated_devices']
    filter_horizontal = ['network_ranges']
    
    inlines = [ScanResultInline]


@admin.register(ScanResult)
class ScanResultAdmin(admin.ModelAdmin):
    list_display = [
        'discovered_device', 'scan_job', 'is_alive', 
        'scan_successful', 'response_time', 'scan_timestamp'
    ]
    search_fields = ['discovered_device__ip_address', 'discovered_device__hostname']
    list_filter = ['is_alive', 'scan_successful', 'scan_timestamp']
    raw_id_fields = ['scan_job', 'discovered_device']
    readonly_fields = ['scan_timestamp']


@admin.register(AssetDiscoveryLog)
class AssetDiscoveryLogAdmin(admin.ModelAdmin):
    list_display = ['level', 'message_short', 'scan_job', 'discovered_device', 'timestamp']
    search_fields = ['message']
    list_filter = ['level', 'timestamp']
    raw_id_fields = ['scan_job', 'discovered_device']
    readonly_fields = ['timestamp']

    def message_short(self, obj):
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    message_short.short_description = 'Message'
