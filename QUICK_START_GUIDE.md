# 🚀 Activity Monitoring System - Quick Start Guide

## ⚡ 5-Minute Setup

Your activity monitoring system is **already installed and running**! Here's how to use it:

---

## 👤 For Employees

### Step 1: Login
```
URL: http://localhost:8000/crm/employee/login/
```

### Step 2: Punch In
- Click the "Punch In" button on your dashboard
- **Important**: Activity tracking only works when you're punched in!

### Step 3: Work Normally
- The system automatically tracks your activity
- No action needed from you!

### Step 4: Check Console (Optional)
- Press `F12` to open browser console
- You'll see: `"Activity tracker initialized successfully"`
- Every 30 seconds: `"Sending X activities to server..."`

### Step 5: Idle Alerts
- After 5 minutes of inactivity, you'll see an alert
- You can provide a reason for being idle (optional)

### Step 6: Punch Out
- Click "Punch Out" when done
- Your productivity metrics are automatically calculated

---

## 👔 For Managers

### View Team Productivity
```
URL: http://localhost:8000/crm/productivity/
```

### Dashboard Features:
- **Real-time status** of all employees (Active/Idle/Offline)
- **Productivity scores** (0-100 scale)
- **Time breakdown** (Productive vs Idle hours)
- **Activity counts** (Mouse, keyboard, clicks)
- **Date filters** (Today, Yesterday, Week, Month)
- **Auto-refresh** every 30 seconds

### Quick Actions:
1. Click "Today" to see current day metrics
2. Click "Week" for 7-day overview
3. Click "Month" for 30-day trends
4. Watch status badges for real-time monitoring

---

## 🔧 For Administrators

### Access Admin Panel
```
URL: http://localhost:8000/admin/
```

### Key Admin Sections:

#### 1. Monitoring Settings
**Path**: CRM > Monitoring Settings

**What you can do**:
- Set idle threshold per employee (default: 5 minutes)
- Enable/disable monitoring
- Toggle idle alerts
- Adjust heartbeat interval

**Quick Edit**:
1. Click on employee name
2. Change "Idle threshold" (in seconds)
3. Save

---

#### 2. Activity Logs
**Path**: CRM > Activity Logs

**What you can see**:
- All user interactions
- Timestamps
- Page URLs
- Activity types

**Filters**:
- By employee
- By date
- By activity type

---

#### 3. Idle Periods
**Path**: CRM > Idle Periods

**What you can see**:
- When employees were idle
- Duration of idle time
- Employee-provided reasons

**Actions**:
- Review idle explanations
- Identify patterns
- Adjust thresholds if needed

---

#### 4. Activity Sessions
**Path**: CRM > Activity Sessions

**What you can see**:
- Productivity scores
- Active vs idle time
- Event counts
- Session summaries

**Actions**:
- Recalculate productivity scores
- Export data
- Analyze trends

---

#### 5. Work Sessions
**Path**: CRM > Work Sessions

**New Fields**:
- Productive Hours
- Idle Hours

**What changed**:
- Now shows productivity breakdown
- Idle time is automatically calculated
- Total hours = Productive + Idle

---

## 🛠️ Management Commands

### Initialize Settings for New Employees
```bash
python manage.py init_monitoring_settings
```

### Reset All Settings
```bash
python manage.py init_monitoring_settings --reset
```

### Custom Thresholds
```bash
python manage.py init_monitoring_settings --idle-threshold 10 --extended-idle-threshold 30
```

### Run Verification Test
```bash
cd assetmanagement
python test_activity_monitoring.py
```

---

## 📊 Understanding the Metrics

### Productivity Score (0-100)
- **90-100**: Excellent - Highly engaged
- **70-89**: Good - Consistently active
- **50-69**: Fair - Moderate activity
- **30-49**: Low - Frequent idle periods
- **0-29**: Very Low - Minimal activity

### Status Indicators
- 🟢 **Active**: Currently working and interacting
- 🟡 **Idle**: No activity for 5+ minutes
- 🔴 **Offline**: Not punched in
- ⚪ **No Activity**: Punched in but no data yet

### Activity Types
- **Mouse Move**: Cursor movement
- **Click**: Mouse clicks
- **Keyboard**: Typing (content not captured)
- **Scroll**: Page scrolling
- **Focus/Blur**: Window switching
- **Heartbeat**: Periodic check-in

---

## 🔍 Common Scenarios

### Scenario 1: Employee Forgot to Punch In
**Problem**: No activity being tracked

**Solution**:
1. Employee should punch in immediately
2. Previous work won't be tracked (by design)
3. Future work will be tracked automatically

---

### Scenario 2: False Idle Detection
**Problem**: Employee marked idle during meeting

**Solution**:
1. Employee can provide reason: "Team meeting"
2. Admin can adjust idle threshold for that employee
3. Consider longer threshold for managers (15 min)

---

### Scenario 3: Low Productivity Score
**Problem**: Good employee has low score

**Possible Reasons**:
- Thinking/planning time (normal for developers)
- Phone calls (not tracked)
- Physical meetings (not tracked)
- Reading/research (low interaction)

**Solution**:
- Review idle period reasons
- Consider role-specific thresholds
- Use score as one metric, not the only metric

---

