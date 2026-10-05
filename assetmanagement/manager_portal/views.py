from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages

from .decorators import require_manager


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

class ManagerLoginView(LoginView):
    """
    Dedicated login view for the management portal.

    - Uses its own template (manager_portal/login.html)
    - On success, only allows admin / project_manager / staff roles through
    - Everyone else is shown an error and sent back to this page
    """
    template_name = 'manager_portal/login.html'
    redirect_authenticated_user = False

    def get_success_url(self):
        return reverse_lazy('manager_portal:home')

    def form_valid(self, form):
        user = form.get_user()

        # Superuser / staff — always allowed
        if user.is_superuser or user.is_staff:
            return super().form_valid(form)

        # Check employee role
        try:
            employee = user.employee_profile
            if employee.role in ('admin', 'project_manager'):
                return super().form_valid(form)
        except AttributeError:
            pass

        # Role not permitted — do NOT log the user in
        messages.error(
            self.request,
            "This portal is for managers only. Please use the staff login."
        )
        return redirect('manager_portal:login')


# ---------------------------------------------------------------------------
# Home
# ---------------------------------------------------------------------------

@require_manager
def home(request):
    from django.utils import timezone
    from datetime import timedelta
    from crm.models import (
        Employee, WorkSession, LeaveRequest,
        MoneyRequest, Task
    )

    now   = timezone.now()
    today = now.date()
    week_start = today - timedelta(days=today.weekday())

    active_employees = Employee.objects.filter(
        employment_status='active'
    ).select_related('user', 'department')

    total_employees = active_employees.count()

    # Today's sessions
    todays_sessions = WorkSession.objects.filter(
        date=today
    ).select_related('employee__user')

    clocked_in_now = todays_sessions.filter(punch_out__isnull=True).count()
    clocked_out    = todays_sessions.filter(punch_out__isnull=False).count()

    # Approved leave today
    on_leave_today = LeaveRequest.objects.filter(
        status='approved',
        start_date__lte=today,
        end_date__gte=today
    ).select_related('employee__user')
    on_leave_count = on_leave_today.count()

    # Absent = active employees with no session today and not on leave
    on_leave_ids = on_leave_today.values_list('employee_id', flat=True)
    sessioned_ids = todays_sessions.values_list('employee_id', flat=True)
    absent_count = active_employees.exclude(
        id__in=list(sessioned_ids) + list(on_leave_ids)
    ).count()

    # Pending approvals
    pending_leave  = LeaveRequest.objects.filter(status='pending').count()
    pending_money  = MoneyRequest.objects.filter(status='pending').count()

    # Tasks
    overdue_tasks = Task.objects.filter(
        status__in=['pending', 'in_progress'],
        due_date__lt=now
    ).count()
    active_tasks = Task.objects.filter(
        status__in=['pending', 'in_progress']
    ).count()

    # This week's hours per employee (for the team table)
    week_sessions = WorkSession.objects.filter(
        date__gte=week_start,
        date__lte=today,
        employee__in=active_employees
    ).select_related('employee__user')

    week_hours_map = {}
    for ws in week_sessions:
        eid = ws.employee_id
        week_hours_map[eid] = week_hours_map.get(eid, 0) + float(ws.worked_hours or 0)

    # Recent pending leave requests (up to 5)
    recent_leave = LeaveRequest.objects.filter(
        status='pending'
    ).select_related('employee__user').order_by('-created_at')[:5]

    # Recent pending money requests (up to 5)
    recent_money = MoneyRequest.objects.filter(
        status='pending'
    ).select_related('employee__user').order_by('-created_at')[:5]

    # Today's attendance snapshot (all active employees)
    session_map = {ws.employee_id: ws for ws in todays_sessions}

    attendance_snapshot = []
    for emp in active_employees:
        if emp.id in list(on_leave_ids):
            status = 'on_leave'
            hours  = 0
        elif emp.id in session_map:
            ws = session_map[emp.id]
            status = 'clocked_in' if not ws.punch_out else 'clocked_out'
            hours  = float(ws.worked_hours or 0)
        else:
            status = 'absent'
            hours  = 0
        attendance_snapshot.append({
            'employee': emp,
            'status':   status,
            'hours':    round(hours, 1),
        })

    context = {
        # Summary cards
        'total_employees':  total_employees,
        'clocked_in_now':   clocked_in_now,
        'clocked_out':      clocked_out,
        'on_leave_count':   on_leave_count,
        'absent_count':     absent_count,
        # Approvals
        'pending_leave':    pending_leave,
        'pending_money':    pending_money,
        'pending_leave_count': pending_leave,   # for base.html badge
        'pending_money_count': pending_money,   # for base.html badge
        # Tasks
        'overdue_tasks':    overdue_tasks,
        'overdue_tasks_count': overdue_tasks,   # for base.html badge
        'active_tasks':     active_tasks,
        # Quick lists
        'recent_leave':     recent_leave,
        'recent_money':     recent_money,
        # Attendance snapshot
        'attendance_snapshot': attendance_snapshot,
        # Meta
        'today': today,
        'now':   now,
    }
    return render(request, 'manager_portal/home.html', context)


