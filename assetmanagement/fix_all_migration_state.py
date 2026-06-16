#!/usr/bin/env python
"""
Automatically fix all migration state issues
"""
import os
import sys
import django
import subprocess

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
django.setup()

from django.db import connection
from django.db.migrations.recorder import MigrationRecorder
from django.apps import apps

def table_exists(table_name):
    """Check if a table exists in the database"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            );
        """, [table_name])
        return cursor.fetchone()[0]

def column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = %s 
                AND column_name = %s
            );
        """, [table_name, column_name])
        return cursor.fetchone()[0]

def check_migration_objects(app_label, migration_name):
    """Check if database objects from a migration already exist"""
    from django.db.migrations.loader import MigrationLoader
    loader = MigrationLoader(connection)
    
    try:
        migration = loader.get_migration(app_label, migration_name)
        issues = []
        
        for operation in migration.operations:
            op_type = type(operation).__name__
            
            if op_type == 'CreateModel':
                table_name = f"{app_label}_{operation.name.lower()}"
                if table_exists(table_name):
                    issues.append(f"Table '{table_name}' already exists")
            
            elif op_type == 'AddField':
                table_name = f"{app_label}_{operation.model_name.lower()}"
                if column_exists(table_name, operation.name):
                    issues.append(f"Column '{table_name}.{operation.name}' already exists")
        
        return issues
    except Exception as e:
        return []

def get_migrations_to_fake():
    """Get all migrations that need to be faked"""
    from django.db.migrations.loader import MigrationLoader
    loader = MigrationLoader(connection)
    recorder = MigrationRecorder(connection)
    applied = set(recorder.applied_migrations())
    
    to_fake = []
    
    for app_config in apps.get_app_configs():
        try:
            for node in loader.graph.nodes:
                if node[0] == app_config.label and node not in applied:
                    issues = check_migration_objects(node[0], node[1])
                    if issues:
                        to_fake.append({
                            'app': node[0],
                            'migration': node[1],
                            'issues': issues
                        })
        except:
            pass
    
    # Sort by app and migration name
    to_fake.sort(key=lambda x: (x['app'], x['migration']))
    return to_fake

print("=" * 70)
print("Automatic Migration State Fix")
print("=" * 70)
print()

migrations_to_fake = get_migrations_to_fake()

if not migrations_to_fake:
    print("✅ No migration state issues found!")
    print("   Running normal migrate...")
    print()
    result = subprocess.run([sys.executable, 'manage.py', 'migrate'], 
                          capture_output=False)
    sys.exit(result.returncode)

print(f"Found {len(migrations_to_fake)} migration(s) that need to be marked as applied:\n")

for item in migrations_to_fake:
    print(f"  • {item['app']}.{item['migration']}")
    for issue in item['issues'][:3]:  # Show first 3 issues
        print(f"    - {issue}")
    if len(item['issues']) > 3:
        print(f"    ... and {len(item['issues']) - 3} more")

print("\n" + "=" * 70)
print("Starting automatic fix...")
print("=" * 70)
print()

success_count = 0
failed = []

for item in migrations_to_fake:
    migration_number = item['migration'].split('_')[0]
    cmd = [sys.executable, 'manage.py', 'migrate', item['app'], migration_number, '--fake']
    
    print(f"Faking {item['app']}.{migration_number}...", end=' ')
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✓")
            success_count += 1
        else:
            print("✗")
            failed.append({
                'app': item['app'],
                'migration': migration_number,
                'error': result.stderr
            })
    except Exception as e:
        print(f"✗ {str(e)}")
        failed.append({
            'app': item['app'],
            'migration': migration_number,
            'error': str(e)
        })

print()
print("=" * 70)
print("Results")
print("=" * 70)
print(f"\n✓ Successfully faked: {success_count} migration(s)")

if failed:
    print(f"✗ Failed: {len(failed)} migration(s)\n")
    for item in failed:
        print(f"  • {item['app']}.{item['migration']}")
        print(f"    Error: {item['error'][:100]}")
else:
    print("\n✅ All migrations successfully marked as applied!")
    print("\nNow running normal migrate to apply remaining migrations...")
    print("=" * 70)
    print()
    
    result = subprocess.run([sys.executable, 'manage.py', 'migrate'], 
                          capture_output=False)
    
    if result.returncode == 0:
        print("\n" + "=" * 70)
        print("✅ ALL DONE! Migration state is now fixed.")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("⚠️  Some migrations may have failed. Check output above.")
        print("=" * 70)