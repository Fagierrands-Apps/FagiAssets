#!/usr/bin/env python3
"""
Comprehensive QR Code System Test

This script tests all aspects of the QR code label printing system.
"""

import os
import sys
import django
import requests
from io import BytesIO
from PIL import Image

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
django.setup()

from django.test import Client, RequestFactory
from django.contrib.auth.models import User
from assets.models import Asset
from assets.utils import generate_qr_code_image, generate_asset_label_data
from assets.views import asset_qr_code_image, asset_label_print

def test_qr_code_generation():
    """Test QR code generation utility"""
    print("🧪 Testing QR Code Generation...")
    
    test_url = "https://example.com/test-asset"
    
    # Test different sizes
    sizes = [100, 200, 400, 600, 1000]
    
    for size in sizes:
        qr_data = generate_qr_code_image(test_url, size=(size, size))
        
        if qr_data:
            # Verify it's a valid data URL
            assert qr_data.startswith('data:image/png;base64,'), f"Invalid data URL format for size {size}"
            
            # Decode and verify it's a valid image
            import base64
            image_data = base64.b64decode(qr_data.split(',')[1])
            
            # Verify it's a PNG image
            with BytesIO(image_data) as img_buffer:
                img = Image.open(img_buffer)
                assert img.format == 'PNG', f"Not a PNG image for size {size}"
                assert img.size == (size, size), f"Wrong image size: expected {size}x{size}, got {img.size}"
            
            print(f"  ✓ Size {size}x{size}: {len(image_data)} bytes")
        else:
            print(f"  ✗ Size {size}x{size}: Generation failed")
            return False
    
    print("✅ QR Code Generation: PASSED\n")
    return True

def test_asset_label_data():
    """Test asset label data generation"""
    print("🧪 Testing Asset Label Data Generation...")
    
    asset = Asset.objects.first()
    if not asset:
        print("  ❌ No assets found for testing")
        return False
    
    # Create a mock request
    factory = RequestFactory()
    request = factory.get('/test/')
    request.META['HTTP_HOST'] = 'testserver'
    
    # Generate label data
    label_data = generate_asset_label_data(asset, request)
    
    # Verify all required fields are present
    required_fields = ['asset', 'qr_image', 'asset_url', 'has_qrcode']
    
    for field in required_fields:
        assert field in label_data, f"Missing required field: {field}"
    
    assert label_data['asset'] == asset, "Asset data mismatch"
    assert label_data['has_qrcode'] is True, "QR code library not detected"
    assert label_data['qr_image'] is not None, "QR image not generated"
    assert 'testserver' in label_data['asset_url'], "Asset URL incorrect"
    
    print(f"  ✓ Asset: {asset.asset_tag}")
    print(f"  ✓ QR Image: {len(label_data['qr_image'])} bytes")
    print(f"  ✓ Asset URL: {label_data['asset_url']}")
    print("✅ Asset Label Data Generation: PASSED\n")
    return True

def test_url_endpoints():
    """Test URL endpoints"""
    print("🧪 Testing URL Endpoints...")
    
    asset = Asset.objects.first()
    if not asset:
        print("  ❌ No assets found for testing")
        return False
    
    # Create a test client
    client = Client()
    
    # Create a test user
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        user = User.objects.create_superuser('testuser', 'test@example.com', 'testpass')
    
    # Login
    client.force_login(user)
    
    # Test endpoints
    endpoints = [
        (f'/assets/{asset.id}/qr-code/', 'QR Code Page'),
        (f'/assets/{asset.id}/print-labels/', 'Label Print Page'),
        (f'/assets/bulk-print-labels/', 'Bulk Print Page'),
        (f'/assets/{asset.id}/qr-code.png', 'QR Code Image'),
        (f'/assets/{asset.id}/download-qr/', 'QR Code Download'),
    ]
    
    for url, name in endpoints:
        response = client.get(url)
        if response.status_code == 200:
            print(f"  ✓ {name}: {response.status_code}")
        else:
            print(f"  ✗ {name}: {response.status_code}")
            return False
    
    print("✅ URL Endpoints: PASSED\n")
    return True

def test_qr_code_image_endpoint():
    """Test QR code image endpoint specifically"""
    print("🧪 Testing QR Code Image Endpoint...")
    
    asset = Asset.objects.first()
    if not asset:
        print("  ❌ No assets found for testing")
        return False
    
    client = Client()
    user = User.objects.filter(is_superuser=True).first()
    if user:
        client.force_login(user)
    
    # Test different sizes
    sizes = [100, 200, 400, 600]
    
    for size in sizes:
        response = client.get(f'/assets/{asset.id}/qr-code.png?size={size}')
        
        if response.status_code == 200:
            assert response['Content-Type'] == 'image/png', f"Wrong content type for size {size}"
            
            # Verify it's a valid PNG
            with BytesIO(response.content) as img_buffer:
                img = Image.open(img_buffer)
                assert img.format == 'PNG', f"Not a PNG image for size {size}"
                assert img.size == (size, size), f"Wrong image size for {size}: got {img.size}"
            
            print(f"  ✓ Size {size}x{size}: {len(response.content)} bytes")
        else:
            print(f"  ✗ Size {size}x{size}: {response.status_code}")
            return False
    
    print("✅ QR Code Image Endpoint: PASSED\n")
    return True

def test_print_quality():
    """Test print quality of generated QR codes"""
    print("🧪 Testing Print Quality...")
    
    # Generate high-resolution QR code
    test_url = "https://example.com/test-high-res"
    qr_data = generate_qr_code_image(test_url, size=(600, 600))
    
    if qr_data:
        import base64
        image_data = base64.b64decode(qr_data.split(',')[1])
        
        with BytesIO(image_data) as img_buffer:
            img = Image.open(img_buffer)
            
            # Check image properties for print quality
            assert img.size == (600, 600), "High-res image wrong size"
            assert img.mode in ['RGB', 'RGBA', 'L'], "Image mode suitable for printing"
            
            # Check if image has good contrast (for QR codes)
            # Convert to grayscale and check pixel values
            gray_img = img.convert('L')
            pixels = list(gray_img.getdata())
            
            # QR codes should have mostly black (0) and white (255) pixels
            black_pixels = sum(1 for p in pixels if p < 50)
            white_pixels = sum(1 for p in pixels if p > 200)
            total_pixels = len(pixels)
            
            contrast_ratio = (black_pixels + white_pixels) / total_pixels
            
            print(f"  ✓ Image Size: {img.size}")
            print(f"  ✓ Image Mode: {img.mode}")
            print(f"  ✓ Contrast Ratio: {contrast_ratio:.2f}")
            print(f"  ✓ File Size: {len(image_data)} bytes")
            
            assert contrast_ratio > 0.8, "Poor contrast for printing"
            
        print("✅ Print Quality: PASSED\n")
        return True
    else:
        print("  ❌ Failed to generate high-res QR code")
        return False

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting QR Code System Tests")
    print("=" * 50)
    
    tests = [
        test_qr_code_generation,
        test_asset_label_data,
        test_url_endpoints,
        test_qr_code_image_endpoint,
        test_print_quality,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ❌ Test failed with error: {e}")
            failed += 1
    
    print("=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Your QR code system is working perfectly.")
        print("\n🏷️ Ready to print professional asset labels!")
        print("   • High-quality QR codes: ✓")
        print("   • Multiple formats: ✓")
        print("   • Print-ready output: ✓")
        print("   • Bulk printing: ✓")
        print("   • Download options: ✓")
    else:
        print(f"⚠️  {failed} test(s) failed. Please check the issues above.")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)