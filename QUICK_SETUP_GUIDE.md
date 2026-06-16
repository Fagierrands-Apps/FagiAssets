# Quick Setup Guide - Employee Portal Auto Clock-Out

## ✅ What Was Fixed

1. **Timesheet Template Error** - Fixed the "Invalid filter: 'div'" error
2. **Automatic Clock-Out at 1:30 PM** - Employees are clocked out for lunch and immediately clocked back in
3. **Automatic Clock-Out at 10:00 PM** - All employees still clocked in are automatically clocked out

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Test the Timesheet Fix
```bash
# Start your server
python manage.py runserver

# Open in browser:
# http://127.0.0.1:8000/crm/employee/timesheet/
```

✅ The page should load without errors now!

---

### Step 2: Test Auto Clock-Out Command
```bash
# Test the command
python manage.py auto_clockout --force
```

✅ You should see a summary of clock-outs performed!

---

### Step 3: Setup Automatic Scheduling

#### Option A: PowerShell (Recommended)
```powershell
# Right-click PowerShell and "Run as Administrator"
cd c:\Users\a\Documents\GitHub\fagiassets\assetmanagement
.\setup_auto_clockout.ps1
```

#### Option B: Batch File
```cmd
# Right-click Command Prompt and "Run as Administrator"
cd c:\Users\a\Documents\GitHub\fagiassets\assetmanagement
setup_auto_clockout.bat
```

✅ Two scheduled tasks will be created:
- "CRM Auto Clock-Out Lunch" - Runs daily at 1:30 PM
- "CRM Auto Clock-Out End of Day" - Runs daily at 10:00 PM

---

### Step 4: Verify Setup
```powershell
# Check if tasks were created
Get-ScheduledTask -TaskName "CRM Auto Clock-Out*"
```

You should see both tasks listed!

---

## 📋 How It Works

### 1:30 PM - Lunch Break
```
Employee clocked in → Auto clock-out at 1:30 PM → Auto clock-in at 1:30:01 PM → Continue working
```

**What happens:**
- System finds all employees currently clocked in
- Creates a "punch_out" entry at 1:30 PM
- Immediately creates a "punch_in" entry at 1:30:01 PM
- Employee continues working without interruption
- Lunch break is properly tracked

### 10:00 PM - End of Day
```
Employee clocked in → Auto clock-out at 10:00 PM → Must manually clock in next day
```

**What happens:**
- System finds all employees still clocked in
- Creates a "punch_out" entry at 10:00 PM
- Work session is marked as complete
- Employee must clock in manually the next day

---

## 🧪 Testing

### Test Lunch Clock-Out
```bash
python manage.py auto_clockout --time 13:30
```

### Test End-of-Day Clock-Out
```bash
python manage.py auto_clockout --time 22:00
```

### Run Full Test Suite
```bash
python test_auto_clockout.py
```

---

## 📊 Viewing Results

### Check Time Entries
1. Go to: http://127.0.0.1:8000/admin/crm/timeentry/
2. Look for entries with:
   - Location: "System Auto Clock-Out"
   - Notes: "Automatic clock-out for lunch break" or "Automatic end-of-day clock-out"

### Check Work Sessions
1. Go to: http://127.0.0.1:8000/admin/crm/worksession/
2. Verify hours are calculated correctly
3. Check that sessions are marked as complete

### Check Employee Timesheet
1. Go to: http://127.0.0.1:8000/crm/employee/timesheet/
2. View your time entries and work sessions
3. Verify average hours per day displays correctly

---

## 🔧 Management Commands

### View Task Status
```powershell
# List all auto clock-out tasks
Get-ScheduledTask -TaskName "CRM Auto Clock-Out*"

# View task details
Get-ScheduledTaskInfo -TaskName "CRM Auto Clock-Out Lunch"
```

### Remove Tasks (If Needed)
```powershell
# Remove lunch task
Unregister-ScheduledTask -TaskName "CRM Auto Clock-Out Lunch" -Confirm:$false

# Remove end-of-day task
Unregister-ScheduledTask -TaskName "CRM Auto Clock-Out End of Day" -Confirm:$false
```

### Re-run Setup
```powershell
# Just run the setup script again
.\setup_auto_clockout.ps1
```

---

## ❓ Troubleshooting

### "Access Denied" when creating tasks
**Solution**: Run PowerShell or Command Prompt as Administrator

### Tasks not running
**Solution**: 
1. Check task history in Task Scheduler
2. Verify Python is in system PATH
3. Test command manually first

### Employees not being clocked out
**Solution**:
1. Verify employees are actually clocked in
2. Check employee status is 'active'
3. Run with `--force` flag to test

### Timesheet still shows error
**Solution**:
1. Restart Django server
2. Clear browser cache
3. Check that changes were saved

---

## 📚 Documentation

For more detailed information, see:
- `AUTO_CLOCKOUT_SYSTEM.md` - Complete auto clock-out documentation
- `TIMESHEET_FIX.md` - Timesheet template fix details
- `EMPLOYEE_PORTAL_FIXES.md` - Comprehensive implementation guide

---

## ✅ Checklist

- [ ] Timesheet loads without errors
- [ ] Auto clock-out command works
- [ ] Scheduled tasks created
- [ ] Tested lunch clock-out
- [ ] Tested end-of-day clock-out
- [ ] Verified time entries in admin
- [ ] Verified work sessions in admin
- [ ] Checked employee timesheet view

---

## 🎉 You're Done!

The system will now automatically:
- ✅ Clock out employees at 1:30 PM for lunch (and clock them back in)
- ✅ Clock out employees at 10:00 PM if still clocked in
- ✅ Calculate work hours accurately
- ✅ Track lunch breaks properly

**No more manual clock-out reminders needed!**