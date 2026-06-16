from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Location, Department, Manufacturer, AssetCategory, AssetModel,
    Asset, AssetHistory, MaintenanceRecord, NetworkInterface, SoftwareInstallation
)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'created_at']
    search_fields = ['name', 'address']
    list_filter = ['created_at']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'manager', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']
    raw_id_fields = ['manager']


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ['name', 'website', 'support_email', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']


@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'created_at']
    search_fields = ['name']
    list_filter = ['parent', 'created_at']


@admin.register(AssetModel)
class AssetModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'category', 'model_number', 'created_at']
    search_fields = ['name', 'manufacturer__name', 'model_number']
    list_filter = ['manufacturer', 'category', 'created_at']
    raw_id_fields = ['manufacturer', 'category']


class NetworkInterfaceInline(admin.TabularInline):
    model = NetworkInterface
    extra = 0


class SoftwareInstallationInline(admin.TabularInline):
    model = SoftwareInstallation
    extra = 0


class AssetHistoryInline(admin.TabularInline):
    model = AssetHistory
    extra = 0
    readonly_fields = ['timestamp']


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = [
        'asset_tag', 'name', 'model', 'category', 'status', 'assigned_to', 
        'location', 'ip_address', 'last_seen', 'created_at'
    ]
    search_fields = [
        'asset_tag', 'name', 'serial_number', 'hostname', 
        'ip_address', 'mac_address', 'device_name', 'device_id'
    ]
    list_filter = [
        'status', 'model__manufacturer', 'category', 
        'department', 'location', 'created_at'
    ]
    raw_id_fields = ['model', 'category', 'assigned_to', 'department', 'location']
    readonly_fields = ['created_at', 'updated_at', 'last_seen']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('asset_tag', 'name', 'model', 'category', 'serial_number', 'status', 'image')
        }),
        ('Assignment', {
            'fields': ('assigned_to', 'department', 'location')
        }),
        ('Financial', {
            'fields': ('purchase_date', 'purchase_cost', 'warranty_expires')
        }),
        ('Technical', {
            'fields': ('ip_address', 'mac_address', 'hostname')
        }),
        ('Device Specifications', {
            'fields': ('device_name', 'processor', 'installed_ram', 'device_id', 'product_id', 'system_type'),
            'classes': ('collapse',)
        }),
        ('Additional', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_seen'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [NetworkInterfaceInline, SoftwareInstallationInline, AssetHistoryInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'model', 'model__manufacturer', 'assigned_to', 'department', 'location'
        )


@admin.register(AssetHistory)
class AssetHistoryAdmin(admin.ModelAdmin):
    list_display = ['asset', 'action', 'user', 'timestamp']
    search_fields = ['asset__asset_tag', 'asset__name', 'description']
    list_filter = ['action', 'timestamp']
    raw_id_fields = ['asset', 'user']
    readonly_fields = ['timestamp']


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = [
        'asset', 'title', 'maintenance_type', 'status', 
        'scheduled_date', 'performed_by', 'cost'
    ]
    search_fields = ['asset__asset_tag', 'title', 'description']
    list_filter = ['maintenance_type', 'status', 'scheduled_date']
    raw_id_fields = ['asset', 'performed_by']
    date_hierarchy = 'scheduled_date'


@admin.register(NetworkInterface)
class NetworkInterfaceAdmin(admin.ModelAdmin):
    list_display = [
        'asset', 'interface_name', 'mac_address', 'ip_address', 
        'is_primary', 'is_active', 'speed'
    ]
    search_fields = ['asset__asset_tag', 'interface_name', 'mac_address', 'ip_address']
    list_filter = ['is_primary', 'is_active', 'speed']
    raw_id_fields = ['asset']


@admin.register(SoftwareInstallation)
class SoftwareInstallationAdmin(admin.ModelAdmin):
    list_display = [
        'asset', 'name', 'version', 'publisher', 
        'install_date', 'is_licensed'
    ]
    search_fields = ['asset__asset_tag', 'name', 'version', 'publisher']
    list_filter = ['is_licensed', 'install_date', 'publisher']
    raw_id_fields = ['asset']
