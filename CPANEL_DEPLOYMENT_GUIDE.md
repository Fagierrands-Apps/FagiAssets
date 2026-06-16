# Django Project - cPanel Deployment Guide

## Prerequisites
- cPanel hosting account with Python support
- PostgreSQL database access
- SSH access (recommended) or FTP access
- Your domain or subdomain configured

## Step-by-Step Deployment

### 1. Prepare PostgreSQL Database

1. **Login to cPanel**
2. **Navigate to PostgreSQL Databases**
3. **Create Database:**
   - Database name: `fagiassets_db` (or your choice)
   - Click "Create Database"
4. **Create User:**
   - Username: `fagiassets_user`
   - Password: Generate a strong password
   - Click "Create User"
5. **Add User to Database:**
   - Select user and database
   - Grant ALL PRIVILEGES
   - Click "Add"
6. **Note down credentials:**
   ```
   Database Name: yourusername_fagiassets_db
   Database User: yourusername_fagiassets_user
   Database Password: [your password]
   Database Host: localhost
   Database Port: 5432
   ```

### 2. Set Up Python Application

1. **In cPanel, go to "Setup Python App"**
2. **Click "Create Application"**
3. **Configure:**
   ```
   Python Version: 3.9 (or highest available)
   Application Root: /home/yourusername/fagiassets
   Application URL: / (or your subdomain)
   Application Startup File: passenger_wsgi.py
   Application Entry Point: application
   ```
4. **Click "Create"**
5. **Note the virtual environment path** (e.g., `/home/yourusername/virtualenv/fagiassets/3.9`)

### 3. Upload Project Files

#### Option A: Using Git (Recommended)
```bash
# SSH into your server
ssh yourusername@yourdomain.com

# Navigate to home directory
cd ~

# Clone repository
git clone https://github.com/yourusername/fagiassets.git

# Or if already exists, pull latest changes
cd fagiassets
git pull origin main
```

#### Option B: Using FTP
1. Connect via FTP client (FileZilla, etc.)
2. Upload all project files to `/home/yourusername/fagiassets`
3. Ensure all files are uploaded including hidden files (.htaccess, .env)

#### Option C: Using cPanel File Manager
1. Go to File Manager in cPanel
2. Navigate to home directory
3. Upload project as ZIP file
4. Extract the ZIP file

### 4. Configure Environment Variables

Create a `.env` file in your project root:

```bash
# SSH into your server
cd ~/fagiassets
nano .env
```

Add the following (replace with your actual values):

```env
# Django Settings
SECRET_KEY=your-secret-key-here-change-this-in-production
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database Settings
DB_NAME=yourusername_fagiassets_db
DB_USER=yourusername_fagiassets_user
DB_PASSWORD=your_database_password_here
DB_HOST=localhost
DB_PORT=5432

# Application Settings
DJANGO_SETTINGS_MODULE=assetmanager.settings
```

Save and exit (Ctrl+X, then Y, then Enter)

### 5. Update Settings for cPanel

Edit `assetmanagement/assetmanager/settings.py`:

```python
# At the top, add:
from decouple import config
import dj_database_url

# Update SECRET_KEY
SECRET_KEY = config('SECRET_KEY', default='django-insecure-)uydf_yg5c=z5^)xi+&$1@y$7w@)lboa2l#eom$!4uk1l!22u0')

# Update DEBUG
DEBUG = config('DEBUG', default=False, cast=bool)

# Update ALLOWED_HOSTS
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Update DATABASES
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='fagiassets_db'),
        'USER': config('DB_USER', default='fagiassets_user'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {
            'connect_timeout': 30,
        },
        'CONN_MAX_AGE': 600,
    }
}
```

### 6. Install Dependencies and Deploy

```bash
# SSH into your server
cd ~/fagiassets

# Make deployment script executable
chmod +x cpanel_deploy.sh

# Run deployment script
./cpanel_deploy.sh
```

Or manually:

```bash
# Activate virtual environment
source ~/virtualenv/fagiassets/3.9/bin/activate

# Install dependencies
pip install -r requirements.txt

# Navigate to Django project
cd assetmanagement

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser
```

### 7. Configure Static Files

#### Option A: Serve via Apache (Recommended)
Edit `.htaccess` in project root:

