from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction



class UserProfile(models.Model):
    """Extended user profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Personal Information
    employee_id = models.CharField(max_length=50, blank=True, unique=True)
    phone = models.CharField(max_length=20, blank=True)
    mobile = models.CharField(max_length=20, blank=True)
    
    # Work Information
    job_title = models.CharField(max_length=100, blank=True)
    department = models.ForeignKey('assets.Department', on_delete=models.SET_NULL, null=True, blank=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')
    location = models.ForeignKey('assets.Location', on_delete=models.SET_NULL, null=True, blank=True)
    
    # System Preferences
    timezone = models.CharField(max_length=50, default='UTC')
    language = models.CharField(max_length=10, default='en')
    notifications_enabled = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    
    # Avatar
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Generate unique employee ID if not provided
        if not self.employee_id:
            self.employee_id = self.generate_unique_employee_id()
        super().save(*args, **kwargs)
    
    def generate_unique_employee_id(self):
        """Generate a unique employee ID in FGE format (FGE001, FGE002, etc.)"""
        
        prefix = "FGE"
        
        with transaction.atomic():
            # Find the highest existing employee ID with FGE prefix
            existing_ids = UserProfile.objects.filter(
                employee_id__startswith=prefix
            ).values_list('employee_id', flat=True)
            
            # Extract numbers from existing IDs
            numbers = []
            for emp_id in existing_ids:
                try:
                    # Extract the 3-digit number part after FGE
                    number_part = emp_id[3:]  # Remove "FGE" prefix
                    if number_part.isdigit() and len(number_part) == 3:
                        numbers.append(int(number_part))
                except (IndexError, ValueError):
                    continue
            
            # Get next number
            next_number = max(numbers) + 1 if numbers else 1
            
            # Format with leading zeros (3 digits)
            return f"{prefix}{next_number:03d}"

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} Profile"

    class Meta:
        ordering = ['user__last_name', 'user__first_name']
        constraints = [
            models.UniqueConstraint(fields=['user'], name='unique_user_profile')
        ]


@receiver(post_save, sender=User)
def manage_user_profile(sender, instance, created, **kwargs):
    """Create or update user profile when user is created or updated"""
    # Skip profile creation in read-only environments
    from django.conf import settings
    import os

    # Check if we're in a read-only environment (like Vercel with SQLite)
    is_readonly = (
        not (os.environ.get('VERCEL') or os.environ.get('DATABASE_URL') or
             'vercel.app' in os.environ.get('VERCEL_URL', '')) and
        'sqlite3' in settings.DATABASES['default']['ENGINE']
    )

    if is_readonly:
        return  # Skip profile creation in read-only SQLite environments

    # Use atomic transaction to prevent race conditions
    try:
        with transaction.atomic():
            if created:
                # Only create profile if user was just created
                try:
                    # Use select_for_update to prevent concurrent access issues
                    profile, profile_created = UserProfile.objects.select_for_update().get_or_create(
                        user=instance,
                        defaults={'employee_id': ''}  # Will be generated in save()
                    )
                    # Employee ID will be automatically generated in the save method if needed
                    if profile_created and not profile.employee_id:
                        profile.save()  # This will trigger the employee ID generation
                except Exception as e:
                    # If there's an error creating the profile, log it but don't fail
                    print(f"Error creating profile for user {instance.username}: {e}")
            else:
                # User was updated, ensure profile exists and save it if it does
                try:
                    if hasattr(instance, 'profile'):
                        instance.profile.save()
                except UserProfile.DoesNotExist:
                    # Profile doesn't exist, create it
                    try:
                        profile, profile_created = UserProfile.objects.select_for_update().get_or_create(
                            user=instance,
                            defaults={'employee_id': ''}  # Will be generated in save()
                        )
                        if profile_created and not profile.employee_id:
                            profile.save()
                    except Exception as e:
                        print(f"Error creating profile for existing user {instance.username}: {e}")
    except Exception as e:
        # If transaction fails, log but don't crash
        print(f"Transaction failed for user profile management: {e}")


@receiver(post_save, sender=User)
def manage_employee_profile(sender, instance, created, **kwargs):
    """Create or update employee profile when user is created or updated"""
    # Skip profile creation in read-only environments
    from django.conf import settings
    from crm.models import Employee
    import os

    # Check if we're in a read-only environment (like Vercel with SQLite)
    is_readonly = (
        not (os.environ.get('VERCEL') or os.environ.get('DATABASE_URL') or
             'vercel.app' in os.environ.get('VERCEL_URL', '')) and
        'sqlite3' in settings.DATABASES['default']['ENGINE']
    )

    if is_readonly:
        return  # Skip profile creation in read-only SQLite environments

    # Use atomic transaction to prevent race conditions
    try:
        with transaction.atomic():
            if created:
                # Only create employee profile if user was just created
                try:
                    # Use select_for_update to prevent concurrent access issues
                    employee, employee_created = Employee.objects.select_for_update().get_or_create(
                        user=instance,
                        defaults={
                            'employee_id': '',  # Will be generated or copied from UserProfile
                            'position': 'User',
                            'employment_status': 'active',
                            'employment_type': 'full_time',
                            'role': 'user',
                        }
                    )
                    # If employee profile was created, try to populate from existing UserProfile
                    if employee_created:
                        try:
                            if hasattr(instance, 'profile'):
                                profile = instance.profile
                                # Copy data from UserProfile to Employee
                                employee.employee_id = profile.employee_id or employee.employee_id
                                employee.department = profile.department
                                employee.manager = profile.manager
                                employee.position = profile.job_title or employee.position
                                employee.phone = profile.phone
                                # Set hire_date to today if not set
                                if not employee.hire_date:
                                    from django.utils import timezone
                                    employee.hire_date = timezone.now().date()
                                employee.save()
                        except Exception as e:
                            print(f"Error copying UserProfile data to Employee for user {instance.username}: {e}")
                            # Still save the employee profile even if copying fails
                            employee.save()
                except Exception as e:
                    # If there's an error creating the employee profile, log it but don't fail
                    print(f"Error creating employee profile for user {instance.username}: {e}")
            else:
                # User was updated, ensure employee profile exists
                try:
                    if not hasattr(instance, 'employee_profile'):
                        # Create employee profile if it doesn't exist
                        employee, employee_created = Employee.objects.select_for_update().get_or_create(
                            user=instance,
                            defaults={
                                'employee_id': '',
                                'position': 'User',
                                'employment_status': 'active',
                                'employment_type': 'full_time',
                                'role': 'user',
                            }
                        )
                        if employee_created:
                            # Try to populate from UserProfile
                            try:
                                if hasattr(instance, 'profile'):
                                    profile = instance.profile
                                    employee.employee_id = profile.employee_id or employee.employee_id
                                    employee.department = profile.department
                                    employee.manager = profile.manager
                                    employee.position = profile.job_title or employee.position
                                    employee.phone = profile.phone
                                    if not employee.hire_date:
                                        from django.utils import timezone
                                        employee.hire_date = timezone.now().date()
                                    employee.save()
                            except Exception as e:
                                print(f"Error copying UserProfile data to Employee for existing user {instance.username}: {e}")
                                employee.save()
                except Employee.DoesNotExist:
                    # Employee profile doesn't exist, create it
                    try:
                        employee, employee_created = Employee.objects.select_for_update().get_or_create(
                            user=instance,
                            defaults={
                                'employee_id': '',
                                'position': 'User',
                                'employment_status': 'active',
                                'employment_type': 'full_time',
                                'role': 'user',
                            }
                        )
                        if employee_created:
                            # Try to populate from UserProfile
                            try:
                                if hasattr(instance, 'profile'):
                                    profile = instance.profile
                                    employee.employee_id = profile.employee_id or employee.employee_id
                                    employee.department = profile.department
                                    employee.manager = profile.manager
                                    employee.position = profile.job_title or employee.position
                                    employee.phone = profile.phone
                                    if not employee.hire_date:
                                        from django.utils import timezone
                                        employee.hire_date = timezone.now().date()
                                    employee.save()
                            except Exception as e:
                                print(f"Error copying UserProfile data to Employee for existing user {instance.username}: {e}")
                                employee.save()
                    except Exception as e:
                        print(f"Error creating employee profile for existing user {instance.username}: {e}")
    except Exception as e:
        # If transaction fails, log but don't crash
        print(f"Transaction failed for employee profile management: {e}")


class UserSession(models.Model):
    """Track user sessions for audit purposes"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.login_time}"

    class Meta:
        ordering = ['-login_time']


class UserActivity(models.Model):
    """Track user activities for audit trail"""
    ACTION_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('export', 'Export'),
        ('import', 'Import'),
        ('scan', 'Network Scan'),
        ('assign', 'Asset Assignment'),
        ('maintenance', 'Maintenance'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    description = models.TextField()
    
    # Related objects
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    
    # Request details
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Additional data
    extra_data = models.JSONField(default=dict, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']
