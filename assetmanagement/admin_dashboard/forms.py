from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from assets.models import (
    Asset, AssetCategory, Manufacturer, AssetModel, 
    Location, Department, MaintenanceRecord
)
from users.models import UserProfile
from crm.models import Employee
from discovery.models import NetworkRange, DiscoveryRule


class UserCreateForm(UserCreationForm):
    """Form for creating new users"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    is_staff = forms.BooleanField(required=False, help_text="Can access admin dashboard")
    is_superuser = forms.BooleanField(required=False, help_text="Has all permissions")
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_superuser')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class UserEditForm(forms.ModelForm):
    """Form for editing existing users"""
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add role field choices from Employee model ROLE_CHOICES
        from crm.models import Employee
        self.fields['role'] = forms.ChoiceField(
            choices=Employee.ROLE_CHOICES,
            required=False,
            widget=forms.Select(attrs={'class': 'form-select'})
        )


class EmployeeForm(forms.ModelForm):
    """Form for editing employee profiles"""
    class Meta:
        model = Employee
        fields = ('employee_id', 'department', 'manager', 'position', 'phone', 'employment_status', 'employment_type', 'role', 'hire_date', 'salary', 'weekly_target', 'is_manager')
        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'manager': forms.Select(attrs={'class': 'form-select'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'employment_status': forms.Select(attrs={'class': 'form-select'}),
            'employment_type': forms.Select(attrs={'class': 'form-select'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'hire_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'weekly_target': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'step': '1'}),
            'is_manager': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AssetForm(forms.ModelForm):
    """Form for creating/editing assets"""
    class Meta:
        model = Asset
        fields = [
            'asset_tag', 'name', 'model', 'category', 'serial_number', 'status',
            'assigned_to', 'assigned_users', 'department', 'location',
            'purchase_date', 'purchase_cost', 'warranty_expires',
            'ip_address', 'mac_address', 'hostname',
            'device_name', 'processor', 'installed_ram', 'device_id',
            'product_id', 'system_type', 'notes'
        ]
        widgets = {
            'asset_tag': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'assigned_users': forms.SelectMultiple(attrs={'class': 'form-select', 'multiple': 'multiple'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.Select(attrs={'class': 'form-select'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'purchase_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'warranty_expires': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ip_address': forms.TextInput(attrs={'class': 'form-control'}),
            'mac_address': forms.TextInput(attrs={'class': 'form-control'}),
            'hostname': forms.TextInput(attrs={'class': 'form-control'}),
            'device_name': forms.TextInput(attrs={'class': 'form-control'}),
            'processor': forms.TextInput(attrs={'class': 'form-control'}),
            'installed_ram': forms.TextInput(attrs={'class': 'form-control'}),
            'device_id': forms.TextInput(attrs={'class': 'form-control'}),
            'product_id': forms.TextInput(attrs={'class': 'form-control'}),
            'system_type': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class AssetCategoryForm(forms.ModelForm):
    """Form for creating/editing asset categories"""
    class Meta:
        model = AssetCategory
        fields = ('name', 'description', 'parent')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
        }


class ManufacturerForm(forms.ModelForm):
    """Form for creating/editing manufacturers"""
    class Meta:
        model = Manufacturer
        fields = ('name', 'website', 'support_email', 'support_phone')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'support_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'support_phone': forms.TextInput(attrs={'class': 'form-control'}),
        }


class AssetModelForm(forms.ModelForm):
    """Form for creating/editing asset models"""
    class Meta:
        model = AssetModel
        fields = ('name', 'manufacturer', 'category', 'model_number', 'description', 'image')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'manufacturer': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'model_number': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }


class LocationForm(forms.ModelForm):
    """Form for creating/editing locations"""
    class Meta:
        model = Location
        fields = ('name', 'address', 'description')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class DepartmentForm(forms.ModelForm):
    """Form for creating/editing departments"""
    class Meta:
        model = Department
        fields = ('name', 'description', 'manager')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'manager': forms.Select(attrs={'class': 'form-select'}),
        }


class NetworkRangeForm(forms.ModelForm):
    """Form for creating/editing network ranges"""
    class Meta:
        model = NetworkRange
        fields = ('name', 'network', 'description', 'is_active', 'scan_frequency')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'network': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '192.168.1.0/24'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'scan_frequency': forms.NumberInput(attrs={'class': 'form-control', 'min': '60'}),
        }


class MaintenanceRecordForm(forms.ModelForm):
    """Form for creating/editing maintenance records"""
    class Meta:
        model = MaintenanceRecord
        fields = [
            'asset', 'maintenance_type', 'status', 'title', 'description',
            'scheduled_date', 'completed_date', 'performed_by', 'cost', 'notes'
        ]
        widgets = {
            'asset': forms.Select(attrs={'class': 'form-select'}),
            'maintenance_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'scheduled_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'completed_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'performed_by': forms.Select(attrs={'class': 'form-select'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class BulkAssetActionForm(forms.Form):
    """Form for bulk actions on assets"""
    ACTION_CHOICES = [
        ('', 'Select Action'),
        ('assign_user', 'Assign to User'),
        ('change_status', 'Change Status'),
        ('change_location', 'Change Location'),
        ('change_department', 'Change Department'),
        ('delete', 'Delete Assets'),
    ]
    
    action = forms.ChoiceField(choices=ACTION_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    assets = forms.CharField(widget=forms.HiddenInput())
    
    # Optional fields for different actions
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        choices=Asset.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )