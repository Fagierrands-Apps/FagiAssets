# 🔄 Automatic Lunch Break System - Flow Diagram

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AUTOMATIC LUNCH BREAK SYSTEM                  │
└─────────────────────────────────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
            ┌───────▼────────┐       ┌───────▼────────┐
            │   MIDDLEWARE   │       │    COMMAND     │
            │   (Real-time)  │       │  (Scheduled)   │
            └───────┬────────┘       └───────┬────────┘
                    │                         │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   LUNCH BREAK LOGIC     │
                    │  (Duplicate Prevention) │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   CREATE TIME ENTRIES   │
                    │  • break_start (1 PM)   │
                    │  • break_end (2 PM)     │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   WORK SESSION UPDATE   │
                    │  calculate_hours()      │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   VISUAL FEEDBACK       │
                    │  • Alert Banner         │
                    │  • Status Update        │
                    └─────────────────────────┘
```

---

## 🕐 Timeline Flow (Typical Day)

```
09:00 AM  ┌─────────────────────────────────────────────┐
          │ Employee punches in                         │
          │ Status: Working                             │
          └─────────────────────────────────────────────┘
          
12:59 PM  ┌─────────────────────────────────────────────┐
          │ Employee still working                      │
          │ No lunch break yet                          │
          └─────────────────────────────────────────────┘
          
01:00 PM  ┌─────────────────────────────────────────────┐
          │ 🍽️ AUTOMATIC LUNCH BREAK TRIGGERED          │
          │                                             │
          │ ✅ Middleware detects lunch time            │
          │ ✅ Creates break_start entry (1:00 PM)      │
          │ ✅ Creates break_end entry (2:00 PM)        │
          │ ✅ Alert banner appears                     │
          │ ✅ Status changes to "On Break"             │
          └─────────────────────────────────────────────┘
          
01:30 PM  ┌─────────────────────────────────────────────┐
          │ Employee on lunch break                     │
          │ Alert still visible                         │
          │ Status: On Break                            │
          └─────────────────────────────────────────────┘
          
02:00 PM  ┌─────────────────────────────────────────────┐
          │ Lunch break ends automatically              │
          │ Alert disappears                            │
          │ Status returns to "Working"                 │
          └─────────────────────────────────────────────┘
          
05:00 PM  ┌─────────────────────────────────────────────┐
          │ Employee punches out                        │
          │                                             │
          │ 📊 HOURS CALCULATION:                       │
          │ Total Time: 8 hours (9 AM - 5 PM)          │
          │ Lunch Break: 1 hour (1 PM - 2 PM)          │
          │ Worked Hours: 7 hours                       │
          └─────────────────────────────────────────────┘
```

---

## 🔀 Decision Flow

```
                    ┌─────────────────┐
                    │  HTTP Request   │
                    │   or Cron Job   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Is it 1 PM?     │
                    │ (13:00-13:59)   │
                    └────┬───────┬────┘
                         │       │
                      NO │       │ YES
                         │       │
                    ┌────▼────┐  │
                    │  SKIP   │  │
                    └─────────┘  │
                                 │
                    ┌────────────▼────────────┐
                    │ Is it Mon-Sat?          │
                    │ (weekday < 6)           │
                    └────┬───────────┬────────┘
                         │           │
                      NO │           │ YES
                         │           │
                    ┌────▼────┐      │
                    │  SKIP   │      │
                    └─────────┘      │
                                     │
                    ┌────────────────▼────────────┐
                    │ Is user authenticated?      │
                    │ Has employee profile?       │
                    └────┬───────────────┬────────┘
                         │               │
                      NO │               │ YES
                         │               │
                    ┌────▼────┐          │
                    │  SKIP   │          │
                    └─────────┘          │
                                         │
                    ┌────────────────────▼────────┐
                    │ Is role == 'call_center'?   │
                    └────┬───────────────┬────────┘
                         │               │
                     YES │               │ NO
                         │               │
                    ┌────▼────┐          │
                    │  SKIP   │          │
                    │ (Exempt)│          │
                    └─────────┘          │
                                         │
                    ┌────────────────────▼────────┐
                    │ Is employee punched in?     │
                    │ (status == 'working')       │
                    └────┬───────────────┬────────┘
                         │               │
                      NO │               │ YES
                         │               │
                    ┌────▼────┐          │
                    │  SKIP   │          │
                    └─────────┘          │
                                         │
                    ┌────────────────────▼────────┐
                    │ Does lunch break already    │
                    │ exist for today?            │
                    └────┬───────────────┬────────┘
                         │               │
                     YES │               │ NO
                         │               │
                    ┌────▼────┐          │
                    │  SKIP   │          │
                    │(Prevent │          │
                    │Duplicate)          │
                    └─────────┘          │
                                         │
                    ┌────────────────────▼────────┐
                    │ ✅ CREATE LUNCH BREAK       │
                    │                             │
                    │ 1. break_start at 1:00 PM   │
                    │ 2. break_end at 2:00 PM     │
                    │ 3. Update work session      │
                    │ 4. Show alert banner        │
                    └─────────────────────────────┘
