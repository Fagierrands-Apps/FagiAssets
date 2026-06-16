"""
Activity Monitoring API Views
Handles receiving and processing user activity data from the frontend
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
import json

from .models import (
    Employee, WorkSession, ActivityLog, IdlePeriod, 
    ActivitySession, MonitoringSettings
)


@login_required
@require_http_methods(["POST"])
def log_activity(request):
    """
    Receive and store activity data from frontend
    Expected POST data:
    {
        "activities": [
            {
                "type": "mouse_move|mouse_click|keyboard|scroll|window_focus|window_blur|heartbeat",
                "timestamp": "ISO timestamp",
                "details": {...},
                "page_url": "current page URL",
                "page_title": "current page title"
            }
        ]
    }
    """
    try:
        # Get employee profile
        try:
            employee = request.user.employee_profile
        except Employee.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Employee profile not found'
            }, status=400)
        
        # Check if monitoring is enabled
        try:
            settings = employee.monitoring_settings
            if not settings.enable_monitoring:
                return JsonResponse({
                    'success': True,
                    'message': 'Monitoring disabled for this employee'
                })
        except MonitoringSettings.DoesNotExist:
            # Create default settings
            settings = MonitoringSettings.objects.create(employee=employee)
        
        # Parse request data
        data = json.loads(request.body)
        activities = data.get('activities', [])
        
        if not activities:
            return JsonResponse({
                'success': False,
                'error': 'No activities provided'
            }, status=400)
        
        # Get or create today's work session
        today = timezone.now().date()
        work_session = WorkSession.objects.filter(
            employee=employee,
            date=today
        ).first()
        
        if not work_session:
            return JsonResponse({
                'success': False,
                'error': 'No active work session found. Please punch in first.'
            }, status=400)
        
        # Store activities in bulk
        activity_logs = []
        for activity_data in activities:
            activity_type = activity_data.get('type')
            timestamp_str = activity_data.get('timestamp')
            details = activity_data.get('details', {})
            page_url = activity_data.get('page_url', '')
            page_title = activity_data.get('page_title', '')
            
            # Parse timestamp
            if timestamp_str:
                timestamp = timezone.datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                timestamp = timezone.now()
            
            activity_logs.append(ActivityLog(
                employee=employee,
                work_session=work_session,
                activity_type=activity_type,
                timestamp=timestamp,
                details=details,
                page_url=page_url[:500],  # Truncate to field max length
                page_title=page_title[:200]
            ))
        
        # Bulk create activity logs
        ActivityLog.objects.bulk_create(activity_logs)
        
        # Update or create activity session
        activity_session, created = ActivitySession.objects.get_or_create(
            work_session=work_session,
            defaults={'employee': employee}
        )
        
        # Check for idle periods
        check_and_create_idle_periods(employee, work_session, settings)
        
        return JsonResponse({
            'success': True,
            'message': f'Logged {len(activity_logs)} activities',
            'activities_logged': len(activity_logs)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_monitoring_settings(request):
    """
    Get monitoring settings for the current employee
    Returns settings like idle threshold, heartbeat interval, etc.
    """
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Employee profile not found'
        }, status=400)
    
    # Get or create monitoring settings
    settings, created = MonitoringSettings.objects.get_or_create(
        employee=employee
    )
    
    return JsonResponse({
        'success': True,
        'settings': {
            'enable_monitoring': settings.enable_monitoring,
            'idle_threshold': settings.idle_threshold,
            'extended_idle_threshold': settings.extended_idle_threshold,
            'heartbeat_interval': settings.heartbeat_interval,
            'enable_idle_alerts': settings.enable_idle_alerts,
        }
    })


@login_required
@require_http_methods(["POST"])
def report_idle_reason(request):
    """
    Allow employee to provide a reason for an idle period
    Expected POST data:
    {
        "idle_period_id": 123,
        "reason": "Meeting with client"
    }
    """
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Employee profile not found'
        }, status=400)
    
    try:
        data = json.loads(request.body)
        idle_period_id = data.get('idle_period_id')
        reason = data.get('reason', '')
        
        # Get the idle period
        idle_period = IdlePeriod.objects.get(
            id=idle_period_id,
            employee=employee
        )
        
        # Update reason
        idle_period.reason = reason[:200]  # Truncate to field max length
        idle_period.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Idle reason updated'
        })
        
    except IdlePeriod.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Idle period not found'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_activity_summary(request):
    """
    Get activity summary for the current employee's active session
    """
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Employee profile not found'
        }, status=400)
    
    # Get today's work session
    today = timezone.now().date()
    work_session = WorkSession.objects.filter(
        employee=employee,
        date=today
    ).first()
    
    if not work_session:
        return JsonResponse({
            'success': False,
            'error': 'No active work session found'
        }, status=404)
    
    # Get activity session
    try:
        activity_session = work_session.activity_session
        activity_session.update_metrics()  # Update metrics before returning
        
        return JsonResponse({
            'success': True,
            'summary': {
                'total_active_time': activity_session.total_active_time,
                'total_idle_time': activity_session.total_idle_time,
                'productivity_score': float(activity_session.productivity_score),
                'total_mouse_movements': activity_session.total_mouse_movements,
                'total_mouse_clicks': activity_session.total_mouse_clicks,
                'total_keyboard_events': activity_session.total_keyboard_events,
                'total_scroll_events': activity_session.total_scroll_events,
                'last_activity_at': activity_session.last_activity_at.isoformat() if activity_session.last_activity_at else None,
            }
        })
    except ActivitySession.DoesNotExist:
        return JsonResponse({
            'success': True,
            'summary': {
                'total_active_time': 0,
                'total_idle_time': 0,
                'productivity_score': 0,
                'total_mouse_movements': 0,
                'total_mouse_clicks': 0,
                'total_keyboard_events': 0,
                'total_scroll_events': 0,
                'last_activity_at': None,
            }
        })


@login_required
@require_http_methods(["GET"])
def get_idle_periods(request):
    """
    Get list of idle periods for today's session
    """
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Employee profile not found'
        }, status=400)
    
    # Get today's work session
    today = timezone.now().date()
    work_session = WorkSession.objects.filter(
        employee=employee,
        date=today
    ).first()
    
    if not work_session:
        return JsonResponse({
            'success': True,
            'idle_periods': []
        })
    
    # Get idle periods
    idle_periods = work_session.get_idle_periods_list()
    
    return JsonResponse({
        'success': True,
        'idle_periods': idle_periods
    })


def check_and_create_idle_periods(employee, work_session, settings):
    """
    Check for idle periods based on activity logs and create IdlePeriod records
    """
    # Get the last activity
    last_activity = ActivityLog.objects.filter(
        employee=employee,
        work_session=work_session
    ).exclude(activity_type='heartbeat').order_by('-timestamp').first()
    
    if not last_activity:
        return
    
    # Check if enough time has passed since last activity
    now = timezone.now()
    time_since_activity = (now - last_activity.timestamp).total_seconds()
    
    if time_since_activity >= settings.idle_threshold:
        # Check if there's already an ongoing idle period
        ongoing_idle = IdlePeriod.objects.filter(
            employee=employee,
            work_session=work_session,
            end_time__isnull=True
        ).first()
        
        if not ongoing_idle:
            # Create new idle period
            idle_start = last_activity.timestamp + timedelta(seconds=settings.idle_threshold)
            
            idle_period = IdlePeriod.objects.create(
                employee=employee,
                work_session=work_session,
                start_time=idle_start,
                is_extended_idle=(time_since_activity >= settings.extended_idle_threshold)
            )
    else:
        # End any ongoing idle periods
        ongoing_idles = IdlePeriod.objects.filter(
            employee=employee,
            work_session=work_session,
            end_time__isnull=True
        )
        
        for idle_period in ongoing_idles:
            idle_period.end_time = last_activity.timestamp
            idle_period.calculate_duration()
            
            # Check if it became an extended idle
            if idle_period.duration_seconds >= settings.extended_idle_threshold:
                idle_period.is_extended_idle = True
                idle_period.save()