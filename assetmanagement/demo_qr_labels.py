#!/usr/bin/env python3
"""
Demo script showing how to use the QR Code Label Printing System

This script demonstrates:
1. How to access the printable QR code labels
2. Different label formats available
3. How to print single or multiple labels
4. How to use the bulk printing feature
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetmanager.settings')
django.setup()

from django.contrib.auth.models import User
from assets.models import Asset
from assets.utils import generate_qr_code_image, generate_asset_label_data

def demo_qr_code_generation():
    """Demonstrate QR code generation"""
    print("=== QR Code Generation Demo ===\n")
    
    # Get a sample asset
    asset = Asset.objects.first()
    if not asset:
        print("No assets found. Please add some assets first.")
        return
    
    print(f"Generating QR code for asset: {asset.asset_tag}")
    
    # Generate QR code
    asset_url = f"http://127.0.0.1:8000/assets/{asset.id}/"
    qr_image = generate_qr_code_image(asset_url)
    
    if qr_image:
        print(f"✓ QR code generated successfully!")
        print(f"  Asset: {asset.name}")
        print(f"  URL: {asset_url}")
        print(f"  QR Code: {qr_image[:50]}...")
    else:
        print("✗ QR code generation failed (qrcode library not installed)")
    
    print()

def demo_label_printing_urls():
    """Show the URLs for accessing label printing features"""
    print("=== Label Printing URLs ===\n")
    
    # Get a sample asset
    asset = Asset.objects.first()
    if not asset:
        print("No assets found. Please add some assets first.")
        return
    
    base_url = "http://127.0.0.1:8000"
    
    print(f"Asset: {asset.asset_tag} - {asset.name}")
    print(f"Asset Detail Page: {base_url}/assets/{asset.id}/")
    print(f"QR Code Page: {base_url}/assets/{asset.id}/qr-code/")
    print(f"Professional Label Printing: {base_url}/assets/{asset.id}/print-labels/")
    print(f"Bulk Label Printing: {base_url}/assets/bulk-print-labels/")
    print()

def demo_available_formats():
    """Show available label formats"""
    print("=== Available Label Formats ===\n")
    
    formats = [
        {
            'name': 'Standard',
            'size': '2.5" × 2"',
            'description': 'General purpose asset labels',
            'use_case': 'Desktop computers, printers, larger equipment'
        },
        {
            'name': 'Avery 5160',
            'size': '2.625" × 1"',
            'description': 'Compatible with Avery 5160 label sheets (30 per sheet)',
            'use_case': 'Small items, cables, peripherals'
        },
        {
            'name': 'Large Format',
            'size': '3.5" × 2.5"',
            'description': 'Large labels for easy reading',
            'use_case': 'Servers, network equipment, high-value items'
        }
    ]
    
    for fmt in formats:
        print(f"• {fmt['name']} ({fmt['size']})")
        print(f"  Description: {fmt['description']}")
        print(f"  Best for: {fmt['use_case']}")
        print()

def demo_features():
    """Show features of the QR code system"""
    print("=== QR Code Label Features ===\n")
    
    features = [
        "✓ High-quality QR codes that scan reliably",
        "✓ Professional print-ready layouts",
        "✓ Multiple label formats (Standard, Avery 5160, Large)",
        "✓ Bulk printing for multiple assets",
        "✓ Asset information included on each label",
        "✓ Company branding space",
        "✓ Print preview with real-time updates",
        "✓ Browser-based printing (Print to PDF supported)",
        "✓ Responsive design for different screen sizes",
        "✓ QR codes link directly to asset detail pages"
    ]
    
    for feature in features:
        print(feature)
    
    print()

def demo_usage_instructions():
    """Show how to use the system"""
    print("=== How to Use the QR Code Label System ===\n")
    
    instructions = [
        "1. Start the Django development server:",
        "   python manage.py runserver",
        "",
        "2. Navigate to an asset detail page or asset list",
        "",
        "3. For single asset labels:",
        "   - Click the 'Print Labels' button on any asset detail page",
        "   - Choose your preferred label format",
        "   - Select the number of labels to print",
        "   - Click 'Print Labels' to open the print dialog",
        "",
        "4. For bulk printing:",
        "   - Go to the asset list page",
        "   - Click 'Bulk Print Labels'",
        "   - Select which assets to print",
        "   - Choose your label format",
        "   - Generate and print labels",
        "",
        "5. Printing Tips:",
        "   - Use 'Print to PDF' to save labels as PDF files",
        "   - For best results, use high-quality label paper",
        "   - Test print alignment with regular paper first",
        "   - Avery 5160 format works with standard Avery label sheets"
    ]
    
    for instruction in instructions:
        print(instruction)
    
    print()

def main():
    """Main demo function"""
    print("🏷️  Asset Management QR Code Label System Demo\n")
    print("=" * 60)
    
    # Check if we have assets
    asset_count = Asset.objects.count()
    print(f"Assets in database: {asset_count}")
    
    if asset_count == 0:
        print("\n⚠️  No assets found in the database.")
        print("Please add some assets through the admin interface first:")
        print("http://127.0.0.1:8000/admin/")
        return
    
    print("\n")
    
    # Run demos
    demo_qr_code_generation()
    demo_label_printing_urls()
    demo_available_formats()
    demo_features()
    demo_usage_instructions()
    
    print("🎉 Demo completed! Your QR code label system is ready to use.")
    print("\nTo get started:")
    print("1. Run: python manage.py runserver")
    print("2. Visit: http://127.0.0.1:8000/assets/")
    print("3. Click 'Print Labels' on any asset or 'Bulk Print Labels' for multiple assets")

if __name__ == "__main__":
    main()