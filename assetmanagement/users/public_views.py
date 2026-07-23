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
    """Download employee QR code as a high-quality PDF — no login required."""
    import io
    from users.models import UserProfile
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm
    from reportlab.lib.utils import ImageReader
    from PIL import Image as PILImage
    import qrcode, base64

    up   = get_object_or_404(UserProfile, qr_token=qr_token)
    user = up.user
    emp  = getattr(user, 'employee_profile', None)
    name = user.get_full_name() or user.username
    role = (emp.position if emp else None) or "Employee"

    public_url = request.build_absolute_uri(f'/users/public/{qr_token}/')

    # Generate high-res QR with logo in centre
    import os
    from PIL import ImageDraw
    from django.conf import settings as _s

    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H,
                       box_size=20, border=3)
    qr.add_data(public_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#0D1B6E", back_color="white").convert("RGBA")

    # Embed logo
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

    qr_buf = io.BytesIO()
    qr_img.convert("RGB").save(qr_buf, format='PNG', dpi=(300, 300))
    qr_buf.seek(0)

    # PDF page: 80x100mm
    pw, ph = 80*mm, 100*mm
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(pw, ph))

    # White background
    c.setFillColorRGB(1, 1, 1)
    c.rect(0, 0, pw, ph, fill=1, stroke=0)

    # QR code centred
    qr_size = 60*mm
    qr_x = (pw - qr_size) / 2
    qr_y = ph - 10*mm - qr_size
    c.drawImage(ImageReader(qr_buf), qr_x, qr_y, width=qr_size, height=qr_size)

    # Name
    c.setFillColorRGB(0.05, 0.11, 0.43)  # navy
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(pw/2, qr_y - 8*mm, name.upper())

    # Role
    c.setFillColorRGB(0.91, 0.23, 0)  # orange
    c.setFont("Helvetica", 8)
    c.drawCentredString(pw/2, qr_y - 13*mm, role)

    # Tagline
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.setFont("Helvetica", 7)
    c.drawCentredString(pw/2, 6*mm, "Scan to view profile • fagierrands.com")

    c.save()
    buf.seek(0)

    filename = f"{user.username}_qr.pdf"
    response = HttpResponse(buf.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
