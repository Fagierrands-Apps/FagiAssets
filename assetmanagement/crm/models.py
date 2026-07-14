from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import EmailValidator
from assets.models import Asset
import uuid


class Department(models.Model):
    """Department model for organizing employees"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    manager = models.ForeignKey(
        'Employee', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='managed_departments'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Employee(models.Model):
    """Employee model extending User with business information"""
    EMPLOYMENT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('terminated', 'Terminated'),
        ('on_leave', 'On Leave'),
    ]
    
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('intern', 'Intern'),
    ]

    ROLE_CHOICES = [
        ('call_center', 'Call Center'),
        ('sales', 'Sales'),
        ('user', 'User'),
        ('admin', 'Admin'),
        ('accountant', 'Accountant'),
        ('receptionist', 'Receptionist'),
        ('project_support', 'Project Support'),
        ('hr', 'HR'),
        ('project_manager', 'Project Manager'),
        ('dev', 'Developer'),
        ('handler', 'Handler'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='direct_reports')
    position = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS_CHOICES, default='active')
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default='full_time')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    hire_date = models.DateField()
    termination_date = models.DateField(null=True, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_manager = models.BooleanField(default=False)
    weekly_target = models.IntegerField(default=10, help_text="Weekly call target for this employee")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['user__last_name', 'user__first_name']
        indexes = [
            models.Index(fields=['employee_id']),
            models.Index(fields=['employment_status']),
            models.Index(fields=['department']),
            models.Index(fields=['role']),
        ]

    def save(self, *args, **kwargs):
        # Generate unique employee ID if not provided
        if not self.employee_id:
            self.employee_id = self.generate_unique_employee_id()
        super().save(*args, **kwargs)

    def generate_unique_employee_id(self):
        """Generate a unique employee ID in EMP format (EMP001, EMP002, etc.)"""
        from django.db import transaction

        prefix = "EMP"

        with transaction.atomic():
            # Find the highest existing employee ID with EMP prefix
            existing_ids = Employee.objects.filter(
                employee_id__startswith=prefix
            ).values_list('employee_id', flat=True)

            # Extract numbers from existing IDs
            numbers = []
            for emp_id in existing_ids:
                try:
                    # Extract the 3-digit number part after EMP
                    number_part = emp_id[3:]  # Remove "EMP" prefix
                    if number_part.isdigit() and len(number_part) == 3:
                        numbers.append(int(number_part))
                except (IndexError, ValueError):
                    continue

            # Get next number
            next_number = max(numbers) + 1 if numbers else 1

            # Format with leading zeros (3 digits)
            return f"{prefix}{next_number:03d}"

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"

    @property
    def full_name(self):
        return self.user.get_full_name()

    def get_current_month_performance(self):
        """Get performance metrics for current month"""
        from datetime import datetime
        current_month_start = datetime.now().replace(day=1)
        
        # Get KPIs for current month
        kpis = self.kpis.filter(
            period_start__gte=current_month_start
        )
        
        performance = {}
        for kpi in kpis:
            performance[kpi.kpi_type] = {
                'value': kpi.value,
                'target': kpi.target_value,
                'achievement': kpi.achievement_percentage
            }
        
        return performance

    def get_current_status(self):
        """Get current punch in/out status"""
        today = timezone.now().date()
        latest_entry = self.time_entries.filter(
            timestamp__date=today
        ).first()

        if not latest_entry:
            return 'Not Punched In'

        if latest_entry.entry_type == 'punch_in':
            return 'Working'
        elif latest_entry.entry_type == 'punch_out':
            return 'Punched Out'
        elif latest_entry.entry_type == 'break_start':
            return 'On Break'
        elif latest_entry.entry_type == 'break_end':
            return 'Working'

        return 'Unknown'

    def get_today_hours(self):
        """Get hours worked today (real-time if currently working)"""
        from decimal import Decimal
        today = timezone.now().date()
        try:
            session = self.work_sessions.get(date=today)
            # If still working (no punch_out), calculate real-time hours
            if not session.punch_out:
                current_time = timezone.now()
                total_time = current_time - session.punch_in
                real_time_hours = total_time.total_seconds() / 3600
                # Convert break_hours to float for subtraction
                break_hours_float = float(session.break_hours) if session.break_hours else 0.0
                return real_time_hours - break_hours_float
            else:
                return float(session.worked_hours) if session.worked_hours else 0.0
        except WorkSession.DoesNotExist:
            return 0

    def get_pending_tasks_count(self):
        """Get count of pending tasks"""
        return self.assigned_tasks.filter(status__in=['pending', 'in_progress']).count()

    def get_monthly_kpi_summary(self, month=None, year=None):
        """Get KPI summary for a specific month"""
        if not month:
            month = timezone.now().month
        if not year:
            year = timezone.now().year
            
        kpis = self.kpis.filter(
            period_start__month=month,
            period_start__year=year
        )
        
        summary = {}
        for kpi in kpis:
            summary[kpi.kpi_type] = {
                'value': float(kpi.value),
                'target': float(kpi.target_value) if kpi.target_value else None,
                'achievement': kpi.achievement_percentage
            }
        
        return summary


class Customer(models.Model):
    """Customer model for CRM functionality"""
    CUSTOMER_TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('business', 'Business'),
        ('government', 'Government'),
        ('non_profit', 'Non-Profit'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('prospect', 'Prospect'),
        ('former', 'Former Customer'),
    ]
    
    CONTACT_METHOD_CHOICES = [
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('mail', 'Mail'),
        ('in_person', 'In Person'),
    ]

    # Basic Information
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    company_name = models.CharField(max_length=100, blank=True)
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPE_CHOICES, default='individual')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Contact Information
    email = models.EmailField(validators=[EmailValidator()])
    phone = models.CharField(max_length=20)
    alternate_phone = models.CharField(max_length=20, blank=True)
    preferred_contact_method = models.CharField(max_length=20, choices=CONTACT_METHOD_CHOICES, default='email')
    
    # Address Information
    address_line1 = models.CharField(max_length=100)
    address_line2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=50, default='USA')
    
    # Business Information
    assigned_employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='customers')
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    lifetime_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['assigned_employee']),
            models.Index(fields=['status']),
            models.Index(fields=['customer_type']),
        ]

    def __str__(self):
        if self.company_name:
            return f"{self.company_name} ({self.full_name})"
        return self.full_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def full_address(self):
        address_parts = [self.address_line1]
        if self.address_line2:
            address_parts.append(self.address_line2)
        address_parts.append(f"{self.city}, {self.state} {self.postal_code}")
        if self.country != 'USA':
            address_parts.append(self.country)
        return '\n'.join(address_parts)


class CustomerNote(models.Model):
    """Notes associated with customers"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='notes')
    note = models.TextField()
    is_important = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Note for {self.customer.full_name} - {self.created_at.strftime('%Y-%m-%d')}"


