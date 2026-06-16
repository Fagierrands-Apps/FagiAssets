# 🚀 Render.com Deployment Guide

## Prerequisites
- GitHub account with your repo: https://github.com/Fagierrands-Apps/FagiAssets
- Render.com account (free tier works)
- Your code is already Render-ready!

---

## Step 1: Push to GitHub (if not done)

```bash
cd /home/fagitone/Documents/GitHub/FagiAssets
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

---

## Step 2: Create Render Account

1. Go to https://render.com
2. Click **"Get Started"**
3. Sign up with GitHub (recommended)
4. Authorize Render to access your GitHub repos

---

## Step 3: Create Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your repository: `Fagierrands-Apps/FagiAssets`
3. Configure:

**Basic Settings:**
- Name: `fagiassets` (or your choice)
- Region: Choose closest to Kenya (e.g., Singapore or Frankfurt)
- Branch: `main`
- Root Directory: *leave empty*
- Runtime: **Python 3**

**Build & Deploy:**
- Build Command: `./build.sh`
- Start Command: `cd assetmanagement && gunicorn assetmanager.wsgi:application --bind 0.0.0.0:$PORT`

**Instance Type:**
- Free (for testing)
- Starter (for production - $7/month)

---

## Step 4: Environment Variables

In Render dashboard, add these environment variables:

### Required:
```
DEBUG=False
SECRET_KEY=django-insecure-)uydf_yg5c=z5^)xi+&$1@y$7w@)lboa2l#eom$!4uk1l!22u0
DJANGO_SETTINGS_MODULE=assetmanager.settings
PYTHONPATH=/opt/render/project/src/assetmanagement
```

### Optional (if changing database):
```
DB_NAME=postgres
DB_USER=postgres.dxesmzogjpxswxhsomgf
DB_PASSWORD=OnFRtf0SmpHwgNaQ
DB_HOST=aws-0-ap-southeast-1.pooler.supabase.com
DB_PORT=6543
```

---

## Step 5: Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repo
   - Run `build.sh`
   - Install dependencies
   - Run migrations
   - Collect static files
   - Start gunicorn

Watch the logs in real-time!

---

## Step 6: Get Your URL

Once deployed, your app will be at:
```
https://fagiassets.onrender.com
```
(or whatever name you chose)

---

## Step 7: Update ALLOWED_HOSTS

After first deployment, add your Render URL to settings:

Update `assetmanagement/assetmanager/settings.py`:
```python
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver', '10.246.23.10', 
                 'fagiassets.vercel.app', '*.vercel.app', 
                 'fagiassets.onrender.com', '*.onrender.com', '*']
```

Then push and Render auto-redeploys:
```bash
git add .
git commit -m "Add Render to ALLOWED_HOSTS"
git push origin main
```

---

## 🎉 Access Your App

- **Main Site:** https://fagiassets.onrender.com/
- **Login:** https://fagiassets.onrender.com/login/
- **Admin:** https://fagiassets.onrender.com/admin/

**Default Credentials:**
- Username: `admin`
- Password: `FagiAssets2024!`

**⚠️ Change password immediately after first login!**

---

## 📊 What's Deployed

✅ Asset Management System
✅ CRM System
✅ Employee Management
✅ Time Tracking
✅ QR Code Generation
✅ Admin Dashboard
✅ PostgreSQL Database (Supabase)
✅ Static Files (WhiteNoise)

---

## ⚠️ Known Limitations on Free Tier

- **Cold starts:** App sleeps after 15 min of inactivity (30 sec wake-up)
- **750 hours/month:** Covers 24/7 for one app
- **No background workers:** Celery tasks won't run (but app works fine)

Upgrade to Starter ($7/mo) to remove cold starts.

---

## 🔄 Auto-Deploy

Render automatically redeploys when you push to `main`:

```bash
# Make changes
git add .
git commit -m "Your changes"
git push origin main
# Render auto-deploys in ~2 minutes
```

---

## 🐛 Troubleshooting

### Build Failed?

Check Render logs for errors. Common fixes:

1. **Missing dependencies:**
```bash
# Locally verify requirements.txt works
pip install -r requirements.txt
```

2. **Build script not executable:**
```bash
chmod +x build.sh
git add build.sh
git commit -m "Make build.sh executable"
git push
```

### App Crashes?

Check Render logs:
1. Go to your service
2. Click **"Logs"**
3. Look for Python errors

Common issues:
- ALLOWED_HOSTS not including Render URL
- Database connection issues
- Missing environment variables

### Static Files Not Loading?

Should work automatically via WhiteNoise. If not:
1. Check `STATIC_ROOT` in settings.py
2. Verify build.sh runs `collectstatic`
3. Check Render logs for errors

---

## 🔐 Production Checklist

After deployment:

- [ ] Change admin password
- [ ] Generate new SECRET_KEY:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```
- [ ] Update SECRET_KEY in Render environment variables
- [ ] Set DEBUG=False (already done)
- [ ] Add your custom domain (optional)
- [ ] Set up database backups
- [ ] Monitor logs regularly

---

## 💰 Cost Estimate

**Free Tier:**
- Web Service: $0 (750 hours/month)
- Database: $0 (using external Supabase)
- Bandwidth: 100GB/month free
- **Total: FREE** ✅

**Starter Tier (Recommended for Production):**
- Web Service: $7/month (no cold starts)
- Database: $0 (still using Supabase)
- **Total: $7/month**

---

## 🆚 Render vs cPanel

| Feature | Render | cPanel |
|---------|--------|--------|
| Setup Time | 5 minutes | 30+ minutes |
| Auto-deploy | ✅ Yes | ❌ Manual |
| Free Tier | ✅ Yes | ❌ No |
| SSL/HTTPS | ✅ Automatic | ⚠️ Manual |
| Logs | ✅ Real-time | ⚠️ Limited |
| Scaling | ✅ Easy | ❌ Complex |
| Current Config | ✅ Ready | ❌ Needs fixes |

---

## 📞 Support

- Render Docs: https://render.com/docs
- Django Deployment: https://docs.djangoproject.com/en/4.2/howto/deployment/
- Issues: Check Render logs first

---

## 🎯 Quick Start (TL;DR)

```bash
# 1. Push to GitHub
cd /home/fagitone/Documents/GitHub/FagiAssets
git push origin main

# 2. Go to render.com → New Web Service
# 3. Connect FagiAssets repo
# 4. Set:
#    Build: ./build.sh
#    Start: cd assetmanagement && gunicorn assetmanager.wsgi:application --bind 0.0.0.0:$PORT
# 5. Add env vars (DEBUG=False, SECRET_KEY=...)
# 6. Click Deploy
# 7. Visit your URL!
```

**That's it! Your app is live! 🎉**
