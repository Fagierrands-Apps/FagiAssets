from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views

app_name = 'manager_portal'

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────────────────────
    path('login/', views.ManagerLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='manager_portal:login'), name='logout'),

    # ── Home ──────────────────────────────────────────────────────────────
    path('', views.home, name='home'),

    # ── Attendance ────────────────────────────────────────────────────────
    path('attendance/', views.attendance, name='attendance'),

    # ── Leave Requests ────────────────────────────────────────────────────
    path('leave/', views.leave_list, name='leave_list'),
    path('leave/<int:pk>/approve/', views.leave_approve, name='leave_approve'),
    path('leave/<int:pk>/reject/', views.leave_reject, name='leave_reject'),
    path('leave/balances/', views.leave_balances, name='leave_balances'),

    # ── Money Requests ────────────────────────────────────────────────────
    path('money/', views.money_list, name='money_list'),
    path('money/<int:pk>/approve/', views.money_approve, name='money_approve'),
    path('money/<int:pk>/reject/', views.money_reject, name='money_reject'),

    # ── Tasks ─────────────────────────────────────────────────────────────
    path('tasks/', views.tasks, name='tasks'),
    path('tasks/assign/', views.task_assign, name='task_assign'),
    path('tasks/<int:pk>/update/', views.task_update, name='task_update'),

    # ── Reports ───────────────────────────────────────────────────────────
    path('reports/', views.reports, name='reports'),
    path('reports/download/time/', views.report_download_time, name='report_download_time'),
    path('reports/download/payroll/', views.report_download_payroll, name='report_download_payroll'),

    # ── Employees ─────────────────────────────────────────────────────────
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.employee_add, name='employee_add'),
    path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('employees/<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('employees/<int:pk>/hr-note/add/', views.hr_note_add, name='hr_note_add'),
]