class AssetCustomerAssignment(models.Model):
    """Track asset assignments to customers"""
    ASSIGNMENT_TYPE_CHOICES = [
        ('owned', 'Owned by Customer'),
        ('leased', 'Leased to Customer'),
        ('serviced', 'Under Service Contract'),
        ('temporary', 'Temporary Assignment'),
    ]

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='crm_assignments')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='asset_assignments')
    assignment_type = models.CharField(max_length=20, choices=ASSIGNMENT_TYPE_CHOICES, default='owned')
    is_active = models.BooleanField(default=True)
    
    # Assignment Details
    assigned_date = models.DateTimeField(default=timezone.now)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='crm_assignments_created')
    contract_number = models.CharField(max_length=50, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    
    # Financial Information
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Additional Information
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-assigned_date']
        indexes = [
            models.Index(fields=['asset', 'is_active']),
            models.Index(fields=['customer', 'is_active']),
            models.Index(fields=['assignment_type']),
        ]
        unique_together = ['asset', 'customer', 'is_active']

    def __str__(self):
        return f"{self.asset.asset_tag} → {self.customer.full_name} ({self.get_assignment_type_display()})"


class Lead(models.Model):
    """Lead management for potential customers"""
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('proposal', 'Proposal Sent'),
        ('negotiation', 'In Negotiation'),
        ('won', 'Won'),
        ('lost', 'Lost'),
    ]
    
    SOURCE_CHOICES = [
        ('website', 'Website'),
        ('referral', 'Referral'),
        ('cold_call', 'Cold Call'),
        ('email', 'Email Campaign'),
        ('social_media', 'Social Media'),
        ('trade_show', 'Trade Show'),
        ('other', 'Other'),
    ]

    # Basic Information
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    company_name = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=100, blank=True)
    
    # Contact Information
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    
    # Lead Information
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='website')
    assigned_employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='leads')
    estimated_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    expected_close_date = models.DateField(null=True, blank=True)
    
    # Additional Information
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['assigned_employee']),
            models.Index(fields=['source']),
        ]

    def __str__(self):
        return f"{self.full_name} - {self.company_name or 'Individual'}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def convert_to_customer(self):
        """Convert lead to customer"""
        customer = Customer.objects.create(
            first_name=self.first_name,
            last_name=self.last_name,
            company_name=self.company_name,
            email=self.email,
            phone=self.phone,
            assigned_employee=self.assigned_employee,
            status='active'
        )
        
        # Update lead status
        self.status = 'won'
        self.save()
        
        return customer