# ---------------------------------------------------------------------------
# Attendance
# ---------------------------------------------------------------------------

@require_manager
def attendance(request):
    from django.utils import timezone
    from datetime import date, timedelta
    from crm.models import Employee, WorkSession, LeaveRequest

    # ── Date filter ──────────────────────────────────────────────────────
    date_str = request.GET.get('date', '')
    try:
        selected_date = date.fromisoformat(date_str)
    except ValueError:
        selected_date = timezone.now().date()

    # Clamp to today at most
    today = timezone.now().date()
    if selected_date > today:
        selected_date = today

    prev_date = selected_date - timedelta(days=1)
    next_date = selected_date + timedelta(days=1)
    can_go_next = next_date <= today

    # ── Data ─────────────────────────────────────────────────────────────
    active_employees = Employee.objects.filter(
        employment_status='active'
    ).select_related('user', 'department').order_by('user__first_name')

    sessions = WorkSession.objects.filter(
        date=selected_date
    ).select_related('employee__user')

    on_leave_qs = LeaveRequest.objects.filter(
        status='approved',
        start_date__lte=selected_date,
        end_date__gte=selected_date,
    ).select_related('employee__user')

    session_map   = {ws.employee_id: ws for ws in sessions}
    on_leave_ids  = set(on_leave_qs.values_list('employee_id', flat=True))

    # Build a map of employee_id -> punch_in source for the selected date
    from crm.models import TimeEntry
    device_punch_ids = set(
        TimeEntry.objects.filter(
            timestamp__date=selected_date,
            entry_type='punch_in',
            source='device',
        ).values_list('employee_id', flat=True)
    )

    # Department filter
    dept_filter = request.GET.get('dept', '')
    status_filter = request.GET.get('status', '')

    # Build rows
    rows = []
    for emp in active_employees:
        if dept_filter and str(getattr(emp.department, 'name', '')) != dept_filter:
            continue

        if emp.id in on_leave_ids:
            status = 'on_leave'
            punch_in = punch_out = None
            worked_h = break_h = 0.0
        elif emp.id in session_map:
            ws = session_map[emp.id]
            punch_in  = ws.punch_in
            punch_out = ws.punch_out
            worked_h  = float(ws.worked_hours or 0)
            break_h   = float(ws.break_hours  or 0)
            status    = 'clocked_in' if not ws.punch_out else 'clocked_out'
        else:
            status    = 'absent'
            punch_in  = punch_out = None
            worked_h  = break_h = 0.0

        if status_filter and status != status_filter:
            continue

        rows.append({
            'employee':  emp,
            'status':    status,
            'punch_in':  punch_in,
            'punch_out': punch_out,
            'worked_h':  round(worked_h, 1),
            'break_h':   round(break_h, 1),
            'from_device': emp.id in device_punch_ids,
        })

    # ── Summary counts ───────────────────────────────────────────────────
    all_rows_unfiltered = []
    for emp in active_employees:
        if emp.id in on_leave_ids:
            s = 'on_leave'
        elif emp.id in session_map:
            ws = session_map[emp.id]
            s = 'clocked_in' if not ws.punch_out else 'clocked_out'
        else:
            s = 'absent'
        all_rows_unfiltered.append(s)

    summary = {
        'total':       len(all_rows_unfiltered),
        'clocked_in':  all_rows_unfiltered.count('clocked_in'),
        'clocked_out': all_rows_unfiltered.count('clocked_out'),
        'on_leave':    all_rows_unfiltered.count('on_leave'),
        'absent':      all_rows_unfiltered.count('absent'),
    }

    # Departments for filter dropdown
    from crm.models import Department
    departments = Department.objects.filter(
        employees__employment_status='active'
    ).distinct().order_by('name')

    context = {
        'rows':           rows,
        'summary':        summary,
        'selected_date':  selected_date,
        'today':          today,
        'prev_date':      prev_date,
        'next_date':      next_date,
        'can_go_next':    can_go_next,
        'departments':    departments,
        'dept_filter':    dept_filter,
        'status_filter':  status_filter,
        # base.html badges
        'pending_leave_count':  LeaveRequest.objects.filter(status='pending').count(),
        'pending_money_count':  0,
        'overdue_tasks_count':  0,
    }
    return render(request, 'manager_portal/attendance.html', context)


