# 🚀 Django Project Hosting Guide

Complete guide for hosting your Django Asset Management & CRM system.

## 📋 Table of Contents
1. [Quick Start (cPanel)](#quick-start-cpanel)
2. [Alternative Hosting Options](#alternative-hosting-options)
3. [Files Overview](#files-overview)
4. [Troubleshooting](#troubleshooting)

---

## 🎯 Quick Start (cPanel)

Since you mentioned you're using cPanel, here's the fastest way to get your project live:

### Prerequisites
- ✅ cPanel hosting account with Python support
- ✅ PostgreSQL database (you mentioned you have this)
- ✅ SSH or FTP access
- ✅ Your domain configured

### 5-Step Deployment

#### Step 1: Prepare Your Local Project
```powershell
# Navigate to your project
cd c:\Users\a\Documents\GitHub\fagiassets

# Install python-decouple (if not already installed)
pip install python-decouple

# Run the setup configuration
python setup_cpanel.py
```

#### Step 2: Upload to cPanel
Choose one method:

**Method A: Git (Recommended)**
```bash
ssh yourusername@yourdomain.com
cd ~
git clone https://github.com/yourusername/fagiassets.git
```

**Method B: FTP**
- Use FileZilla or any FTP client
- Upload all files to `/home/yourusername/fagiassets`

**Method C: cPanel File Manager**
- Zip your project
- Upload via File Manager
- Extract the zip

#### Step 3: Configure Database in cPanel
1. Login to cPanel
2. Go to **PostgreSQL Databases**
3. Create database (e.g., `fagiassets_db`)
4. Create user with strong password
5. Add user to database with ALL PRIVILEGES
6. Note down the credentials

#### Step 4: Deploy
```bash
# SSH into your server
ssh yourusername@yourdomain.com
cd ~/fagiassets

# Make script executable
chmod +x cpanel_deploy.sh

# Run deployment
./cpanel_deploy.sh
```

#### Step 5: Setup Python App in cPanel
1. Go to **Setup Python App** in cPanel
2. Click **Create Application**
3. Configure:
   - **Python Version:** 3.9 or higher
   - **Application Root:** `/home/yourusername/fagiassets`
   - **Application URL:** `/` (or subdomain)
   - **Startup File:** `passenger_wsgi.py`
   - **Entry Point:** `application`
4. Click **Create**
5. Click **Restart**

### 🎉 Done!

Visit your domain: `https://yourdomain.com/login/`

**Default Admin Credentials:**
- Username: `admin`
- Password: `FagiAssets2024!`

---

## 🌐 Alternative Hosting Options

If cPanel doesn't work out, here are other excellent options:

### Option 1: Railway (Easiest)
**Best for:** Production apps, includes database
**Cost:** $5/month free credit
**Setup Time:** 10 minutes

1. Sign up at https://railway.app
2. Click "New Project" → "Deploy from GitHub"
3. Select your repository
4. Add PostgreSQL database
5. Deploy automatically

**Pros:**
- ✅ Includes database hosting
- ✅ Automatic deployments
- ✅ Easy setup
- ✅ No serverless limitations

### Option 2: Render (Free Tier)
**Best for:** Small projects, testing
**Cost:** Free tier available
**Setup Time:** 15 minutes

1. Sign up at https://render.com
2. Create Web Service from GitHub
3. Add PostgreSQL database (free)
4. Configure build/start commands
5. Deploy

**Pros:**
- ✅ Free tier with PostgreSQL
- ✅ Easy to use
- ✅ Good documentation

**Cons:**
- ❌ Spins down after inactivity (free tier)

### Option 3: Vercel (Already Configured!)
**Best for:** Quick deployments
**Cost:** Free tier available
**Setup Time:** 5 minutes

Your project is already configured for Vercel!

```powershell
# Install Vercel CLI
npm install -g vercel

# Deploy
cd c:\Users\a\Documents\GitHub\fagiassets
vercel --prod
```

**Note:** You'll need to use your existing PostgreSQL database (Supabase).

**Pros:**
- ✅ Already configured
- ✅ Fast deployment
- ✅ Global CDN

**Cons:**
- ❌ Requires external database
- ❌ 10-second timeout limit

### Option 4: DigitalOcean App Platform
**Best for:** Professional production apps
**Cost:** Starting at $5/month
**Setup Time:** 15 minutes

1. Sign up at https://digitalocean.com
2. Create App from GitHub
3. Add PostgreSQL database
4. Auto-detects Django
5. Deploy

**Pros:**
- ✅ Professional hosting
- ✅ Scalable
- ✅ Great performance

### Option 5: PythonAnywhere
**Best for:** Beginners, learning
**Cost:** Free tier available
**Setup Time:** 20 minutes

1. Sign up at https://pythonanywhere.com
2. Upload code via Git
3. Setup virtual environment
4. Configure WSGI
5. Use SQLite or upgrade for PostgreSQL

**Pros:**
- ✅ Very beginner-friendly
- ✅ Free tier
- ✅ Good documentation

---

## 📁 Files Overview

Here are the files I created to help you deploy:

### Core Deployment Files

| File | Purpose |
|------|---------|
| `passenger_wsgi.py` | cPanel WSGI entry point |
| `.htaccess` | Apache configuration for cPanel |
| `cpanel_deploy.sh` | Automated deployment script |
| `setup_cpanel.py` | Interactive configuration helper |
| `update_settings_for_cpanel.py` | Updates settings.py for env vars |

### Documentation Files

| File | Purpose |
|------|---------|
| `CPANEL_DEPLOYMENT_GUIDE.md` | Detailed cPanel deployment guide |
| `QUICK_CPANEL_SETUP.md` | Quick reference guide |
| `README_HOSTING.md` | This file - hosting overview |

### Configuration Files

| File | Purpose |
|------|---------|
| `.env.template` | Environment variables template |
| `cpanel_settings.py` | Production settings for cPanel |

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. 500 Internal Server Error

**Check logs:**
```bash
tail -f ~/fagiassets/assetmanagement/django_errors.log
tail -f ~/logs/error_log
```

**Common causes:**
- Incorrect database credentials → Check `.env` file
- Missing dependencies → Run `pip install -r requirements.txt`
- File permissions → Run `chmod -R 755 ~/fagiassets`
- Wrong ALLOWED_HOSTS → Add your domain to `.env`

#### 2. Database Connection Error

**Test connection:**
```bash
cd ~/fagiassets/assetmanagement
python manage.py dbshell
```

**Solutions:**
- Verify credentials in `.env`
- Check PostgreSQL is running
- Ensure user has correct privileges
- Test with: `psql -U username -d database -h host`

#### 3. Static Files Not Loading

**Solutions:**
```bash
# Collect static files again
cd ~/fagiassets/assetmanagement
python manage.py collectstatic --noinput

# Check permissions
chmod -R 755 ~/fagiassets/assetmanagement/staticfiles

# Verify .htaccess configuration
cat ~/fagiassets/.htaccess
```

#### 4. Module Not Found

**Solution:**
```bash
# Activate virtual environment
source ~/virtualenv/fagiassets/3.9/bin/activate

# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

#### 5. Permission Denied

**Solution:**
```bash
cd ~/fagiassets
chmod -R 755 .
chmod -R 777 assetmanagement/media
chmod -R 777 assetmanagement/staticfiles
chmod +x cpanel_deploy.sh
```

---

## 🔄 Updating Your Deployed App

When you make changes to your code:

```bash
# SSH into server
cd ~/fagiassets

# Pull latest changes
git pull origin main

# Activate virtual environment
source ~/virtualenv/fagiassets/3.9/bin/activate

# Install new dependencies
pip install -r requirements.txt

# Run migrations
cd assetmanagement
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart app in cPanel
# Go to Setup Python App → Click Restart
```

---

## 🔒 Security Checklist

Before going live, ensure:

- [ ] Changed `SECRET_KEY` in production
- [ ] Set `DEBUG=False`
- [ ] Updated `ALLOWED_HOSTS` with your domain
- [ ] Using strong database password
- [ ] SSL certificate installed (HTTPS)
- [ ] File permissions set correctly (755 for dirs, 644 for files)
- [ ] Database backups configured
- [ ] Regular security updates scheduled
- [ ] Changed default admin password
- [ ] Removed test/demo users

---

## 📊 Performance Tips

### 1. Enable Database Connection Pooling
Already configured in settings.py with `CONN_MAX_AGE = 600`

### 2. Enable Caching
```python
# Add to settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_cache_table',
    }
}
```

Then run:
```bash
python manage.py createcachetable
```

### 3. Enable Gzip Compression
Already configured in `.htaccess`

### 4. Optimize Static Files
Already using WhiteNoise for static file serving

---

## 💾 Backup Strategy

### Database Backup
```bash
# Create backup script
nano ~/backup_db.sh
```

Add:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=~/backups
mkdir -p $BACKUP_DIR
pg_dump -U your_db_user -h localhost your_db_name > $BACKUP_DIR/db_backup_$DATE.sql
```

Run:
```bash
chmod +x ~/backup_db.sh
./backup_db.sh
```

### Automated Backups
Add to crontab:
```bash
crontab -e
```

Add line:
```
0 2 * * * /home/yourusername/backup_db.sh
```

---

## 📞 Getting Help

1. **Check Documentation:**
   - `CPANEL_DEPLOYMENT_GUIDE.md` - Detailed cPanel guide
   - `QUICK_CPANEL_SETUP.md` - Quick reference
   - `DEPLOYMENT.md` - Original deployment docs

2. **Check Logs:**
   - Django: `~/fagiassets/assetmanagement/django_errors.log`
   - Apache: `~/logs/error_log`
   - Application: cPanel → Setup Python App → View logs

3. **Test Locally First:**
   ```powershell
   cd c:\Users\a\Documents\GitHub\fagiassets\assetmanagement
   python manage.py runserver
   ```

4. **Contact Support:**
   - Your hosting provider for cPanel issues
   - Django documentation: https://docs.djangoproject.com/
   - PostgreSQL docs: https://www.postgresql.org/docs/

---

## 🎓 Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [cPanel Documentation](https://docs.cpanel.net/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [WhiteNoise Documentation](http://whitenoise.evans.io/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)

---

## 📝 Summary

You now have everything you need to host your Django project:

1. **For cPanel:** Use the files and guides I created
2. **For other platforms:** Choose from the alternatives listed
3. **Already configured:** Vercel deployment is ready to go
4. **Database:** You have PostgreSQL ready

**Recommended Path:**
Since you have cPanel and PostgreSQL, I recommend following the **Quick Start (cPanel)** section above. It's the most straightforward for your setup.

**Need help?** Check the troubleshooting section or the detailed guides.

---

**Good luck with your deployment! 🚀**