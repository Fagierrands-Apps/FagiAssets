from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import CRMCustomer, AssetCustomerAssignment, SyncLog, IntegrationSettings


@admin.register(CRMCustomer)
class CRMCustomerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'company_name', 'email', 'phone', 'assigned_employee', 'sync_status', 'last_synced']
    list_filter = ['sync_status', 'customer_type', 'status', 'assigned_employee']
    search_fields = ['first_name', 'last_name', 'company_name', 'email', 'phone']
    readonly_fields = ['crm_customer_id', 'last_synced', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('crm_customer_id', 'first_name', 'last_name', 'company_name', 'customer_type')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country')
        }),
        ('Assignment', {
            'fields': ('assigned_employee', 'status')
        }),
        ('Sync Information', {
            'fields': ('sync_status', 'sync_error', 'last_synced'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('assigned_employee')


@admin.register(AssetCustomerAssignment)
class AssetCustomerAssignmentAdmin(admin.ModelAdmin):
    list_display = ['asset_link', 'customer_link', 'assignment_type', 'is_active', 'assigned_date', 'assigned_by']
    list_filter = ['assignment_type', 'is_active', 'assigned_date']
    search_fields = ['asset__asset_tag', 'asset__name', 'customer__first_name', 'customer__last_name', 'customer__company_name']
    readonly_fields = ['assigned_date', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Assignment Details', {
            'fields': ('asset', 'customer', 'assignment_type', 'is_active', 'assigned_by')
        }),
        ('Contract Information', {
            'fields': ('contract_number', 'start_date', 'end_date'),
            'classes': ('collapse',)
        }),
        ('Financial Information', {
            'fields': ('monthly_fee', 'total_value'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('assigned_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def asset_link(self, obj):
        if obj.asset:
            url = reverse('admin:assets_asset_change', args=[obj.asset.pk])
            return format_html('<a href="{}">{}</a>', url, obj.asset.asset_tag)
        return '-'
    asset_link.short_description = 'Asset'
    
    def customer_link(self, obj):
        if obj.customer:
            url = reverse('admin:crm_integration_crmcustomer_change', args=[obj.customer.pk])
            return format_html('<a href="{}">{}</a>', url, obj.customer.full_name)
        return '-'
    customer_link.short_description = 'Customer'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('asset', 'customer', 'assigned_by')


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ['sync_type', 'sync_action', 'status', 'records_processed', 'records_success', 'records_error', 'started_at', 'duration_seconds']
    list_filter = ['sync_type', 'sync_action', 'status', 'started_at']
    search_fields = ['sync_id', 'error_message']
    readonly_fields = ['sync_id', 'started_at', 'completed_at', 'duration_seconds']
    
    fieldsets = (
        ('Sync Information', {
            'fields': ('sync_type', 'sync_action', 'status', 'sync_id', 'initiated_by')
        }),
        ('Results', {
            'fields': ('records_processed', 'records_success', 'records_error')
        }),
        ('Error Details', {
            'fields': ('error_message', 'error_details'),
            'classes': ('collapse',)
        }),
        ('Timing', {
            'fields': ('started_at', 'completed_at', 'duration_seconds'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False  # Sync logs are created automatically
    
    def has_change_permission(self, request, obj=None):
        return False  # Sync logs should not be modified
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('initiated_by')


@admin.register(IntegrationSettings)
class IntegrationSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('CRM Connection', {
            'fields': ('crm_base_url', 'crm_api_key')
        }),
        ('Synchronization Settings', {
            'fields': ('auto_sync_enabled', 'sync_interval_minutes')
        }),
        ('Sync Direction', {
            'fields': ('sync_customers_to_assets', 'sync_assets_to_crm', 'sync_employees')
        }),
        ('Notifications', {
            'fields': ('notify_on_sync_error', 'notification_email')
        }),
        ('Advanced Settings', {
            'fields': ('customer_assignment_field_mapping',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def has_add_permission(self, request):
        # Only allow one settings instance
        return not IntegrationSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False  # Don't allow deletion of settings