```apache
# Static files
Alias /static /home/yourusername/fagiassets/assetmanagement/staticfiles
<Directory /home/yourusername/fagiassets/assetmanagement/staticfiles>
    Require all granted
</Directory>

# Media files
Alias /media /home/yourusername/fagiassets/assetmanagement/media
<Directory /home/yourusername/fagiassets/assetmanagement/media>
    Require all granted
</Directory>
```

#### Option B: Create Symbolic Links
```bash
cd ~/public_html
ln -s ~/fagiassets/assetmanagement/staticfiles static
ln -s ~/fagiassets/assetmanagement/media media
```

### 8. Set File Permissions

```bash
cd ~/fagiassets

# Set directory permissions
find . -type d -exec chmod 755 {} \;

# Set file permissions
find . -type f -exec chmod 644 {} \;

# Make scripts executable
chmod +x cpanel_deploy.sh

# Set write permissions for media and logs
chmod -R 777 assetmanagement/media
chmod -R 777 assetmanagement/staticfiles
```

### 9. Restart Python Application

1. **Go to cPanel → Setup Python App**
2. **Find your application**
3. **Click "Restart"** or **"Stop/Start"**
4. **Wait for the application to restart**

### 10. Test Your Deployment

1. **Visit your domain:** `https://yourdomain.com`
2. **Test login:** `https://yourdomain.com/login/`
3. **Access admin:** `https://yourdomain.com/admin/`
4. **Check static files are loading** (CSS, JS, images)

## Troubleshooting

### Issue: 500 Internal Server Error

**Check error logs:**
```bash
# View Django error log
tail -f ~/fagiassets/assetmanagement/django_errors.log

# View Apache error log
tail -f ~/logs/error_log
```

**Common causes:**
- Incorrect database credentials
- Missing dependencies
- File permission issues
- Incorrect ALLOWED_HOSTS

### Issue: Static Files Not Loading

**Solutions:**
1. Run `python manage.py collectstatic` again
2. Check `.htaccess` configuration
3. Verify file permissions (755 for directories, 644 for files)
4. Check STATIC_ROOT and STATIC_URL in settings.py

### Issue: Database Connection Error

**Check:**
1. Database credentials in `.env` file
2. PostgreSQL service is running
3. User has correct privileges
4. Database exists

**Test connection:**
```bash
cd ~/fagiassets/assetmanagement
python manage.py dbshell
```

### Issue: Module Not Found

**Solution:**
```bash
# Activate virtual environment
source ~/virtualenv/fagiassets/3.9/bin/activate

# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

### Issue: Permission Denied

**Solution:**
```bash
# Fix permissions
cd ~/fagiassets
chmod -R 755 .
chmod -R 777 assetmanagement/media
chmod -R 777 assetmanagement/staticfiles
```

## Updating Your Application

When you make changes to your code:

```bash
# SSH into server
cd ~/fagiassets

# Pull latest changes (if using Git)
git pull origin main

# Activate virtual environment
source ~/virtualenv/fagiassets/3.9/bin/activate

# Install any new dependencies
pip install -r requirements.txt

# Run migrations
cd assetmanagement
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart application in cPanel
# Go to Setup Python App → Click Restart
```

## Security Checklist

- [ ] Changed SECRET_KEY in production
- [ ] Set DEBUG=False
- [ ] Updated ALLOWED_HOSTS with your domain
- [ ] Using strong database password
- [ ] SSL certificate installed (HTTPS)
- [ ] File permissions set correctly
- [ ] Database backups configured
- [ ] Regular security updates

## Performance Optimization

### Enable Caching
Add to settings.py:
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_cache_table',
    }
}
```

Create cache table:
```bash
python manage.py createcachetable
```

### Enable Gzip Compression
Add to `.htaccess`:
```apache
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css text/javascript application/javascript
</IfModule>
```

### Database Connection Pooling
Already configured in settings.py with `CONN_MAX_AGE = 600`

## Backup Strategy

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
pg_dump -U yourusername_fagiassets_user -h localhost fagiassets_db > $BACKUP_DIR/db_backup_$DATE.sql
```

Make executable and run:
```bash
chmod +x ~/backup_db.sh
./backup_db.sh
```

### File Backup
```bash
# Backup media files
tar -czf ~/backups/media_backup_$(date +%Y%m%d).tar.gz ~/fagiassets/assetmanagement/media
```

## Support

If you encounter issues:
1. Check error logs
2. Review this guide
3. Contact your hosting provider for cPanel-specific issues
4. Check Django documentation: https://docs.djangoproject.com/

## Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [cPanel Documentation](https://docs.cpanel.net/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)