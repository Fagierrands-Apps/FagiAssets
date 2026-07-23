# Employee Name Tag & Permanent QR Code Feature

## Status: READY TO BUILD — All decisions confirmed

---

## 1. Data Model Changes

### UserProfile (users/models.py)
- Add `qr_token` — UUID, auto-generated once, never changes
- `avatar` — already exists
- `employee_id`, `job_title`, `department`, `phone`, `mobile` — already exist

### Migration
- `users/migrations/0006_add_qr_token_to_userprofile.py`

---

## 2. Public Profile Page (No Login Required)

### URL
`/users/public/<qr_token>/`

### Shows
- Company logo
- Company name: Fagi Errands Services Limited
- Company website: www.fagierrands.com
- Profile photo
- Full name
- Job title
- Department
- Employee ID
- Phone / Mobile

### Does NOT show
- Assigned assets
- Email
- Manager
- System info

---

## 3. Permanent QR Code

- Encodes: `https://<domain>/users/public/<qr_token>/`
- Token: UUID, generated once on profile creation, never regenerated
- Physical card QR remains valid forever even if employee details change

---

## 4. Name Tag PDF — FRONT SIDE
Size: CR80 — 85.6mm × 54mm (credit card)

Layout (top to bottom):
```
┌─────────────────────────────────┐
│  [BLUE HEADER BAR]              │
│  Company Logo    Company Name   │
├─────────────────────────────────┤
│                                 │
│        [Profile Photo]          │
│        circular, centered       │
│                                 │
│   FULL NAME (bold, black)       │
│   Job Title (orange)            │
│   Department (grey)             │
│                                 │
│  EMP ID: FGE001    [QR CODE]    │
└─────────────────────────────────┘
```

Colors:
- Header bar: Blue #1A1AFF
- Header text: White
- Name: Black #000000, bold
- Job title: Orange #E83A00
- Department: Grey #555555
- Employee ID: Grey #777777
- QR code border: Blue #1A1AFF
- Background: White #FFFFFF

---

## 5. Name Tag PDF — BACK SIDE
Size: CR80 — 85.6mm × 54mm

Layout:
```
┌─────────────────────────────────┐
│  [BLUE HEADER BAR]              │
│  Fagi Errands Services Limited  │
├─────────────────────────────────┤
│                                 │
│      [Company Logo, large]      │
│                                 │
│   Employee ID: FGE001           │
│   Dept: Operations              │
│   Phone: +254...                │
│                                 │
│   www.fagierrands.com           │
└─────────────────────────────────┘
```

Colors: Same as front

---

## 6. PDF Generation

- Library: `reportlab` (already installed)
- Output: 2-page PDF (page 1 = front, page 2 = back), CR80 size
- Trigger: Button on user detail page ("Download Name Tag")
- Bulk: Button on user list page to download selected users (multi-employee PDF, 2 pages per employee)

---

## 7. Views & URLs

| URL | View | Auth | Description |
|-----|------|------|-------------|
| `/users/public/<qr_token>/` | `user_public_profile` | None | Public profile via QR scan |
| `/users/<id>/nametag/` | `download_nametag_pdf` | Login | Download single name tag PDF |
| `/admin-dashboard/users/nametag/bulk/` | `bulk_nametag_pdf` | Login | Bulk download selected users |

---

## 8. UI Changes

### admin_dashboard/user_detail.html
- Add "Download Name Tag" button (blue, prominent)
- Add QR code preview thumbnail
- Add public profile link (copyable)

### admin_dashboard/user_list.html
- Add "Download Name Tags" to bulk actions dropdown

---

## 9. Branding Constants (settings.py additions)

```python
COMPANY_NAME = "Fagi Errands Services Limited"
COMPANY_WEBSITE = "www.fagierrands.com"
COMPANY_LOGO_PATH = BASE_DIR / "static/images/company_logo.png"
BRAND_BLUE = "#1A1AFF"
BRAND_ORANGE = "#E83A00"
```

---

## 10. Files to Create / Modify

### New
- `users/migrations/0006_add_qr_token_to_userprofile.py`
- `users/nametag.py` — PDF generation (reportlab)
- `templates/users/user_public_profile.html` — public profile page

### Modified
- `users/models.py` — add `qr_token`
- `users/views.py` — add nametag + public profile views
- `users/urls.py` — add new URLs
- `assetmanager/settings.py` — add branding constants
- `templates/admin_dashboard/user_detail.html` — add download button + QR preview
- `templates/admin_dashboard/user_list.html` — add bulk action

---

## 11. Build Order

1. `users/models.py` — add `qr_token`
2. Run migration
3. `assetmanager/settings.py` — add branding constants
4. `users/nametag.py` — PDF generation logic
5. `users/public_views.py` — public profile view
6. `templates/users/user_public_profile.html`
7. `users/views.py` — nametag download view + bulk
8. `users/urls.py` — wire up URLs
9. `templates/admin_dashboard/user_detail.html` — button + QR preview
10. `templates/admin_dashboard/user_list.html` — bulk action

---

## All Decisions Confirmed

| # | Question | Answer |
|---|----------|--------|
| 1 | Back side content | Logo, company name, emp ID, dept, phone, www.fagierrands.com |
| 2 | Card size | CR80 — 85.6mm × 54mm (credit card) |
| 3 | Public profile content | Personal + dept + company info. NO assets |
| 4 | PDF trigger | Button on user detail page. Also bulk on user list |
| 5 | Brand colors | Blue #1A1AFF, Orange #E83A00, Yellow #FFD700 |
| 6 | Company name | Fagi Errands Services Limited |
| 7 | Company website | www.fagierrands.com |
| 8 | Logo | static/images/company_logo.png |
