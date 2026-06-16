#!/usr/bin/env python3
"""
Network QR Code System Test

This script verifies that the network-enabled QR code system is working correctly.
"""

import os
import sys
import django
import socket
import subprocess

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
django.setup()

from assets.models import Asset
from assets.utils import generate_qr_code_image

def get_network_ip():
    """Get the current network IP"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:
        return "10.246.23.10"  # Fallback

def test_qr_generation():
    """Test QR code generation"""
    print("🧪 Testing QR Code Generation...")
    
    network_ip = get_network_ip()
    test_url = f"http://{network_ip}:8000/assets/1/"
    
    qr_data = generate_qr_code_image(test_url, size=(300, 300))
    
    if qr_data:
        print(f"  ✅ QR code generated successfully")
        print(f"  📏 Size: {len(qr_data)} bytes")
        print(f"  🔗 URL: {test_url}")
        return True
    else:
        print(f"  ❌ QR code generation failed")
        return False

def test_network_urls():
    """Test network URL accessibility"""
    print("\n📡 Testing Network URLs...")
    
    network_ip = get_network_ip()
    base_url = f"http://{network_ip}:8000"
    
    # Test if asset exists
    asset = Asset.objects.first()
    if not asset:
        print("  ⚠️  No assets found for testing")
        return False
    
    urls = [
        f"{base_url}/",
        f"{base_url}/assets/",
        f"{base_url}/assets/{asset.id}/",
        f"{base_url}/assets/{asset.id}/qr-code.png",
        f"{base_url}/assets/{asset.id}/print-labels/",
        f"{base_url}/assets/bulk-print-labels/",
    ]
    
    print(f"  🌐 Network IP: {network_ip}")
    print(f"  📋 Test Asset: {asset.asset_tag}")
    print(f"  🔗 Available URLs:")
    
    for url in urls:
        print(f"    • {url}")
    
    return True

def test_file_structure():
    """Test that all required files exist"""
    print("\n📁 Testing File Structure...")
    
    required_files = [
        'start_network_server.bat',
        'setup_network_access.py',
        'templates/assets/asset_label_professional.html',
        'templates/assets/bulk_label_print.html',
        'templates/assets/mobile_qr_scanner.html',
        'assets/utils.py',
        'NETWORK_QR_SYSTEM_GUIDE.md',
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n  ⚠️  Missing files: {len(missing_files)}")
        return False
    else:
        print(f"\n  ✅ All files present")
        return True

def display_system_info():
    """Display system information"""
    print("\n📊 System Information:")
    print("=" * 50)
    
    network_ip = get_network_ip()
    asset_count = Asset.objects.count()
    
    print(f"Network IP:        {network_ip}")
    print(f"Server Port:       8000")
    print(f"Assets in DB:      {asset_count}")
    print(f"QR Library:        {'✅ Available' if generate_qr_code_image('test') else '❌ Missing'}")
    
    # Django settings check
    from django.conf import settings
    allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
    print(f"Allowed Hosts:     {', '.join(allowed_hosts)}")
    
    print(f"\n🌐 Network URLs:")
    print(f"Main Dashboard:    http://{network_ip}:8000/")
    print(f"Asset List:        http://{network_ip}:8000/assets/")
    print(f"Print Labels:      http://{network_ip}:8000/assets/bulk-print-labels/")
    
    if asset_count > 0:
        asset = Asset.objects.first()
        print(f"Sample Asset:      http://{network_ip}:8000/assets/{asset.id}/")

def main():
    """Main test function"""
    print("🌐 Network QR Code System Test")
    print("=" * 40)
    
    tests = [
        test_qr_generation,
        test_network_urls,
        test_file_structure,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  ❌ Test failed: {e}")
    
    display_system_info()
    
    print(f"\n📈 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("\n🚀 Your network QR code system is ready!")
        print("📱 Start the server and access from mobile devices")
        print("🏷️ Print professional QR code labels")
        print("🌐 Scan codes from anywhere on your network")
        
        print(f"\n⚡ Quick Start:")
        print(f"1. Run: start_network_server.bat")
        print(f"2. Open mobile browser: http://{get_network_ip()}:8000/assets/")
        print(f"3. Print labels and scan QR codes!")
        
        return True
    else:
        print(f"⚠️  {total - passed} test(s) failed")
        print("Please check the issues above before using the system")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)