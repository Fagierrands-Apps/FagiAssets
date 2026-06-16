# 🔐 CRM System Login Details

## 🌐 **System Access**
**URL**: http://localhost:8000/

---

## 👥 **MANAGEMENT/ADMIN ACCOUNTS**

### **Super Administrator**
- **Username**: `admin`
- **Password**: `[Your admin password]`
- **Email**: admin@fagiassets.com
- **Access Level**: Full system access
- **Features**: All CRM features + Django Admin

### **Staff Administrator**
- **Username**: `admin1`
- **Password**: `[Your admin1 password]`
- **Email**: wayneryan@gmail.com
- **Access Level**: Staff access
- **Features**: CRM management features

---

## 👤 **EMPLOYEE ACCOUNTS**

### **Employee 1 - Sales Representative**
- **Username**: `test.sales`
- **Password**: `employee123`
- **Employee Name**: Test Sales
- **Department**: Sales Test
- **Position**: Sales Rep
- **Access Level**: Employee features only

**Employee Dashboard**: http://localhost:8000/crm/employee/

### **Employee 2 - General Employee**
- **Username**: `employee1`
- **Password**: `employee123`
- **Employee Name**: John Smith
- **Department**: General
- **Position**: Employee
- **Access Level**: Employee features only

**Employee Dashboard**: http://localhost:8000/crm/employee/

---

## 🚀 **QUICK START GUIDE**

### **For Employees:**

1. **Login**
   - Go to: http://localhost:8000/
   - Username: `test.sales` or `employee1`
   - Password: `employee123`

2. **Access Employee Features**
   - After login, go to: http://localhost:8000/crm/employee/
   - Or click "CRM" in the main navigation, then access employee features

3. **Start Using Features**
   - **Punch In**: Click "Punch In/Out" to start your work day
   - **View Tasks**: Check your assigned tasks
   - **Track KPIs**: Monitor your performance metrics
   - **Log Communications**: Record customer interactions
   - **View Timesheet**: Check your work hours

### **For Managers:**

1. **Login**
   - Go to: http://localhost:8000/
   - Username: `admin` or `admin1`
   - Password: `[Your password]`

2. **Access CRM Dashboard**
   - Go to: http://localhost:8000/crm/
   - Full management dashboard with all features

3. **Manage Employees**
   - View employee performance
   - Assign tasks
   - Monitor time tracking
   - Review KPIs

---

## 🔧 **EMPLOYEE FEATURE ACCESS**

### **Available Employee Features:**

| Feature | URL | Description |
|---------|-----|-------------|
| **Employee Dashboard** | `/crm/employee/` | Personal workspace overview |
| **Punch In/Out** | `/crm/employee/punch/` | Time tracking system |
| **Timesheet** | `/crm/employee/timesheet/` | Work hours history |
| **KPI Tracking** | `/crm/employee/kpis/` | Performance metrics |
| **Task Management** | `/crm/employee/tasks/` | Assigned tasks |
| **Communications** | `/crm/employee/communications/` | Customer interactions |
| **Add Communication** | `/crm/employee/communications/add/` | Log new interaction |

---

## 🎯 **TESTING THE SYSTEM**

### **Employee Workflow Test:**

1. **Login as Employee**
   ```
   Username: test.sales
   Password: employee123
   ```

2. **Access Employee Dashboard**
   ```
   URL: http://localhost:8000/crm/employee/
   ```

3. **Test Time Tracking**
   ```
   1. Click "Punch In/Out"
   2. Click "Punch In" to start work
   3. View real-time status updates
   4. Try "Start Break" and "End Break"
   5. Finally "Punch Out"
   ```

4. **Test KPI Tracking**
   ```
   1. Go to "My KPIs"
   2. Click "Add KPI" to create a performance metric
   3. Set targets and track progress
   ```

5. **Test Communication Logging**
   ```
   1. Go to "Communications"
   2. Click "Log Communication"
   3. Record a customer interaction
   4. Set follow-up requirements
   ```

---

## 🔒 **SECURITY NOTES**

### **Password Security:**
- Default passwords are set to `employee123` for testing
- **IMPORTANT**: Change passwords in production environment
- Use strong passwords for all accounts

### **Access Control:**
- Employee accounts have limited access to employee features only
- Admin accounts have full system access
- All actions are logged with timestamps and IP addresses

### **Data Privacy:**
- Time tracking includes location data (GPS coordinates)
- IP addresses are logged for security
- All employee activities are tracked for audit purposes

---

## 🛠️ **ADMIN TASKS**

### **Creating New Employee Accounts:**

1. **Access Django Admin**
   ```
   URL: http://localhost:8000/admin/
   Login with admin credentials
   ```

2. **Create User Account**
   ```
   1. Go to "Users" → "Add User"
   2. Set username and password
   3. Add email and personal details
   4. Set is_active = True
   5. Set is_staff = False (for employees)
   ```

3. **Create Employee Profile**
   ```
   1. Go to "CRM" → "Employees" → "Add Employee"
   2. Link to the user account created above
   3. Set department, position, hire date
   4. Set employee ID and contact details
   ```

### **Managing Employee Access:**

- **Enable/Disable**: Toggle `is_active` in user account
- **Change Permissions**: Modify user groups and permissions
- **Reset Passwords**: Use Django admin to reset employee passwords
- **View Activity**: Check time entries and work sessions

---

## 📱 **MOBILE ACCESS**

The system is fully responsive and works on:
- **Smartphones**: Full employee features available
- **Tablets**: Optimized touch interface
- **Desktop**: Complete feature set
- **Any Browser**: Cross-browser compatibility

**Mobile URL**: Same as desktop - http://localhost:8000/

---

## 🆘 **TROUBLESHOOTING**

### **Common Issues:**

1. **Can't Access Employee Features**
   - Ensure user has an associated Employee record
   - Check that user account is active
   - Verify employee record is active

2. **Time Tracking Not Working**
   - Check browser location permissions
   - Ensure JavaScript is enabled
   - Verify network connectivity

3. **KPIs Not Showing**
   - Create KPI records first
   - Check date filters
   - Verify employee association

### **Getting Help:**
- Check Django admin for user/employee records
- Review server logs for errors
- Verify database migrations are applied

---

## 🎉 **SUCCESS!**

Your CRM system is ready with complete employee features!

**Test the system now:**
1. Login with employee credentials: `test.sales` / `employee123`
2. Access employee dashboard: http://localhost:8000/crm/employee/
3. Start using time tracking, KPIs, tasks, and communications!

---

**🚀 Your employees now have a complete productivity platform!**