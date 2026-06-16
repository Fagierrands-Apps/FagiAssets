# cPanel Deployment Instructions for fagicrm.fagitone.com

## 📋 Prerequisites Checklist

Before starting, ensure you have:
- ✅ cPanel access with Python support
- ✅ SSH access to your server (recommended)
- ✅ Domain: `fagicrm.fagitone.com` configured
- ✅ Supabase PostgreSQL database credentials
- ✅ cPanel username: `distinc3`

## 🚀 Quick Deployment Steps

### Step 1: Setup Python Application in cPanel

1. **Login to cPanel** at your hosting provider
2. **Navigate to "Setup Python App"** (under Software section)
3. **Click "Create Application"**
4. **Configure the application:**
   ```
   Python Version: 3.11
   Application Root: /home/distinc3/fagiassets
   Application URL: / (or leave blank for root domain)
   Application Startup File: passenger_wsgi.py
   Application Entry Point: application
   ```
5. **Click "Create"**
6. **Note the virtual environment path** (should be `/home/distinc3/virtualenv/fagiassets/3.11`)

### Step 2: Upload Project Files

#### Option A: Using SSH and Git (Recommended)

```bash
# SSH into your server
ssh distinc3@fagicrm.fagitone.com

# Navigate to home directory
cd ~

# Clone your repository
git clone https://github.com/yourusername/fagiassets.git

# Or if already exists, pull latest changes
cd fagiassets
git pull origin main
```

#### Option B: Using FTP/SFTP

1. Connect using FileZilla or similar FTP client
2. Upload all files to `/home/distinc3/fagiassets`
3. **Important:** Make sure to upload hidden files:
   - `.htaccess`
   - `.env`
   - `.gitignore`

#### Option C: Using cPanel File Manager

1. Go to **File Manager** in cPanel
2. Navigate to home directory
3. Click **Upload** and select your project ZIP file
4. Right-click the ZIP file and select **Extract**

### Step 3: Configure Environment Variables

The `.env` file is already configured with your settings. **Important:** Update the SECRET_KEY!

```bash
# SSH into your server
cd ~/fagiassets

# Generate a new SECRET_KEY
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Edit .env file
nano .env
```

Replace the SECRET_KEY line with your newly generated key:
```env
SECRET_KEY=your-newly-generated-secret-key-here
```

Save and exit (Ctrl+X, then Y, then Enter)

### Step 4: Run Deployment Script

```bash
# SSH into your server
cd ~/fagiassets

# Make the deployment script executable
chmod +x cpanel_deploy.sh

# Run the deployment script
./cpanel_deploy.sh
```

The script will:
- ✅ Activate virtual environment
- ✅ Install all dependencies
- ✅ Test database connection
- ✅ Run migrations
- ✅ Collect static files
- ✅ Create admin user
- ✅ Set proper permissions

### Step 5: Restart Python Application

1. **Go back to cPanel**
2. **Navigate to "Setup Python App"**
3. **Find your application** (fagiassets)
4. **Click the "Restart" button** (circular arrow icon)
5. **Wait for the application to restart** (usually takes 10-30 seconds)

### Step 6: Test Your Deployment

1. **Visit your domain:** https://fagicrm.fagitone.com
2. **Test login page:** https://fagicrm.fagitone.com/login/
3. **Login with default credentials:**
   - Username: `admin`
   - Password: `FagiAssets2024!`
4. **Access admin panel:** https://fagicrm.fagitone.com/admin/

## 📁 Important Files Configured

### 1. `.htaccess` - Apache Configuration
Located at: `/home/distinc3/fagiassets/.htaccess`

Features:
- ✅ Passenger configuration for Python 3.11
- ✅ HTTPS redirect (forces SSL)
- ✅ Static files served directly by Apache
- ✅ Media files served directly by Apache
- ✅ Security headers
- ✅ Gzip compression
- ✅ Protection for sensitive files

### 2. `.env` - Environment Variables
Located at: `/home/distinc3/fagiassets/.env`

Contains:
- ✅ Django settings (DEBUG, SECRET_KEY, ALLOWED_HOSTS)
- ✅ Database credentials (Supabase PostgreSQL)
- ✅ Static/Media file paths
- ✅ Security settings
- ✅ Application settings

### 3. `passenger_wsgi.py` - WSGI Entry Point
Located at: `/home/distinc3/fagiassets/passenger_wsgi.py`

Features:
- ✅ Loads environment variables from .env
- ✅ Configures Python path
- ✅ Error handling and logging
- ✅ Django WSGI application

## 🔧 Troubleshooting

### Issue: 500 Internal Server Error

**Check error logs:**
```bash
# Apache error log
tail -f ~/logs/error_log

# Django application log (if configured)
tail -f ~/fagiassets/assetmanagement/logs/django.log
```

**Common causes:**
1. Incorrect database credentials → Check `.env` file
2. Missing dependencies → Run `./cpanel_deploy.sh` again
3. File permission issues → Run `chmod -R 755 ~/fagiassets`
4. Incorrect ALLOWED_HOSTS → Check `.env` has correct domain

### Issue: Static Files Not Loading (CSS/JS missing)

