# Option B Setup - Use Old Supabase as Backup

## ✅ What We're Doing
Using OLD Supabase as temporary backup since it works with IPv4.

---

## 📋 Files to Update

### 1. Upload Updated settings.py
Replace `assetmanagement/assetmanager/settings.py` with the updated version.

**Changes:**
- `backup` now points to OLD Supabase (works with IPv4)
- `new_supabase` kept for future when IPv6 is available

---

## 🚀 Setup Steps

### Step 1: Upload Updated Files
Via cPanel File Manager:
1. Upload **updated settings.py** → `assetmanagement/assetmanager/`
2. Upload **setup_backup_old_supabase.py** → root directory

### Step 2: Restart Application
In cPanel Python App:
1. Click **Restart**
2. Wait 30 seconds

### Step 3: Run Initial Backup Sync
Execute via Python App:
```
setup_backup_old_supabase.py
```

This will sync all your cPanel data to OLD Supabase.

---

## 🔄 Setup Automatic Backup (Cron Job)

In cPanel **Cron Jobs**, add:

**Every 6 hours:**
```bash
0 */6 * * * cd ~/fagiassets.fagitone.com/fagierrands-Assets/assetmanagement && source ~/virtualenv/fagiassets.fagitone.com/fagierrands-Assets/3.12/bin/activate && python manage.py sync_to_backup >> ~/logs/backup_sync.log 2>&1
```

**Or Daily at 2 AM:**
```bash
0 2 * * * cd ~/fagiassets.fagitone.com/fagierrands-Assets/assetmanagement && source ~/virtualenv/fagiassets.fagitone.com/fagierrands-Assets/3.12/bin/activate && python manage.py sync_to_backup >> ~/logs/backup_sync.log 2>&1
```

---

## 📊 Current Architecture

```
┌─────────────────────┐
│   Django App        │
│   (cPanel)          │
└──────┬──────────────┘
       │
       ├─────────────────────┐
       │                     │
       ▼                     ▼
┌──────────────┐    ┌────────────────┐
│ PRIMARY DB   │───▶│  BACKUP DB     │
│ (cPanel      │    │  (Old Supabase)│
│  PostgreSQL) │    │  IPv4 - Works! │
└──────────────┘    └────────────────┘
   localhost         aws-0-ap...
   
   127,851 records   Auto-sync every 6h
   13 users          
   71 assets         
```

---

## 🎯 Benefits

✅ **Primary on cPanel** - Fast, local, under your control
✅ **Backup on Supabase** - Cloud backup, automatic
✅ **Works now** - No IPv6 required
✅ **Keep new Supabase** - Switch to it when IPv6 ready

---

## 🔮 Future Migration

When IPv6 is available on your server:

1. Switch `backup` to point to new Supabase
2. Run one final sync
3. Delete old Supabase project

**Simple config change - no data migration needed!**

---

## ✅ Final Checklist

- [ ] Upload updated settings.py
- [ ] Restart Python app
- [ ] Run setup_backup_old_supabase.py
- [ ] Verify sync worked (users/assets match)
- [ ] Setup cron job for automatic backup
- [ ] Test application works normally

---

## 🆘 Quick Verification

After setup, verify with this script `verify_setup.py`:

```python
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
django.setup()

from django.contrib.auth.models import User
from assets.models import Asset

print("PRIMARY (cPanel):")
print(f"  Users: {User.objects.using('default').count()}")
print(f"  Assets: {Asset.objects.using('default').count()}")

print("\nBACKUP (Supabase):")
print(f"  Users: {User.objects.using('backup').count()}")
print(f"  Assets: {Asset.objects.using('backup').count()}")
```

Both should show: **13 users, 71 assets**

---

Ready to proceed! Upload the files and let's get your backup working. 🚀
