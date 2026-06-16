from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils import timezone
from .models import (
    Department, Employee, Customer, CustomerNote, 
    AssetCustomerAssignment, Lead, Notification,
    TimeEntry, WorkSession, EmployeeKPI, Task, Communication, MissedCall,
    MonitoringSettings, ActivityLog, IdlePeriod, ActivitySession, MoneyRequest,
    HandlerReport
)


class EmployeeInline(admin.StackedInline):
    model = Employee
    can_delete = False
    verbose_name_plural = 'Employee Profile'
    fields = (
        'employee_id', 'department', 'manager', 'position',
        'phone', 'employment_status', 'employment_type', 'role',
        'hire_date', 'salary', 'weekly_target', 'is_manager'
    )


class UserAdmin(BaseUserAdmin):
    inlines = (EmployeeInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_employee_id')
    list_filter = BaseUserAdmin.list_filter + ('employee_profile__department',)
    
    def get_employee_id(self, obj):
        try:
            return obj.employee_profile.employee_id
        except Employee.DoesNotExist:
            return '-'
    get_employee_id.short_description = 'Employee ID'


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'manager', 'employee_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    
    def employee_count(self, obj):
        return obj.employees.count()
    employee_count.short_description = 'Employees'


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'employee_id', 'department', 'position', 'role', 'weekly_target', 'employment_status', 'hire_date')
    list_filter = ('employment_status', 'employment_type', 'department', 'role', 'is_manager')
    search_fields = ('user__first_name', 'user__last_name', 'employee_id', 'position')
    raw_id_fields = ('user', 'manager')
    date_hierarchy = 'hire_date'

    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Employee Details', {
            'fields': ('employee_id', 'department', 'manager', 'position', 'phone')
        }),
        ('Employment Information', {
            'fields': ('employment_status', 'employment_type', 'role', 'hire_date', 'termination_date', 'salary', 'is_manager')
        }),
        ('Performance Targets', {
            'fields': ('weekly_target',),
            'description': 'Set the weekly call target for this employee'
        }),
    )


class CustomerNoteInline(admin.TabularInline):
    model = CustomerNote
    extra = 1
    fields = ('note', 'is_important', 'created_by')
    readonly_fields = ('created_by',)


class AssetCustomerAssignmentInline(admin.TabularInline):
    model = AssetCustomerAssignment
    extra = 0
    fields = ('asset', 'assignment_type', 'is_active', 'assigned_date', 'monthly_fee')
    readonly_fields = ('assigned_date',)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'company_name', 'email', 'phone', 'status', 'assigned_employee', 'created_at')
    list_filter = ('status', 'customer_type', 'assigned_employee__department', 'created_at')
    search_fields = ('first_name', 'last_name', 'company_name', 'email', 'phone')
    raw_id_fields = ('assigned_employee',)
    date_hierarchy = 'created_at'
    inlines = [CustomerNoteInline, AssetCustomerAssignmentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('first_name', 'last_name', 'company_name', 'customer_type', 'status')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'alternate_phone', 'preferred_contact_method')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country')
        }),
        ('Business Information', {
            'fields': ('assigned_employee', 'total_spent', 'lifetime_value')
        }),
    )


@admin.register(CustomerNote)
class CustomerNoteAdmin(admin.ModelAdmin):
    list_display = ('customer', 'note_preview', 'is_important', 'created_by', 'created_at')
    list_filter = ('is_important', 'created_at', 'customer__assigned_employee')
    search_fields = ('customer__first_name', 'customer__last_name', 'note')
    raw_id_fields = ('customer', 'created_by')
    date_hierarchy = 'created_at'
    
    def note_preview(self, obj):
        return obj.note[:50] + '...' if len(obj.note) > 50 else obj.note
    note_preview.short_description = 'Note'