class Notification(models.Model):
    """System notifications for users"""
    NOTIFICATION_TYPES = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('success', 'Success'),
        ('task', 'Task'),
        ('reminder', 'Reminder'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    
    # Related objects (optional)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, null=True, blank=True)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', 'is_dismissed']),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class TimeEntry(models.Model):
    """Employee time tracking for punch in/out functionality"""
    ENTRY_TYPE_CHOICES = [
        ('punch_in', 'Punch In'),
        ('punch_out', 'Punch Out'),
        ('break_start', 'Break Start'),
        ('break_end', 'Break End'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='time_entries')
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPE_CHOICES)
    timestamp = models.DateTimeField(default=timezone.now)
    location = models.CharField(max_length=100, blank=True)  # Optional GPS/location info
    notes = models.TextField(blank=True)
    
    # System tracking
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['employee', 'timestamp']),
            models.Index(fields=['entry_type', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.employee.full_name} - {self.get_entry_type_display()} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class WorkSession(models.Model):
    """Calculated work sessions from time entries"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='work_sessions')
    date = models.DateField()
    punch_in = models.DateTimeField()
    punch_out = models.DateTimeField(null=True, blank=True)
    
    # Calculated fields
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    break_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    worked_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Activity tracking fields
    productive_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Time with activity")
    idle_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Time without activity")
    
    # Status
    is_complete = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['employee', 'date']
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"{self.employee.full_name} - {self.date}"

    def calculate_hours(self):
        """Calculate total hours worked including productive and idle time"""
        from decimal import Decimal
        
        if self.punch_out:
            total_time = self.punch_out - self.punch_in
            self.total_hours = Decimal(str(total_time.total_seconds() / 3600))
            self.worked_hours = self.total_hours - self.break_hours
            self.is_complete = True
            
            # Calculate idle hours from idle periods
            idle_periods = self.idle_periods.filter(end_time__isnull=False)
            total_idle_seconds = sum(period.duration_seconds for period in idle_periods)
            self.idle_hours = Decimal(str(total_idle_seconds / 3600))
            
            # Productive hours = worked hours - idle hours
            self.productive_hours = max(Decimal('0'), self.worked_hours - self.idle_hours)
        else:
            self.is_complete = False
        self.save()
    
    def get_idle_periods_list(self):
        """Get list of idle time ranges for display"""
        idle_periods = self.idle_periods.filter(end_time__isnull=False).order_by('start_time')
        return [
            {
                'start': period.start_time,
                'end': period.end_time,
                'duration': period.get_duration_display(),
                'duration_minutes': period.duration_minutes,
                'reason': period.reason
            }
            for period in idle_periods
        ]


class EmployeeKPI(models.Model):
    """Employee Key Performance Indicators tracking"""
    KPI_TYPE_CHOICES = [
        ('sales_count', 'Sales Count'),
        ('revenue_generated', 'Revenue Generated'),
        ('customer_satisfaction', 'Customer Satisfaction'),
        ('tasks_completed', 'Tasks Completed'),
        ('calls_made', 'Calls Made'),
        ('emails_sent', 'Emails Sent'),
        ('meetings_attended', 'Meetings Attended'),
        ('leads_converted', 'Leads Converted'),
        ('response_time', 'Average Response Time (hours)'),
        ('attendance_rate', 'Attendance Rate (%)'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='kpis')
    kpi_type = models.CharField(max_length=30, choices=KPI_TYPE_CHOICES)
    value = models.DecimalField(max_digits=12, decimal_places=2)
    target_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Time period
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Additional context
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-period_end', 'employee']
        unique_together = ['employee', 'kpi_type', 'period_start', 'period_end']
        indexes = [
            models.Index(fields=['employee', 'kpi_type']),
            models.Index(fields=['period_start', 'period_end']),
        ]

    def __str__(self):
        return f"{self.employee.full_name} - {self.get_kpi_type_display()}: {self.value}"

    @property
    def achievement_percentage(self):
        """Calculate achievement percentage against target"""
        if self.target_value and self.target_value > 0:
            return (self.value / self.target_value) * 100
        return 0


class Task(models.Model):
    """Task management for employees"""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    assigned_to = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='assigned_tasks')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_tasks')
    
    # Task details
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateTimeField(null=True, blank=True)
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    actual_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Related objects
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, null=True, blank=True)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['priority', 'status']),
        ]

    def __str__(self):
        return f"{self.title} - {self.assigned_to.full_name}"

    def mark_completed(self):
        """Mark task as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()


class Communication(models.Model):
    """Communication tracking (calls, emails, meetings)"""
    COMMUNICATION_TYPE_CHOICES = [
        ('call', 'Phone Call'),
        ('email', 'Email'),
        ('meeting', 'Meeting'),
        ('chat', 'Chat/Message'),
        ('note', 'Note'),
    ]
    
    DIRECTION_CHOICES = [
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='communications')
    communication_type = models.CharField(max_length=20, choices=COMMUNICATION_TYPE_CHOICES)
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES, default='outbound')
    
    # Contact information
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, null=True, blank=True)
    contact_name = models.CharField(max_length=100, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    
    # Communication details
    subject = models.CharField(max_length=200)
    content = models.TextField()
    duration_minutes = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Duration in minutes (e.g., 2.5 = 2 min 30 sec)")  # For calls/meetings
    
    # Follow-up
    requires_followup = models.BooleanField(default=False)
    followup_date = models.DateTimeField(null=True, blank=True)

    # Sourced contact
    is_sourced = models.BooleanField(default=False, help_text="Indicates if this contact was sourced")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employee', 'communication_type']),
            models.Index(fields=['customer']),
            models.Index(fields=['lead']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        contact = self.customer or self.lead or self.contact_name
        return f"{self.get_communication_type_display()} with {contact} by {self.employee.full_name}"


class MissedCall(models.Model):
    """Track missed calls for follow-up"""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Callback'),
        ('attempted', 'Callback Attempted'),
        ('completed', 'Callback Completed'),
        ('no_callback_needed', 'No Callback Needed'),
    ]

    # Employee who missed the call
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='missed_calls')
    
    # Caller information
    caller_name = models.CharField(max_length=100)
    caller_phone = models.CharField(max_length=20)
    caller_company = models.CharField(max_length=100, blank=True)
    
    # Optional link to existing customer or lead
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='missed_calls')
    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True, related_name='missed_calls')
    
    # Call details
    missed_at = models.DateTimeField(default=timezone.now)
    reason_for_call = models.TextField(blank=True, help_text="Why was the caller calling?")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Follow-up information
    follow_up_notes = models.TextField(blank=True)
    callback_scheduled_at = models.DateTimeField(null=True, blank=True)
    callback_completed_at = models.DateTimeField(null=True, blank=True)
    callback_completed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='completed_callbacks')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-missed_at']
        indexes = [
            models.Index(fields=['employee', 'status']),
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['missed_at']),
            models.Index(fields=['caller_phone']),
        ]

    def __str__(self):
        return f"Missed call from {self.caller_name} ({self.caller_phone}) - {self.employee.full_name}"
    
    def mark_completed(self, completed_by_user):
        """Mark the callback as completed"""
        self.status = 'completed'
        self.callback_completed_at = timezone.now()
        self.callback_completed_by = completed_by_user
        self.save()
    
    @property
    def is_overdue(self):
        """Check if callback is overdue"""
        if self.callback_scheduled_at and self.status == 'pending':
            return timezone.now() > self.callback_scheduled_at
        return False


