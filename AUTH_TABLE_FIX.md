# Auth Table Fix - Missing auth_user_user_permissions

## Problem

The Django admin panel was throwing a `ProgrammingError` when trying to access user edit pages:

```
ProgrammingError at /admin/auth/user/21/change/
relation "auth_user_user_permissions" does not exist
LINE 1: ...ion"."codename" FROM "auth_permission" INNER JOIN "auth_user...
```

## Root Cause

The database had incomplete Django auth migrations. Only `auth.0001_initial` was applied, but Django 4.2.7 requires migrations up to `auth.0012_alter_user_first_name_max_length`.

The missing table `auth_user_user_permissions` is created in one of the later auth migrations and is essential for Django's permission system.

### Database State Before Fix

- ✅ `auth_user` table existed
- ✅ `auth_group` table existed  
- ✅ `auth_permission` table existed
- ✅ `auth_group_permissions` table existed
- ❌ `auth_user_user_permissions` table **MISSING**
- ❌ `auth_user_groups` table **MISSING**

### Migration State Before Fix

Only 2 migrations were applied:
- `auth.0001_initial`
- `contenttypes.0001_initial`

## Solution

Created the missing `auth_user_user_permissions` table manually and updated migration records.

### What Was Fixed

1. **Created missing table:**
   ```sql
   CREATE TABLE auth_user_user_permissions (
       id SERIAL PRIMARY KEY,
       user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
       permission_id INTEGER NOT NULL REFERENCES auth_permission(id) ON DELETE CASCADE,
       UNIQUE (user_id, permission_id)
   );
   ```

2. **Added indexes for performance:**
   ```sql
   CREATE INDEX auth_user_user_permissions_user_id_idx ON auth_user_user_permissions(user_id);
   CREATE INDEX auth_user_user_permissions_permission_id_idx ON auth_user_user_permissions(permission_id);
   ```

3. **Updated migration records** to reflect all auth migrations:
   - `auth.0002_alter_permission_name_max_length`
   - `auth.0003_alter_user_email_max_length`
   - `auth.0004_alter_user_username_opts`
   - `auth.0005_alter_user_last_login_null`
   - `auth.0006_require_contenttypes_0002`
   - `auth.0007_alter_validators_add_error_messages`
   - `auth.0008_alter_user_username_max_length`
   - `auth.0009_alter_user_last_name_max_length`
   - `auth.0010_alter_group_name_max_length`
   - `auth.0011_update_proxy_permissions`
   - `auth.0012_alter_user_first_name_max_length`
   - `contenttypes.0002_remove_content_type_name`

## Scripts Used

### 1. `fix_missing_auth_tables.py`
Main fix script that creates the missing table and updates migration records.

**Usage:**
```bash
python fix_missing_auth_tables.py
```

### 2. `verify_auth_fix.py`
Verification script to confirm the fix worked.

**Usage:**
```bash
python verify_auth_fix.py
```

### 3. `complete_auth_fix.py`
Adds the missing contenttypes migration to prevent warnings.

**Usage:**
```bash
python complete_auth_fix.py
```

### 4. Updated `restore_auth_migrations.py`
Enhanced version that now also creates missing tables, not just migration records.

## Verification

After running the fix, the following query now works correctly:

```sql
SELECT COUNT(*) 
FROM auth_permission 
INNER JOIN auth_user_user_permissions 
ON auth_permission.id = auth_user_user_permissions.permission_id
```

## Result

✅ **The admin panel now works correctly!**

You can now access user edit pages without errors:
- https://fagiassets.onrender.com/admin/auth/user/21/change/
- All Django admin user management features are functional

## Prevention

To prevent this issue in the future:

1. Always run `python manage.py migrate` after deploying
2. Check migration status with `python manage.py showmigrations`
3. Ensure all Django core app migrations are applied before custom app migrations
4. Use the updated `restore_auth_migrations.py` script if migrations need to be restored

## Technical Details

### Table Structure

```
auth_user_user_permissions
├── id (SERIAL PRIMARY KEY)
├── user_id (INTEGER, FK to auth_user.id)
├── permission_id (INTEGER, FK to auth_permission.id)
└── UNIQUE constraint on (user_id, permission_id)

Indexes:
- auth_user_user_permissions_user_id_idx
- auth_user_user_permissions_permission_id_idx
```

### Why This Table Is Important

The `auth_user_user_permissions` table is a many-to-many relationship table that:
- Links users to their individual permissions
- Is separate from group permissions (stored in `auth_user_groups`)
- Is required by Django's admin panel to display and manage user permissions
- Is used by Django's permission checking system (`user.has_perm()`)

## Related Files

- `/assetmanagement/assetmanager/settings.py` - Django settings
- `/fix_missing_auth_tables.py` - Main fix script
- `/verify_auth_fix.py` - Verification script
- `/complete_auth_fix.py` - Contenttypes migration fix
- `/restore_auth_migrations.py` - Updated migration restore script
- `/diagnose_db.py` - Database diagnostic tool