```

---

## 👥 User Type Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         EMPLOYEE LOGIN                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
    ┌───────────▼──────────┐   ┌─────────▼──────────┐
    │  REGULAR EMPLOYEE    │   │  CALL CENTER AGENT │
    │  (Sales, PM, etc.)   │   │  (role='call_center')│
    └───────────┬──────────┘   └─────────┬──────────┘
                │                         │
                │                         │
    ┌───────────▼──────────┐   ┌─────────▼──────────┐
    │  AT 1:00 PM          │   │  AT 1:00 PM        │
    │                      │   │                    │
    │  ✅ Alert appears    │   │  ❌ No alert       │
    │  ✅ Auto break       │   │  ❌ No auto break  │
    │  ✅ Status: On Break │   │  ✅ Status: Working│
    │  ✅ 1 hour deducted  │   │  ✅ Full hours     │
    └──────────────────────┘   └────────────────────┘
```

---

## 🗄️ Database Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    LUNCH BREAK TRIGGERED                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
    ┌───────────▼──────────┐   ┌─────────▼──────────┐
    │   TimeEntry #1       │   │   TimeEntry #2     │
    │                      │   │                    │
    │ entry_type:          │   │ entry_type:        │
    │   'break_start'      │   │   'break_end'      │
    │                      │   │                    │
    │ timestamp:           │   │ timestamp:         │
    │   2025-01-15 13:00   │   │   2025-01-15 14:00 │
    │                      │   │                    │
    │ notes:               │   │ notes:             │
    │   'Automatic lunch   │   │   'Automatic lunch │
    │    break'            │   │    break'          │
    │                      │   │                    │
    │ ip_address: 'System' │   │ ip_address: 'System'│
    │                      │   │                    │
    │ user_agent:          │   │ user_agent:        │
    │   'Auto Lunch Break  │   │   'Auto Lunch Break│
    │    System'           │   │    System'         │
    └───────────┬──────────┘   └─────────┬──────────┘
                │                         │
                └────────────┬────────────┘
                             │
                ┌────────────▼────────────┐
                │   WorkSession Update    │
                │                         │
                │ calculate_hours()       │
                │                         │
                │ total_hours: 8.0        │
                │ break_hours: 1.0        │
                │ worked_hours: 7.0       │
                └─────────────────────────┘
