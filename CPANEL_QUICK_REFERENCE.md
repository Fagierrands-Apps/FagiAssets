# cPanel Quick Reference Card

## 🚀 Quick Deploy Commands

```bash
# SSH into server
ssh distinc3@fagicrm.fagitone.com

# Navigate to project
cd ~/fagiassets

# Deploy/Update
./cpanel_deploy.sh

# Restart app in cPanel → Setup Python App → Restart
```

## 📁 Important Paths

```
Project Root:    /home/distinc3/fagiassets
Virtual Env:     /home/distinc3/virtualenv/fagiassets/3.11
Django Project:  /home/distinc3/fagiassets/assetmanagement
Static Files:    /home/distinc3/fagiassets/assetmanagement/staticfiles
Media Files:     /home/distinc3/fagiassets/assetmanagement/media
Logs:            ~/logs/error_log
```

## 🔑 Default Credentials

```
Username: admin
Password: FagiAssets2024!
Domain:   https://fagicrm.fagitone.com
```

## 🛠️ Common Commands

### Activate Virtual Environment
```bash
source ~/virtualenv/fagiassets/3.11/bin/activate
```

### Update Application
```bash
cd ~/fagiassets
git pull origin main
./cpanel_deploy.sh
# Then restart in cPanel
```

### Collect Static Files
```bash
cd ~/fagiassets/assetmanagement
python manage.py collectstatic --noinput
```

### Run Migrations
```bash
cd ~/fagiassets/assetmanagement
python manage.py migrate
```

### Create Superuser
```bash
cd ~/fagiassets/assetmanagement
python manage.py createsuperuser
```

### Change Admin Password
```bash
cd ~/fagiassets/assetmanagement
python manage.py changepassword admin
```

### Check Django Configuration
```bash
cd ~/fagiassets/assetmanagement
python manage.py check
```

### Test Database Connection
```bash
cd ~/fagiassets/assetmanagement
python manage.py check --database default
```

## 📊 View Logs

```bash
# Apache error log (real-time)
tail -f ~/logs/error_log

# Apache error log (last 50 lines)
tail -n 50 ~/logs/error_log

# Apache access log
tail -f ~/logs/access_log
```

## 🔧 Fix Common Issues

### 500 Error
```bash
# Check logs
tail -f ~/logs/error_log

# Redeploy
cd ~/fagiassets
./cpanel_deploy.sh
```

### Static Files Not Loading
```bash
cd ~/fagiassets/assetmanagement
source ~/virtualenv/fagiassets/3.11/bin/activate
python manage.py collectstatic --noinput --clear
# Restart app in cPanel
```

### Permission Issues
```bash
cd ~/fagiassets
chmod -R 755 .
chmod -R 775 assetmanagement/media
chmod -R 775 assetmanagement/staticfiles
```

### Database Connection Error
```bash
# Check .env file
cat ~/fagiassets/.env | grep DB_

# Test connection
cd ~/fagiassets/assetmanagement
python manage.py check --database default
```

## 📝 Important Files

```
.htaccess              → Apache configuration
.env                   → Environment variables
passenger_wsgi.py      → WSGI entry point
cpanel_deploy.sh       → Deployment script
requirements.txt       → Python dependencies
```

## 🔄 Restart Application

**Method 1: cPanel (Recommended)**
1. Login to cPanel
2. Go to "Setup Python App"
3. Find your app
4. Click "Restart" button

**Method 2: Touch passenger_wsgi.py**
```bash
touch ~/fagiassets/passenger_wsgi.py
```

## 🔐 Security

### Generate New SECRET_KEY
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Update .env with new key
```bash
nano ~/fagiassets/.env
# Update SECRET_KEY line
# Save: Ctrl+X, Y, Enter
```

## 📦 Install New Package

```bash
cd ~/fagiassets
source ~/virtualenv/fagiassets/3.11/bin/activate
pip install package-name
pip freeze > requirements.txt
```

## 🗄️ Database Operations

### Backup Database
```bash
cd ~/fagiassets/assetmanagement
python manage.py dumpdata > backup_$(date +%Y%m%d).json
```

### Restore Database
```bash
cd ~/fagiassets/assetmanagement
python manage.py loaddata backup_20240101.json
```

### Django Shell
```bash
cd ~/fagiassets/assetmanagement
python manage.py shell
```

## 🌐 URLs

```
Main Site:    https://fagicrm.fagitone.com
Admin Panel:  https://fagicrm.fagitone.com/admin/
Login Page:   https://fagicrm.fagitone.com/login/
```

## 📞 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| 500 Error | Check `tail -f ~/logs/error_log` |
| No CSS/JS | Run `collectstatic` and restart |
| Can't login | Check database connection |
| Permission denied | Run `chmod -R 755 ~/fagiassets` |
| Module not found | Run `pip install -r requirements.txt` |

## 💡 Pro Tips

1. **Always activate virtual environment** before running Python commands
2. **Restart app after changes** to .env or Python files
3. **Check logs first** when troubleshooting
4. **Backup before major changes**
5. **Test locally** before deploying to production

## 🆘 Emergency Commands

```bash
# Stop everything and redeploy
cd ~/fagiassets
./cpanel_deploy.sh

# Reset permissions
chmod -R 755 ~/fagiassets
chmod -R 775 ~/fagiassets/assetmanagement/media

# Clear Python cache
find ~/fagiassets -type d -name __pycache__ -exec rm -r {} +
find ~/fagiassets -type f -name "*.pyc" -delete

# Force restart
touch ~/fagiassets/passenger_wsgi.py
```

---

**Keep this file handy for quick reference!**