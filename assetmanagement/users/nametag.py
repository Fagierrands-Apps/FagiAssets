"""
ID card generator — overlays employee data onto the Fagi Errands PDF template.
"""
import io

from PIL import Image as PILImage, ImageDraw
from reportlab.lib.units import mm
pt = 1  # ReportLab internal unit is already points
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics

# ── Page size (matches the Canva template exactly) ────────────────────────────
PAGE_W = 1054 * pt
PAGE_H = 1492 * pt

# ── Colours ───────────────────────────────────────────────────────────────────
NAVY  = colors.HexColor("#0D1B6E")
WHITE = colors.white

# ── Layout constants (in pts, origin = bottom-left) ───────────────────────────
# Photo placeholder rounded-rect
PHOTO_X1 = 109.0 * pt
PHOTO_Y1  = 1169.5 * pt
PHOTO_X2  = 335.7 * pt
PHOTO_Y2  = 1396.0 * pt

# Name baseline
NAME_Y = 1084.0 * pt

# Info rows — icon center x, and y centres for each of the 5 rows
ICON_X   = 213.9 * pt
ROW_YS   = [542.2 * pt, 464.3 * pt, 389.3 * pt, 313.8 * pt, 237.7 * pt]

# Text starts just right of the vertical divider line
TEXT_X = 245.0 * pt


# ── Helpers ───────────────────────────────────────────────────────────────────

def _template_reader():
    """Return an ImageReader of the front template (converts PDF→PNG on first call)."""
    import os, subprocess, tempfile
    pdf_path = os.path.join(os.path.dirname(__file__), 'id_template_front.pdf')
    png_path = pdf_path.replace('.pdf', '_cached.png')

    if not os.path.exists(png_path):
        subprocess.run(
            ['pdftoppm', '-r', '150', '-png', '-singlefile', pdf_path,
             png_path.replace('.png', '')],
            check=True
        )

    return ImageReader(png_path)


def _rounded_photo(path, w_px, h_px, radius_ratio=0.08):
    """Return ImageReader of photo cropped to rounded rectangle."""
    size = (int(w_px), int(h_px))
    try:
        img = PILImage.open(path).convert("RGBA")
        iw, ih = img.size
        # centre-crop to target aspect
        target_ratio = w_px / h_px
        if iw / ih > target_ratio:
            new_w = int(ih * target_ratio)
            img = img.crop(((iw - new_w) // 2, 0, (iw + new_w) // 2, ih))
        else:
            new_h = int(iw / target_ratio)
            img = img.crop((0, (ih - new_h) // 2, iw, (ih + new_h) // 2))
        img = img.resize(size, PILImage.LANCZOS)
    except Exception:
        img = PILImage.new("RGBA", size, (200, 200, 200, 255))
        d = ImageDraw.Draw(img)
        cx, cy = size[0]//2, size[1]//2
        r = min(cx, cy) // 2
        d.ellipse([cx-r, cy-r*2, cx+r, cy], fill=(160,160,160,255))
        d.ellipse([cx-r*2, cy, cx+r*2, cy+r*3], fill=(160,160,160,255))

    # Rounded-rect mask
    mask = PILImage.new("L", size, 0)
    radius = int(min(size) * radius_ratio * 6)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size[0]-1, size[1]-1],
                                           radius=radius, fill=255)
    out = PILImage.new("RGBA", size, (255, 255, 255, 0))
    out.paste(img, mask=mask)
    buf = io.BytesIO()
    out.save(buf, format="PNG")
    buf.seek(0)
    return ImageReader(buf)


def _resolve_profile(user):
    from types import SimpleNamespace
    up  = getattr(user, 'profile', None)
    emp = getattr(user, 'employee_profile', None)

    def _get(*attrs):
        for src in (up, emp):
            if not src:
                continue
            for a in attrs:
                v = getattr(src, a, None)
                if v:
                    return v
        return None

    dept_obj  = _get('department')
    dept_name = (dept_obj.name if hasattr(dept_obj, 'name') else str(dept_obj)) if dept_obj else None

    return SimpleNamespace(
        employee_id = _get('employee_id'),
        job_title   = _get('job_title', 'position'),
        department  = SimpleNamespace(name=dept_name) if dept_name else None,
        phone       = _get('phone', 'mobile'),
        avatar      = _get('avatar'),
        qr_token    = _get('qr_token'),
        email       = getattr(user, 'email', None),
    )


# ── Card renderer ─────────────────────────────────────────────────────────────

def _draw_card(c, user, profile):
    from reportlab.platypus import Image as RLImage

    # 1. Stamp the template as background
    c.drawImage(_template_reader(), 0, 0, width=PAGE_W, height=PAGE_H)

    # 2. Photo
    photo_w = PHOTO_X2 - PHOTO_X1
    photo_h = PHOTO_Y2 - PHOTO_Y1

    photo_path = None
    if profile and profile.avatar:
        try:
            photo_path = profile.avatar.path
        except Exception:
            pass

    c.drawImage(
        _rounded_photo(photo_path, photo_w * 4, photo_h * 4),
        PHOTO_X1, PHOTO_Y1,
        width=photo_w, height=photo_h,
        mask='auto',
    )

    # 3. Full name (centred on card)
    name = (user.get_full_name() or user.username).strip().upper()
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 52)
    c.drawCentredString(PAGE_W / 2, NAME_Y, name)

    # 4. Info rows — icon already on template, just draw the value text
    emp_id = (profile.employee_id if profile and profile.employee_id else None) or "N/A"
    phone  = (profile.phone       if profile and profile.phone       else None) or "N/A"
    email  = (profile.email       if profile and profile.email       else None) or "N/A"
    dept   = (profile.department.name if profile and profile.department else None) or "N/A"
    loc    = "Next Gen Mall"

    values = [emp_id, phone, email, dept, loc]

    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 28)
    for row_y, val in zip(ROW_YS, values):
        # vertically centre text on icon
        c.drawString(TEXT_X, row_y - 10 * pt, val[:35])


# ── Public entry points ───────────────────────────────────────────────────────

def generate_nametag_pdf(user, request):
    profile = _resolve_profile(user)
    buf = io.BytesIO()
    c   = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))
    _draw_card(c, user, profile)
    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()


def generate_bulk_nametag_pdf(users, request):
    buf = io.BytesIO()
    c   = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))
    for user in users:
        profile = _resolve_profile(user)
        _draw_card(c, user, profile)
        c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()
