import os, django, sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'assetmanager.settings_production'
django.setup()

from django.conf import settings
from django.contrib.auth.models import User
from crm.models import Employee

issues = []
warnings = []
info = []

# ── 1. Django security checks ──────────────────────────────────────────────
from django.core.management import call_command
from io import StringIO
out = StringIO()
call_command('check', '--deploy', stdout=out, stderr=out)
output = out.getvalue()
for line in output.splitlines():
    if line.strip():
        issues.append(f"[DJANGO CHECK] {line.strip()}")

# ── 2. Settings audit ──────────────────────────────────────────────────────
if settings.DEBUG:
    issues.append("[CRITICAL] DEBUG=True in production")
if settings.SECRET_KEY in ('your-secret-key-here', 'django-insecure', ''):
    issues.append("[CRITICAL] SECRET_KEY is default/empty")
if not settings.SECURE_SSL_REDIRECT:
    warnings.append("[WARN] SECURE_SSL_REDIRECT is False")
if not settings.SESSION_COOKIE_SECURE:
    warnings.append("[WARN] SESSION_COOKIE_SECURE is False")
if not settings.CSRF_COOKIE_SECURE:
    warnings.append("[WARN] CSRF_COOKIE_SECURE is False")
if not getattr(settings, 'SECURE_HSTS_SECONDS', 0):
    warnings.append("[WARN] HSTS not configured (SECURE_HSTS_SECONDS=0)")
if not getattr(settings, 'X_FRAME_OPTIONS', None):
    warnings.append("[WARN] X_FRAME_OPTIONS not set (clickjacking risk)")
if '*' in settings.ALLOWED_HOSTS:
    warnings.append("[WARN] ALLOWED_HOSTS contains wildcard '*'")

# ── 3. Database credentials in code ───────────────────────────────────────
import subprocess
result = subprocess.run(
    ['grep', '-rn', '-E', 'PASSWORD|password|secret|SECRET', '--include=*.py',
     '--exclude=security_check.py', '.'],
    capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__))
)
for line in result.stdout.splitlines():
    if any(x in line for x in ['Pa7swrd', 'OnFRtf0', 'U)5z5z', 'your-secret']):
        issues.append(f"[CRITICAL] Hardcoded credential: {line.strip()[:120]}")

# ── 4. User audit ──────────────────────────────────────────────────────────
superusers = User.objects.filter(is_superuser=True)
info.append(f"[INFO] Superusers: {[u.username for u in superusers]}")

no_profile = []
for u in User.objects.filter(is_superuser=False, is_staff=False):
    if not hasattr(u, 'employee_profile'):
        no_profile.append(u.username)
if no_profile:
    warnings.append(f"[WARN] Users without employee profile: {no_profile}")

# ── 5. Exposed sensitive URLs ──────────────────────────────────────────────
from django.urls import reverse
try:
    reverse('django.contrib.admin:index')
    info.append("[INFO] Django /admin/ is enabled — ensure it's restricted")
except:
    pass

# ── 6. Missing migrations ──────────────────────────────────────────────────
out2 = StringIO()
call_command('migrate', '--check', stdout=out2, stderr=out2)
migrate_out = out2.getvalue()
if 'unapplied' in migrate_out.lower() or 'no migrations' in migrate_out.lower():
    warnings.append(f"[WARN] Unapplied migrations detected")
else:
    info.append("[INFO] All migrations applied")

# ── 7. Static files ────────────────────────────────────────────────────────
static_root = getattr(settings, 'STATIC_ROOT', '')
if not os.path.exists(static_root):
    warnings.append(f"[WARN] STATIC_ROOT does not exist: {static_root}")
else:
    info.append(f"[INFO] Static files present at {static_root}")

# ── Report ─────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("SECURITY & HEALTH REPORT")
print("="*60)

if issues:
    print(f"\n🔴 CRITICAL ISSUES ({len(issues)}):")
    for i in issues: print(f"  {i}")

if warnings:
    print(f"\n🟡 WARNINGS ({len(warnings)}):")
    for w in warnings: print(f"  {w}")

if info:
    print(f"\n🟢 INFO ({len(info)}):")
    for i in info: print(f"  {i}")

print("\n" + "="*60)
print(f"Total: {len(issues)} critical, {len(warnings)} warnings")
print("="*60 + "\n")
