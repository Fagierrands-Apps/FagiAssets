#!/usr/bin/env python
"""
Check specific table existence
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
django.setup()

from django.db import connection

def check_table(table_name):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            );
        """, [table_name])
        return cursor.fetchone()[0]

tables_to_check = [
    'assets_asset_assigned_users',
    'authtoken_token',
    'django_session',
]

print("Checking table existence:")
print("-" * 50)
for table in tables_to_check:
    exists = check_table(table)
    status = "✓ EXISTS" if exists else "✗ MISSING"
    print(f"{status}: {table}")