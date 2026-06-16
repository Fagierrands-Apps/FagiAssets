#!/usr/bin/env python
"""
Check all unapplied migrations for existing database objects
"""
import os
import sys
import django

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

def get_migration_info():
    """Get all migrations and their status"""
    recorder = MigrationRecorder(connection)
    applied = set(recorder.applied_migrations())
    
    all_migrations = {}
    for app_config in apps.get_app_configs():
        try:
            from django.db.migrations.loader import MigrationLoader
            loader = MigrationLoader(connection)
            
            app_migrations = []
            for migration_name in loader.graph.leaf_nodes():
                if migration_name[0] == app_config.label:
                    # Get all migrations for this app
                    for node in loader.graph.nodes:
                        if node[0] == app_config.label:
                            is_applied = node in applied
                            app_migrations.append({
                                'name': node[1],
                                'applied': is_applied,
                                'full_name': node
                            })
            
            if app_migrations:
                # Sort by migration name
                app_migrations.sort(key=lambda x: x['name'])
                all_migrations[app_config.label] = app_migrations
        except:
            pass
    
    return all_migrations

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
        return [f"Error checking migration: {str(e)}"]

print("=" * 70)
print("Django Migration State Analysis")
print("=" * 70)
print()

migrations_info = get_migration_info()
problems_found = []

for app_label, migrations in sorted(migrations_info.items()):
    unapplied = [m for m in migrations if not m['applied']]
    
    if unapplied:
        print(f"\n{app_label}")
        print("-" * 70)
        
        for migration in migrations:
            status = "[X]" if migration['applied'] else "[ ]"
            print(f"  {status} {migration['name']}")
            
            # Check unapplied migrations for existing objects
            if not migration['applied']:
                issues = check_migration_objects(app_label, migration['name'])
                if issues:
                    problems_found.append({
                        'app': app_label,
                        'migration': migration['name'],
                        'issues': issues
                    })
                    for issue in issues:
                        print(f"      ⚠️  {issue}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

if problems_found:
    print(f"\n❌ Found {len(problems_found)} migration(s) with existing database objects:\n")
    
    for problem in problems_found:
        print(f"  • {problem['app']}.{problem['migration']}")
        for issue in problem['issues']:
            print(f"    - {issue}")
    
    print("\n" + "=" * 70)
    print("RECOMMENDED FIX")
    print("=" * 70)
    print("\nRun these commands to mark migrations as applied:\n")
    
    for problem in problems_found:
        migration_number = problem['migration'].split('_')[0]
        print(f"python manage.py migrate {problem['app']} {migration_number} --fake")
    
    print("\n# Then run normal migrate to apply any remaining migrations:")
    print("python manage.py migrate")
    
    print("\n" + "=" * 70)
    print("OR - Run this single command to fix all at once:")
    print("=" * 70)
    print()
    for problem in problems_found:
        migration_number = problem['migration'].split('_')[0]
        print(f"python manage.py migrate {problem['app']} {migration_number} --fake")
    print("python manage.py migrate")
    
else:
    print("\n✅ No migration state issues found!")
    print("   All unapplied migrations are safe to run normally.")
    print("\nRun: python manage.py migrate")

print()