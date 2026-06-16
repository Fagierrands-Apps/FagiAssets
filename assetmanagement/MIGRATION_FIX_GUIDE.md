# Django Migration State Fix Guide

## Problem

You're seeing this error:
```
django.db.utils.ProgrammingError: relation "django_admin_log" already exists
```

This happens when:
- Database tables already exist in PostgreSQL
- Django's migration tracking system doesn't know about them
- Django tries to create tables that already exist

## Solution

You have **3 scripts** to fix this issue, from simplest to most comprehensive:

---

## Option 1: Simple Fix (RECOMMENDED - Try This First)

**Script:** `fix_migration_simple.py`

This uses Django's built-in `--fake-initial` flag which automatically detects existing tables.

### Usage:
```bash
python fix_migration_simple.py
```

Or directly:
```bash
python manage.py migrate --fake-initial
```

**What it does:**
- Checks if tables exist
- Marks initial migrations as applied if tables exist
- Skips creating tables that already exist

---

## Option 2: Comprehensive Fix (If Option 1 Fails)

**Script:** `fix_migrations_comprehensive.py`

Interactive tool with multiple methods and detailed diagnostics.

### Usage:
```bash
python fix_migrations_comprehensive.py
```

**Features:**
- Shows database state
- Lists all apps and tables
- Provides 3 different fixing methods
- Shows migration status

**Methods available:**
1. **Fake Initial** - Same as Option 1 but with more feedback
2. **Fake All** - Marks ALL migrations as applied (use if Method 1 fails)
3. **Fake Per App** - Fake migrations for specific apps only

---

## Option 3: Advanced Fix

**Script:** `fix_migration_state.py`

Provides detailed table checking and uses `--fake` flag.

### Usage:
```bash
python fix_migration_state.py
```

---

## Quick Command Reference

### Check Migration Status
```bash
python manage.py showmigrations
```

Shows which migrations are applied (marked with [X]) and which aren't.

### Fake Initial Migrations (Direct Command)
```bash
python manage.py migrate --fake-initial
```

### Fake All Migrations (Direct Command)
```bash
python manage.py migrate --fake
```

### Fake Specific App (Direct Command)
```bash
python manage.py migrate <app_name> --fake
```

Example:
```bash
python manage.py migrate admin --fake
python manage.py migrate auth --fake
python manage.py migrate assets --fake
```

---

## Step-by-Step Fix Process

### Step 1: Check Current State
```bash
python manage.py showmigrations
```

### Step 2: Try Simple Fix
```bash
python manage.py migrate --fake-initial
```

### Step 3: Verify
```bash
python manage.py showmigrations
```

All migrations should now show [X] (applied).

### Step 4: Test
```bash
python manage.py makemigrations
python manage.py migrate
```

Should show "No changes detected" or apply any new migrations.

---

## Understanding the Flags

### `--fake-initial`
- **Safe to use**
- Only fakes initial migrations if tables exist
- Recommended for most cases
- Won't fake migrations if tables don't exist

### `--fake`
- **Use with caution**
- Marks migrations as applied WITHOUT checking if tables exist
- Use when you're 100% sure tables exist
- Can cause issues if tables don't actually exist

---

## Common Scenarios

### Scenario 1: Fresh Database with Existing Tables
**Cause:** Database was created manually or from a dump

**Solution:**
```bash
python manage.py migrate --fake-initial
```

### Scenario 2: Migration Table Missing
**Cause:** `django_migrations` table doesn't exist

**Solution:**
```bash
# Create the migrations table first
python manage.py migrate --run-syncdb
# Then fake the migrations
python manage.py migrate --fake-initial
```

### Scenario 3: Partial Migration State (Column/Table Already Exists)
**Cause:** Specific columns or tables exist but migration not marked as applied

**Error Example:**
```
column "device_id" of relation "assets_asset" already exists
```

**Solution:**
```bash
# Check which migration is failing
python manage.py showmigrations assets

# Fake the specific migration (e.g., 0002)
python manage.py migrate assets 0002 --fake

# Continue with remaining migrations
python manage.py migrate
```

**Alternative - Fake all migrations for the app:**
```bash
python manage.py migrate assets --fake
python manage.py migrate
```

**Or use the fix script:**
```bash
python fix_partial_migrations.py
```

### Scenario 4: Multiple Apps with Partial Migrations
**Cause:** Several apps have columns/tables that exist but migrations not marked

**Solution:**
```bash
# Use the comprehensive fix script
python fix_all_partial_migrations.py
```

**Or manually fake each app:**
```bash
python manage.py migrate admin --fake
python manage.py migrate auth --fake
python manage.py migrate assets --fake
# ... etc for each app
python manage.py migrate
```

---

## Troubleshooting

### Error: "No such table: django_migrations"
**Solution:**
```bash
python manage.py migrate --run-syncdb
```

### Error: "relation already exists" persists
**Solution:**
```bash
# Fake all migrations
python manage.py migrate --fake
```

### Error: Can't connect to database
**Solution:**
- Check database credentials in `settings.py`
- Ensure PostgreSQL is running
- Check network connectivity
- Verify SSL settings

---

## Prevention

To avoid this issue in the future:

1. **Always use migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Don't create tables manually** in the database

3. **When restoring from backup:**
   ```bash
   # After restoring database
   python manage.py migrate --fake-initial
   ```

4. **Keep migration files in version control**

---

## For Production Deployment

When deploying to production with existing data:

```bash
# 1. Backup database first!
# 2. Pull latest code
# 3. Fake initial migrations
python manage.py migrate --fake-initial
# 4. Apply any new migrations
python manage.py migrate
# 5. Collect static files
python manage.py collectstatic --noinput
```

---

## Need Help?

If none of these solutions work:

1. Check the error message carefully
2. Run: `python fix_migrations_comprehensive.py` for detailed diagnostics
3. Check database connection settings
4. Verify all tables exist in the database
5. Check PostgreSQL logs for more details

---

## Summary

**Quick Fix (Most Common):**
```bash
python manage.py migrate --fake-initial
```

**If that doesn't work:**
```bash
python fix_migrations_comprehensive.py
```

**Then verify:**
```bash
python manage.py showmigrations
python manage.py makemigrations
python manage.py migrate
```

Done! Your migration state should now be synchronized with your database.