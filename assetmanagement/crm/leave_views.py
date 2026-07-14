from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import date

from .models import LeaveRequest, LeaveBalance
from .decorators import role_required


def _get_or_create_balance(employee):
    balance, _ = LeaveBalance.objects.get_or_create(
        employee=employee,
        defaults={'year': timezone.now().year}
    )
    return balance


@login_required
def apply_leave(request):
    employee = request.user.employee_profile
    balance = _get_or_create_balance(employee)

    if request.method == 'POST':
        leave_type = request.POST.get('leave_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')

        leave = LeaveRequest(
            employee=employee,
            leave_type=leave_type,
            start_date=date.fromisoformat(start_date),
            end_date=date.fromisoformat(end_date),
            reason=reason,
        )
        leave.save()
        messages.success(request, 'Leave application submitted successfully.')
        return redirect('crm:my_leave_requests')

    return render(request, 'crm/apply_leave.html', {'balance': balance})


@login_required
def my_leave_requests(request):
    employee = request.user.employee_profile
    balance = _get_or_create_balance(employee)
    leave_requests = LeaveRequest.objects.filter(employee=employee)
    return render(request, 'crm/my_leave_requests.html', {
        'leave_requests': leave_requests,
        'balance': balance,
    })


@login_required
@role_required(['admin', 'hr', 'project_manager'])
def leave_decision(request, request_id):
    if request.method != 'POST':
        return redirect('crm:admin_leave_list')

    leave = get_object_or_404(LeaveRequest, id=request_id)
    action = request.POST.get('action')
    review_notes = request.POST.get('review_notes', '')
    reviewer = getattr(request.user, 'employee_profile', None)

    if action == 'approve' and leave.status == 'pending':
        leave.status = 'approved'
        leave.reviewed_by = reviewer
        leave.review_notes = review_notes
        leave.save()

        # Deduct from balance for annual/sick only
        if leave.leave_type in ('annual', 'sick'):
            balance = _get_or_create_balance(leave.employee)
            if leave.leave_type == 'annual':
                balance.annual_days_used += leave.days_requested
            else:
                balance.sick_days_used += leave.days_requested
            balance.save()

        messages.success(request, 'Leave approved.')

    elif action == 'reject' and leave.status == 'pending':
        leave.status = 'rejected'
        leave.reviewed_by = reviewer
        leave.review_notes = review_notes
        leave.save()
        messages.success(request, 'Leave rejected.')

    return redirect('crm:admin_leave_list')


@login_required
@role_required(['admin', 'hr', 'project_manager'])
def admin_leave_list(request):
    status_filter = request.GET.get('status', '')
    leave_requests = LeaveRequest.objects.select_related('employee', 'reviewed_by')
    if status_filter:
        leave_requests = leave_requests.filter(status=status_filter)
    return render(request, 'crm/admin_leave_list.html', {
        'leave_requests': leave_requests,
        'status_filter': status_filter,
        'status_choices': LeaveRequest.STATUS_CHOICES,
    })


@login_required
@role_required(['admin', 'hr', 'project_manager'])
def admin_leave_balances(request):
    from .models import Employee

    # Ensure every employee has a balance record for current year
    year = timezone.now().year
    employees = Employee.objects.filter(employment_status='active').order_by('user__last_name')
    for emp in employees:
        LeaveBalance.objects.get_or_create(employee=emp, defaults={'year': year})

    if request.method == 'POST':
        emp_id = request.POST.get('employee_id')
        field = request.POST.get('field')   # annual_days_used / annual_days_total / sick_days_used / sick_days_total
        value = request.POST.get('value')
        allowed = {'annual_days_used', 'annual_days_total', 'sick_days_used', 'sick_days_total'}
        if emp_id and field in allowed:
            try:
                balance = LeaveBalance.objects.get(employee_id=emp_id)
                setattr(balance, field, int(value))
                balance.save()
                messages.success(request, 'Balance updated.')
            except (LeaveBalance.DoesNotExist, ValueError):
                messages.error(request, 'Invalid update.')
        return redirect('crm:admin_leave_balances')

    balances = LeaveBalance.objects.select_related('employee__user').filter(year=year).order_by('employee__user__last_name')
    return render(request, 'crm/admin_leave_balances.html', {'balances': balances, 'year': year})
