# Login Redirect Fix - Role-Based Authentication

## Problem
Users with non-admin roles (call_center, sales, user) were being redirected to `/assets/` after login, which then redirected them back to login, causing a redirect loop. They should be redirected directly to the employee portal at `/crm/employee/`.

## Solution Implemented

### 1. Custom Login View (`users/views.py`)
Created `RoleBasedLoginView` class that extends Django's `LoginView` to implement role-based redirects:

**Redirect Logic:**
- **Superusers**: → `/assets/` (asset management dashboard)
- **Admin role employees**: → `/assets/` (asset management dashboard)
- **Non-admin employees** (call_center, sales, user): → `/crm/employee/` (employee portal)
- **Staff without employee profile**: → `/assets/` (fallback)
- **Regular users without employee profile**: → `/assets/` (fallback - they need admin to create profile)

### 2. URL Configuration Update (`assetmanager/urls.py`)
Updated the login URL to use the custom `RoleBasedLoginView` instead of Django's default `LoginView`:

```python
# Before
path('login/', auth_views.LoginView.as_view(), name='login'),

# After
path('login/', RoleBasedLoginView.as_view(), name='login'),
```

### 3. Employee Dashboard Access Fix (`crm/views.py`)
Updated the `employee_dashboard` view decorator to include 'sales' role:

```python
# Before
@role_required(['user', 'call_center', 'admin'])

# After
@role_required(['user', 'call_center', 'sales', 'admin'])
```

## How It Works

1. User logs in at `/login/`
2. `RoleBasedLoginView.get_success_url()` is called after successful authentication
3. The method checks:
   - Is user a superuser? → redirect to `/assets/`
   - Does user have an employee profile?
     - Yes: Check role
       - Admin role → `/assets/`
       - Other roles → `/crm/employee/`
     - No: Check if staff → `/assets/` (fallback)
4. User is redirected to the appropriate dashboard

## Testing

To test the fix:

1. **Admin User Login:**
   ```
   Username: admin
   Expected: Redirected to /assets/
   ```

2. **Call Center User Login:**
   ```
   Username: callcenter_test
   Expected: Redirected to /crm/employee/
   ```

3. **Sales User Login:**
   ```
   Username: sales_user
   Expected: Redirected to /crm/employee/
   ```

4. **Regular User Login:**
   ```
   Username: regular_user
   Expected: Redirected to /crm/employee/
   ```

## Files Modified

1. `assetmanagement/users/views.py` - Added `RoleBasedLoginView` class
2. `assetmanagement/assetmanager/urls.py` - Updated login URL to use custom view
3. `assetmanagement/crm/views.py` - Added 'sales' role to employee_dashboard decorator

## Benefits

- ✅ No more redirect loops for non-admin users
- ✅ Users land on the appropriate dashboard based on their role
- ✅ Maintains security with role-based access control
- ✅ Respects the `?next=` parameter when appropriate
- ✅ Graceful fallback for users without employee profiles