# Quick cPanel Setup Guide

## 🚀 Fast Track Deployment (15 minutes)

### Step 1: Prepare Database (5 minutes)
1. Login to cPanel
2. Go to **PostgreSQL Databases**
3. Create database: `fagiassets_db`
4. Create user with strong password
5. Add user to database with ALL PRIVILEGES
6. **Write down credentials!**

### Step 2: Upload Files (3 minutes)
```bash
# Option A: Git (Recommended)
ssh yourusername@yourdomain.com
cd ~
git clone https://github.com/yourusername/fagiassets.git

# Option B: FTP
# Upload all files to /home/yourusername/fagiassets
```

### Step 3: Configure Environment (2 minutes)
```bash
cd ~/fagiassets
python3 setup_cpanel.py
# Follow the prompts to enter your database credentials
```

### Step 4: Deploy (3 minutes)
```bash
chmod +x cpanel_deploy.sh
./cpanel_deploy.sh
```

### Step 5: Setup Python App in cPanel (2 minutes)
1. Go to **Setup Python App**
2. Click **Create Application**
3. Set:
   - Python: 3.9
   - App Root: `/home/yourusername/fagiassets`
   - App URL: `/` (or your subdomain)
   - Startup: `passenger_wsgi.py`
   - Entry: `application`
4. Click **Create**
5. Click **Restart**

### Step 6: Test! ✅
Visit: `https://yourdomain.com/login/`

**Default Admin:**
- Username: `admin`
- Password: `FagiAssets2024!`

---

## 🔧 Troubleshooting

### Can't connect to database?
```bash
# Test database connection
cd ~/fagiassets/assetmanagement
python manage.py dbshell
```

### 500 Error?
```bash
# Check logs
tail -f ~/fagiassets/assetmanagement/django_errors.log
tail -f ~/logs/error_log
```

### Static files not loading?
```bash
cd ~/fagiassets/assetmanagement
python manage.py collectstatic --noinput
# Then restart app in cPanel
```

### Module not found?
```bash
source ~/virtualenv/fagiassets/3.9/bin/activate
pip install -r requirements.txt
```

---

## 📝 Important Files Created

- `passenger_wsgi.py` - cPanel WSGI entry point
- `.htaccess` - Apache configuration
- `cpanel_deploy.sh` - Deployment script
- `setup_cpanel.py` - Configuration helper
- `.env` - Environment variables (created by setup)

---

## 🔄 Updating Your App

```bash
cd ~/fagiassets
git pull origin main
source ~/virtualenv/fagiassets/3.9/bin/activate
pip install -r requirements.txt
cd assetmanagement
python manage.py migrate
python manage.py collectstatic --noinput
# Restart app in cPanel
```

---

## 📞 Need Help?

1. Check `CPANEL_DEPLOYMENT_GUIDE.md` for detailed instructions
2. Review error logs
3. Contact your hosting provider for cPanel issues

---

## ✅ Post-Deployment Checklist

- [ ] Database created and configured
- [ ] Files uploaded to server
- [ ] .env file configured
- [ ] Dependencies installed
- [ ] Migrations run
- [ ] Static files collected
- [ ] Superuser created
- [ ] Python app created in cPanel
- [ ] App restarted
- [ ] Website accessible
- [ ] Login working
- [ ] Admin panel accessible
- [ ] SSL certificate installed (recommended)

---

**That's it! Your Django app should now be live on cPanel! 🎉**