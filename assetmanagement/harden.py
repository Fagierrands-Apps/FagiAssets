import os, re, secrets
from pathlib import Path

BASE = Path(__file__).parent

# ── 1. Remove Supabase entries from settings.py ────────────────────────────
settings_path = BASE / 'assetmanager' / 'settings.py'
content = settings_path.read_text()

content = re.sub(
    r'\n\n        # BACKUP: Old Supabase.*?        \}\n    \}',
    '\n\n    }',
    content,
    flags=re.DOTALL
)

settings_path.write_text(content)

# Verify removal
remaining = [l.strip() for l in content.splitlines()
             if any(x in l for x in ['supabase', 'OnFRtf0', 'U)5z5z', 'dxesmzogjpxswxhsomgf'])]
if remaining:
    print(f"WARNING: Supabase refs still found: {remaining}")
else:
    print("✅ Supabase credentials removed from settings.py")

# ── 2. Generate new SECRET_KEY ─────────────────────────────────────────────
new_key = secrets.token_urlsafe(50)
print(f"✅ New SECRET_KEY generated")

# ── 3. Update .env.production ──────────────────────────────────────────────
env_path = BASE / '.env.production'
env_content = env_path.read_text()

if 'SECRET_KEY=' in env_content:
    env_content = re.sub(r'SECRET_KEY=.*', f'SECRET_KEY={new_key}', env_content)
else:
    env_content += f'\nSECRET_KEY={new_key}\n'

env_path.write_text(env_content)
print(f"✅ .env.production updated with new SECRET_KEY")
print(f"\nDone. Restart the app to apply changes.")
