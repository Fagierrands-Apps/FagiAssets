#!/usr/bin/env python
import os
import sys
import django

# Setup Django first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
sys.path.insert(0, 'assetmanagement')
django.setup()

from crm.models import Employee
from django.db import transaction

def fix_employee_ids():
    """Fix employee IDs for employees that don't have them"""
    print("Checking employees without employee_id...")

    employees_without_id = Employee.objects.filter(employee_id__in=['', None])

    if not employees_without_id.exists():
        print("All employees already have employee_id assigned.")
        return

    print(f"Found {employees_without_id.count()} employees without employee_id")

    # Generate unique employee IDs
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

        for employee in employees_without_id:
            # Generate new employee ID
            employee_id = f"{prefix}{next_number:03d}"
            employee.employee_id = employee_id
            employee.save()
            print(f"Assigned employee_id {employee_id} to {employee.user.get_full_name()}")
            next_number += 1

    print("Employee ID assignment completed!")

if __name__ == '__main__':
    fix_employee_ids()