class MoneyRequest(models.Model):
    """Employee fund request submissions"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='money_requests')
    from_entity = models.CharField(max_length=255)
    to_entity = models.CharField(max_length=255)
    request_date = models.DateField()
    amount = models.PositiveIntegerField(default=100)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    decision_notes = models.TextField(blank=True)
    processed_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_money_requests'
    )
    processed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['employee', 'status']),
            models.Index(fields=['request_date']),
        ]

    def __str__(self):
        return f"{self.employee.full_name} - {self.from_entity} to {self.to_entity} ({self.request_date})"


class MonitoringSettings(models.Model):
    """User preferences and thresholds for activity monitoring"""
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='monitoring_settings')
    
    # Thresholds (in seconds)
    idle_threshold = models.IntegerField(default=300, help_text="Seconds of inactivity before considered idle (default: 5 minutes)")
    extended_idle_threshold = models.IntegerField(default=900, help_text="Seconds for extended idle warning (default: 15 minutes)")
    
    # Monitoring preferences
    enable_monitoring = models.BooleanField(default=True, help_text="Enable activity monitoring for this employee")
    enable_idle_alerts = models.BooleanField(default=True, help_text="Send alerts when idle threshold is reached")
    enable_screenshots = models.BooleanField(default=False, help_text="Enable periodic screenshots (if implemented)")
    
    # Data collection intervals (in seconds)
    heartbeat_interval = models.IntegerField(default=60, help_text="How often to send activity data (default: 60 seconds)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Monitoring Settings"
        verbose_name_plural = "Monitoring Settings"

    def __str__(self):
        return f"Monitoring Settings for {self.employee.full_name}"


class ActivityLog(models.Model):
    """Store user interactions (mouse movements, keyboard presses, clicks)"""
    ACTIVITY_TYPE_CHOICES = [
        ('mouse_move', 'Mouse Movement'),
        ('mouse_click', 'Mouse Click'),
        ('keyboard', 'Keyboard Input'),
        ('scroll', 'Scroll'),
        ('window_focus', 'Window Focus'),
        ('window_blur', 'Window Blur'),
        ('heartbeat', 'Heartbeat Signal'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='activity_logs')
    work_session = models.ForeignKey(WorkSession, on_delete=models.CASCADE, related_name='activity_logs', null=True, blank=True)
    
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPE_CHOICES)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    
    # Activity details (stored as JSON-like text for flexibility)
    details = models.JSONField(default=dict, blank=True, help_text="Additional activity details (coordinates, keys, etc.)")
    
    # Page/URL information
    page_url = models.CharField(max_length=500, blank=True)
    page_title = models.CharField(max_length=200, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['employee', 'timestamp']),
            models.Index(fields=['work_session', 'timestamp']),
            models.Index(fields=['activity_type', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.employee.full_name} - {self.get_activity_type_display()} at {self.timestamp}"


class IdlePeriod(models.Model):
    """Track periods of inactivity with start/end times"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='idle_periods')
    work_session = models.ForeignKey(WorkSession, on_delete=models.CASCADE, related_name='idle_periods')
    
    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField(null=True, blank=True, db_index=True)
    
    # Calculated duration in seconds
    duration_seconds = models.IntegerField(default=0, help_text="Duration of idle period in seconds")
    
    # Classification
    is_extended_idle = models.BooleanField(default=False, help_text="Idle period exceeded extended threshold")
    
    # Optional reason (if employee provides one)
    reason = models.CharField(max_length=200, blank=True, help_text="Reason for idle time (optional)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['employee', 'start_time']),
            models.Index(fields=['work_session', 'start_time']),
            models.Index(fields=['start_time', 'end_time']),
        ]

    def __str__(self):
        duration = self.get_duration_display()
        return f"{self.employee.full_name} - Idle for {duration} starting at {self.start_time}"
    
    def calculate_duration(self):
        """Calculate and update duration in seconds"""
        if self.end_time:
            delta = self.end_time - self.start_time
            self.duration_seconds = int(delta.total_seconds())
            self.save()
    
    def get_duration_display(self):
        """Get human-readable duration"""
        if self.duration_seconds == 0 and not self.end_time:
            return "Ongoing"
        
        hours = self.duration_seconds // 3600
        minutes = (self.duration_seconds % 3600) // 60
        seconds = self.duration_seconds % 60
        
        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if seconds > 0 or not parts:
            parts.append(f"{seconds}s")
        
        return " ".join(parts)
    
    @property
    def duration_minutes(self):
        """Get duration in minutes (decimal)"""
        return round(self.duration_seconds / 60, 2)