# ---------------------------------------------------------------------------
# Leave Requests
# ---------------------------------------------------------------------------

@require_manager
def leave_list(request):
    from django.utils import timezone
    from crm.models import LeaveRequest, Employee

    # Filters
    status_filter = request.GET.get('status', 'pending')
    type_filter   = request.GET.get('type', '')
    search_q      = request.GET.get('q', '').strip()

    qs = LeaveRequest.objects.select_related(
        'employee__user', 'employee__department', 'reviewed_by__user'
    ).order_by('-created_at')

    if status_filter:
        qs = qs.filter(status=status_filter)
    if type_filter:
        qs = qs.filter(leave_type=type_filter)
    if search_q:
        qs = qs.filter(
            employee__user__first_name__icontains=search_q
        ) | qs.filter(
            employee__user__last_name__icontains=search_q
        )

    # Counts for tabs
    pending_count  = LeaveRequest.objects.filter(status='pending').count()
    approved_count = LeaveRequest.objects.filter(status='approved').count()
    rejected_count = LeaveRequest.objects.filter(status='rejected').count()

    context = {
        'requests':       qs,
        'status_filter':  status_filter,
        'type_filter':    type_filter,
        'search_q':       search_q,
        'pending_count':  pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        # base.html badges
        'pending_leave_count':  pending_count,
        'pending_money_count':  0,
        'overdue_tasks_count':  0,
    }
    return render(request, 'manager_portal/leave_list.html', context)


@require_manager
def leave_approve(request, pk):
    from django.utils import timezone
    from crm.models import LeaveRequest
    if request.method == 'POST':
        try:
            leave = LeaveRequest.objects.get(pk=pk)
            leave.status = 'approved'
            leave.review_notes = request.POST.get('notes', '')
            try:
                leave.reviewed_by = request.user.employee_profile
            except Exception:
                pass
            leave.save()
            messages.success(request, f"Leave approved for {leave.employee.full_name}.")
        except LeaveRequest.DoesNotExist:
            messages.error(request, "Leave request not found.")
    return redirect('manager_portal:leave_list')


@require_manager
def leave_reject(request, pk):
    from crm.models import LeaveRequest
    if request.method == 'POST':
        try:
            leave = LeaveRequest.objects.get(pk=pk)
            leave.status = 'rejected'
            leave.review_notes = request.POST.get('notes', '')
            try:
                leave.reviewed_by = request.user.employee_profile
            except Exception:
                pass
            leave.save()
            messages.success(request, f"Leave rejected for {leave.employee.full_name}.")
        except LeaveRequest.DoesNotExist:
            messages.error(request, "Leave request not found.")
    return redirect('manager_portal:leave_list')


@require_manager
def leave_balances(request):
    from crm.models import Employee, LeaveBalance
    from django.utils import timezone

    search_q    = request.GET.get('q', '').strip()
    dept_filter = request.GET.get('dept', '')

    employees = Employee.objects.filter(
        employment_status='active'
    ).select_related('user', 'department', 'leave_balance').order_by(
        'user__first_name', 'user__last_name'
    )

    if search_q:
        employees = employees.filter(
            user__first_name__icontains=search_q
        ) | employees.filter(user__last_name__icontains=search_q)

    if dept_filter:
        employees = employees.filter(department__name=dept_filter)

    # Build rows — attach balance or defaults
    current_year = timezone.now().year
    rows = []
    for emp in employees:
        try:
            bal = emp.leave_balance
            if bal.year != current_year:
                bal = None
        except Exception:
            bal = None

        rows.append({
            'employee':         emp,
            'annual_total':     bal.annual_days_total    if bal else 21,
            'annual_used':      bal.annual_days_used     if bal else 0,
            'annual_remaining': bal.annual_days_remaining if bal else 21,
            'sick_total':       bal.sick_days_total      if bal else 10,
            'sick_used':        bal.sick_days_used       if bal else 0,
            'sick_remaining':   bal.sick_days_remaining  if bal else 10,
        })

    from crm.models import Department
    departments = Department.objects.filter(
        employees__employment_status='active'
    ).distinct().order_by('name')

    from crm.models import LeaveRequest
    context = {
        'rows':         rows,
        'search_q':     search_q,
        'dept_filter':  dept_filter,
        'departments':  departments,
        'current_year': current_year,
        # base.html badges
        'pending_leave_count': LeaveRequest.objects.filter(status='pending').count(),
        'pending_money_count': 0,
        'overdue_tasks_count': 0,
    }
    return render(request, 'manager_portal/leave_balances.html', context)


