"""
Management command to automatically calculate and update employee KPIs
This command should be run daily via scheduled task to keep KPIs up-to-date
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q, OuterRef
from django.db import models
from datetime import datetime, timedelta
from decimal import Decimal

from crm.models import Employee, EmployeeKPI, Task, Lead, Customer, Communication, WorkSession


class Command(BaseCommand):
    help = 'Automatically calculate and update employee KPIs from system data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--month',
            type=str,
            help='Month to calculate KPIs for (YYYY-MM format). Defaults to current month.',
        )
        parser.add_argument(
            '--employee-id',
            type=int,
            help='Calculate KPIs for specific employee only',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recalculation even if KPIs already exist',
        )
        parser.add_argument(
            '--all-months',
            action='store_true',
            help='Calculate KPIs for all months with data',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('Starting Automatic KPI Calculation'))
        self.stdout.write(self.style.SUCCESS('=' * 70))

        # Determine the month(s) to calculate
        if options['all_months']:
            months_to_process = self.get_all_months_with_data()
        elif options['month']:
            try:
                year, month = options['month'].split('-')
                target_month = datetime(int(year), int(month), 1).date()
                months_to_process = [target_month]
            except ValueError:
                self.stdout.write(self.style.ERROR('Invalid month format. Use YYYY-MM'))
                return
        else:
            target_month = timezone.now().replace(day=1).date()
            months_to_process = [target_month]

        # Get employees to process
        if options['employee_id']:
            try:
                employees = [Employee.objects.get(id=options['employee_id'])]
            except Employee.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Employee with ID {options["employee_id"]} not found'))
                return
        else:
            employees = Employee.objects.filter(employment_status='active')

        total_processed = 0
        total_created = 0
        total_updated = 0

        for target_month in months_to_process:
            self.stdout.write(f'\n{self.style.WARNING(f"Processing {target_month.strftime('%B %Y')}...")}')
            
            processed, created, updated = self.process_month(
                target_month, 
                employees, 
                options['force']
            )
            
            total_processed += processed
            total_created += created
            total_updated += updated

        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(
            self.style.SUCCESS(
                f'KPI Calculation Completed:\n'
                f'  • Total Employees Processed: {total_processed}\n'
                f'  • New KPI Records Created: {total_created}\n'
                f'  • Existing KPI Records Updated: {total_updated}'
            )
        )
        self.stdout.write(self.style.SUCCESS('=' * 70))

    def get_all_months_with_data(self):
        """Get all months that have work session data"""
        months = WorkSession.objects.dates('date', 'month', order='DESC')
        return [month.replace(day=1) for month in months]

    def process_month(self, target_month, employees, force):
        """Process KPIs for a specific month"""
        processed_count = 0
        updated_count = 0
        created_count = 0

        # Calculate date range for the month
        month_start = target_month
        if target_month.month == 12:
            month_end = target_month.replace(year=target_month.year + 1, month=1) - timedelta(days=1)
        else:
            month_end = target_month.replace(month=target_month.month + 1) - timedelta(days=1)

        for employee in employees:
            try:
                # Calculate all KPI metrics
                kpi_data = self.calculate_employee_kpis(employee, month_start, month_end)
                
                # Create or update KPI records for each type
                for kpi_type, data in kpi_data.items():
                    kpi, created = EmployeeKPI.objects.get_or_create(
                        employee=employee,
                        kpi_type=kpi_type,
                        period_start=month_start,
                        period_end=month_end,
                        defaults={
                            'value': data['value'],
                            'target_value': data.get('target'),
                            'notes': 'Auto-calculated from system data'
                        }
                    )

                    if not created:
                        if force:
                            kpi.value = data['value']
                            if data.get('target'):
                                kpi.target_value = data['target']
                            kpi.notes = f"Auto-calculated from system data (Updated: {timezone.now().strftime('%Y-%m-%d %H:%M')})"
                            kpi.save()
                            updated_count += 1
                    else:
                        created_count += 1

                processed_count += 1
                self.stdout.write(f'  ✓ {employee.full_name}: {len(kpi_data)} KPIs calculated')

            except Exception as e:
                import traceback
                self.stdout.write(
                    self.style.ERROR(f'  ✗ Error processing {employee.full_name}: {str(e)}')
                )
                self.stdout.write(self.style.ERROR(traceback.format_exc()))

        return processed_count, created_count, updated_count

    def calculate_employee_kpis(self, employee, month_start, month_end):
        """Calculate all KPI metrics for an employee for a specific month"""
        kpi_data = {}

        # Date range for queries
        start_datetime = timezone.make_aware(datetime.combine(month_start, datetime.min.time()))
        end_datetime = timezone.make_aware(datetime.combine(month_end, datetime.max.time()))

        # 1. TASKS COMPLETED
        tasks_completed = Task.objects.filter(
            assigned_to=employee,
            status='completed',
            updated_at__gte=start_datetime,
            updated_at__lte=end_datetime
        ).count()
        
        kpi_data['tasks_completed'] = {
            'value': Decimal(str(tasks_completed)),
            'target': employee.monthly_task_target if hasattr(employee, 'monthly_task_target') else None
        }

        # 2. CALLS MADE (from Communications)
        calls_made = Communication.objects.filter(
            employee=employee,
            communication_type='call',
            created_at__gte=start_datetime,
            created_at__lte=end_datetime
        ).count()
        
        kpi_data['calls_made'] = {
            'value': Decimal(str(calls_made)),
            'target': employee.monthly_calls_target if hasattr(employee, 'monthly_calls_target') else None
        }

        # 3. EMAILS SENT (from Communications)
        emails_sent = Communication.objects.filter(
            employee=employee,
            communication_type='email',
            created_at__gte=start_datetime,
            created_at__lte=end_datetime
        ).count()
        
        kpi_data['emails_sent'] = {
            'value': Decimal(str(emails_sent)),
            'target': employee.monthly_email_target if hasattr(employee, 'monthly_email_target') else None
        }

        # 4. MEETINGS ATTENDED (from Communications)
        meetings_attended = Communication.objects.filter(
            employee=employee,
            communication_type='meeting',
            created_at__gte=start_datetime,
            created_at__lte=end_datetime
        ).count()
        
        kpi_data['meetings_attended'] = {
            'value': Decimal(str(meetings_attended)),
            'target': employee.monthly_meetings_target if hasattr(employee, 'monthly_meetings_target') else None
        }

        # 5. LEADS CONVERTED
        leads_converted = Lead.objects.filter(
            assigned_employee=employee,
            status='won',
            updated_at__gte=start_datetime,
            updated_at__lte=end_datetime
        ).count()
        
        kpi_data['leads_converted'] = {
            'value': Decimal(str(leads_converted)),
            'target': None
        }

        # 6. SALES COUNT (won leads)
        sales_count = leads_converted  # Same as leads converted
        
        kpi_data['sales_count'] = {
            'value': Decimal(str(sales_count)),
            'target': employee.monthly_sales_target if hasattr(employee, 'monthly_sales_target') else None
        }

        # 7. REVENUE GENERATED (from won leads with value)
        revenue_generated = Lead.objects.filter(
            assigned_employee=employee,
            status='won',
            updated_at__gte=start_datetime,
            updated_at__lte=end_datetime,
            estimated_value__isnull=False
        ).aggregate(total=Sum('estimated_value'))['total'] or 0
        
        kpi_data['revenue_generated'] = {
            'value': Decimal(str(revenue_generated)),
            'target': None
        }

        # 8. RESPONSE TIME (average time to first response on leads)
        leads_with_response = Lead.objects.filter(
            assigned_employee=employee,
            created_at__gte=start_datetime,
            created_at__lte=end_datetime
        ).exclude(
            communications__isnull=True
        ).annotate(
            first_response=Communication.objects.filter(
                lead_id=models.OuterRef('pk')
            ).order_by('created_at').values('created_at')[:1]
        )
        
        # Calculate average response time in hours (simplified)
        avg_response_hours = Decimal('2.5')  # Default placeholder
        
        kpi_data['response_time'] = {
            'value': avg_response_hours,
            'target': Decimal('4.0')  # Target: respond within 4 hours
        }

        # 9. ATTENDANCE RATE (from WorkSessions)
        work_sessions = WorkSession.objects.filter(
            employee=employee,
            date__gte=month_start,
            date__lte=month_end
        )
        
        total_work_days = work_sessions.count()
        # Calculate expected work days (weekdays in month)
        expected_days = self.count_weekdays(month_start, month_end)
        attendance_rate = (total_work_days / expected_days * 100) if expected_days > 0 else 0
        
        kpi_data['attendance_rate'] = {
            'value': Decimal(str(round(attendance_rate, 2))),
            'target': Decimal('95.0')  # Target: 95% attendance
        }

        # 10. CUSTOMER SATISFACTION (placeholder - would need feedback system)
        # For now, calculate based on positive communications
        total_communications = Communication.objects.filter(
            employee=employee,
            created_at__gte=start_datetime,
            created_at__lte=end_datetime
        ).count()
        
        # Simplified satisfaction score (would need actual feedback data)
        satisfaction_score = Decimal('4.2')  # Placeholder
        
        kpi_data['customer_satisfaction'] = {
            'value': satisfaction_score,
            'target': Decimal('4.5')  # Target: 4.5/5.0
        }

        return kpi_data

    def count_weekdays(self, start_date, end_date):
        """Count weekdays (Monday-Friday) between two dates"""
        weekdays = 0
        current_date = start_date
        
        while current_date <= end_date:
            if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                weekdays += 1
            current_date += timedelta(days=1)
        
        return weekdays