class ActivitySession(models.Model):
    """Link activity data to work sessions with aggregated metrics"""
    work_session = models.OneToOneField(WorkSession, on_delete=models.CASCADE, related_name='activity_session')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='activity_sessions')
    
    # Activity metrics
    total_mouse_movements = models.IntegerField(default=0)
    total_mouse_clicks = models.IntegerField(default=0)
    total_keyboard_events = models.IntegerField(default=0)
    total_scroll_events = models.IntegerField(default=0)
    
    # Time metrics (in seconds)
    total_active_time = models.IntegerField(default=0, help_text="Total time with activity in seconds")
    total_idle_time = models.IntegerField(default=0, help_text="Total idle time in seconds")
    
    # Productivity score (0-100)
    productivity_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Calculated productivity score")
    
    # Last activity timestamp
    last_activity_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employee', 'created_at']),
            models.Index(fields=['work_session']),
        ]

    def __str__(self):
        return f"Activity Session for {self.employee.full_name} on {self.work_session.date}"
    
    def calculate_productivity_score(self):
        """Calculate productivity score based on activity metrics"""
        from decimal import Decimal
        
        # Get total session time
        if self.work_session.punch_out:
            total_time = (self.work_session.punch_out - self.work_session.punch_in).total_seconds()
        else:
            total_time = (timezone.now() - self.work_session.punch_in).total_seconds()
        
        if total_time == 0:
            return Decimal('0')
        
        # Calculate active time percentage
        active_percentage = (self.total_active_time / total_time) * 100
        
        # Calculate activity intensity (events per minute of active time)
        if self.total_active_time > 0:
            active_minutes = self.total_active_time / 60
            total_events = (self.total_mouse_movements + 
                          self.total_mouse_clicks + 
                          self.total_keyboard_events + 
                          self.total_scroll_events)
            events_per_minute = total_events / active_minutes
            
            # Normalize to 0-50 scale (assuming 10+ events per minute is very active)
            intensity_score = min(50, (events_per_minute / 10) * 50)
        else:
            intensity_score = 0
        
        # Combine scores (50% active time, 50% intensity)
        productivity_score = Decimal(str((active_percentage * 0.5) + intensity_score))
        
        self.productivity_score = min(Decimal('100'), productivity_score)
        self.save()
        
        return self.productivity_score
    
    def update_metrics(self):
        """Update aggregated metrics from activity logs and idle periods"""
        # Count activity events
        activities = self.work_session.activity_logs.all()
        
        self.total_mouse_movements = activities.filter(activity_type='mouse_move').count()
        self.total_mouse_clicks = activities.filter(activity_type='mouse_click').count()
        self.total_keyboard_events = activities.filter(activity_type='keyboard').count()
        self.total_scroll_events = activities.filter(activity_type='scroll').count()
        
        # Calculate idle time
        idle_periods = self.work_session.idle_periods.filter(end_time__isnull=False)
        self.total_idle_time = sum(period.duration_seconds for period in idle_periods)
        
        # Calculate active time
        if self.work_session.punch_out:
            total_time = (self.work_session.punch_out - self.work_session.punch_in).total_seconds()
        else:
            total_time = (timezone.now() - self.work_session.punch_in).total_seconds()
        
        # Subtract break time and idle time
        break_seconds = float(self.work_session.break_hours) * 3600 if self.work_session.break_hours else 0
        self.total_active_time = int(max(0, total_time - break_seconds - self.total_idle_time))
        
        # Get last activity
        last_activity = activities.order_by('-timestamp').first()
        if last_activity:
            self.last_activity_at = last_activity.timestamp
        
        self.save()
        
        # Calculate productivity score
        self.calculate_productivity_score()