# ---------------------------------------------------------------------------
# Money Requests
# ---------------------------------------------------------------------------

@require_manager
def money_list(request):
    from crm.models import MoneyRequest, LeaveRequest

    status_filter = request.GET.get('status', 'pending')
    search_q      = request.GET.get('q', '').strip()

    qs = MoneyRequest.objects.select_related(
        'employee__user', 'employee__department', 'processed_by__user'
    ).order_by('-created_at')

    if status_filter:
        qs = qs.filter(status=status_filter)
    if search_q:
        qs = qs.filter(
            employee__user__first_name__icontains=search_q
        ) | qs.filter(
            employee__user__last_name__icontains=search_q
        )

    pending_count  = MoneyRequest.objects.filter(status='pending').count()
    approved_count = MoneyRequest.objects.filter(status='approved').count()
    rejected_count = MoneyRequest.objects.filter(status='rejected').count()

    # Total value of pending requests
    from django.db.models import Sum
    pending_total = MoneyRequest.objects.filter(status='pending').aggregate(
        total=Sum('amount')
    )['total'] or 0

    context = {
        'requests':       qs,
        'status_filter':  status_filter,
        'search_q':       search_q,
        'pending_count':  pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'pending_total':  pending_total,
        # base.html badges
        'pending_leave_count': LeaveRequest.objects.filter(status='pending').count(),
        'pending_money_count': pending_count,
        'overdue_tasks_count': 0,
    }
    return render(request, 'manager_portal/money_list.html', context)


@require_manager
def money_approve(request, pk):
    from crm.models import MoneyRequest
    from django.utils import timezone
    if request.method == 'POST':
        try:
            req = MoneyRequest.objects.get(pk=pk)
            req.status       = 'approved'
            req.decision_notes = request.POST.get('notes', '')
            req.processed_at = timezone.now()
            try:
                req.processed_by = request.user.employee_profile
            except Exception:
                pass
            req.save()
            messages.success(request, f"Money request approved for {req.employee.full_name} (KES {req.amount:,}).")
        except MoneyRequest.DoesNotExist:
            messages.error(request, "Request not found.")
    return redirect('manager_portal:money_list')


@require_manager
def money_reject(request, pk):
    from crm.models import MoneyRequest
    from django.utils import timezone
    if request.method == 'POST':
        try:
            req = MoneyRequest.objects.get(pk=pk)
            req.status         = 'rejected'
            req.decision_notes = request.POST.get('notes', '')
            req.processed_at   = timezone.now()
            try:
                req.processed_by = request.user.employee_profile
            except Exception:
                pass
            req.save()
            messages.success(request, f"Money request rejected for {req.employee.full_name}.")
        except MoneyRequest.DoesNotExist:
            messages.error(request, "Request not found.")
    return redirect('manager_portal:money_list')


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

@require_manager
def tasks(request):
    from django.utils import timezone
    from crm.models import Task, Employee, LeaveRequest

    status_filter   = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    search_q        = request.GET.get('q', '').strip()

    qs = Task.objects.select_related(
        'assigned_to__user', 'assigned_to__department', 'assigned_by'
    ).order_by('due_date', '-created_at')

    if status_filter:
        qs = qs.filter(status=status_filter)
    if priority_filter:
        qs = qs.filter(priority=priority_filter)
    if search_q:
        qs = qs.filter(title__icontains=search_q) | qs.filter(
            assigned_to__user__first_name__icontains=search_q
        ) | qs.filter(
            assigned_to__user__last_name__icontains=search_q
        )

    now = timezone.now()

    # Counts
    all_count      = Task.objects.count()
    pending_count  = Task.objects.filter(status='pending').count()
    active_count   = Task.objects.filter(status='in_progress').count()
    completed_count= Task.objects.filter(status='completed').count()
    overdue_count  = Task.objects.filter(
        status__in=['pending', 'in_progress'], due_date__lt=now
    ).count()

    # Annotate each task with is_overdue so the template doesn't need logic
    task_list = []
    for task in qs:
        task.is_overdue = (
            task.due_date is not None
            and task.due_date < now
            and task.status not in ('completed', 'cancelled')
        )
        task_list.append(task)

    context = {
        'tasks':            task_list,
        'status_filter':    status_filter,
        'priority_filter':  priority_filter,
        'search_q':         search_q,
        'now':              now,
        'all_count':        all_count,
        'pending_count':    pending_count,
        'active_count':     active_count,
        'completed_count':  completed_count,
        'overdue_count':    overdue_count,
        # base.html badges
        'pending_leave_count': LeaveRequest.objects.filter(status='pending').count(),
        'pending_money_count': 0,
        'overdue_tasks_count': overdue_count,
    }
    return render(request, 'manager_portal/tasks.html', context)


