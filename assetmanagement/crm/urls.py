from django.urls import path
from . import views
from . import activity_views

app_name = 'crm'

urlpatterns = [
    # Dashboard
    path('', views.crm_dashboard, name='dashboard'),
    
    # Customers
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/<int:customer_id>/', views.customer_detail, name='customer_detail'),
    
    # Leads
    path('leads/', views.lead_list, name='lead_list'),
    path('leads/create/', views.lead_create, name='lead_create'),
    path('leads/<int:lead_id>/', views.lead_detail, name='lead_detail'),
    path('leads/<int:lead_id>/convert/', views.convert_lead, name='convert_lead'),
    
    # Asset Assignments
    path('assignments/', views.assignment_list, name='assignment_list'),
    path('assign-asset/', views.assign_asset, name='assign_asset'),
    
    # Notifications
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/<int:notification_id>/dismiss/', views.dismiss_notification, name='dismiss_notification'),
    
    # Employee Features
    path('employee/', views.employee_dashboard, name='employee_dashboard'),
    path('employee/punch/', views.punch_in_out, name='punch_in_out'),
    path('employee/timesheet/', views.employee_timesheet, name='employee_timesheet'),
    path('employee/kpis/', views.employee_kpis, name='employee_kpis'),
    path('employee/tasks/', views.employee_tasks, name='employee_tasks'),
    path('employee/tasks/<int:task_id>/update/', views.update_task_status, name='update_task_status'),
    path('employee/communications/', views.employee_communications, name='employee_communications'),
    path('employee/communications/add/', views.add_communication, name='add_communication'),
    path('employee/money-request/', views.money_request, name='money_request'),
    path('employee/money-requests/', views.money_request_list, name='money_request_list'),
    path('employee/money-requests/<int:request_id>/decision/', views.money_request_decision, name='money_request_decision'),
    
    # Manager Task Management
    path('manager/tasks/', views.manager_task_list, name='manager_task_list'),
    path('manager/tasks/create/', views.manager_create_task, name='manager_create_task'),
    path('manager/tasks/<int:task_id>/edit/', views.manager_edit_task, name='manager_edit_task'),
    path('manager/tasks/<int:task_id>/delete/', views.manager_delete_task, name='manager_delete_task'),
    
    # Missed Calls
    path('missed-calls/', views.missed_calls_list, name='missed_calls_list'),
    path('missed-calls/log/', views.log_missed_call, name='log_missed_call'),
    path('missed-calls/<int:call_id>/edit/', views.edit_missed_call, name='edit_missed_call'),
    path('missed-calls/<int:call_id>/delete/', views.delete_missed_call, name='delete_missed_call'),
    
    # Productivity Dashboard
    path('productivity/', views.productivity_dashboard, name='productivity_dashboard'),
    
    # Handler Reports
    path('handler-reports/', views.handler_reports, name='handler_reports'),
    path('handler-reports/create/', views.handler_report_create, name='handler_report_create'),
    path('handler-reports/<int:report_id>/', views.handler_report_detail, name='handler_report_detail'),
    
    # Admin Reports
    path('admin/reports/', views.admin_reports, name='admin_reports'),
    
    # API endpoints
    path('api/customers/search/', views.customer_search_api, name='customer_search_api'),
    path('api/assets/search/', views.asset_search_api, name='asset_search_api'),
    
    # Activity Monitoring API
    path('activity/log/', activity_views.log_activity, name='log_activity'),
    path('activity/settings/', activity_views.get_monitoring_settings, name='get_monitoring_settings'),
    path('activity/summary/', activity_views.get_activity_summary, name='get_activity_summary'),
    path('activity/idle-periods/', activity_views.get_idle_periods, name='get_idle_periods'),
    path('activity/idle-reason/', activity_views.report_idle_reason, name='report_idle_reason'),
]