class HandlerReport(models.Model):
    """Weekly reporting for handlers"""
    handler = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='handler_reports')
    week_start = models.DateField()
    week_end = models.DateField()
    
    weekly_target = models.IntegerField(default=10)
    calls_made = models.IntegerField(default=0)
    successful_calls = models.IntegerField(default=0)
    errands_made = models.IntegerField(default=0)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-week_start']
        indexes = [
            models.Index(fields=['handler', 'week_start']),
            models.Index(fields=['week_start']),
        ]
        unique_together = ['handler', 'week_start']
    
    def __str__(self):
        return f"{self.handler.full_name} - Week of {self.week_start.strftime('%Y-%m-%d')}"
    
    @property
    def success_rate(self):
        """Calculate success rate percentage"""
        if self.calls_made == 0:
            return 0
        return round((self.successful_calls / self.calls_made) * 100, 2)
    
    @property
    def target_achievement(self):
        """Calculate target achievement percentage"""
        if self.weekly_target == 0:
            return 0
        return round((self.calls_made / self.weekly_target) * 100, 2)


class LeaveRequest(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('annual', 'Annual'),
        ('sick', 'Sick'),
        ('emergency', 'Emergency'),
        ('unpaid', 'Unpaid'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    days_requested = models.IntegerField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_leaves')
    review_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee.full_name} - {self.get_leave_type_display()} ({self.start_date} to {self.end_date})"

    def save(self, *args, **kwargs):
        if self.start_date and self.end_date:
            delta = self.end_date - self.start_date
            self.days_requested = delta.days + 1
        super().save(*args, **kwargs)


class LeaveBalance(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='leave_balance')
    annual_days_total = models.IntegerField(default=21)
    annual_days_used = models.IntegerField(default=0)
    sick_days_total = models.IntegerField(default=10)
    sick_days_used = models.IntegerField(default=0)
    year = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee.full_name} - Leave Balance {self.year}"

    @property
    def annual_days_remaining(self):
        return self.annual_days_total - self.annual_days_used

    @property
    def sick_days_remaining(self):
        return self.sick_days_total - self.sick_days_used