@require_manager
def task_assign(request):
    from crm.models import Employee, LeaveRequest

    employees = Employee.objects.filter(
        employment_status='active'
    ).select_related('user', 'department').order_by('user__first_name')

    if request.method == 'POST':
        from crm.models import Task
        title       = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        assigned_id = request.POST.get('assigned_to', '')
        priority    = request.POST.get('priority', 'medium')
        due_date    = request.POST.get('due_date', '')
        est_hours   = request.POST.get('estimated_hours', '')

        errors = []
        if not title:       errors.append('Title is required.')
        if not assigned_id: errors.append('Please select an employee.')

        if not errors:
            from django.utils import timezone
            from datetime import datetime
            try:
                emp = Employee.objects.get(pk=assigned_id)
                task = Task(
                    title=title,
                    description=description,
                    assigned_to=emp,
                    assigned_by=request.user,
                    priority=priority,
                )
                if due_date:
                    task.due_date = datetime.fromisoformat(due_date)
                if est_hours:
                    task.estimated_hours = float(est_hours)
                task.save()
                messages.success(request, f'Task "{title}" assigned to {emp.full_name}.')
                return redirect('manager_portal:tasks')
            except Employee.DoesNotExist:
                errors.append('Employee not found.')
            except Exception as e:
                errors.append(str(e))

        context = {
            'employees': employees,
            'errors':    errors,
            'post':      request.POST,
            'pending_leave_count': LeaveRequest.objects.filter(status='pending').count(),
            'pending_money_count': 0,
            'overdue_tasks_count': 0,
        }
        return render(request, 'manager_portal/task_assign.html', context)

    context = {
        'employees': employees,
        'pending_leave_count': LeaveRequest.objects.filter(status='pending').count(),
        'pending_money_count': 0,
        'overdue_tasks_count': 0,
    }
    return render(request, 'manager_portal/task_assign.html', context)


@require_manager
def task_update(request, pk):
    from crm.models import Task
    if request.method == 'POST':
        try:
            task = Task.objects.get(pk=pk)
            new_status = request.POST.get('status', '')
            if new_status in dict(Task.STATUS_CHOICES):
                if new_status == 'completed':
                    task.mark_completed()
                else:
                    task.status = new_status
                    task.save()
                messages.success(request, f'Task "{task.title}" updated to {task.get_status_display()}.')
            else:
                messages.error(request, 'Invalid status.')
        except Task.DoesNotExist:
            messages.error(request, 'Task not found.')
    return redirect('manager_portal:tasks')


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