```

---

## 🔄 Middleware Request Cycle

```
┌─────────────────────────────────────────────────────────────────┐
│                      EMPLOYEE MAKES REQUEST                      │
│                  (e.g., visits Time Tracking page)               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                ┌────────────▼────────────┐
                │  Django Middleware      │
                │  Stack Processing       │
                └────────────┬────────────┘
                             │
                ┌────────────▼────────────┐
                │ AutoLunchBreakMiddleware│
                │ .process_request()      │
                └────────────┬────────────┘
                             │
                    ┌────────▼────────┐
                    │ Check Conditions│
                    │ (see Decision   │
                    │  Flow above)    │
                    └────────┬────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
    ┌───────────▼──────────┐   ┌─────────▼──────────┐
    │  CONDITIONS MET      │   │  CONDITIONS NOT MET│
    │                      │   │                    │
    │ Create lunch break   │   │ Skip processing    │
    │ entries              │   │                    │
    └───────────┬──────────┘   └─────────┬──────────┘
                │                         │
                └────────────┬────────────┘
                             │
                ┌────────────▼────────────┐
                │  Continue to View       │
                │  (punch_in_out view)    │
                └────────────┬────────────┘
                             │
                ┌────────────▼────────────┐
                │  Render Template        │
                │  • Show alert if lunch  │
                │  • Display status       │
                │  • Show time entries    │
                └────────────┬────────────┘
                             │
                ┌────────────▼────────────┐
                │  Return Response        │
                │  to Employee            │
                └─────────────────────────┘
```

---

## 📊 Hour Calculation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    EMPLOYEE PUNCHES OUT                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                ┌────────────▼────────────┐
                │ WorkSession.            │
                │ calculate_hours()       │
                └────────────┬────────────┘
                             │
                ┌────────────▼────────────┐
                │ Get all TimeEntry       │
                │ records for today       │
                └────────────┬────────────┘
                             │
                ┌────────────▼────────────┐
                │ Calculate total_hours   │
                │ (punch_out - punch_in)  │
                │                         │
                │ 17:00 - 09:00 = 8 hours │
                └────────────┬────────────┘
                             │
                ┌────────────▼────────────┐
                │ Find all break pairs    │
                │ (break_start/break_end) │
                │                         │
                │ Found: 1 PM - 2 PM      │
                └────────────┬────────────┘
                             │
                ┌────────────▼────────────┐
                │ Calculate break_hours   │
                │                         │
                │ 14:00 - 13:00 = 1 hour  │
                └────────────┬────────────┘
                             │
                ┌────────────▼────────────┐
                │ Calculate worked_hours  │
                │                         │
                │ 8 hours - 1 hour = 7 hrs│
                └────────────┬────────────┘
                             │
                ┌────────────▼────────────┐
                │ Save WorkSession        │
                │                         │
                │ total_hours: 8.0        │
                │ break_hours: 1.0        │
                │ worked_hours: 7.0       │
                └─────────────────────────┘
```

---

## 🎯 Integration Points

```
┌─────────────────────────────────────────────────────────────────┐
│              AUTOMATIC LUNCH BREAK SYSTEM                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼────────┐  ┌────────▼────────┐  ┌───────▼────────┐
│  TimeEntry     │  │  WorkSession    │  │  Employee      │
│  Model         │  │  Model          │  │  Model         │
│                │  │                 │  │                │
│ • entry_type   │  │ • total_hours   │  │ • role         │
│ • timestamp    │  │ • break_hours   │  │ • status       │
│ • notes        │  │ • worked_hours  │  │ • get_current_ │
│                │  │ • calculate_    │  │   status()     │
│                │  │   hours()       │  │                │
└───────┬────────┘  └────────┬────────┘  └───────┬────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼────────┐  ┌────────▼────────┐  ┌───────▼────────┐
│  Timesheet     │  │  Reports        │  │  Dashboard     │
│  View          │  │  View           │  │  View          │
│                │  │                 │  │                │
│ • Shows lunch  │  │ • Includes      │  │ • Shows alert  │
│   breaks       │  │   lunch hours   │  │   banner       │
│ • Correct      │  │ • Compliance    │  │ • Current      │
│   hours        │  │   tracking      │  │   status       │
└────────────────┘  └─────────────────┘  └────────────────┘
```

---

