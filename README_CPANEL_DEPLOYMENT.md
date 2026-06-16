# 🚀 cPanel Deployment - Quick Start Guide

## Your Application is Ready for Deployment!

All configuration files have been created and configured for hosting on **fagicrm.fagitone.com** via cPanel.

---

## 📁 What Has Been Configured

| File | Status | Purpose |
|------|--------|---------|
| `.htaccess` | ✅ Ready | Apache web server configuration |
| `.env` | ⚠️ Update SECRET_KEY | Environment variables |
| `passenger_wsgi.py` | ✅ Ready | WSGI entry point for Passenger |
| `cpanel_deploy.sh` | ✅ Ready | Automated deployment script |
| `requirements.txt` | ✅ Updated | Python dependencies |

---

## ⚡ Quick Start (5 Steps)

### 1️⃣ Generate New SECRET_KEY

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and update `.env` file:
```env
SECRET_KEY=your-newly-generated-key-here
```

### 2️⃣ Upload Files to cPanel

**Via Git (Recommended):**
```bash
ssh distinc3@fagicrm.fagitone.com
cd ~
git clone https://github.com/yourusername/fagiassets.git
```

**Or via FTP:** Upload all files to `/home/distinc3/fagiassets`

### 3️⃣ Setup Python App in cPanel

1. Login to cPanel
2. Go to "Setup Python App"
3. Click "Create Application"
4. Configure:
   - Python: **3.11**
   - Root: **/home/distinc3/fagiassets**
   - Startup: **passenger_wsgi.py**
   - Entry: **application**

### 4️⃣ Run Deployment Script

```bash
ssh distinc3@fagicrm.fagitone.com
cd ~/fagiassets
chmod +x cpanel_deploy.sh
./cpanel_deploy.sh
```

### 5️⃣ Restart & Test

1. In cPanel → Setup Python App → Click "Restart"
2. Visit: **https://fagicrm.fagitone.com**
3. Login: **admin** / **FagiAssets2024!**

---

## 📚 Documentation Files

| Document | Description |
|----------|-------------|
| **DEPLOYMENT_READY.md** | Start here - Overview of what's configured |
| **CPANEL_DEPLOYMENT_INSTRUCTIONS.md** | Complete step-by-step deployment guide |
| **CPANEL_QUICK_REFERENCE.md** | Quick command reference for daily use |
| **DEPLOYMENT_CHECKLIST.txt** | Printable 45-step checklist |
| **CONFIGURATION_SUMMARY.md** | Detailed configuration information |

---

## 🎯 Configuration Summary

```
Domain:          fagicrm.fagitone.com
cPanel User:     distinc3
Python Version:  3.11
Database:        Supabase PostgreSQL
Timezone:        Africa/Nairobi
```

---

## 🔐 Default Credentials

```
URL:      https://fagicrm.fagitone.com/admin/
Username: admin
Password: FagiAssets2024!
```

**⚠️ Change password after first login!**

---

## 🛠️ Common Commands

```bash
# Deploy/Update
cd ~/fagiassets && ./cpanel_deploy.sh

# View Logs
tail -f ~/logs/error_log

# Restart App
touch ~/fagiassets/passenger_wsgi.py

# Collect Static Files
cd ~/fagiassets/assetmanagement
python manage.py collectstatic --noinput
```

---

## 🆘 Troubleshooting

### 500 Error
```bash
tail -f ~/logs/error_log
```

### Static Files Not Loading
```bash
cd ~/fagiassets/assetmanagement
python manage.py collectstatic --noinput --clear
# Then restart app in cPanel
```

### Database Connection Error
```bash
cd ~/fagiassets/assetmanagement
python manage.py check --database default
```

---

## ✅ Pre-Deployment Checklist

- [ ] Generated new SECRET_KEY
- [ ] Updated .env file
- [ ] Verified database credentials
- [ ] Uploaded all files to server
- [ ] Created Python app in cPanel
- [ ] Made cpanel_deploy.sh executable

---

## 📖 Next Steps

1. **Read:** DEPLOYMENT_READY.md
2. **Follow:** CPANEL_DEPLOYMENT_INSTRUCTIONS.md
3. **Track:** DEPLOYMENT_CHECKLIST.txt
4. **Reference:** CPANEL_QUICK_REFERENCE.md

---

## 🎉 Ready to Deploy!

Everything is configured and ready. Follow the documentation to deploy your application.

**Good luck! 🚀**

---

**Questions?** Check the troubleshooting section in CPANEL_DEPLOYMENT_INSTRUCTIONS.md