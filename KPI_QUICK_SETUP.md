# Quick Setup Guide: Automatic KPI Calculation

## 🚀 5-Minute Setup

### Step 1: Run Setup Script (Choose One)

#### Option A: PowerShell (Recommended)
```powershell
# Open PowerShell as Administrator
cd c:\Users\a\Documents\GitHub\fagiassets\assetmanagement
.\setup_kpi_calculation.ps1
```

#### Option B: Batch File
```
Right-click setup_kpi_calculation.bat → Run as Administrator
```

### Step 2: Test the System
```bash
# Run manual calculation to test
python manage.py calculate_kpis --force
```

### Step 3: View Results
```
Visit: http://localhost:8000/crm/employee/kpis/
```

## ✅ That's It!

KPIs will now be automatically calculated daily at 11:30 PM.

## 📊 What Gets Calculated

- ✅ Tasks Completed
- ✅ Calls Made
- ✅ Emails Sent
- ✅ Meetings Attended
- ✅ Leads Converted
- ✅ Sales Count
- ✅ Revenue Generated
- ✅ Response Time
- ✅ Attendance Rate
- ✅ Customer Satisfaction

## 🔧 Quick Commands

### Run Calculation Now
```bash
python manage.py calculate_kpis
```

### Force Recalculation
```bash
python manage.py calculate_kpis --force
```

### Calculate Specific Month
```bash
python manage.py calculate_kpis --month 2024-01
```

### Calculate All Historical Data
```bash
python manage.py calculate_kpis --all-months --force
```

## 🎯 Key Features

- **Fully Automatic**: No manual input needed
- **Always Accurate**: Based on real system data
- **Daily Updates**: Runs automatically every night
- **Zero Maintenance**: Set it and forget it

## 📱 Where to View KPIs

### Employees
```
Portal → Performance KPIs
http://localhost:8000/crm/employee/kpis/
```

### Admins
```
Admin → CRM → Employee KPIs
http://localhost:8000/admin/crm/employeekpi/
```

## ❓ Troubleshooting

### No KPIs showing?
```bash
# Run manual calculation
python manage.py calculate_kpis --force
```

### Task not running?
```powershell
# Check task status
Get-ScheduledTask -TaskName "CRM Auto Calculate KPIs"

# Run manually
Start-ScheduledTask -TaskName "CRM Auto Calculate KPIs"
```

## 📚 Full Documentation

For detailed information, see: `AUTOMATIC_KPI_SYSTEM.md`

---

**Need Help?** Check the full documentation or contact your system administrator.