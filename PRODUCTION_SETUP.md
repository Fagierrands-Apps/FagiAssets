# Production Environment Setup

This document explains how automatic admin user creation is configured for the production environment on Vercel.

## Automatic Admin User Creation

The system now automatically creates an admin user when deployed to production. This happens through multiple mechanisms to ensure reliability:

### 1. Build-time Initialization

During Vercel deployment, the `build.sh` script runs:
```bash
python manage.py init_production
```

This command:
- Detects production environment (Vercel)
- Creates admin user with credentials from environment variables
- Runs database migrations
- Collects static files

### 2. Runtime Health Check

A health check endpoint at `/users/health/` ensures the admin user exists:
- Automatically creates/updates admin user if missing
- Can be called periodically to maintain admin access
- Returns system status information

### 3. App Initialization

The `users` app automatically initializes the admin user when Django starts in production.

## Environment Variables

The following environment variables control admin user creation:

```bash
ADMIN_USERNAME=admin                    # Default: admin
ADMIN_PASSWORD=FagiAssets2024!         # Default: FagiAssets2024!
ADMIN_EMAIL=admin@fagiassets.com       # Default: admin@fagiassets.com
```

These are configured in `vercel.json` but can be overridden in Vercel's dashboard.

## Production Login Credentials

**Username:** `admin`  
**Password:** `FagiAssets2024!`  
**Email:** `admin@fagiassets.com`

## Manual Commands

If you need to manually manage the admin user:

### Create/Reset Admin User
```bash
python manage.py setup_admin --reset
```

### Initialize Production Environment
```bash
python manage.py init_production
```

### Check Session Health
```bash
python manage.py check_sessions
```

## Verification

After deployment, verify the setup by:

1. **Visit the health check:** `https://fagiassets.vercel.app/users/health/`
2. **Login with admin credentials:** `https://fagiassets.vercel.app/login/`
3. **Check session status:** `https://fagiassets.vercel.app/users/session-status/` (after login)

## Session Persistence Improvements

The following improvements ensure sessions persist properly:

- **Extended session duration:** 24 hours (was 1 hour)
- **Browser-close persistence:** Sessions survive browser restarts
- **Serverless reliability:** Automatic session recovery in serverless environments
- **Database session storage:** Uses PostgreSQL for session persistence
- **Security headers:** Proper cookie security for HTTPS

## Troubleshooting

### If admin login fails:
1. Check the health endpoint: `/users/health/`
2. Verify environment variables in Vercel dashboard
3. Check deployment logs for initialization errors

### If sessions don't persist:
1. Check session status: `/users/session-status/`
2. Verify database connectivity
3. Check browser cookie settings

### Manual admin reset:
If needed, you can run the initialization command manually through Vercel's console or redeploy the application.

## Files Modified

- `build.sh` - Added production initialization
- `vercel.json` - Added environment variables
- `users/management/commands/init_production.py` - Production initialization command
- `users/management/commands/setup_admin.py` - Admin user management
- `users/management/commands/check_sessions.py` - Session debugging
- `users/health_views.py` - Health check endpoint
- `users/apps.py` - App-level initialization
- `users/middleware.py` - Session reliability middleware
- `assetmanager/settings.py` - Session configuration improvements
- `users/backends.py` - Enhanced authentication backend

## Security Notes

- Admin credentials are stored as environment variables
- Sessions use secure cookies in production (HTTPS only)
- Session cookies are HTTP-only to prevent XSS
- CSRF protection is enabled
- Database sessions ensure server-side validation