#!/usr/bin/env python3
"""
Quick setup script for cPanel deployment
Run this to configure your environment variables
"""

import os
import secrets

def generate_secret_key():
    """Generate a secure Django SECRET_KEY"""
    return secrets.token_urlsafe(50)

def main():
    print("=" * 60)
    print("Django cPanel Deployment - Configuration Setup")
    print("=" * 60)
    print()
    
    # Get user input
    print("Please provide the following information:")
    print()
    
    domain = input("Your domain (e.g., yourdomain.com): ").strip()
    www_domain = f"www.{domain}"
    
    print()
    print("PostgreSQL Database Information:")
    db_name = input("Database name: ").strip()
    db_user = input("Database user: ").strip()
    db_password = input("Database password: ").strip()
    db_host = input("Database host [localhost]: ").strip() or "localhost"
    db_port = input("Database port [5432]: ").strip() or "5432"
    
    print()
    generate_key = input("Generate new SECRET_KEY? (y/n) [y]: ").strip().lower()
    if generate_key != 'n':
        secret_key = generate_secret_key()
        print(f"Generated SECRET_KEY: {secret_key}")
    else:
        secret_key = input("Enter your SECRET_KEY: ").strip()
    
    print()
    debug = input("Enable DEBUG mode? (y/n) [n]: ").strip().lower() == 'y'
    
    # Create .env file
    env_content = f"""# Django Settings
SECRET_KEY={secret_key}
DEBUG={'True' if debug else 'False'}
ALLOWED_HOSTS={domain},{www_domain},localhost,127.0.0.1

# Database Settings
DB_NAME={db_name}
DB_USER={db_user}
DB_PASSWORD={db_password}
DB_HOST={db_host}
DB_PORT={db_port}

# Application Settings
DJANGO_SETTINGS_MODULE=assetmanager.settings
"""
    
    # Write .env file
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print()
    print("=" * 60)
    print("✓ Configuration saved to .env file")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Upload your project files to cPanel")
    print("2. Upload the .env file to your project root")
    print("3. Run: ./cpanel_deploy.sh")
    print("4. Restart your Python application in cPanel")
    print()
    print("Your configuration:")
    print(f"  Domain: {domain}")
    print(f"  Database: {db_name}")
    print(f"  Debug: {debug}")
    print()
    print("=" * 60)

if __name__ == '__main__':
    main()