@require_manager
def reports(request):
    from django.utils import timezone
    from datetime import timedelta, date
    from crm.models import (
        Employee, WorkSession, LeaveRequest, MoneyRequest, Task
    )
    from django.db.models import Sum, Count, Avg

    today      = timezone.now().date()
    this_month = today.replace(day=1)
    last_month_end   = this_month - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)
    week_start = today - timedelta(days=today.weekday())

    active_employees = Employee.objects.filter(employment_status='active')
    total_employees  = active_employees.count()

    # ── This month attendance ────────────────────────────────────────────
    month_sessions = WorkSession.objects.filter(
        date__gte=this_month, date__lte=today
    )
    total_hours_month = float(
        month_sessions.aggregate(s=Sum('worked_hours'))['s'] or 0
    )
    avg_hours_per_day = round(
        total_hours_month / max((today - this_month).days + 1, 1), 1
    )

    # ── This week ────────────────────────────────────────────────────────
    week_sessions = WorkSession.objects.filter(
        date__gte=week_start, date__lte=today
    )
    total_hours_week = float(
        week_sessions.aggregate(s=Sum('worked_hours'))['s'] or 0
    )

    # ── Leave stats ──────────────────────────────────────────────────────
    leave_this_month = LeaveRequest.objects.filter(
        status='approved',
        start_date__gte=this_month,
    )
    leave_by_type = leave_this_month.values('leave_type').annotate(
        count=Count('id'), days=Sum('days_requested')
    ).order_by('-days')

    # ── Money stats ──────────────────────────────────────────────────────
    money_this_month = MoneyRequest.objects.filter(
        status='approved',
        processed_at__date__gte=this_month,
    )
    total_money_approved = float(
        money_this_month.aggregate(s=Sum('amount'))['s'] or 0
    )

    # ── Task stats ───────────────────────────────────────────────────────
    tasks_total     = Task.objects.count()
    tasks_completed = Task.objects.filter(status='completed').count()
    tasks_overdue   = Task.objects.filter(
        status__in=['pending', 'in_progress'],
        due_date__lt=timezone.now()
    ).count()
    completion_rate = round(tasks_completed / max(tasks_total, 1) * 100)

    # ── Top workers this month (by hours) ────────────────────────────────
    from django.db.models import FloatField
    top_workers = WorkSession.objects.filter(
        date__gte=this_month, date__lte=today
    ).values(
        'employee__user__first_name',
        'employee__user__last_name',
        'employee__employee_id',
        'employee__department__name',
    ).annotate(
        total_h=Sum('worked_hours')
    ).order_by('-total_h')[:8]

    # ── Daily attendance trend (last 14 days) ────────────────────────────
    trend_days = []
    for i in range(13, -1, -1):
        d = today - timedelta(days=i)
        count = WorkSession.objects.filter(date=d).count()
        trend_days.append({'date': d, 'count': count})

    context = {
        # Attendance
        'total_employees':     total_employees,
        'total_hours_month':   round(total_hours_month, 1),
        'total_hours_week':    round(total_hours_week, 1),
        'avg_hours_per_day':   avg_hours_per_day,
        # Leave
        'leave_by_type':       leave_by_type,
        # Money
        'total_money_approved': total_money_approved,
        # Tasks
        'tasks_total':         tasks_total,
        'tasks_completed':     tasks_completed,
        'tasks_overdue':       tasks_overdue,
        'completion_rate':     completion_rate,
        # Lists
        'top_workers':         top_workers,
        'trend_days':          trend_days,
        # Meta
        'today':         today,
        'this_month':    this_month,
        'week_start':    week_start,
        # base.html badges
        'pending_leave_count': LeaveRequest.objects.filter(status='pending').count(),
        'pending_money_count': MoneyRequest.objects.filter(status='pending').count(),
        'overdue_tasks_count': tasks_overdue,
    }
    return render(request, 'manager_portal/reports.html', context)


@require_manager
def report_download_time(request):
    return redirect('manager_portal:reports')


@require_manager
def report_download_payroll(request):
    return redirect('manager_portal:reports')


# ---------------------------------------------------------------------------
# Employees & HR
# ---------------------------------------------------------------------------

@require_manager
def employee_list(request):
    from crm.models import Employee, Department, LeaveRequest, MoneyRequest, Task
    from django.utils import timezone

    search_q    = request.GET.get('q', '').strip()
    dept_filter = request.GET.get('dept', '')
    role_filter = request.GET.get('role', '')
    type_filter = request.GET.get('type', '')

    qs = Employee.objects.filter(
        employment_status='active'
    ).select_related('user', 'department').order_by(
        'user__first_name', 'user__last_name'
    )

    if search_q:
        qs = qs.filter(user__first_name__icontains=search_q) | \
             qs.filter(user__last_name__icontains=search_q) | \
             qs.filter(employee_id__icontains=search_q)
    if dept_filter:
        qs = qs.filter(department__name=dept_filter)
    if role_filter:
        qs = qs.filter(role=role_filter)
    if type_filter:
        qs = qs.filter(employment_type=type_filter)

    departments = Department.objects.filter(
        employees__employment_status='active'
    ).distinct().order_by('name')

    context = {
        'employees':    qs,
        'search_q':     search_q,
        'dept_filter':  dept_filter,
        'role_filter':  role_filter,
        'type_filter':  type_filter,
        'departments':  departments,
        'total_count':  Employee.objects.filter(employment_status='active').count(),
        'role_choices': Employee.ROLE_CHOICES,
        'type_choices': Employee.EMPLOYMENT_TYPE_CHOICES,
        # base badges
        'pending_leave_count': LeaveRequest.objects.filter(status='pending').count(),
        'pending_money_count': MoneyRequest.objects.filter(status='pending').count(),
        'overdue_tasks_count': Task.objects.filter(
            status__in=['pending', 'in_progress'],
            due_date__lt=timezone.now()
        ).count(),
    }
    return render(request, 'manager_portal/employee_list.html', context)