**Solution:**
```bash
cd ~/fagiassets
source ~/virtualenv/fagiassets/3.11/bin/activate
cd assetmanagement
python manage.py collectstatic --noinput --clear
```

Then restart the Python app in cPanel.

### Issue: Database Connection Error

**Test database connection:**
```bash
cd ~/fagiassets/assetmanagement
source ~/virtualenv/fagiassets/3.11/bin/activate
python manage.py check --database default
```

**If it fails:**
1. Verify Supabase credentials in `.env`
2. Check if Supabase allows connections from your server IP
3. Test connection manually:
   ```bash
   psql -h aws-0-ap-southeast-1.pooler.supabase.com -p 6543 -U postgres.dxesmzogjpxswxhsomgf -d postgres
   ```

### Issue: Module Not Found

**Reinstall dependencies:**
```bash
cd ~/fagiassets
source ~/virtualenv/fagiassets/3.11/bin/activate
pip install -r requirements.txt --force-reinstall
```

### Issue: Permission Denied

**Fix permissions:**
```bash
cd ~/fagiassets
chmod -R 755 .
chmod -R 775 assetmanagement/media
chmod -R 775 assetmanagement/staticfiles
chmod +x cpanel_deploy.sh
```

## 🔄 Updating Your Application

When you make changes to your code:

```bash
# SSH into server
cd ~/fagiassets

# Pull latest changes (if using Git)
git pull origin main

# Run deployment script
./cpanel_deploy.sh

# Restart application in cPanel
# Go to Setup Python App → Click Restart
```

## 🔒 Security Checklist

After deployment, verify:

- [ ] Changed SECRET_KEY in `.env` file
- [ ] DEBUG=False in `.env` file
- [ ] ALLOWED_HOSTS contains only your domain
- [ ] HTTPS is working (SSL certificate installed)
- [ ] Changed default admin password
- [ ] File permissions are correct (755 for dirs, 644 for files)
- [ ] Sensitive files are protected by .htaccess
- [ ] Database backups are configured

## 📊 Performance Optimization

### Enable Database Caching

```bash
cd ~/fagiassets/assetmanagement
source ~/virtualenv/fagiassets/3.11/bin/activate
python manage.py createcachetable
```

### Monitor Application Performance

```bash
# Check memory usage
free -h

# Check disk usage
df -h

# Check Python processes
ps aux | grep python

# Monitor logs in real-time
tail -f ~/logs/error_log
```

## 🔐 SSL Certificate Setup

If SSL is not already configured:

1. **In cPanel, go to "SSL/TLS Status"**
2. **Find your domain** (fagicrm.fagitone.com)
3. **Click "Run AutoSSL"**
4. **Wait for certificate to be issued** (usually 1-5 minutes)
5. **Verify HTTPS works:** https://fagicrm.fagitone.com

## 📞 Support & Resources

### Useful Commands

```bash
# Check Python version
python --version

# Check Django version
python -c "import django; print(django.get_version())"

# Test Django configuration
cd ~/fagiassets/assetmanagement
python manage.py check

# Create new superuser
python manage.py createsuperuser

# View database tables
python manage.py dbshell

# Run Django shell
python manage.py shell
```

### Log Files Locations

- Apache Error Log: `~/logs/error_log`
- Apache Access Log: `~/logs/access_log`
- Django Logs: `~/fagiassets/assetmanagement/logs/`

### Important URLs

- **Application:** https://fagicrm.fagitone.com
- **Admin Panel:** https://fagicrm.fagitone.com/admin/
- **Login Page:** https://fagicrm.fagitone.com/login/
- **API Docs:** https://fagicrm.fagitone.com/api/ (if configured)

## 🎯 Default Login Credentials

**Admin User:**
- Username: `admin`
- Password: `FagiAssets2024!`
- Email: `admin@fagicrm.fagitone.com`

**⚠️ IMPORTANT:** Change this password immediately after first login!

```bash
cd ~/fagiassets/assetmanagement
source ~/virtualenv/fagiassets/3.11/bin/activate
python manage.py changepassword admin
```

## 📝 Configuration Summary

| Setting | Value |
|---------|-------|
| Domain | fagicrm.fagitone.com |
| cPanel User | distinc3 |
| Python Version | 3.11 |
| Project Root | /home/distinc3/fagiassets |
| Virtual Env | /home/distinc3/virtualenv/fagiassets/3.11 |
| Django Project | /home/distinc3/fagiassets/assetmanagement |
| Static Files | /home/distinc3/fagiassets/assetmanagement/staticfiles |
| Media Files | /home/distinc3/fagiassets/assetmanagement/media |
| Database | Supabase PostgreSQL |
| WSGI File | passenger_wsgi.py |

## ✅ Post-Deployment Checklist

- [ ] Application loads at https://fagicrm.fagitone.com
- [ ] Login page works
- [ ] Admin panel accessible
- [ ] Static files (CSS/JS) loading correctly
- [ ] Database connection working
- [ ] Can create/edit/delete records
- [ ] Media uploads working
- [ ] HTTPS redirect working
- [ ] Changed default admin password
- [ ] Tested all major features

---

**Need Help?** Check the logs first:
```bash
tail -f ~/logs/error_log
```

**Still stuck?** Review the troubleshooting section above or contact your hosting provider's support.