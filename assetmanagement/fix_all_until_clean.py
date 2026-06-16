#!/usr/bin/env python
"""
Keep fixing migrations until all are clean
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
django.setup()

from django.db import connection
from django.db.migrations.recorder import MigrationRecorder
from django.db.migrations.loader import MigrationLoader
from django.core.management import call_command
from io import StringIO

def table_exists(table_name):
    """Check if a table exists"""
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
    """Check if a column exists"""
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

def check_migration_has_existing_objects(app_label, migration_name):
    """Check if migration creates objects that already exist"""
    loader = MigrationLoader(connection)
    
    try:
        migration = loader.get_migration(app_label, migration_name)
        
        for operation in migration.operations:
            op_type = type(operation).__name__
            
            if op_type == 'CreateModel':
                table_name = f"{app_label}_{operation.name.lower()}"
                if table_exists(table_name):
                    return True, f"Table '{table_name}' exists"
            
            elif op_type == 'AddField':
                table_name = f"{app_label}_{operation.model_name.lower()}"
                if column_exists(table_name, operation.name):
                    return True, f"Column '{table_name}.{operation.name}' exists"
        
        return False, None
    except Exception as e:
        return False, None

def get_next_unapplied_migration():
    """Get the next unapplied migration that has existing objects"""
    loader = MigrationLoader(connection)
    recorder = MigrationRecorder(connection)
    applied = set(recorder.applied_migrations())
    
    # Get migration plan
    targets = loader.graph.leaf_nodes()
    plan = []
    
    for target in targets:
        try:
            plan.extend(loader.graph.forwards_plan(target))
        except:
            pass
    
    # Remove duplicates while preserving order
    seen = set()
    unique_plan = []
    for item in plan:
        if item not in seen:
            seen.add(item)
            unique_plan.append(item)
    
    # Find first unapplied migration with existing objects
    for app_label, migration_name in unique_plan:
        if (app_label, migration_name) not in applied:
            has_existing, reason = check_migration_has_existing_objects(app_label, migration_name)
            if has_existing:
                return app_label, migration_name, reason
    
    return None, None, None

print("=" * 70)
print("Iterative Migration State Fix")
print("=" * 70)
print()

iteration = 0
max_iterations = 50
fixed_count = 0

while iteration < max_iterations:
    iteration += 1
    
    # Check for next problematic migration
    app_label, migration_name, reason = get_next_unapplied_migration()
    
    if not app_label:
        print("\n✅ No more problematic migrations found!")
        break
    
    print(f"[{iteration}] Found: {app_label}.{migration_name}")
    print(f"     Reason: {reason}")
    print(f"     Action: Marking as applied...", end=' ')
    
    try:
        recorder = MigrationRecorder(connection)
        recorder.record_applied(app_label, migration_name)
        print("✓")
        fixed_count += 1
    except Exception as e:
        print(f"✗ {str(e)}")
        break

print()
print("=" * 70)
print("Summary")
print("=" * 70)
print(f"\n✓ Fixed {fixed_count} migration(s)")

if iteration >= max_iterations:
    print("\n⚠️  Reached maximum iterations. There may be more issues.")
else:
    print("\n✅ All problematic migrations have been marked as applied!")
    print("\nNow attempting to run remaining migrations...")
    print("=" * 70)
    print()
    
    try:
        call_command('migrate', verbosity=2)
        print("\n" + "=" * 70)
        print("✅ SUCCESS! All migrations applied.")
        print("=" * 70)
    except Exception as e:
        print(f"\n⚠️  Error during migrate: {str(e)}")
        print("\nYou may need to manually check remaining migrations.")