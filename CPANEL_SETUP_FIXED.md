# cPanel Deployment Guide - New Supabase Database

## ✅ What's Configured

Your application is now configured to use YOUR NEW Supabase database:
- **Host**: db.kqvalmeduggynzmlddqx.supabase.co
- **Database**: postgres
- **User**: postgres
- **Password**: U)5z5zB#8DqrREe

## 📋 Deployment Steps

### 1. Push to GitHub
```bash
cd /home/fagitone/Documents/GitHub/FagiAssets
git push origin main
```

### 2. Set Up Python Application in cPanel

1. Log into cPanel
2. Go to **Setup Python App**
3. Click **Create Application**

Configure:
- **Python Version**: 3.12
- **Application Root**: /home/yourusername/FagiAssets
- **Application URL**: your-domain.com (or subdomain)
- **Application Startup File**: passenger_wsgi.py
- **Application Entry Point**: application

### 3. Clone Repository

In cPanel Terminal:
```bash
cd ~
git clone https://github.com/yourusername/FagiAssets.git
cd FagiAssets
```

### 4. Configure Environment

Create `.env` file in cPanel File Manager or terminal:
```bash
nano .env
```

Paste this content:
```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database (Supabase)
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=U)5z5zB#8DqrREe
DB_HOST=db.kqvalmeduggynzmlddqx.supabase.co
DB_PORT=5432

# Supabase
SUPABASE_URL=https://kqvalmeduggynzmlddqx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtxdmFsbWVkdWdneW56bWxkZHF4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzM5MTk1MzAsImV4cCI6MjA0OTQ5NTUzMH0.3C_u7TZOoxR7iZKP1XVBiETiDLdcCt47p17Z5_l2x5w

# Redis (optional)
REDIS_URL=redis://127.0.0.1:6379/0
```

### 5. Install Dependencies

In the Python App interface:
1. Click **Run Pip Install**
2. Or in terminal:
```bash
source /home/yourusername/virtualenv/FagiAssets/3.12/bin/activate
pip install -r requirements.txt
```

### 6. Run Migrations

```bash
source /home/yourusername/virtualenv/FagiAssets/3.12/bin/activate
cd ~/FagiAssets/assetmanagement
python manage.py migrate
python manage.py collectstatic --noinput
```

### 7. Create Superuser

```bash
python manage.py createsuperuser
```

### 8. Restart Application

In cPanel Python App interface, click **Restart**

## 🎯 Your New Database Benefits

With your own Supabase database you get:

1. **Full Control** - You own and manage the database
2. **Free Tier Includes**:
   - 500MB database space
   - Unlimited API requests
   - 50,000 monthly active users
   - Real-time subscriptions
   
3. **Automatic Backups** - Supabase provides daily backups
4. **Database Dashboard** - Visual interface at supabase.com
5. **No Data Loss** - Your data is independent of any hosting

## 🔧 Accessing Your Database

### Via Supabase Dashboard
1. Go to https://supabase.com
2. Sign in with your account
3. Select your project
4. Use Table Editor, SQL Editor, or API

### Direct Connection
Use these credentials with any PostgreSQL client:
```
Host: db.kqvalmeduggynzmlddqx.supabase.co
Port: 5432
Database: postgres
User: postgres
Password: U)5z5zB#8DqrREe
```

## 📊 Monitoring

Monitor your database at: https://supabase.com/dashboard/project/kqvalmeduggynzmlddqx

Check:
- Database size
- API requests
- Active connections
- Query performance

## 🚨 Troubleshooting

### Application won't start
```bash
# Check logs in cPanel Python App interface
# Or check passenger logs:
tail -f ~/logs/passenger.log
```

### Database connection fails
```bash
# Test connection:
python manage.py dbshell
# Should connect to your Supabase database
```

### Static files not loading
```bash
python manage.py collectstatic --clear --noinput
```

## ✅ Verification Checklist

- [ ] Application accessible at your domain
- [ ] Can login as superuser
- [ ] Database queries working
- [ ] Static files loading
- [ ] No error in logs

## 📝 Important Files

- `passenger_wsgi.py` - Application entry point (fixed)
- `.env` - Environment variables (create this)
- `assetmanagement/assetmanager/settings.py` - Reads from .env
- `.env.cpanel` - Reference for cPanel configuration

## 🎉 Success!

Once deployed, your application will:
- Run on cPanel hosting
- Use YOUR Supabase database
- Have automatic SSL
- Include automatic backups
- Be fully under your control
