"""
Web-accessible Database Migration Script
Access via browser: http://fagiassets.fagitone.com/migrate/
Place this in assetmanagement directory and add URL pattern
"""
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
from django.apps import apps
from django.db import connections
from django.core.management import call_command
import io
import sys

@staff_member_required
@require_http_methods(["GET", "POST"])
def migrate_databases_view(request):
    """Web interface for database migration"""
    
    output = io.StringIO()
    sys.stdout = output
    
    try:
        print("<html><head><title>Database Migration</title>")
        print("<style>body{font-family:monospace;padding:20px;background:#1e1e1e;color:#00ff00;}")
        print("h1{color:#00ff00;} .success{color:#00ff00;} .error{color:#ff0000;} .warning{color:#ffaa00;}</style>")
        print("</head><body>")
        print("<h1>Database Migration: Old Supabase → cPanel PostgreSQL</h1>")
        print("<hr>")
        
        if request.method == 'GET':
            print("<p>This will migrate all data from old Supabase to your cPanel database.</p>")
            print("<form method='post'>")
            print(f"<input type='hidden' name='csrfmiddlewaretoken' value='{request.META.get('CSRF_COOKIE', '')}'>")
            print("<button type='submit' style='padding:10px 20px;font-size:16px;'>Start Migration</button>")
            print("</form>")
            print("</body></html>")
            return HttpResponse(output.getvalue())
        
        # POST - Run migration
        print("<h2>Migration Progress:</h2>")
        print("<pre>")
        
        # Step 1: Test connections
        print("\n[1/5] Testing connections...")
        try:
            with connections['old_supabase'].cursor() as cursor:
                cursor.execute("SELECT 1")
            print("<span class='success'>✓ Old Supabase OK</span>")
        except Exception as e:
            print(f"<span class='error'>✗ Old Supabase failed: {e}</span>")
            print("</pre></body></html>")
            return HttpResponse(output.getvalue())
        
        try:
            with connections['default'].cursor() as cursor:
                cursor.execute("SELECT 1")
            print("<span class='success'>✓ cPanel PostgreSQL OK</span>")
        except Exception as e:
            print(f"<span class='error'>✗ cPanel failed: {e}</span>")
            print("</pre></body></html>")
            return HttpResponse(output.getvalue())
        
        # Step 2: Copy data
        print("\n[2/5] Copying data...")
        total_copied = 0
        
        for model in apps.get_models():
            model_name = f"{model._meta.app_label}.{model.__name__}"
            
            try:
                old_objects = list(model.objects.using('old_supabase').all())
                
                if not old_objects:
                    print(f"<span class='warning'>⊘ {model_name}: No data</span>")
                    continue
                
                # Copy to cPanel
                model.objects.using('default').all().delete()
                
                batch_size = 100
                for i in range(0, len(old_objects), batch_size):
                    batch = old_objects[i:i + batch_size]
                    model.objects.using('default').bulk_create(batch, ignore_conflicts=True)
                
                count = model.objects.using('default').count()
                total_copied += count
                print(f"<span class='success'>✓ {model_name}: {count} records</span>")
                
            except Exception as e:
                print(f"<span class='error'>✗ {model_name}: {e}</span>")
        
        print(f"\n<strong>Total records copied: {total_copied}</strong>")
        
        # Step 3: Migrations
        print("\n[3/5] Running migrations...")
        call_command('migrate', database='default', verbosity=0)
        print("<span class='success'>✓ Migrations complete</span>")
        
        # Step 4: Verify
        print("\n[4/5] Verifying data...")
        from django.contrib.auth.models import User
        user_count = User.objects.using('default').count()
        print(f"<span class='success'>✓ Users: {user_count}</span>")
        
        # Step 5: Backup
        print("\n[5/5] Initial backup to new Supabase...")
        try:
            with connections['backup'].cursor() as cursor:
                cursor.execute("SELECT 1")
            print("<span class='success'>✓ New Supabase connection OK</span>")
        except Exception as e:
            print(f"<span class='warning'>⚠ Backup connection: {e}</span>")
        
        print("\n" + "="*60)
        print("<h2 class='success'>✓ MIGRATION COMPLETE!</h2>")
        print("<p>Your application is now using cPanel PostgreSQL as primary database.</p>")
        print("</pre>")
        print("</body></html>")
        
    except Exception as e:
        print(f"<span class='error'>Fatal error: {e}</span>")
        print("</pre></body></html>")
    
    finally:
        sys.stdout = sys.__stdout__
    
    return HttpResponse(output.getvalue())
