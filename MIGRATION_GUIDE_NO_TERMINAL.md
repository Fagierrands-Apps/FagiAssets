# Database Migration & Sync Setup (No Terminal Required)

## 📦 Files to Upload to cPanel

Upload these files via cPanel File Manager:

1. **setup_sync_system.py** → Root directory
2. **migrate_databases.py** → Root directory  
3. **migrate_web_view.py** → Root directory
4. **Updated settings.py** → assetmanagement/assetmanager/
5. **.env.cpanel.updated** → Rename to `.env` in root

---

## 🚀 Step-by-Step Setup (No Terminal)

### Method 1: Using Python App Interface

#### Step 1: Upload Files
1. Open cPanel File Manager
2. Navigate to `~/fagiassets.fagitone.com/fagierrands-Assets/`
3. Upload all files from your local computer
4. Rename `.env.cpanel.updated` to `.env`

#### Step 2: Run Setup Script
1. In cPanel, go to **Setup Python App**
2. Click on your application
3. Click **Run Python Script**
4. Select `setup_sync_system.py`
5. Click **Execute**

This creates all necessary directories and management commands.

#### Step 3: Update Database Settings
1. File Manager → Edit `assetmanagement/assetmanager/settings.py`
2. Replace DATABASES section with the triple-database config
3. Save

#### Step 4: Run Migration
1. Go back to **Python App**
2. Click **Run Python Script**
3. Select `migrate_databases.py`
4. Click **Execute**

This will:
- Test all database connections
- Copy data from old Supabase to cPanel
- Run Django migrations
- Initial sync to new Supabase backup

---

### Method 2: Using Web Interface

#### Setup URL Pattern
1. Edit `assetmanagement/assetmanager/urls.py`
2. Add this import at top:
```python
from migrate_web_view import migrate_databases_view
```

3. Add this to urlpatterns:
```python
path('admin/migrate-db/', migrate_databases_view, name='migrate_db'),
```

#### Access via Browser
1. Login as admin
2. Go to: `https://fagiassets.fagitone.com/admin/migrate-db/`
3. Click "Start Migration" button
4. Watch progress in browser

---

## 🔄 After Migration Complete

### Test Everything
1. Browse your application
2. Login as admin
3. Check all data is present
4. Create a test asset
5. Verify it saves correctly

### Verify Sync Command
Via Python App interface, run:
```python
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
django.setup()
from django.core.management import call_command
call_command('sync_to_backup', '--dry-run')
```

### Setup Automatic Backup (Cron Job)

Since you can't use terminal, use cPanel Cron Jobs interface:

1. Go to **Cron Jobs** in cPanel
2. Select: "Common Settings" → "Twice per day"
3. Or custom: `0 */6 * * *` (every 6 hours)
4. Command:
```bash
cd ~/fagiassets.fagitone.com/fagierrands-Assets/assetmanagement && source ~/virtualenv/fagiassets.fagitone.com/fagierrands-Assets/3.12/bin/activate && python manage.py sync_to_backup >> ~/logs/db_sync.log 2>&1
```

---

## 📊 Verify Sync is Working

Create a simple Python script `check_sync.py`:

```python
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
django.setup()

from django.contrib.auth.models import User
from assets.models import Asset

print("=== Database Record Counts ===")
print(f"Primary (cPanel):")
print(f"  Users: {User.objects.using('default').count()}")
print(f"  Assets: {Asset.objects.using('default').count()}")

print(f"\nBackup (Supabase):")
print(f"  Users: {User.objects.using('backup').count()}")
print(f"  Assets: {Asset.objects.using('backup').count()}")

print("\n✓ Check complete")
```

Run via Python App interface.

---

## 🗑️ Delete Old Supabase (After 1 Week)

Once everything works for 1 week:

1. Edit `settings.py`
2. Remove `'old_supabase'` from DATABASES
3. Go to https://supabase.com
4. Delete project `dxesmzogjpxswxhsomgf`

---

## 🆘 Troubleshooting

### "Connection refused" error
- Check database credentials in `.env`
- Verify cPanel PostgreSQL is running
- Check database exists: `distinc3_crm`

### "Module not found" error
- Ensure `setup_sync_system.py` ran successfully
- Check directories exist: `assets/management/commands/`

### Sync not working
- Check cron job logs: `~/logs/db_sync.log`
- Run manual sync via Python App interface

---

## 📁 Final File Structure

```
~/fagiassets.fagitone.com/fagierrands-Assets/
├── .env                          # Database credentials
├── setup_sync_system.py          # Setup script
├── migrate_databases.py          # Migration script
├── check_sync.py                 # Verification script
└── assetmanagement/
    ├── assetmanager/
    │   └── settings.py           # Triple database config
    └── assets/
        └── management/
            └── commands/
                └── sync_to_backup.py  # Sync command
```

---

## ✅ Success Checklist

- [ ] All files uploaded to cPanel
- [ ] `.env` file updated with correct credentials
- [ ] `setup_sync_system.py` executed
- [ ] `migrate_databases.py` completed successfully
- [ ] Application loads and works normally
- [ ] Test data appears in both databases
- [ ] Cron job configured for automatic sync
- [ ] Sync logs show successful runs

---

Ready to proceed! Start with uploading the files. 🚀
