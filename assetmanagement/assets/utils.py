"""
Utility functions for asset management
"""
import base64
import io
from PIL import Image, ImageDraw, ImageFont
try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False


def generate_qr_code_image(data, size=(200, 200), logo_path=None):
    """Generate QR code image as base64 string, with optional centre logo."""
    if not HAS_QRCODE:
        return None

    from django.core.cache import cache
    cache_key = f"qr_{hash(data)}_{size[0]}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=12,  # larger box = sharper at any display size
        border=3,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#0D1B6E", back_color="white").convert("RGBA")

    if not logo_path:
        import os
        from django.conf import settings as _s
        logo_path = str(getattr(_s, 'COMPANY_LOGO_PATH',
                                os.path.join(_s.BASE_DIR, 'static', 'images', 'company_logo.png')))
    try:
        logo = Image.open(logo_path).convert("RGBA")
        qr_w, qr_h = img.size
        logo_size = int(qr_w * 0.18)  # smaller — 18% so it doesn't block modules
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
        pad = int(logo_size * 0.15)
        circle_d = logo_size + pad * 2
        circle = Image.new("RGBA", (circle_d, circle_d), (0, 0, 0, 0))
        ImageDraw.Draw(circle).ellipse([0, 0, circle_d - 1, circle_d - 1], fill=(255, 255, 255, 255))
        circle.paste(logo, (pad, pad), logo)
        pos = ((qr_w - circle_d) // 2, (qr_h - circle_d) // 2)
        img.paste(circle, pos, circle)
    except Exception:
        pass

    img = img.resize(size, Image.Resampling.BILINEAR)
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    result = f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"

    cache.set(cache_key, result, timeout=86400)  # cache for 24h
    return result


def generate_asset_label_data(asset, request):
    """
    Generate all data needed for asset labels
    """
    from django.conf import settings
    
    # Build network URL for the asset (accessible from mobile devices without login)
    if hasattr(settings, 'QR_CODE_BASE_URL') and settings.QR_CODE_BASE_URL:
        asset_url = f"{settings.QR_CODE_BASE_URL}/assets/{asset.id}/public/"
    else:
        # Fallback to request-based URL (public view)
        asset_url = request.build_absolute_uri(f'/assets/{asset.id}/public/')
    
    # Generate QR code image
    qr_image = generate_qr_code_image(asset_url)
    
    return {
        'asset': asset,
        'qr_image': qr_image,
        'asset_url': asset_url,
        'company_name': getattr(request, 'company_name', 'Your Company'),
        'has_qrcode': HAS_QRCODE,
    }


def generate_user_qr_data(user, request):
    """
    Generate QR code data for user containing all user details except password and manager,
    plus assets assigned to that user
    """
    from django.conf import settings
    from django.contrib.auth.models import User
    import json
    
    # Get user profile if it exists
    profile = getattr(user, 'profile', None)
    
    # Get assigned assets
    assigned_assets = []
    if hasattr(user, 'assigned_assets'):
        for asset in user.assigned_assets.all():
            assigned_assets.append({
                'id': asset.id,
                'asset_tag': asset.asset_tag,
                'name': asset.name,
                'category': asset.category.name if asset.category else None,
                'serial_number': asset.serial_number,
                'status': asset.status,
            })
    
    # Build user data (excluding password and manager)
    user_data = {
        'user_id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'is_active': user.is_active,
        'date_joined': user.date_joined.isoformat() if user.date_joined else None,
    }
    
    # Add profile data if available
    if profile:
        user_data.update({
            'employee_id': profile.employee_id,
            'phone': profile.phone,
            'mobile': profile.mobile,
            'job_title': profile.job_title,
            'department': profile.department.name if profile.department else None,
            'location': profile.location.name if profile.location else None,
            'timezone': profile.timezone,
            'language': profile.language,
        })
    
    # Add assigned assets
    user_data['assigned_assets'] = assigned_assets
    
    # Convert to JSON string for QR code
    qr_data = json.dumps(user_data, indent=2)
    
    # Build user profile URL (public view for QR code scanning)
    if hasattr(settings, 'QR_CODE_BASE_URL') and settings.QR_CODE_BASE_URL:
        user_url = f"{settings.QR_CODE_BASE_URL}/users/{user.id}/public/"
    else:
        user_url = request.build_absolute_uri(f'/users/{user.id}/public/')
    
    # Generate QR code image with user data
    qr_image = generate_qr_code_image(qr_data)
    
    return {
        'user': user,
        'user_data': user_data,
        'qr_data': qr_data,
        'qr_image': qr_image,
        'user_url': user_url,
        'assigned_assets': assigned_assets,
        'has_qrcode': HAS_QRCODE,
    }


def create_avery_5160_layout():
    """
    Create layout data for Avery 5160 labels (30 labels per sheet)
    """
    # Avery 5160 specifications (in inches)
    page_width = 8.5
    page_height = 11
    label_width = 2.625
    label_height = 1
    left_margin = 0.1875
    top_margin = 0.5
    horizontal_spacing = 0.125
    vertical_spacing = 0
    
    labels_per_row = 3
    rows_per_page = 10
    
    positions = []
    
    for row in range(rows_per_page):
        for col in range(labels_per_row):
            x = left_margin + (col * (label_width + horizontal_spacing))
            y = top_margin + (row * (label_height + vertical_spacing))
            
            positions.append({
                'x': x,
                'y': y,
                'width': label_width,
                'height': label_height,
            })
    
    return {
        'page_width': page_width,
        'page_height': page_height,
        'positions': positions,
        'labels_per_page': len(positions),
    }


def create_standard_label_layout():
    """
    Create layout for standard 2.5" x 2" labels
    """
    # Standard layout (4 labels per page)
    page_width = 8.5
    page_height = 11
    label_width = 2.5
    label_height = 2
    margin = 0.5
    
    labels_per_row = 3
    rows_per_page = 4
    
    positions = []
    
    for row in range(rows_per_page):
        for col in range(labels_per_row):
            if col * (label_width + margin) + label_width > page_width - margin:
                break
            if row * (label_height + margin) + label_height > page_height - margin:
                break
                
            x = margin + (col * (label_width + margin))
            y = margin + (row * (label_height + margin))
            
            positions.append({
                'x': x,
                'y': y,
                'width': label_width,
                'height': label_height,
            })
    
    return {
        'page_width': page_width,
        'page_height': page_height,
        'positions': positions,
        'labels_per_page': len(positions),
    }