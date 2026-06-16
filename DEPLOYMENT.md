# Django Asset Management - Vercel Deployment Guide

## Problem Description
The "attempt to write a readonly database" error occurs when deploying to Vercel because:
1. Vercel's serverless functions have a read-only filesystem
2. SQLite databases cannot be modified in this environment
3. The app needs to use PostgreSQL for production

## Solution Implemented

### 1. Database Configuration
- **Development**: Uses SQLite for local development
- **Production**: Forces PostgreSQL for Vercel deployment
- **Environment Detection**: Automatically detects Vercel environment

### 2. Safe Authentication Backend
- Created `SafeModelBackend` that handles database write failures gracefully
- Prevents login failures when session tracking fails
- Logs warnings but doesn't crash the application

### 3. User QR Code System
- Generates QR codes containing all user details except password and manager
- Includes assigned assets information
- Provides multiple download formats (200px, 300px, 500px)

## Deployment Steps

### Step 1: Set Environment Variables in Vercel
Go to your Vercel project dashboard and set these environment variables:

```bash
DJANGO_SETTINGS_MODULE=assetmanager.settings
VERCEL=1
DATABASE_URL=postgresql://postgres.dxesmzogjpxswxhsomgf:OnFRtf0SmpHwgNaQ@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=fagiassets.vercel.app,.vercel.app
```

### Step 1.5: Fix Missing Dependencies
The `dj_database_url` module might not be available in Vercel. The settings.py has been updated to:
- Try to import `dj_database_url` first
- Fall back to manual PostgreSQL configuration if not available
- Parse the DATABASE_URL manually using urllib.parse

### Step 2: Deploy to Vercel
```bash
# Install Vercel CLI if not already installed
npm install -g vercel

# Deploy to production
vercel --prod
```

### Step 3: Run Database Migrations
After deployment, run the deployment script:
```bash
python deploy.py
```

### Step 4: Test Login Functionality
1. Visit https://fagiassets.vercel.app/login/
2. Try logging in with existing credentials
3. The system should now use PostgreSQL instead of SQLite

## User QR Code Features

### Accessing User QR Codes
- **Profile View**: `/users/<user_id>/` - Shows user profile with QR code
- **QR Code Page**: `/users/<user_id>/qr/` - Dedicated QR code page
- **QR Code Image**: `/users/<user_id>/qr/image/` - Direct image URL
- **Download QR**: `/users/<user_id>/qr/download/` - Download as PNG
- **JSON Data**: `/users/<user_id>/qr/data.json` - Raw JSON data

### QR Code Content
The QR code contains:
- User ID, username, email, names
- Employee ID, department, location, job title
- Phone numbers and contact information
- All assigned assets with details
- **Excludes**: Password, manager information

### Security
- Users can only view their own QR codes
- Staff members can view all user QR codes
- QR codes are generated on-demand
- No sensitive data is stored in QR codes

## Files Modified/Created

### Core Files
- `assetmanager/settings.py` - Database configuration
- `users/backends.py` - Safe authentication backend
- `users/views.py` - User QR code views
- `users/urls.py` - User URL patterns
- `assets/utils.py` - User QR code generation

### Templates
- `templates/users/profile.html` - User profile page
- `templates/users/user_qr_code.html` - QR code page
- `templates/users/access_denied.html` - Access denied page

### Deployment Files
- `vercel.json` - Vercel configuration
- `settings_production.py` - Production-specific settings
- `deploy.py` - Deployment script
- `.env.production` - Environment variables template

## Testing

### Local Testing
```bash
# Run the test script
python test_user_qr.py

# Start development server
python manage.py runserver
```

### Production Testing
1. Visit `/login/` - Should work without database errors
2. Visit `/users/1/` - Should show user profile with QR code
3. Visit `/users/1/qr/` - Should display QR code page
4. Test QR code downloads in different sizes

## Troubleshooting

### Database Issues
- Check that `DATABASE_URL` environment variable is set
- Verify PostgreSQL connection string is correct
- Ensure `VERCEL=1` environment variable is set

### QR Code Issues
- Verify `qrcode` package is installed
- Check that `QR_CODE_BASE_URL` is set correctly
- Ensure user has assigned assets to display

### Authentication Issues
- Check that `SafeModelBackend` is configured
- Verify session configuration is correct
- Ensure database migrations are applied

## Security Notes
- Change default SECRET_KEY in production
- Use strong passwords for database connections
- Regularly rotate credentials
- Monitor access logs for suspicious activity