## 🔐 Security & Validation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    LUNCH BREAK REQUEST                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                ┌────────────▼────────────┐
                │ Authentication Check    │
                │ request.user.is_        │
                │ authenticated?          │
                └────┬───────────┬────────┘
                     │           │
                  NO │           │ YES
                     │           │
                ┌────▼────┐      │
                │ REJECT  │      │
                └─────────┘      │
                                 │
                ┌────────────────▼────────┐
                │ Employee Profile Check  │
                │ Has employee_profile?   │
                └────┬───────────┬────────┘
                     │           │
                  NO │           │ YES
                     │           │
                ┌────▼────┐      │
                │ REJECT  │      │
                └─────────┘      │
                                 │
                ┌────────────────▼────────┐
                │ Role Validation         │
                │ Check exemptions        │
                └────┬───────────┬────────┘
                     │           │
              EXEMPT │           │ ELIGIBLE
                     │           │
                ┌────▼────┐      │
                │  SKIP   │      │
                └─────────┘      │
                                 │
                ┌────────────────▼────────┐
                │ Status Validation       │
                │ Is punched in?          │
                └────┬───────────┬────────┘
                     │           │
                  NO │           │ YES
                     │           │
                ┌────▼────┐      │
                │  SKIP   │      │
                └─────────┘      │
                                 │
                ┌────────────────▼────────┐
                │ Duplicate Check         │
                │ Already has lunch break?│
                └────┬───────────┬────────┘
                     │           │
                 YES │           │ NO
                     │           │
                ┌────▼────┐      │
                │  SKIP   │      │
                └─────────┘      │
                                 │
                ┌────────────────▼────────┐
                │ ✅ CREATE LUNCH BREAK   │
                │ All validations passed  │
                └─────────────────────────┘
```

---

## 📱 User Interface Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    TIME TRACKING PAGE                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │ Page Load       │
                    │ (GET request)   │
                    └────────┬────────┘
                             │
                ┌────────────▼────────────┐
                │ Middleware Processes    │
                │ (creates lunch break    │
                │  if conditions met)     │
                └────────────┬────────────┘
                             │
                ┌────────────▼────────────┐
                │ View Processes          │
                │ • Get employee status   │
                │ • Calculate hours       │
                │ • Check is_lunch_time   │
                └────────────┬────────────┘
                             │
                ┌────────────▼────────────┐
                │ Template Renders        │
                └────────────┬────────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
    ┌───────────▼──────────┐   ┌─────────▼──────────┐
    │  LUNCH TIME          │   │  NOT LUNCH TIME    │
    │  (1:00 PM - 1:59 PM) │   │                    │
    │                      │   │                    │
    │  ┌────────────────┐ │   │  ┌──────────────┐ │
    │  │ 🍽️ ALERT      │ │   │  │ No Alert     │ │
    │  │ Lunch Break    │ │   │  │              │ │
    │  │ Time           │ │   │  │              │ │
    │  └────────────────┘ │   │  └──────────────┘ │
    │                      │   │                    │
    │  ┌────────────────┐ │   │  ┌──────────────┐ │
    │  │ Status:        │ │   │  │ Status:      │ │
    │  │ On Break       │ │   │  │ Working      │ │
    │  └────────────────┘ │   │  └──────────────┘ │
    │                      │   │                    │
    │  ┌────────────────┐ │   │  ┌──────────────┐ │
    │  │ Recent Entries:│ │   │  │ Recent       │ │
    │  │ • break_start  │ │   │  │ Entries      │ │
    │  │   1:00 PM      │ │   │  │              │ │
    │  │ • break_end    │ │   │  │              │ │
    │  │   2:00 PM      │ │   │  │              │ │
    │  └────────────────┘ │   │  └──────────────┘ │
    └──────────────────────┘   └────────────────────┘
```

---

## 🎯 Summary

This automatic lunch break system provides:

✅ **Dual Enforcement:** Middleware (real-time) + Command (scheduled)
✅ **Smart Detection:** Time, day, role, and status validation
✅ **Duplicate Prevention:** Checks existing entries before creating
✅ **Seamless Integration:** Works with existing time tracking
✅ **Visual Feedback:** Alert banner for user awareness
✅ **Accurate Calculations:** Automatic hour deduction
✅ **Role-Based Exemptions:** Call center agents excluded

**Status:** ✅ Fully Operational & Production Ready