@admin.register(AssetCustomerAssignment)
class AssetCustomerAssignmentAdmin(admin.ModelAdmin):
    list_display = ('asset', 'customer', 'assignment_type', 'is_active', 'assigned_date', 'monthly_fee', 'assigned_by')
    list_filter = ('assignment_type', 'is_active', 'assigned_date', 'asset__status')
    search_fields = ('asset__asset_tag', 'asset__name', 'customer__first_name', 'customer__last_name')
    raw_id_fields = ('asset', 'customer', 'assigned_by')
    date_hierarchy = 'assigned_date'
    
    fieldsets = (
        ('Assignment Details', {
            'fields': ('asset', 'customer', 'assignment_type', 'is_active')
        }),
        ('Dates', {
            'fields': ('assigned_date', 'start_date', 'end_date')
        }),
        ('Contract Information', {
            'fields': ('contract_number', 'monthly_fee', 'total_value')
        }),
        ('Additional Information', {
            'fields': ('assigned_by', 'notes')
        }),
    )


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'company_name', 'email', 'status', 'source', 'assigned_employee', 'estimated_value', 'created_at')
    list_filter = ('status', 'source', 'assigned_employee__department', 'created_at')
    search_fields = ('first_name', 'last_name', 'company_name', 'email')
    raw_id_fields = ('assigned_employee',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('first_name', 'last_name', 'company_name', 'title')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone')
        }),
        ('Lead Information', {
            'fields': ('status', 'source', 'assigned_employee', 'estimated_value', 'expected_close_date')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )
    
    actions = ['convert_to_customer']
    
    def convert_to_customer(self, request, queryset):
        converted = 0
        for lead in queryset:
            if lead.status != 'won':
                lead.convert_to_customer()
                converted += 1
        
        self.message_user(request, f'Successfully converted {converted} leads to customers.')
    convert_to_customer.short_description = 'Convert selected leads to customers'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'notification_type', 'is_read', 'is_dismissed', 'created_at')
    list_filter = ('notification_type', 'is_read', 'is_dismissed', 'created_at')
    search_fields = ('title', 'message', 'user__username')
    raw_id_fields = ('user', 'customer', 'lead', 'asset')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Notification Details', {
            'fields': ('user', 'notification_type', 'title', 'message')
        }),
        ('Status', {
            'fields': ('is_read', 'is_dismissed')
        }),
        ('Related Objects', {
            'fields': ('customer', 'lead', 'asset'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ('employee', 'entry_type', 'timestamp', 'location', 'ip_address')
    list_filter = ('entry_type', 'timestamp', 'employee__department')
    search_fields = ('employee__user__first_name', 'employee__user__last_name', 'employee__employee_id')
    raw_id_fields = ('employee',)
    date_hierarchy = 'timestamp'
    readonly_fields = ('ip_address', 'user_agent', 'created_at')
    
    fieldsets = (
        ('Time Entry Details', {
            'fields': ('employee', 'entry_type', 'timestamp', 'location', 'notes')
        }),
        ('System Information', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )


@admin.register(WorkSession)
class WorkSessionAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'punch_in', 'punch_out', 'worked_hours', 'productive_hours', 'idle_hours', 'is_complete')
    list_filter = ('date', 'is_complete', 'employee__department')
    search_fields = ('employee__user__first_name', 'employee__user__last_name', 'employee__employee_id')
    raw_id_fields = ('employee',)
    date_hierarchy = 'date'
    readonly_fields = ('total_hours', 'worked_hours', 'productive_hours', 'idle_hours', 'is_complete', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Session Details', {
            'fields': ('employee', 'date', 'punch_in', 'punch_out')
        }),
        ('Calculated Hours', {
            'fields': ('total_hours', 'break_hours', 'worked_hours', 'is_complete'),
        }),
        ('Activity Tracking', {
            'fields': ('productive_hours', 'idle_hours'),
            'description': 'Productive hours = time with activity, Idle hours = time without activity'
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Override save to recalculate hours when punch_out is updated"""
        super().save_model(request, obj, form, change)
        # Recalculate hours after saving
        obj.calculate_hours()


@admin.register(EmployeeKPI)
class EmployeeKPIAdmin(admin.ModelAdmin):
    list_display = ('employee', 'kpi_type', 'value', 'target_value', 'achievement_percentage', 'period_start', 'period_end', 'auto_calculated')
    list_filter = ('kpi_type', 'period_start', 'employee__department')
    search_fields = ('employee__user__first_name', 'employee__user__last_name', 'employee__employee_id')
    raw_id_fields = ('employee',)
    date_hierarchy = 'period_start'
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('KPI Details', {
            'fields': ('employee', 'kpi_type', 'value', 'target_value'),
            'description': 'KPIs are automatically calculated. Manual edits will be overwritten on next calculation.'
        }),
        ('Time Period', {
            'fields': ('period_start', 'period_end')
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )
    
    def achievement_percentage(self, obj):
        return f"{obj.achievement_percentage:.1f}%" if obj.achievement_percentage else "N/A"
    achievement_percentage.short_description = 'Achievement %'
    
    def auto_calculated(self, obj):
        return "Auto-calculated" if "Auto-calculated" in obj.notes else "Manual"
    auto_calculated.short_description = 'Source'
    
    def has_add_permission(self, request):
        # Discourage manual addition - KPIs should be auto-calculated
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        # Allow deletion only for superusers
        return request.user.is_superuser


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'assigned_to', 'priority', 'status', 'due_date', 'assigned_by', 'created_at')
    list_filter = ('priority', 'status', 'assigned_to__department', 'due_date', 'created_at')
    search_fields = ('title', 'description', 'assigned_to__user__first_name', 'assigned_to__user__last_name')
    raw_id_fields = ('assigned_to', 'assigned_by', 'customer', 'lead', 'asset')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Task Details', {
            'fields': ('title', 'description', 'assigned_to', 'assigned_by')
        }),
        ('Task Properties', {
            'fields': ('priority', 'status', 'due_date', 'estimated_hours', 'actual_hours')
        }),
        ('Related Objects', {
            'fields': ('customer', 'lead', 'asset'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('completed_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_completed']
    
    def mark_completed(self, request, queryset):
        updated = 0
        for task in queryset:
            if task.status != 'completed':
                task.mark_completed()
                updated += 1
        
        self.message_user(request, f'Successfully marked {updated} tasks as completed.')
    mark_completed.short_description = 'Mark selected tasks as completed'


@admin.register(Communication)
class CommunicationAdmin(admin.ModelAdmin):
    list_display = ('employee', 'communication_type', 'direction', 'subject', 'contact_info', 'duration_minutes', 'created_at')
    list_filter = ('communication_type', 'direction', 'requires_followup', 'employee__department', 'created_at')
    search_fields = ('subject', 'content', 'contact_name', 'contact_email', 'employee__user__first_name', 'employee__user__last_name')
    raw_id_fields = ('employee', 'customer', 'lead')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Communication Details', {
            'fields': ('employee', 'communication_type', 'direction', 'subject', 'content')
        }),
        ('Contact Information', {
            'fields': ('customer', 'lead', 'contact_name', 'contact_email', 'contact_phone')
        }),
        ('Additional Details', {
            'fields': ('duration_minutes', 'requires_followup', 'followup_date')
        }),
    )
    
    def contact_info(self, obj):
        if obj.customer:
            return f"Customer: {obj.customer.full_name}"
        elif obj.lead:
            return f"Lead: {obj.lead.full_name}"
        elif obj.contact_name:
            return f"Contact: {obj.contact_name}"
        return "N/A"
    contact_info.short_description = 'Contact'


@admin.register(MissedCall)
class MissedCallAdmin(admin.ModelAdmin):
    list_display = ('caller_name', 'caller_phone', 'employee', 'priority', 'status', 'missed_at', 'callback_scheduled_at')
    list_filter = ('status', 'priority', 'employee__department', 'missed_at')
    search_fields = ('caller_name', 'caller_phone', 'caller_company', 'employee__user__first_name', 'employee__user__last_name')
    raw_id_fields = ('employee', 'customer', 'lead', 'callback_completed_by')
    date_hierarchy = 'missed_at'
    readonly_fields = ('created_at', 'updated_at', 'callback_completed_at')
    
    fieldsets = (
        ('Caller Information', {
            'fields': ('caller_name', 'caller_phone', 'caller_company')
        }),
        ('Call Details', {
            'fields': ('employee', 'missed_at', 'reason_for_call', 'priority', 'status')
        }),
        ('Related Records', {
            'fields': ('customer', 'lead'),
            'classes': ('collapse',)
        }),
        ('Follow-up Information', {
            'fields': ('follow_up_notes', 'callback_scheduled_at', 'callback_completed_at', 'callback_completed_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_callback_completed']
    
    def mark_callback_completed(self, request, queryset):
        updated = 0
        for missed_call in queryset:
            if missed_call.status != 'completed':
                missed_call.mark_completed(request.user)
                updated += 1
        
        self.message_user(request, f'Successfully marked {updated} callbacks as completed.')
    mark_callback_completed.short_description = 'Mark selected callbacks as completed'


@admin.register(MoneyRequest)
class MoneyRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'from_entity', 'to_entity', 'amount', 'request_date', 'status', 'created_at')
    list_filter = ('status', 'request_date', 'employee__department', 'created_at')
    search_fields = ('employee__user__first_name', 'employee__user__last_name', 'from_entity', 'to_entity')
    raw_id_fields = ('employee', 'processed_by')
    date_hierarchy = 'request_date'
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Request Details', {
            'fields': ('employee', 'from_entity', 'to_entity', 'amount', 'request_date', 'notes')
        }),
        ('Status', {
            'fields': ('status', 'decision_notes')
        }),
        ('Processing Information', {
            'fields': ('processed_by', 'processed_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_requests', 'reject_requests']
    
    def approve_requests(self, request, queryset):
        updated = queryset.filter(status='pending').update(
            status='approved',
            processed_by=request.user.employee_profile,
            processed_at=timezone.now()
        )
        self.message_user(request, f'Successfully approved {updated} money requests.')
    approve_requests.short_description = 'Approve selected requests'
    
    def reject_requests(self, request, queryset):
        updated = queryset.filter(status='pending').update(
            status='rejected',
            processed_by=request.user.employee_profile,
            processed_at=timezone.now()
        )
        self.message_user(request, f'Successfully rejected {updated} money requests.')
    reject_requests.short_description = 'Reject selected requests'


@admin.register(MonitoringSettings)
class MonitoringSettingsAdmin(admin.ModelAdmin):
    list_display = ('employee', 'enable_monitoring', 'idle_threshold_display', 'heartbeat_interval', 'enable_idle_alerts')
    list_filter = ('enable_monitoring', 'enable_idle_alerts', 'enable_screenshots')
    search_fields = ('employee__user__first_name', 'employee__user__last_name', 'employee__employee_id')
    raw_id_fields = ('employee',)
    
    fieldsets = (
        ('Employee', {
            'fields': ('employee',)
        }),
        ('Monitoring Settings', {
            'fields': ('enable_monitoring', 'enable_idle_alerts', 'enable_screenshots')
        }),
        ('Thresholds', {
            'fields': ('idle_threshold', 'extended_idle_threshold'),
            'description': 'Time in seconds before user is considered idle'
        }),
        ('Data Collection', {
            'fields': ('heartbeat_interval',),
            'description': 'How often activity data is sent to server (in seconds)'
        }),
    )
    
    def idle_threshold_display(self, obj):
        minutes = obj.idle_threshold // 60
        return f"{minutes} min"
    idle_threshold_display.short_description = 'Idle Threshold'


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('employee', 'activity_type', 'timestamp', 'page_title', 'work_session')
    list_filter = ('activity_type', 'timestamp', 'employee__department')
    search_fields = ('employee__user__first_name', 'employee__user__last_name', 'page_url', 'page_title')
    raw_id_fields = ('employee', 'work_session')
    date_hierarchy = 'timestamp'
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Activity Details', {
            'fields': ('employee', 'work_session', 'activity_type', 'timestamp')
        }),
        ('Page Information', {
            'fields': ('page_url', 'page_title')
        }),
        ('Additional Details', {
            'fields': ('details',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Activity logs should only be created by the system
        return False


@admin.register(IdlePeriod)
class IdlePeriodAdmin(admin.ModelAdmin):
    list_display = ('employee', 'work_session', 'start_time', 'end_time', 'duration_display', 'is_extended_idle', 'reason')
    list_filter = ('is_extended_idle', 'start_time', 'employee__department')
    search_fields = ('employee__user__first_name', 'employee__user__last_name', 'reason')
    raw_id_fields = ('employee', 'work_session')
    date_hierarchy = 'start_time'
    readonly_fields = ('duration_seconds', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Idle Period Details', {
            'fields': ('employee', 'work_session', 'start_time', 'end_time')
        }),
        ('Duration', {
            'fields': ('duration_seconds', 'is_extended_idle')
        }),
        ('Additional Information', {
            'fields': ('reason',)
        }),
    )
    
    def duration_display(self, obj):
        return obj.get_duration_display()
    duration_display.short_description = 'Duration'
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Recalculate duration after saving
        obj.calculate_duration()


@admin.register(ActivitySession)
class ActivitySessionAdmin(admin.ModelAdmin):
    list_display = ('employee', 'work_session', 'productivity_score', 'total_active_hours', 'total_idle_hours', 'total_events', 'last_activity_at')
    list_filter = ('work_session__date', 'employee__department')
    search_fields = ('employee__user__first_name', 'employee__user__last_name')
    raw_id_fields = ('employee', 'work_session')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Session Details', {
            'fields': ('employee', 'work_session')
        }),
        ('Activity Metrics', {
            'fields': ('total_mouse_movements', 'total_mouse_clicks', 'total_keyboard_events', 'total_scroll_events')
        }),
        ('Time Metrics', {
            'fields': ('total_active_time', 'total_idle_time', 'last_activity_at')
        }),
        ('Productivity', {
            'fields': ('productivity_score',)
        }),
    )
    
    def total_active_hours(self, obj):
        hours = obj.total_active_time / 3600
        return f"{hours:.2f}h"
    total_active_hours.short_description = 'Active Time'
    
    def total_idle_hours(self, obj):
        hours = obj.total_idle_time / 3600
        return f"{hours:.2f}h"
    total_idle_hours.short_description = 'Idle Time'
    
    def total_events(self, obj):
        return (obj.total_mouse_movements + obj.total_mouse_clicks + 
                obj.total_keyboard_events + obj.total_scroll_events)
    total_events.short_description = 'Total Events'
    
    actions = ['recalculate_metrics']
    
    def recalculate_metrics(self, request, queryset):
        updated = 0
        for session in queryset:
            session.update_metrics()
            updated += 1
        
        self.message_user(request, f'Successfully recalculated metrics for {updated} activity sessions.')
    recalculate_metrics.short_description = 'Recalculate metrics for selected sessions'


@admin.register(HandlerReport)
class HandlerReportAdmin(admin.ModelAdmin):
    list_display = ('handler', 'week_start', 'calls_made', 'successful_calls', 'success_rate', 'target_achievement', 'created_at')
    list_filter = ('week_start', 'handler__department', 'created_at')
    search_fields = ('handler__user__first_name', 'handler__user__last_name', 'handler__employee_id')
    raw_id_fields = ('handler',)
    date_hierarchy = 'week_start'
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Report Details', {
            'fields': ('handler', 'week_start', 'week_end')
        }),
        ('Performance Metrics', {
            'fields': ('weekly_target', 'calls_made', 'successful_calls', 'errands_made')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def success_rate(self, obj):
        return f"{obj.success_rate}%"
    success_rate.short_description = 'Success Rate'
    
    def target_achievement(self, obj):
        return f"{obj.target_achievement}%"
    target_achievement.short_description = 'Target Achievement'


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)