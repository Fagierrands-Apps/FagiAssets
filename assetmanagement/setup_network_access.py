#!/usr/bin/env python3
"""
Network Access Setup for Asset Management System

This script configures the system for network access and provides
all the necessary URLs for accessing from mobile devices and other computers.
"""

import os
import socket
import subprocess
import sys

def get_local_ip():
    """Get the local network IP address"""
    try:
        # Connect to a remote server to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Connect to Google's DNS server
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        return local_ip
    except:
        # Fallback method
        try:
            result = subprocess.run(['ipconfig'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            for line in lines:
                if 'IPv4 Address' in line and '10.' in line:
                    return line.split(':')[1].strip()
            return None
        except:
            return None

def update_django_settings(ip_address):
    """Update Django settings to allow network access"""
    settings_path = 'assetmanager/settings.py'
    
    if not os.path.exists(settings_path):
        print(f"❌ Settings file not found: {settings_path}")
        return False
    
    # Read current settings
    with open(settings_path, 'r') as f:
        content = f.read()
    
    # Update ALLOWED_HOSTS if needed
    if ip_address not in content:
        if "ALLOWED_HOSTS = [" in content:
            content = content.replace(
                "ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver', '10.246.23.10', '*']",
                f"ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver', '{ip_address}', '*']"
            )
        
        # Write updated settings
        with open(settings_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Updated ALLOWED_HOSTS to include {ip_address}")
    else:
        print(f"✅ IP address {ip_address} already in ALLOWED_HOSTS")
    
    return True

def test_network_access(ip_address, port=8000):
    """Test if the network port is accessible"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip_address, port))
        sock.close()
        return result == 0
    except:
        return False

def display_network_info(ip_address, port=8000):
    """Display network access information"""
    print(f"\n🌐 Network Access Configuration")
    print("=" * 50)
    
    print(f"📍 Your Network IP: {ip_address}")
    print(f"🔌 Server Port: {port}")
    
    base_url = f"http://{ip_address}:{port}"
    
    print(f"\n📱 Access URLs:")
    print(f"• Main Dashboard: {base_url}/")
    print(f"• Asset List: {base_url}/assets/")
    print(f"• Admin Panel: {base_url}/admin/")
    print(f"• Bulk Print Labels: {base_url}/assets/bulk-print-labels/")
    
    print(f"\n📱 Mobile Device Instructions:")
    print(f"1. Connect your mobile device to the same WiFi network")
    print(f"2. Open a web browser on your mobile device")
    print(f"3. Navigate to: {base_url}/assets/")
    print(f"4. Click 'Print Labels' or 'Bulk Print Labels'")
    print(f"5. The QR codes will link back to: {base_url}")
    
    print(f"\n🏷️ QR Code Benefits:")
    print(f"• QR codes will contain URLs like: {base_url}/assets/[ID]/")
    print(f"• Scannable from any device on the network")
    print(f"• Mobile-friendly asset detail pages")
    print(f"• Real-time asset information")
    
    print(f"\n🔧 Server Commands:")
    print(f"• Start server: python manage.py runserver 0.0.0.0:{port}")
    print(f"• Or specific IP: python manage.py runserver {ip_address}:{port}")

def create_network_start_script(ip_address, port=8000):
    """Create a convenient start script for network access"""
    
    # Windows batch script
    batch_script = f"""@echo off
echo Starting Asset Management System on Network...
echo.
echo Network IP: {ip_address}
echo Server URL: http://{ip_address}:{port}/
echo.
echo Press Ctrl+C to stop the server
echo.
python manage.py runserver 0.0.0.0:{port}
pause
"""
    
    with open('start_network_server.bat', 'w') as f:
        f.write(batch_script)
    
    # PowerShell script
    ps_script = f"""# Asset Management System Network Startup Script
Write-Host "Starting Asset Management System on Network..." -ForegroundColor Green
Write-Host ""
Write-Host "Network IP: {ip_address}" -ForegroundColor Yellow
Write-Host "Server URL: http://{ip_address}:{port}/" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Cyan
Write-Host ""

# Start the Django server
python manage.py runserver 0.0.0.0:{port}
"""
    
    with open('start_network_server.ps1', 'w') as f:
        f.write(ps_script)
    
    print(f"\n📄 Created startup scripts:")
    print(f"• Windows: start_network_server.bat")
    print(f"• PowerShell: start_network_server.ps1")

def check_firewall_info():
    """Provide firewall information"""
    print(f"\n🔒 Firewall & Security Notes:")
    print(f"• Windows Firewall may block incoming connections")
    print(f"• You may need to allow Python through the firewall")
    print(f"• This is normal for network access")
    print(f"• The system will prompt you when first starting the server")

def main():
    """Main setup function"""
    print("🌐 Asset Management System - Network Access Setup")
    print("=" * 60)
    
    # Get local IP
    ip_address = get_local_ip()
    
    if not ip_address:
        print("❌ Could not determine local IP address")
        print("Please check your network connection and try again.")
        return False
    
    print(f"🔍 Detected Network IP: {ip_address}")
    
    # Update Django settings
    if not update_django_settings(ip_address):
        return False
    
    # Display network information
    display_network_info(ip_address)
    
    # Create startup scripts
    create_network_start_script(ip_address)
    
    # Firewall info
    check_firewall_info()
    
    print(f"\n🚀 Next Steps:")
    print(f"1. Run: start_network_server.bat")
    print(f"2. Or run: python manage.py runserver 0.0.0.0:8000")
    print(f"3. Allow Python through Windows Firewall if prompted")
    print(f"4. Access from mobile: http://{ip_address}:8000/assets/")
    print(f"5. Print QR codes that work across your network!")
    
    print(f"\n🎉 Network access configured successfully!")
    return True

if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        sys.exit(1)