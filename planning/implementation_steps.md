# Employee Name Tag — Step-by-Step Implementation Plan

Each step has a clear task and a test to verify before moving to the next step.

---

## STEP 1 — Add qr_token to UserProfile

**File:** `users/models.py`
- Import `uuid`
- Add `qr_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)` to `UserProfile`

**Migration strategy — 3 operations in one migration:**
1. Add `qr_token` column as `null=True` first (so existing rows don't break)
2. Data migration — loop all existing `UserProfile` rows, assign `uuid.uuid4()` to any with null token
3. Alter column to `null=False` (enforce non-null going forward)

This ensures every existing employee in the system gets a permanent QR token automatically.

**Test:**
- Run `makemigrations` — should produce `0006_add_qr_token_to_userprofile.py`
- Run `migrate` — should apply cleanly with no errors
- Open Django shell:
  - `UserProfile.objects.filter(qr_token=None).count()` → must be 0
  - Fetch 3–4 existing users, confirm each has a unique UUID `qr_token`
  - Confirm no two profiles share the same token
- Create a new user, confirm `qr_token` is auto-assigned

---

## STEP 2 — Add Branding Constants to Settings

**File:** `assetmanager/settings.py`
- Add `COMPANY_NAME`, `COMPANY_WEBSITE`, `COMPANY_LOGO_PATH`, `BRAND_BLUE`, `BRAND_ORANGE`

**Test:**
- Open Django shell
- `from django.conf import settings`
- Print each constant, confirm values are correct
- Confirm logo file exists at the path

---

## STEP 3 — Build PDF Name Tag Generator

**File:** `users/nametag.py` (new file)
- Function `generate_nametag_pdf(user, request)` → returns PDF bytes
- Front page: logo, company name, profile photo, name, job title, department, employee ID, QR code
- Back page: logo, company name, employee ID, department, phone, website
- Uses `reportlab`, CR80 size (85.6mm × 54mm)
- QR encodes `https://<domain>/users/public/<qr_token>/`

**Test:**
- Open Django shell
- Call `generate_nametag_pdf(user, mock_request)` for an existing user
- Write output bytes to `/tmp/test_nametag.pdf`
- Open the PDF, visually verify front and back layout, colors, QR code

---

## STEP 4 — Build Public Profile View

**File:** `users/public_views.py` (modify existing)
- Add view `user_public_profile(request, qr_token)`
- Fetches `UserProfile` by `qr_token`
- No login required
- Context: name, photo, job title, department, employee ID, phone, company name, website, logo

**File:** `templates/users/user_public_profile.html` (new)
- Clean, mobile-friendly design
- Company logo at top
- Profile photo, name, job title, department
- Company website link at bottom
- Branded with blue + orange colors

**Test:**
- Start dev server
- Visit `/users/public/<valid_qr_token>/` — should show profile page, no login prompt
- Visit `/users/public/invalid-token/` — should return 404
- Test on mobile browser (or resize) — should be responsive

---

## STEP 5 — Wire Up URLs

**File:** `users/urls.py`
- Add `/users/public/<uuid:qr_token>/` → `user_public_profile`
- Add `/users/<int:user_id>/nametag/` → `download_nametag_pdf`
- Add `/admin-dashboard/users/nametag/bulk/` → `bulk_nametag_pdf`

**Test:**
- Run `python manage.py show_urls | grep nametag` — confirm all 3 URLs registered
- Run `python manage.py show_urls | grep public` — confirm public URL registered
- Hit each URL in browser, confirm correct view loads (or 405 for wrong method)

---

## STEP 6 — Build Single Name Tag Download View

**File:** `users/views.py`
- Add `download_nametag_pdf(request, user_id)`
- Login required
- Calls `generate_nametag_pdf(user, request)`
- Returns `HttpResponse` with `Content-Type: application/pdf` and download header

**Test:**
- Log in as admin
- Visit `/users/<id>/nametag/`
- Browser should prompt PDF download
- Open PDF — verify front and back are correct for that user
- Test with a user that has no photo — should use placeholder, not crash

---

## STEP 7 — Build Bulk Name Tag Download View

**File:** `users/views.py`
- Add `bulk_nametag_pdf(request)`
- POST with list of user IDs
- Generates one PDF with 2 pages per user (front + back)
- Returns combined PDF download

**Test:**
- Select 3 users from user list, trigger bulk download
- PDF should have 6 pages (2 per user)
- Each user's front/back should show correct info
- Test with 1 user selected — should work
- Test with 0 users selected — should return error message, not crash

---

## STEP 8 — Update User Detail Page UI

**URL:** `http://<domain>/admin-dashboard/users/<id>/`
**File:** `templates/admin_dashboard/user_detail.html`

Add a new card in the right sidebar (after Quick Actions), containing:
- QR code preview image (uses `/users/<id>/qr/image/` endpoint)
- "Download Name Tag" button → `/users/<id>/nametag/` (blue, full width)
- "Public Profile Link" — copyable URL: `https://<domain>/users/public/<qr_token>/`

The sidebar already has: Edit User, Activate/Deactivate, Assign Asset, Delete.
The new "Name Tag" card sits below Quick Actions.

**Test:**
- Open `http://127.0.0.1:8000/admin-dashboard/users/46/`
- Confirm new Name Tag card is visible in right sidebar
- Confirm QR code preview renders
- Confirm public profile link is correct and opens in new tab
- Click "Download Name Tag" — PDF should download immediately

---

## STEP 9 — Update User List Page UI

**File:** `templates/admin_dashboard/user_list.html`
- Add "Download Name Tags" option to bulk actions dropdown
- On select, POST selected user IDs to `/admin-dashboard/users/nametag/bulk/`

**Test:**
- Open user list page
- Select 2–3 users using checkboxes
- Choose "Download Name Tags" from bulk actions
- Confirm PDF downloads with correct pages
- Confirm selecting 0 users shows a validation message

---

## STEP 10 — End-to-End Final Test

**Full flow test:**
1. Create a brand new user with photo, job title, department, phone
2. Go to user detail page — confirm QR token assigned, public link visible
3. Click "Download Name Tag" — verify PDF front and back
4. Scan the QR code on the PDF — should open public profile page
5. Verify public profile shows correct info, no assets, no sensitive data
6. Update the user's job title
7. Scan QR again — public profile should show updated job title (same URL)
8. Go to user list, select multiple users, bulk download — verify all pages correct

---

## Notes

- Do NOT move to the next step until the current step's test passes
- If a test fails, fix before proceeding
- Migrations must be run against Supabase (pooler connection)
- PDF visual check is mandatory for Steps 3, 6, 7
