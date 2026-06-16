import re

# Read the file
with open('assetmanagement/admin_dashboard/forms.py', 'r') as f:
    content = f.read()

# Add Employee import
content = re.sub(
    r'from users\.models import UserProfile\nfrom discovery\.models import NetworkRange, DiscoveryRule',
    'from users.models import UserProfile\nfrom crm.models import Employee\nfrom discovery.models import NetworkRange, DiscoveryRule',
    content
)

# Replace UserProfileForm with EmployeeForm
content = re.sub(
    r'class UserProfileForm\(forms\.ModelForm\):\s*"""Form for editing user profiles"""\s*class Meta:\s*model = UserProfile\s*fields = \([^)]+\)\s*widgets = \{[^}]+\}',
    '''class EmployeeForm(forms.ModelForm):
    """Form for editing employee profiles"""
    class Meta:
        model = Employee
        fields = ('employee_id', 'department', 'manager', 'position', 'phone', 'employment_status', 'employment_type', 'role', 'hire_date', 'salary', 'is_manager')
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
            'is_manager': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }''',
    content,
    flags=re.DOTALL
)

# Write back
with open('assetmanagement/admin_dashboard/forms.py', 'w') as f:
    f.write(content)

print('Forms updated successfully')