@require_manager
def employee_add(request):
    from crm.models import Employee, Department, LeaveRequest, MoneyRequest, Task
    from django.contrib.auth.models import User
    from django.utils import timezone

    departments = Department.objects.all().order_by('name')

    if request.method == 'POST':
        p = request.POST
        errors = []

        first_name  = p.get('first_name', '').strip()
        last_name   = p.get('last_name', '').strip()
        username    = p.get('username', '').strip()
        email       = p.get('email', '').strip()
        password    = p.get('password', '').strip()
        position    = p.get('position', '').strip()
        phone       = p.get('phone', '').strip()
        dept_id     = p.get('department', '')
        role        = p.get('role', 'user')
        emp_type    = p.get('employment_type', 'full_time')
        hire_date   = p.get('hire_date', '')
        salary      = p.get('salary', '')

        if not first_name: errors.append('First name is required.')
        if not last_name:  errors.append('Last name is required.')
        if not username:   errors.append('Username is required.')
        if not position:   errors.append('Position is required.')
        if not hire_date:  errors.append('Hire date is required.')
        if not password:   errors.append('Password is required.')
        if User.objects.filter(username=username).exists():
            errors.append(f'Username "{username}" is already taken.')

        if not errors:
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                )
                emp = Employee(
                    user=user,
                    position=position,
                    phone=phone,
                    role=role,
                    employment_type=emp_type,
                    hire_date=hire_date,
                    employment_status='active',
                )
                if dept_id:
                    try:
                        emp.department = Department.objects.get(pk=dept_id)
                    except Department.DoesNotExist:
                        pass
                if salary:
                    emp.salary = float(salary)
                emp.save()
                messages.success(request, f'{emp.full_name} ({emp.employee_id}) added successfully.')
                return redirect('manager_portal:employee_detail', pk=emp.pk)
            except Exception as e:
                errors.append(str(e))

        context = {
            'departments': departments,
            'role_choices': Employee.ROLE_CHOICES,
            'type_choices': Employee.EMPLOYMENT_TYPE_CHOICES,
            'errors': errors,
            'post': p,
            'pending_leave_count': 0,
            'pending_money_count': 0,
            'overdue_tasks_count': 0,
        }
        return render(request, 'manager_portal/employee_add.html', context)

    context = {
        'departments': departments,
        'role_choices': Employee.ROLE_CHOICES,
        'type_choices': Employee.EMPLOYMENT_TYPE_CHOICES,
        'pending_leave_count': 0,
        'pending_money_count': 0,
        'overdue_tasks_count': 0,
    }
    return render(request, 'manager_portal/employee_add.html', context)


@require_manager
def employee_detail(request, pk):
    from django.shortcuts import get_object_or_404
    from crm.models import Employee, WorkSession, LeaveRequest, MoneyRequest, Task
    from manager_portal.models import HRNote
    from django.utils import timezone
    from datetime import timedelta

    emp   = get_object_or_404(Employee, pk=pk)
    today = timezone.now().date()
    this_month = today.replace(day=1)

    # Attendance summary — this month
    sessions_month = WorkSession.objects.filter(
        employee=emp, date__gte=this_month, date__lte=today
    ).order_by('-date')
    from django.db.models import Sum
    total_hours_month = float(
        sessions_month.aggregate(s=Sum('worked_hours'))['s'] or 0
    )
    days_worked = sessions_month.count()

    # Current status
    try:
        today_session = WorkSession.objects.get(employee=emp, date=today)
        if not today_session.punch_out:
            current_status = 'clocked_in'
        else:
            current_status = 'clocked_out'
    except WorkSession.DoesNotExist:
        on_leave_now = LeaveRequest.objects.filter(
            employee=emp, status='approved',
            start_date__lte=today, end_date__gte=today
        ).exists()
        current_status = 'on_leave' if on_leave_now else 'absent'

    # Recent sessions (last 10)
    recent_sessions = WorkSession.objects.filter(
        employee=emp
    ).order_by('-date')[:10]

    # Leave requests
    leave_requests = LeaveRequest.objects.filter(
        employee=emp
    ).order_by('-created_at')[:8]

    # Active tasks
    active_tasks = Task.objects.filter(
        assigned_to=emp,
        status__in=['pending', 'in_progress']
    ).order_by('due_date')[:6]

    # HR Notes
    hr_notes = HRNote.objects.filter(employee=emp).order_by('-created_at')[:10]

    # Leave balance
    try:
        leave_bal = emp.leave_balance
    except Exception:
        leave_bal = None

    context = {
        'emp':                emp,
        'current_status':     current_status,
        'total_hours_month':  round(total_hours_month, 1),
        'days_worked':        days_worked,
        'recent_sessions':    recent_sessions,
        'leave_requests':     leave_requests,
        'active_tasks':       active_tasks,
        'hr_notes':           hr_notes,
        'leave_bal':          leave_bal,
        'today':              today,
        'this_month':         this_month,
        # base badges
        'pending_leave_count': LeaveRequest.objects.filter(status='pending').count(),
        'pending_money_count': MoneyRequest.objects.filter(status='pending').count(),
        'overdue_tasks_count': Task.objects.filter(
            status__in=['pending', 'in_progress'], due_date__lt=timezone.now()
        ).count(),
    }
    return render(request, 'manager_portal/employee_detail.html', context)


@require_manager
def employee_edit(request, pk):
    from django.shortcuts import get_object_or_404
    from crm.models import Employee, Department, LeaveRequest, MoneyRequest, Task
    from django.utils import timezone

    emp         = get_object_or_404(Employee, pk=pk)
    departments = Department.objects.all().order_by('name')

    if request.method == 'POST':
        p = request.POST
        errors = []

        first_name = p.get('first_name', '').strip()
        last_name  = p.get('last_name', '').strip()
        email      = p.get('email', '').strip()
        position   = p.get('position', '').strip()
        phone      = p.get('phone', '').strip()
        dept_id    = p.get('department', '')
        role       = p.get('role', emp.role)
        emp_type   = p.get('employment_type', emp.employment_type)
        salary     = p.get('salary', '')
        status     = p.get('employment_status', emp.employment_status)
        zkteco_id  = p.get('zkteco_id', '').strip() or None

        if not first_name: errors.append('First name is required.')
        if not last_name:  errors.append('Last name is required.')
        if not position:   errors.append('Position is required.')

        if not errors:
            try:
                emp.user.first_name = first_name
                emp.user.last_name  = last_name
                emp.user.email      = email
                emp.user.save()

                emp.position          = position
                emp.phone             = phone
                emp.role              = role
                emp.employment_type   = emp_type
                emp.employment_status = status
                if dept_id:
                    try:
                        emp.department = Department.objects.get(pk=dept_id)
                    except Department.DoesNotExist:
                        emp.department = None
                else:
                    emp.department = None
                emp.salary = float(salary) if salary else None
                emp.zkteco_id = zkteco_id
                emp.save()
                messages.success(request, f'{emp.full_name} updated successfully.')
                return redirect('manager_portal:employee_detail', pk=emp.pk)
            except Exception as e:
                errors.append(str(e))

        context = {
            'emp': emp, 'departments': departments,
            'role_choices': Employee.ROLE_CHOICES,
            'type_choices': Employee.EMPLOYMENT_TYPE_CHOICES,
            'status_choices': Employee.EMPLOYMENT_STATUS_CHOICES,
            'errors': errors, 'post': p,
            'pending_leave_count': 0,
            'pending_money_count': 0,
            'overdue_tasks_count': 0,
        }
        return render(request, 'manager_portal/employee_edit.html', context)

    context = {
        'emp': emp, 'departments': departments,
        'role_choices': Employee.ROLE_CHOICES,
        'type_choices': Employee.EMPLOYMENT_TYPE_CHOICES,
        'status_choices': Employee.EMPLOYMENT_STATUS_CHOICES,
        'pending_leave_count': 0,
        'pending_money_count': 0,
        'overdue_tasks_count': 0,
    }
    return render(request, 'manager_portal/employee_edit.html', context)


@require_manager
def hr_note_add(request, pk):
    from django.shortcuts import get_object_or_404
    from crm.models import Employee
    from manager_portal.models import HRNote

    emp = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        note_type = request.POST.get('note_type', 'general')
        title     = request.POST.get('title', '').strip()
        content   = request.POST.get('content', '').strip()
        if title and content:
            HRNote.objects.create(
                employee=emp,
                note_type=note_type,
                title=title,
                content=content,
                created_by=request.user,
                is_private=True,
            )
            messages.success(request, 'HR note added.')
        else:
            messages.error(request, 'Title and content are required.')
    return redirect('manager_portal:employee_detail', pk=pk)
