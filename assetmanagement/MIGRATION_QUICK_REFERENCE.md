# 🚀 Django Migration Quick Reference

## ✅ Check Migration Status

```bash
# Show all migrations and their status
python manage.py showmigrations

# Show migrations for specific app
python manage.py showmigrations assets
```

---

## 🔧 Common Migration Commands

### Create New Migrations
```bash
# Create migrations for all apps
python manage.py makemigrations

# Create migration for specific app
python manage.py makemigrations assets

# Create empty migration (for data migrations)
python manage.py makemigrations --empty assets
```

### Apply Migrations
```bash
# Apply all pending migrations
python manage.py migrate

# Apply migrations for specific app
python manage.py migrate assets

# Apply up to specific migration
python manage.py migrate assets 0003
```

### Fake Migrations (When DB Already Has Changes)
```bash
# Fake a specific migration
python manage.py migrate assets 0004 --fake

# Fake all migrations for an app
python manage.py migrate assets --fake

# Fake initial migrations (useful for existing databases)
python manage.py migrate --fake-initial
```

---

## 🐛 Troubleshooting

### Error: "relation already exists"
```bash
# This means the table/column exists but Django doesn't know about it
# Solution: Fake the migration
python manage.py migrate <app> <migration_number> --fake
```

### Error: "column already exists"
```bash
# Same as above - fake the migration
python manage.py migrate <app> <migration_number> --fake
```

### Check What's in the Database
```bash
# Use our diagnostic scripts
python check_all_migrations.py          # Full analysis
python test_migration_fix.py            # Safe check (no changes)
python check_specific_table.py          # Check specific tables
```

---

## 🔄 Migration Workflow

### Normal Development Workflow
```bash
1. Make model changes in models.py
2. python manage.py makemigrations
3. python manage.py migrate
4. git add <migration_files>
5. git commit -m "Add migration for..."
```

### Deploying to Production
```bash
1. git pull                              # Get latest code
2. python manage.py showmigrations       # Check status
3. python manage.py migrate              # Apply migrations
4. python manage.py collectstatic        # Update static files
5. Restart application server
```

### Fixing Migration State Issues
```bash
1. python check_all_migrations.py        # Diagnose
2. python fix_all_migration_state_direct.py  # Auto-fix
3. python manage.py migrate              # Apply remaining
4. python manage.py showmigrations       # Verify
```

---

## 📋 Useful Scripts in This Directory

| Script | Purpose | Safe? |
|--------|---------|-------|
| `test_migration_fix.py` | Diagnose issues without changes | ✅ Yes |
| `check_all_migrations.py` | Detailed migration analysis | ✅ Yes |
| `check_specific_table.py` | Check if tables exist | ✅ Yes |
| `fix_all_migration_state_direct.py` | Auto-fix migration state | ⚠️ Makes changes |
| `fix_partial_migrations.py` | Fix specific migration | ⚠️ Makes changes |
| `fix_all_until_clean.py` | Iterative fix | ⚠️ Makes changes |

---

## 🎯 Quick Fixes

### "I just pulled code and migrations won't apply"
```bash
python manage.py showmigrations
# If you see unapplied migrations with existing tables:
python manage.py migrate --fake-initial
python manage.py migrate
```

### "I manually changed the database"
```bash
# Don't do this! But if you did:
python check_all_migrations.py
# Follow the recommendations
```

### "I want to rollback a migration"
```bash
# Rollback to previous migration
python manage.py migrate assets 0003

# This will unapply migration 0004 and later
```

### "I want to see what SQL a migration will run"
```bash
python manage.py sqlmigrate assets 0004
```

---

## ⚠️ Important Rules

1. **Never modify the database schema manually** - Always use migrations
2. **Never delete migration files** - They are part of your version history
3. **Never edit applied migrations** - Create a new migration instead
4. **Always commit migration files** - They should be in version control
5. **Test migrations locally first** - Before applying to production

---

## 🆘 Emergency Commands

### Reset All Migrations (DANGEROUS - Development Only!)
```bash
# This will delete all migration history
# DO NOT USE IN PRODUCTION!
python manage.py migrate --fake <app> zero
python manage.py migrate <app>
```

### Check Database Connection
```bash
python manage.py dbshell
# Then in PostgreSQL:
\dt                    # List all tables
\d assets_asset        # Describe table structure
\q                     # Quit
```

---

## 📞 Need Help?

1. Check `MIGRATION_FIX_COMPLETED.md` for the full story of the recent fix
2. Run `python test_migration_fix.py` for safe diagnostics
3. Check Django documentation: https://docs.djangoproject.com/en/stable/topics/migrations/
4. Review migration files in `<app>/migrations/` directory

---

**Last Updated:** January 2025  
**Status:** All migrations applied successfully ✅