### Scenario 4: No Data Showing
**Problem**: Dashboard is empty

**Checklist**:
- [ ] Is employee punched in?
- [ ] Is monitoring enabled for that employee?
- [ ] Check browser console for errors
- [ ] Verify activity_tracker.js is loading
- [ ] Check date filter (try "Today")

---

## ⚙️ Configuration Tips

### For Call Center Staff
```
Idle Threshold: 3 minutes (fast-paced environment)
Extended Threshold: 10 minutes
Heartbeat: 30 seconds (more frequent)
```

### For Developers
```
Idle Threshold: 10 minutes (thinking time)
Extended Threshold: 20 minutes
Heartbeat: 60 seconds (standard)
```

### For Managers
```
Idle Threshold: 15 minutes (meetings)
Extended Threshold: 30 minutes
Heartbeat: 60 seconds (standard)
```

### For Sales Team
```
Idle Threshold: 5 minutes (standard)
Extended Threshold: 15 minutes
Heartbeat: 60 seconds (standard)
```

---

## 🐛 Quick Troubleshooting

### Issue: "Activity tracker not loading"
**Fix**:
1. Hard refresh: `Ctrl + Shift + R`
2. Check console for errors
3. Verify you're on employee portal pages

### Issue: "Activities not being saved"
**Fix**:
1. Check if punched in
2. Verify CSRF token in page source
3. Check network tab for 403/500 errors
4. Ensure monitoring is enabled

### Issue: "Idle alerts not showing"
**Fix**:
1. Check monitoring settings
2. Verify `enable_idle_alerts` is True
3. Wait full 5 minutes of inactivity
4. Check browser console for errors

### Issue: "Dashboard shows no employees"
**Fix**:
1. Run: `python manage.py init_monitoring_settings`
2. Verify employees have `enable_monitoring=True`
3. Check date filter
4. Ensure employees have work sessions

---

## 📱 Browser Compatibility

### Fully Supported:
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Edge 90+
- ✅ Safari 14+

### Partially Supported:
- ⚠️ IE 11 (not recommended)
- ⚠️ Older mobile browsers

### Required:
- JavaScript enabled
- Cookies enabled
- LocalStorage available

---

## 🔒 Privacy & Security

### What We Track:
- ✅ Mouse movements (not position)
- ✅ Keyboard activity (not keystrokes)
- ✅ Clicks (not targets)
- ✅ Page URLs
- ✅ Timestamps

### What We DON'T Track:
- ❌ Actual keystrokes
- ❌ Passwords
- ❌ Form data
- ❌ Personal information
- ❌ Screenshots (unless enabled)
- ❌ Clipboard content

### Security Features:
- ✅ CSRF protection
- ✅ Authentication required
- ✅ Role-based access
- ✅ Encrypted connections (HTTPS in production)

---

## 📈 Best Practices

### For Employees:
1. **Always punch in** when starting work
2. **Provide reasons** for idle time when asked
3. **Don't try to game the system** (it's obvious)
4. **Report issues** if tracking seems wrong

### For Managers:
1. **Use as one metric**, not the only metric
2. **Consider context** (meetings, calls, etc.)
3. **Review trends**, not single days
4. **Communicate openly** about monitoring

### For Admins:
1. **Set appropriate thresholds** per role
2. **Archive old data** regularly
3. **Monitor system performance**
4. **Gather feedback** from users

---

## 📞 Getting Help

### Check Documentation:
1. `ACTIVITY_MONITORING_SETUP.md` - Detailed setup guide
2. `ACTIVITY_MONITORING_COMPLETE.md` - Full system documentation
3. This file - Quick reference

### Run Diagnostics:
```bash
cd assetmanagement
python test_activity_monitoring.py
```

### Check Logs:
- Browser Console (F12)
- Django logs
- Network tab in DevTools

---

## ✅ Quick Checklist

### System Health:
- [ ] All employees have monitoring settings
- [ ] Activity tracker loads on employee pages
- [ ] API endpoints respond correctly
- [ ] Dashboard is accessible
- [ ] Admin panels work

### Daily Operations:
- [ ] Employees punch in/out correctly
- [ ] Activities are being logged
- [ ] Idle periods are detected
- [ ] Productivity scores calculate
- [ ] Dashboard shows current data

### Weekly Maintenance:
- [ ] Review productivity trends
- [ ] Check for system errors
- [ ] Adjust thresholds if needed
- [ ] Gather user feedback
- [ ] Archive old data (optional)

---

## 🎯 Success Metrics

### Week 1:
- All employees using the system
- No major technical issues
- Initial productivity baseline established

### Month 1:
- Productivity trends identified
- Thresholds optimized per role
- Employee feedback incorporated
- System running smoothly

### Month 3:
- Clear productivity improvements
- Reduced idle time
- Better time management
- Data-driven decisions

---

## 🎉 You're All Set!

The system is **ready to use right now**. Just:

1. **Employees**: Punch in and work normally
2. **Managers**: Visit `/crm/productivity/` to monitor
3. **Admins**: Configure settings as needed

**Everything is automated** - no manual intervention required!

---

**Questions?** Check the full documentation in:
- `ACTIVITY_MONITORING_SETUP.md`
- `ACTIVITY_MONITORING_COMPLETE.md`

**Happy Tracking!** 🚀