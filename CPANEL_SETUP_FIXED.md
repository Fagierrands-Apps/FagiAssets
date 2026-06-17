# cPanel Deployment - Fixed Version

## Prerequisites
- cPanel account (you have this ✅)
- Your own Supabase database (create above ☝️)
- SSH access (optional but helpful)

---

## Quick Setup (15 minutes)

### 1. Update passenger_wsgi.py

Replace the current one with this fixed version:

```python
import os
import sys
from pathlib import Path

# Project paths
project_home = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(project_home, 'assetmanagement')

# Add to path
sys.path.insert(0, project_home)
sys.path.insert(0, project_dir)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
os.environ['DEBUG'] = 'False'

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(project_home, '.env'))

# Import Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 2. Create .env file in root directory

```env
# Django Settings
SECRET_KEY=your-new-secret-key-here-change-this
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Your NEW Supabase Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
DB_USER=postgres.xxxxxxxxxxxxx
DB_PASSWORD=your-supabase-password
DB_HOST=aws-0-ap-southeast-1.pooler.supabase.com
DB_PORT=6543

# App Settings  
DJANGO_SETTINGS_MODULE=assetmanager.settings
```

### 3. Update settings.py to read from .env

Add this at the top of `assetmanagement/assetmanager/settings.py`:

```python
from decouple import config
import os

# Read from environment
SECRET_KEY = config('SECRET_KEY', default='django-insecure-)uydf_yg5c=z5^)xi+&$1@y$7w@)lboa2l#eom$!4uk1l!22u0')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*').split(',')

# Database from environment
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.postgresql'),
        'NAME': config('DB_NAME', default='postgres'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', default='6543'),
        'OPTIONS': {
            'sslmode': 'require',
            'connect_timeout': 30,
        },
    }
}
```

### 4. Upload to cPanel

**Via FTP/File Manager:**
1. Upload entire project to `/home/yourusername/fagiassets`
2. Upload `.env` file with YOUR database credentials
3. Make sure `passenger_wsgi.py` is in root

**Via Git (better):**
```bash
ssh yourusername@yourdomain.com
cd ~
git clone https://github.com/Fagierrands-Apps/FagiAssets.git fagiassets
cd fagiassets
nano .env  # Add your credentials
```

### 5. Setup Python App in cPanel

1. Go to **Setup Python App**
2. Click **Create Application**
3. Configure:
   - Python version: 3.11 (or 3.9)
   - Application root: `/home/yourusername/fagiassets`
   - Application URL: `/` (or subdomain)
   - Startup file: `passenger_wsgi.py`
   - Entry point: `application`

4. Click **Create**

5. In the Python app page, click **Enter to virtual environment**

6. Run setup commands:
```bash
pip install -r requirements.txt
cd assetmanagement
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 6. Configure .htaccess

The current .htaccess has hardcoded paths. Update it:

```apache
PassengerEnabled On
PassengerAppRoot /home/YOURUSERNAME/fagiassets
PassengerPython /home/YOURUSERNAME/virtualenv/fagiassets/3.11/bin/python

# Replace YOURUSERNAME with your actual cPanel username
```

### 7. Restart App

In cPanel → Python App → Click **Restart**

---

## Migration from Old Supabase to Your New One

Once your new database is set up:

```bash
# SSH into cPanel
cd ~/fagiassets/assetmanagement

# Activate virtual environment
source ~/virtualenv/fagiassets/3.11/bin/activate

# Export data from old database (if you still have access)
python manage.py dumpdata > backup.json

# Update .env with new database credentials
nano ../.env

# Run migrations on new database
python manage.py migrate

# Import data
python manage.py loaddata backup.json

# Create admin user
python manage.py createsuperuser
```

---

## Backup Strategy

With YOUR Supabase:

1. **Automatic backups** (Supabase does daily)
2. **Manual export:**
```bash
python manage.py dumpdata --indent 2 > backup_$(date +%Y%m%d).json
```

3. **Download from Supabase dashboard:**
   - Settings → Database → Backups
   - Can restore to any point in time (paid plans)

---

## Cost Summary

| Service | Cost | What You Get |
|---------|------|--------------|
| cPanel | $X/month | Hosting (already paying) |
| Supabase | **FREE** | 500MB DB, daily backups |
| **Total** | Same as now | Full control! |

---

## Benefits of This Setup

✅ Use cPanel you're already paying for
✅ Own your database with full access
✅ Daily automatic backups
✅ Can export/import data anytime
✅ No vendor lock-in
✅ Better performance (cPanel + Supabase)
✅ Can migrate to PostgreSQL on cPanel later

---

## Next Steps

1. Create your Supabase account
2. Get new database credentials
3. Update `.env` and `settings.py`
4. Push to GitHub
5. Deploy to cPanel
6. Migrate data from old database

**Want me to help you with any of these steps?**
