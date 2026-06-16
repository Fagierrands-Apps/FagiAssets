# Timesheet Template Fix

## Problem
When viewing the employee timesheet at `/crm/employee/timesheet/`, the following error occurred:

```
TemplateSyntaxError at /crm/employee/timesheet/
Invalid filter: 'div'
```

**Location**: Line 109 in `employee_timesheet.html`

**Cause**: Django doesn't have a built-in `div` filter for division operations in templates.

## Solution

### 1. Created Custom `div` Filter
Added a custom template filter in `crm/templatetags/crm_tags.py`:

```python
@register.filter
def div(value, arg):
    """Divide the value by the argument"""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError, TypeError):
        return 0
```

### 2. Updated View to Calculate Average
Modified `employee_timesheet` view in `crm/views.py` to calculate the average hours per day:

```python
avg_hours_per_day = total_hours / total_days if total_days > 0 else 0
```

Added to context:
```python
'avg_hours_per_day': avg_hours_per_day,
```

### 3. Updated Template
Changed the template to use the pre-calculated value instead of the `div` filter:

**Before:**
```django
{{ total_hours|floatformat:1|div:total_days|floatformat:1 }}
```

**After:**
```django
{{ avg_hours_per_day|floatformat:1 }}
```

## Benefits

1. **Better Performance**: Calculation done once in the view instead of in the template
2. **Cleaner Code**: Logic in the view where it belongs
3. **Error Handling**: Proper division by zero handling
4. **Maintainability**: Easier to test and modify

## Files Modified

1. `crm/templatetags/crm_tags.py` - Added `div` filter (as backup)
2. `crm/views.py` - Added `avg_hours_per_day` calculation
3. `templates/crm/employee_timesheet.html` - Updated to use calculated value

## Testing

1. Navigate to: http://127.0.0.1:8000/crm/employee/timesheet/
2. Verify the "Avg Hours/Day" displays correctly
3. Test with different date ranges
4. Verify no template errors occur

## Result

✅ The timesheet page now loads without errors and displays the average hours per day correctly.