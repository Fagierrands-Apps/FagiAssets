"""
Public views for users (accessible without login via QR codes)
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods


def user_public_view(request, user_id):
    """Public view for user information (accessible via QR code without login)"""
    user = get_object_or_404(User, id=user_id)
    
    # Get user profile if it exists
    profile = getattr(user, 'profile', None)
    
    # Get assigned assets (public information only)
    assigned_assets = []
    if hasattr(user, 'assigned_assets'):
        for asset in user.assigned_assets.filter(status__in=['active', 'assigned']):
            assigned_assets.append({
                'asset_tag': asset.asset_tag,
                'name': asset.name,
                'category': asset.category.name if asset.category else None,
                'status': asset.status,
            })
    
    context = {
        'profile_user': user,
        'profile': profile,
        'assigned_assets': assigned_assets,
        'is_public_view': True,
    }
    
    return render(request, 'users/user_public_view.html', context)


@require_http_methods(["GET"])
def user_public_data_json(request, user_id):
    """Public JSON endpoint for user data (accessible via QR code without login)"""
    user = get_object_or_404(User, id=user_id)
    
    # Get user profile if it exists
    profile = getattr(user, 'profile', None)
    
    # Get assigned assets (public information only)
    assigned_assets = []
    if hasattr(user, 'assigned_assets'):
        for asset in user.assigned_assets.filter(status__in=['active', 'assigned']):
            assigned_assets.append({
                'asset_tag': asset.asset_tag,
                'name': asset.name,
                'category': asset.category.name if asset.category else None,
                'status': asset.status,
            })
    
    # Build public user data (safe information only)
    user_data = {
        'user_id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'is_active': user.is_active,
        'assigned_assets': assigned_assets,
    }
    
    # Add safe profile data if available
    if profile:
        user_data.update({
            'employee_id': profile.employee_id,
            'phone': profile.phone,
            'job_title': profile.job_title,
            'department': profile.department.name if profile.department else None,
            'location': profile.location.name if profile.location else None,
        })
    
    return JsonResponse(user_data, json_dumps_params={'indent': 2})


def user_public_profile(request, qr_token):
    from users.models import UserProfile
    from django.conf import settings
    from types import SimpleNamespace

    up   = get_object_or_404(UserProfile, qr_token=qr_token)
    user = up.user
    emp  = getattr(user, 'employee_profile', None)

    # Merge: prefer employee_profile data, fall back to UserProfile
    profile = SimpleNamespace(
        employee_id = (emp.employee_id if emp else None) or up.employee_id or "N/A",
        job_title   = (emp.position    if emp else None) or up.job_title   or "N/A",
        department  = SimpleNamespace(name=str(emp.department)) if emp and emp.department else (
                      up.department if up.department else None),
        phone       = (emp.phone       if emp else None) or up.phone or up.mobile or "N/A",
        avatar      = up.avatar if up.avatar else None,
    )

    context = {
        'profile_user': user,
        'profile': profile,
        'qr_token': str(up.qr_token),
        'company_name': getattr(settings, 'COMPANY_NAME', 'Fagi Errands Services Limited'),
        'company_website': getattr(settings, 'COMPANY_WEBSITE', 'fagierrands.com'),
    }
    return render(request, 'users/user_public_profile.html', context)


def user_qr_pdf(request, qr_token):
    """Download employee QR code as a high-quality JPEG."""
    import io, os
    from users.models import UserProfile
    from PIL import Image as PILImage, ImageDraw, ImageFont
    from django.conf import settings as _s
    import qrcode

    up   = get_object_or_404(UserProfile, qr_token=qr_token)
    user = up.user
    emp  = getattr(user, 'employee_profile', None)
    name = (user.get_full_name() or user.username).upper()
    role = (emp.position if emp else None) or "Employee"

    public_url = request.build_absolute_uri(f'/users/public/{qr_token}/')

    # High-res QR
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H,
                       box_size=20, border=3)
    qr.add_data(public_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#0D1B6E", back_color="white").convert("RGBA")

    # Logo in centre
    logo_path = str(getattr(_s, 'COMPANY_LOGO_PATH',
                            os.path.join(_s.BASE_DIR, 'static', 'images', 'company_logo.png')))
    try:
        logo = PILImage.open(logo_path).convert("RGBA")
        qr_w = qr_img.size[0]
        ls = int(qr_w * 0.18)
        logo = logo.resize((ls, ls), PILImage.Resampling.LANCZOS)
        pad = int(ls * 0.2)
        cd = ls + pad * 2
        circle = PILImage.new("RGBA", (cd, cd), (0, 0, 0, 0))
        ImageDraw.Draw(circle).ellipse([0, 0, cd-1, cd-1], fill=(255, 255, 255, 255))
        circle.paste(logo, (pad, pad), logo)
        qr_img.paste(circle, ((qr_w - cd)//2, (qr_w - cd)//2), circle)
    except Exception:
        pass

    # Compose final image: white canvas, QR + name + role
    qr_rgb = qr_img.convert("RGB")
    qr_w, qr_h = qr_rgb.size
    padding = 60
    text_area = 120
    canvas_w = qr_w + padding * 2
    canvas_h = qr_h + padding * 2 + text_area

    out = PILImage.new("RGB", (canvas_w, canvas_h), (255, 255, 255))
    out.paste(qr_rgb, (padding, padding))

    draw = ImageDraw.Draw(out)
    # Name text
    try:
        font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        font_reg  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    except Exception:
        font_bold = ImageFont.load_default()
        font_reg  = font_bold

    # Name centred
    bbox = draw.textbbox((0, 0), name, font=font_bold)
    tw = bbox[2] - bbox[0]
    draw.text(((canvas_w - tw) // 2, qr_h + padding + 20), name,
              fill=(13, 27, 110), font=font_bold)

    # Role centred
    bbox2 = draw.textbbox((0, 0), role, font=font_reg)
    tw2 = bbox2[2] - bbox2[0]
    draw.text(((canvas_w - tw2) // 2, qr_h + padding + 78), role,
              fill=(255, 107, 0), font=font_reg)

    buf = io.BytesIO()
    out.save(buf, format='JPEG', quality=95, dpi=(300, 300))
    buf.seek(0)

    response = HttpResponse(buf.read(), content_type='image/jpeg')
    response['Content-Disposition'] = f'attachment; filename="{user.username}_qr.jpg"'
    return response


def rider_public_profile(request, qr_token):
    """Public profile page for a rider — accessible via QR scan, no login needed."""
    from users.models import Rider
    from django.conf import settings
    rider = get_object_or_404(Rider, qr_token=qr_token)
    context = {
        'rider': rider,
        'company_name': getattr(settings, 'COMPANY_NAME', 'Fagi Errands Services Limited'),
        'company_website': getattr(settings, 'COMPANY_WEBSITE', 'fagierrands.com'),
    }
    return render(request, 'users/rider_public_profile.html', context)


def rider_qr_download(request, qr_token):
    """Download rider QR code as a high-quality JPEG."""
    import io, os
    from users.models import Rider
    from PIL import Image as PILImage, ImageDraw, ImageFont
    from django.conf import settings as _s
    import qrcode

    rider = get_object_or_404(Rider, qr_token=qr_token)
    public_url = request.build_absolute_uri(f'/users/rider/{qr_token}/')

    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=20, border=3)
    qr.add_data(public_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#0D1B6E", back_color="white").convert("RGBA")

    # Logo in centre
    logo_path = str(getattr(_s, 'COMPANY_LOGO_PATH',
                            os.path.join(_s.BASE_DIR, 'static', 'images', 'company_logo.png')))
    try:
        logo = PILImage.open(logo_path).convert("RGBA")
        qr_w = qr_img.size[0]
        ls = int(qr_w * 0.18)
        logo = logo.resize((ls, ls), PILImage.Resampling.LANCZOS)
        pad = int(ls * 0.2)
        cd = ls + pad * 2
        circle = PILImage.new("RGBA", (cd, cd), (0, 0, 0, 0))
        ImageDraw.Draw(circle).ellipse([0, 0, cd-1, cd-1], fill=(255, 255, 255, 255))
        circle.paste(logo, (pad, pad), logo)
        qr_img.paste(circle, ((qr_w - cd)//2, (qr_w - cd)//2), circle)
    except Exception:
        pass

    qr_rgb = qr_img.convert("RGB")
    qr_w, qr_h = qr_rgb.size
    padding, text_area = 60, 120
    canvas_w = qr_w + padding * 2
    canvas_h = qr_h + padding * 2 + text_area

    out = PILImage.new("RGB", (canvas_w, canvas_h), (255, 255, 255))
    out.paste(qr_rgb, (padding, padding))
    draw = ImageDraw.Draw(out)

    try:
        font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        font_reg  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    except Exception:
        font_bold = font_reg = ImageFont.load_default()

    name = rider.name.upper()
    role = f"Rider · {rider.rider_id}"

    bbox = draw.textbbox((0, 0), name, font=font_bold)
    draw.text(((canvas_w - (bbox[2]-bbox[0])) // 2, qr_h + padding + 20),
              name, fill=(13, 27, 110), font=font_bold)
    bbox2 = draw.textbbox((0, 0), role, font=font_reg)
    draw.text(((canvas_w - (bbox2[2]-bbox2[0])) // 2, qr_h + padding + 78),
              role, fill=(255, 107, 0), font=font_reg)

    buf = io.BytesIO()
    out.save(buf, format='JPEG', quality=95, dpi=(300, 300))
    buf.seek(0)
    response = HttpResponse(buf.read(), content_type='image/jpeg')
    response['Content-Disposition'] = f'attachment; filename="rider_{rider.rider_id}_qr.jpg"'
    return response
