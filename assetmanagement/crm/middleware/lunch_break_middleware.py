"""
Middleware to automatically enforce lunch break at 1 PM for non-call-center employees
"""
from django.utils import timezone
from django.shortcuts import redirect
from django.contrib import messages
from datetime import time
from crm.models import Employee, TimeEntry
import logging

logger = logging.getLogger(__name__)


class AutoLunchBreakMiddleware:
    """
    Automatically creates lunch break entries and enforces break time
    for non-call-center employees between 1 PM - 2 PM (Monday-Saturday)
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if user is authenticated and has employee profile
        if request.user.is_authenticated and hasattr(request.user, 'employee_profile'):
            try:
                employee = request.user.employee_profile
                now = timezone.now()
                current_time = now.time()
                current_day = now.weekday()  # 0=Monday, 6=Sunday
                
                # Only apply Monday-Saturday (0-5)
                if current_day != 6:  # Not Sunday
                    lunch_start = time(13, 0)  # 1 PM
                    lunch_end = time(14, 0)    # 2 PM
                    
                    # Check if it's lunch time
                    if lunch_start <= current_time < lunch_end:
                        # Exempt call center agents
                        if employee.role != 'call_center':
                            # Check if employee is currently punched in
                            current_status = employee.get_current_status()
                            
                            if current_status in ['punched_in', 'working']:
                                # Auto-create lunch break if not already created
                                self._auto_create_lunch_break(employee, now)
                                
                                # Check if already on break
                                if current_status != 'on_break':
                                    # Force break status
                                    logger.info(f'Enforcing lunch break for {employee.full_name}')
                            
            except Employee.DoesNotExist:
                pass
            except Exception as e:
                logger.error(f'Error in AutoLunchBreakMiddleware: {str(e)}')
        
        response = self.get_response(request)
        return response
    
    def _auto_create_lunch_break(self, employee, now):
        """
        Automatically create lunch break entries if not already created
        """
        try:
            # Check if lunch break already created today
            today_lunch_break = TimeEntry.objects.filter(
                employee=employee,
                entry_type='break_start',
                timestamp__date=now.date(),
                timestamp__hour=13,
                notes__contains='Automatic lunch break'
            ).exists()
            
            if not today_lunch_break:
                # Create break_start entry at 1 PM
                TimeEntry.objects.create(
                    employee=employee,
                    entry_type='break_start',
                    timestamp=now.replace(hour=13, minute=0, second=0, microsecond=0),
                    notes='Automatic lunch break (1 PM - 2 PM)',
                    ip_address=None
                )
                
                # Create break_end entry at 2 PM
                TimeEntry.objects.create(
                    employee=employee,
                    entry_type='break_end',
                    timestamp=now.replace(hour=14, minute=0, second=0, microsecond=0),
                    notes='Automatic lunch break end',
                    ip_address=None
                )
                
                logger.info(f'Auto-created lunch break for {employee.full_name}')
                
        except Exception as e:
            logger.error(f'Error auto-creating lunch break for {employee.full_name}: {str(e)}')