# Vercel Deployment Guide for Asset Management System

## Overview
This guide covers deploying the Asset Management System to Vercel under the domain `fagiassets.vercel.app`.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Repository**: Push your code to GitHub
3. **PostgreSQL Database**: Set up a database (Vercel PostgreSQL or external)

## Configuration Changes Made

### 1. Updated QR Code Base URL
```python
# assetmanager/settings.py
QR_CODE_BASE_URL = 'https://fagiassets.vercel.app'
```

### 2. Updated Django Settings
- Added Vercel domain to `ALLOWED_HOSTS`
- Updated CORS settings for Vercel
- Added environment-based DEBUG setting
- Configured database for PostgreSQL/SQLite
- Added WhiteNoise for static files

### 3. Updated Desktop App
- Changed API base URL to `https://fagiassets.vercel.app`
- Updated all references in README

## Deployment Steps

### 1. Prepare Files
Files added/modified for Vercel deployment:
- `vercel.json` - Vercel configuration
- `requirements-vercel.txt` - Python dependencies
- Updated `assetmanager/settings.py`
- Updated `desktop-app/src/js/api.js`

### 2. Database Setup
Choose one of these options:

#### Option A: Vercel PostgreSQL
```bash
# Install Vercel CLI
npm install -g vercel

# Link to your project
vercel link

# Add PostgreSQL
vercel env add DATABASE_URL
```

#### Option B: External PostgreSQL
Set up a PostgreSQL database on:
- Heroku Postgres
- Railway
- Supabase
- PlanetScale

### 3. Environment Variables
Set these in Vercel dashboard:

```bash
DATABASE_URL=postgresql://user:password@host:port/database
DEBUG=False
DJANGO_SETTINGS_MODULE=assetmanager.settings
```

### 4. Deploy to Vercel

#### Via Vercel CLI:
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

#### Via GitHub Integration:
1. Connect your GitHub repository to Vercel
2. Import the project
3. Configure environment variables
4. Deploy

### 5. Post-Deployment Setup

#### Run Database Migrations:
```bash
# Using Vercel CLI
vercel exec python manage.py migrate
```

#### Create Superuser:
```bash
vercel exec python manage.py createsuperuser
```

#### Collect Static Files:
```bash
vercel exec python manage.py collectstatic --noinput
```

## Verification

### 1. Test QR Code Configuration
```bash
python test_qr_config.py
```

### 2. Check Deployment
- Visit: `https://fagiassets.vercel.app`
- Test API: `https://fagiassets.vercel.app/api/assets/`
- Test QR codes: Generate and scan asset QR codes

### 3. Desktop App Testing
- Start desktop app: `npm start`
- Verify connection to Vercel backend
- Test all functionality

## File Structure for Vercel

```
assetmanagement/
├── vercel.json                 # Vercel configuration
├── requirements-vercel.txt     # Python dependencies
├── assetmanager/
│   ├── settings.py            # Updated for Vercel
│   └── wsgi.py                # WSGI entry point
├── desktop-app/
│   └── src/js/api.js          # Updated API URL
└── static/                    # Static files
```

## Key Features After Deployment

✅ **QR Codes**: Now generate with `https://fagiassets.vercel.app/assets/X/`
✅ **Mobile Access**: QR codes work from any mobile device
✅ **Global Access**: Available from anywhere with internet
✅ **Desktop App**: Works with cloud backend
✅ **Scalable**: Vercel handles traffic scaling
✅ **HTTPS**: Secure connections by default

## Troubleshooting

### Common Issues

#### 1. Static Files Not Loading
```bash
# Ensure WhiteNoise is configured
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
```

#### 2. Database Connection Issues
- Check `DATABASE_URL` environment variable
- Verify PostgreSQL credentials
- Test database connectivity

#### 3. CORS Issues
- Ensure `fagiassets.vercel.app` is in `CORS_ALLOWED_ORIGINS`
- Check `ALLOWED_HOSTS` includes Vercel domain

#### 4. Desktop App Connection Issues
- Verify API URL in `desktop-app/src/js/api.js`
- Check internet connection
- Test API endpoints directly

### Debug Commands

```bash
# Check environment variables
vercel env ls

# View logs
vercel logs

# Run shell commands
vercel exec python manage.py shell
```

## Production Checklist

- [ ] Database configured and migrated
- [ ] Environment variables set
- [ ] Static files collected
- [ ] QR codes tested and working
- [ ] Desktop app connects to Vercel
- [ ] All API endpoints accessible
- [ ] Mobile QR scanning works
- [ ] HTTPS certificate active
- [ ] Domain `fagiassets.vercel.app` accessible

## Post-Deployment Benefits

1. **Global Accessibility**: Access from anywhere
2. **Mobile QR Codes**: Work from any device
3. **Professional URLs**: Clean, branded domain
4. **Auto-scaling**: Handles traffic automatically
5. **Zero Downtime**: Vercel handles deployments
6. **HTTPS**: Secure by default
7. **CDN**: Fast global content delivery

## Maintenance

### Regular Updates
```bash
# Update code
git push origin main

# Vercel auto-deploys from main branch
```

### Database Backups
- Set up automated backups for PostgreSQL
- Export data regularly
- Test restore procedures

### Monitoring
- Monitor Vercel dashboard for errors
- Check function logs
- Monitor database performance

## Next Steps

After successful deployment:
1. Test all functionality thoroughly
2. Update documentation with new URLs
3. Train users on new system
4. Set up monitoring and backups
5. Configure custom domain (if needed)

Your Asset Management System is now deployed and accessible at `https://fagiassets.vercel.app`!