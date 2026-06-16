#!/usr/bin/env python
"""
Test deployment configuration to ensure it works correctly
"""

import os
import sys
import subprocess

def test_local_development():
    """Test local development configuration"""
    print("Testing local development configuration...")
    
    # Clear production environment variables
    os.environ.pop('VERCEL', None)
    os.environ.pop('DATABASE_URL', None)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'assetmanager.settings'
    
    # Add the Django project directory to Python path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'assetmanagement'))
    
    try:
        import django
        django.setup()
        
        from django.db import connection
        print(f"✓ Database engine: {connection.vendor}")
        print(f"✓ Database file: {connection.settings_dict.get('NAME', 'N/A')}")
        
        if connection.vendor == 'sqlite':
            print("✓ SQLite correctly configured for development")
            return True
        else:
            print("✗ Expected SQLite for development")
            return False
            
    except Exception as e:
        print(f"✗ Local development test failed: {e}")
        return False

def test_production_config():
    """Test production configuration with fallback"""
    print("\nTesting production configuration...")
    
    # Set production environment variables
    os.environ['VERCEL'] = '1'
    os.environ['DATABASE_URL'] = 'postgresql://postgres.dxesmzogjpxswxhsomgf:OnFRtf0SmpHwgNaQ@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres'
    os.environ['DJANGO_SETTINGS_MODULE'] = 'assetmanager.settings'
    
    try:
        # Run as separate process to avoid Django import conflicts
        import subprocess
        result = subprocess.run([
            sys.executable, '-c', 
            "import os; "
            "os.environ['VERCEL'] = '1'; "
            "os.environ['DATABASE_URL'] = 'postgresql://postgres.dxesmzogjpxswxhsomgf:OnFRtf0SmpHwgNaQ@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres'; "
            "os.environ['DJANGO_SETTINGS_MODULE'] = 'assetmanager.settings'; "
            "import sys; sys.path.insert(0, 'assetmanagement'); "
            "import django; django.setup(); "
            "from django.db import connection; "
            "print('ENGINE:', connection.vendor); "
            "print('HOST:', connection.settings_dict.get('HOST', 'N/A')); "
            "print('NAME:', connection.settings_dict.get('NAME', 'N/A'))"
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            output = result.stdout
            if 'ENGINE: postgresql' in output:
                print("✓ PostgreSQL correctly configured for production")
                print("✓ Database engine: postgresql")
                lines = output.strip().split('\n')
                for line in lines:
                    if line.startswith('HOST:'):
                        print(f"✓ Database host: {line.split(':', 1)[1].strip()}")
                    elif line.startswith('NAME:'):
                        print(f"✓ Database name: {line.split(':', 1)[1].strip()}")
                return True
            else:
                print("✗ Expected PostgreSQL for production")
                print(f"Output: {output}")
                return False
        else:
            print(f"✗ Production config test failed: {result.stderr}")
            return False
        
        from django.db import connection
        print(f"✓ Database engine: {connection.vendor}")
        print(f"✓ Database host: {connection.settings_dict.get('HOST', 'N/A')}")
        print(f"✓ Database name: {connection.settings_dict.get('NAME', 'N/A')}")
        
        if connection.vendor == 'postgresql':
            print("✓ PostgreSQL correctly configured for production")
            return True
        else:
            print("✗ Expected PostgreSQL for production")
            return False
            
    except Exception as e:
        print(f"✗ Production configuration test failed: {e}")
        return False

def test_requirements():
    """Test that all required packages are listed in requirements.txt"""
    print("\nTesting requirements.txt...")
    
    try:
        # Check root requirements.txt
        with open('requirements.txt', 'r') as f:
            root_requirements = f.read()
        
        # Check project requirements.txt
        with open('assetmanagement/requirements.txt', 'r') as f:
            project_requirements = f.read()
        
        required_packages = [
            'Django',
            'djangorestframework',
            'django-cors-headers',
            'dj-database-url',
            'psycopg2-binary',
            'qrcode',
            'whitenoise'
        ]
        
        missing_packages = []
        for package in required_packages:
            if package not in root_requirements and package not in project_requirements:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"✗ Missing packages: {', '.join(missing_packages)}")
            return False
        else:
            print("✓ All required packages are in requirements.txt")
            return True
            
    except Exception as e:
        print(f"✗ Requirements test failed: {e}")
        return False

def test_vercel_config():
    """Test Vercel configuration"""
    print("\nTesting Vercel configuration...")
    
    try:
        import json
        
        with open('vercel.json', 'r') as f:
            vercel_config = json.load(f)
        
        # Check basic structure
        if 'builds' not in vercel_config:
            print("✗ Missing 'builds' in vercel.json")
            return False
        
        if 'routes' not in vercel_config:
            print("✗ Missing 'routes' in vercel.json")
            return False
        
        # Check WSGI build
        wsgi_build = None
        for build in vercel_config['builds']:
            if 'wsgi.py' in build['src']:
                wsgi_build = build
                break
        
        if not wsgi_build:
            print("✗ Missing WSGI build configuration")
            return False
        
        print("✓ Vercel configuration looks correct")
        return True
        
    except Exception as e:
        print(f"✗ Vercel configuration test failed: {e}")
        return False

def main():
    """Run all deployment tests"""
    print("=" * 60)
    print("Deployment Configuration Test")
    print("=" * 60)
    
    # Run tests
    tests = [
        test_local_development,
        test_production_config,
        test_requirements,
        test_vercel_config
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ All tests passed! Configuration is ready for deployment.")
        print("\nNext steps:")
        print("1. Commit changes to Git")
        print("2. Push to GitHub")
        print("3. Deploy to Vercel: vercel --prod")
        print("4. Set environment variables in Vercel dashboard")
        print("5. Test login at https://fagiassets.vercel.app/login/")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
    
    print("=" * 60)

if __name__ == '__main__':
    main()