from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.urls import reverse
import json
from datetime import datetime, timedelta

from .models import (
    Asset, AssetModel, AssetCategory, Manufacturer, Location, Department,
    AssetHistory, MaintenanceRecord, NetworkInterface, SoftwareInstallation
)


@login_required
def asset_list(request):
    """Display paginated list of assets with filtering"""
    assets = Asset.objects.select_related(
        'model__manufacturer', 'model__category', 'assigned_to', 'location', 'department'
    ).all()
    
    # Apply filters
    status_filter = request.GET.get('status')
    if status_filter:
        assets = assets.filter(status=status_filter)
    
    location_filter = request.GET.get('location')
    if location_filter:
        assets = assets.filter(location_id=location_filter)
    
    department_filter = request.GET.get('department')
    if department_filter:
        assets = assets.filter(department_id=department_filter)
    
    search_query = request.GET.get('search')
    if search_query:
        assets = assets.filter(
            Q(asset_tag__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(serial_number__icontains=search_query) |
            Q(model__name__icontains=search_query) |
            Q(model__manufacturer__name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(assets, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'assets': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'locations': Location.objects.all(),
        'departments': Department.objects.all(),
    }
    
    return render(request, 'assets/asset_list.html', context)


@login_required
def asset_detail(request, asset_id):
    """Display detailed view of a single asset"""
    asset = get_object_or_404(Asset.objects.select_related(
        'model__manufacturer', 'model__category', 'assigned_to', 'location', 'department'
    ).prefetch_related('assigned_users'), id=asset_id)

    # Get recent history
    recent_history = asset.history.all()[:5]

    # Get recent maintenance
    recent_maintenance = asset.maintenance_records.all()[:3]

    context = {
        'asset': asset,
        'recent_history': recent_history,
        'recent_maintenance': recent_maintenance,
        'users': User.objects.filter(is_active=True),
    }

    return render(request, 'assets/asset_detail.html', context)


@login_required
def asset_form(request, asset_id=None):
    """Create or edit asset form"""
    asset = None
    if asset_id:
        asset = get_object_or_404(Asset, id=asset_id)
    
    if request.method == 'POST':
        try:
            # Basic information
            asset_tag = request.POST.get('asset_tag', '').strip()
            name = request.POST.get('name')
            serial_number = request.POST.get('serial_number', '')
            status = request.POST.get('status')
            
            # Model information
            model_id = request.POST.get('model')
            model = get_object_or_404(AssetModel, id=model_id)

            # Category information
            category_id = request.POST.get('asset_category')
            category = None
            if category_id:
                category = get_object_or_404(AssetCategory, id=category_id)
            
            # Assignment information
            assigned_users_ids = request.POST.getlist('assigned_users')
            assigned_users = User.objects.filter(id__in=assigned_users_ids) if assigned_users_ids else []
            # For backward compatibility, set assigned_to to the first user
            assigned_to = assigned_users[0] if assigned_users else None
            
            department_id = request.POST.get('department')
            department = Department.objects.get(id=department_id) if department_id else None
            
            location_id = request.POST.get('location')
            location = Location.objects.get(id=location_id) if location_id else None
            
            # Financial information
            purchase_date = request.POST.get('purchase_date') or None
            purchase_cost = request.POST.get('purchase_cost') or None
            warranty_expires = request.POST.get('warranty_expires') or None
            
            # Network information
            ip_address = request.POST.get('ip_address', '')
            mac_address = request.POST.get('mac_address', '')
            hostname = request.POST.get('hostname', '')
            
            # Device specifications
            device_name = request.POST.get('device_name', '')
            processor = request.POST.get('processor', '')
            installed_ram = request.POST.get('installed_ram', '')
            device_id = request.POST.get('device_id', '')
            product_id = request.POST.get('product_id', '')
            system_type = request.POST.get('system_type', '')
            
            # Additional information
            notes = request.POST.get('notes', '')
            image = request.FILES.get('image')
            
            if asset:
                # Update existing asset
                previous_values = {
                    'name': asset.name,
                    'status': asset.status,
                    'assigned_to': asset.assigned_to.get_full_name() if asset.assigned_to else None,
                    'location': asset.location.name if asset.location else None,
                    'department': asset.department.name if asset.department else None,
                }
                
                asset.name = name
                asset.serial_number = serial_number
                asset.status = status
                asset.model = model
                asset.category = category
                asset.assigned_to = assigned_to
                asset.department = department
                asset.location = location
                asset.purchase_date = purchase_date
                asset.purchase_cost = purchase_cost
                asset.warranty_expires = warranty_expires
                asset.ip_address = ip_address
                asset.mac_address = mac_address
                asset.hostname = hostname
                asset.device_name = device_name
                asset.processor = processor
                asset.installed_ram = installed_ram
                asset.device_id = device_id
                asset.product_id = product_id
                asset.system_type = system_type
                asset.notes = notes
                if image:
                    asset.image = image
                asset.save()

                # Update assigned users
                asset.assigned_users.set(assigned_users)

                # Create history record
                new_values = {
                    'name': asset.name,
                    'status': asset.status,
                    'assigned_to': asset.assigned_to.get_full_name() if asset.assigned_to else None,
                    'location': asset.location.name if asset.location else None,
                    'department': asset.department.name if asset.department else None,
                }

                AssetHistory.objects.create(
                    asset=asset,
                    action='updated',
                    description=f'Asset {asset.asset_tag} was updated',
                    user=request.user,
                    previous_values=previous_values,
                    new_values=new_values
                )

                messages.success(request, f'Asset {asset.asset_tag} updated successfully!')
            else:
                # Create new asset
                asset = Asset.objects.create(
                    asset_tag=asset_tag if asset_tag else '',
                    name=name,
                    serial_number=serial_number,
                    status=status,
                    model=model,
                    category=category,
                    assigned_to=assigned_to,
                    department=department,
                    location=location,
                    purchase_date=purchase_date,
                    purchase_cost=purchase_cost,
                    warranty_expires=warranty_expires,
                    ip_address=ip_address,
                    mac_address=mac_address,
                    hostname=hostname,
                    device_name=device_name,
                    processor=processor,
                    installed_ram=installed_ram,
                    device_id=device_id,
                    product_id=product_id,
                    system_type=system_type,
                    notes=notes,
                    image=image
                )

                # Set assigned users
                asset.assigned_users.set(assigned_users)

                # Create history record
                AssetHistory.objects.create(
                    asset=asset,
                    action='created',
                    description=f'Asset {asset.asset_tag} was created',
                    user=request.user
                )

                messages.success(request, f'Asset {asset.asset_tag} created successfully!')
            
            return redirect('asset_detail', asset_id=asset.id)
            
        except Exception as e:
            messages.error(request, f'Error saving asset: {str(e)}')
    
    context = {
        'asset': asset,
        'manufacturers': Manufacturer.objects.all(),
        'categories': AssetCategory.objects.all(),
        'models': AssetModel.objects.select_related('manufacturer', 'category'),
        'users': User.objects.filter(is_active=True),
        'departments': Department.objects.all(),
        'locations': Location.objects.all(),
    }
    
    return render(request, 'assets/asset_form.html', context)


@login_required
def asset_qr_code(request, asset_id):
    """Generate QR code for asset"""
    from django.conf import settings
    
    asset = get_object_or_404(Asset, id=asset_id)
    
    # Generate public URL for QR code
    if hasattr(settings, 'QR_CODE_BASE_URL') and settings.QR_CODE_BASE_URL:
        public_url = f"{settings.QR_CODE_BASE_URL}/assets/{asset.id}/public/"
    else:
        public_url = request.build_absolute_uri(f'/assets/{asset.id}/public/')
    
    context = {
        'asset': asset,
        'public_url': public_url,
    }
    
    return render(request, 'assets/asset_qr_code.html', context)


def asset_public_view(request, asset_id):
    """Public view for asset information (accessible via QR code without login)"""
    asset = get_object_or_404(Asset, id=asset_id)
    
    # Get basic asset information that's safe to show publicly
    # Collect assigned users (supports both legacy single assignment and new many-to-many)
    assigned_users = []
    if asset.assigned_to:
        assigned_users.append(asset.assigned_to)
    assigned_users += list(asset.assigned_users.all())
    # Deduplicate
    assigned_users = list({u.id: u for u in assigned_users}.values())

    context = {
        'asset': asset,
        'assigned_users': assigned_users,
        'is_public_view': True,
    }
    
    return render(request, 'assets/asset_public_view.html', context)


@login_required
def asset_label_print(request, asset_id):
    """Generate printable labels for asset"""
    asset = get_object_or_404(Asset, id=asset_id)
    
    from .utils import generate_asset_label_data
    
    # Generate label data including QR code
    label_data = generate_asset_label_data(asset, request)
    
    context = {
        'asset': asset,
        'label_data': label_data,
    }
    
    return render(request, 'assets/asset_label_professional.html', context)


@login_required
def bulk_label_print(request):
    """Generate bulk printable labels for multiple assets"""
    # Get all assets or filter by department/location if specified
    assets = Asset.objects.select_related('model__manufacturer', 'location', 'assigned_to').filter(
        status__in=['active', 'assigned']
    ).order_by('asset_tag')
    
    # Apply filters if provided
    department_id = request.GET.get('department')
    location_id = request.GET.get('location')
    
    if department_id:
        assets = assets.filter(assigned_to__profile__department_id=department_id)
    
    if location_id:
        assets = assets.filter(location_id=location_id)
    
    from django.conf import settings
    public_base = getattr(settings, 'QR_CODE_BASE_URL', '').rstrip('/')

    context = {
        'assets': assets,
        'public_base': public_base,
    }
    
    return render(request, 'assets/bulk_label_print.html', context)


@login_required
def asset_qr_code_image(request, asset_id):
    """Generate high-quality QR code image for asset"""
    from django.http import HttpResponse
    from .utils import generate_qr_code_image
    from django.conf import settings
    import base64
    
    asset = get_object_or_404(Asset, id=asset_id)
    
    # Get size parameter (default 200x200, max 1000x1000)
    size = min(int(request.GET.get('size', 200)), 1000)
    
    # Build network URL for the asset (accessible from mobile devices without login)
    if hasattr(settings, 'QR_CODE_BASE_URL') and settings.QR_CODE_BASE_URL:
        asset_url = f"{settings.QR_CODE_BASE_URL}/assets/{asset.id}/public/"
    else:
        # Fallback to request-based URL (public view)
        asset_url = request.build_absolute_uri(f'/assets/{asset.id}/public/')
    
    # Generate QR code
    qr_data_url = generate_qr_code_image(asset_url, size=(size, size))
    
    if qr_data_url:
        # Extract base64 data
        base64_data = qr_data_url.split(',')[1]
        image_data = base64.b64decode(base64_data)
        
        # Return as PNG image
        response = HttpResponse(image_data, content_type='image/png')
        response['Content-Disposition'] = f'inline; filename="{asset.asset_tag}_qr_{size}x{size}.png"'
        response['Cache-Control'] = 'max-age=3600'  # Cache for 1 hour
        return response
    else:
        # Fallback: return a simple error image
        return HttpResponse("QR code generation failed", status=500)


@login_required
def download_asset_qr_code(request, asset_id):
    """Download high-resolution QR code for asset"""
    from django.http import HttpResponse
    from .utils import generate_qr_code_image
    from django.conf import settings
    import base64
    
    asset = get_object_or_404(Asset, id=asset_id)
    
    # High resolution for printing (600x600)
    size = int(request.GET.get('size', 600))
    
    # Build network URL for the asset (accessible from mobile devices without login)
    if hasattr(settings, 'QR_CODE_BASE_URL') and settings.QR_CODE_BASE_URL:
        asset_url = f"{settings.QR_CODE_BASE_URL}/assets/{asset.id}/public/"
    else:
        # Fallback to request-based URL (public view)
        asset_url = request.build_absolute_uri(f'/assets/{asset.id}/public/')
    
    # Generate QR code
    qr_data_url = generate_qr_code_image(asset_url, size=(size, size))
    
    if qr_data_url:
        # Extract base64 data
        base64_data = qr_data_url.split(',')[1]
        image_data = base64.b64decode(base64_data)
        
        # Return as download
        response = HttpResponse(image_data, content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="{asset.asset_tag}_qr_code_{size}x{size}.png"'
        return response
    else:
        return HttpResponse("QR code generation failed", status=500)


@login_required
def asset_history(request, asset_id):
    """Display asset history"""
    asset = get_object_or_404(Asset, id=asset_id)
    
    history_records = asset.history.all()
    
    # Pagination
    paginator = Paginator(history_records, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    total_records = history_records.count()
    days_since_created = (timezone.now() - asset.created_at).days
    assignment_changes = history_records.filter(action='assigned').count()
    status_changes = history_records.filter(action='status_changed').count()
    
    # Action breakdown
    action_breakdown = history_records.values('action').annotate(count=Count('action')).order_by('-count')
    
    # Recent activity (last 5 records)
    recent_activity = history_records[:5]
    
    context = {
        'asset': asset,
        'history_records': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'total_records': total_records,
        'days_since_created': days_since_created,
        'assignment_changes': assignment_changes,
        'status_changes': status_changes,
        'action_breakdown': action_breakdown,
        'recent_activity': recent_activity,
    }
    
    return render(request, 'assets/asset_history.html', context)


@login_required
def asset_maintenance(request, asset_id):
    """Display asset maintenance records"""
    asset = get_object_or_404(Asset, id=asset_id)
    
    maintenance_records = asset.maintenance_records.all()
    
    # Apply filters
    status_filter = request.GET.get('status')
    if status_filter:
        maintenance_records = maintenance_records.filter(status=status_filter)
    
    type_filter = request.GET.get('maintenance_type')
    if type_filter:
        maintenance_records = maintenance_records.filter(maintenance_type=type_filter)
    
    date_from = request.GET.get('date_from')
    if date_from:
        maintenance_records = maintenance_records.filter(scheduled_date__gte=date_from)
    
    date_to = request.GET.get('date_to')
    if date_to:
        maintenance_records = maintenance_records.filter(scheduled_date__lte=date_to)
    
    # Pagination
    paginator = Paginator(maintenance_records, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    total_maintenance = asset.maintenance_records.count()
    completed_maintenance = asset.maintenance_records.filter(status='completed').count()
    scheduled_maintenance = asset.maintenance_records.filter(status='scheduled').count()
    total_cost = sum(m.cost for m in asset.maintenance_records.filter(cost__isnull=False)) or 0
    
    # Get last and next maintenance
    last_maintenance = asset.maintenance_records.filter(status='completed').first()
    next_maintenance = asset.maintenance_records.filter(
        status='scheduled', 
        scheduled_date__gte=timezone.now()
    ).first()
    
    context = {
        'asset': asset,
        'maintenance_records': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'total_maintenance': total_maintenance,
        'completed_maintenance': completed_maintenance,
        'scheduled_maintenance': scheduled_maintenance,
        'total_cost': total_cost,
        'last_maintenance': last_maintenance,
        'next_maintenance': next_maintenance,
        'users': User.objects.filter(is_active=True),
    }
    
    return render(request, 'assets/asset_maintenance.html', context)


@login_required
@require_POST
def asset_assign_user(request, asset_id):
    """Assign user to asset via AJAX"""
    asset = get_object_or_404(Asset, id=asset_id)
    
    try:
        user_id = request.POST.get('assigned_to')
        assignment_notes = request.POST.get('assignment_notes', '')
        
        previous_user = asset.assigned_to
        
        if user_id:
            new_user = get_object_or_404(User, id=user_id)
            asset.assigned_to = new_user
        else:
            asset.assigned_to = None
            new_user = None
        
        asset.save()
        
        # Create history record
        if previous_user != new_user:
            action = 'assigned' if new_user else 'unassigned'
            description = f'Asset {asset.asset_tag} was '
            
            if new_user:
                description += f'assigned to {new_user.get_full_name()}'
            else:
                description += 'unassigned'
            
            if assignment_notes:
                description += f'. Notes: {assignment_notes}'
            
            AssetHistory.objects.create(
                asset=asset,
                action=action,
                description=description,
                user=request.user,
                previous_values={'assigned_to': previous_user.get_full_name() if previous_user else None},
                new_values={'assigned_to': new_user.get_full_name() if new_user else None}
            )
        
        return JsonResponse({'success': True, 'message': 'User assignment updated successfully'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
@require_POST
def asset_schedule_maintenance(request, asset_id):
    """Schedule maintenance for asset"""
    asset = get_object_or_404(Asset, id=asset_id)
    
    try:
        maintenance_type = request.POST.get('maintenance_type')
        scheduled_date = request.POST.get('scheduled_date')
        title = request.POST.get('title')
        description = request.POST.get('description')
        performed_by_id = request.POST.get('performed_by')
        cost = request.POST.get('cost')
        notes = request.POST.get('notes', '')
        
        performed_by = None
        if performed_by_id:
            performed_by = get_object_or_404(User, id=performed_by_id)
        
        # Convert scheduled_date string to datetime
        scheduled_datetime = datetime.fromisoformat(scheduled_date.replace('T', ' '))
        
        maintenance = MaintenanceRecord.objects.create(
            asset=asset,
            maintenance_type=maintenance_type,
            title=title,
            description=description,
            scheduled_date=scheduled_datetime,
            performed_by=performed_by,
            cost=cost if cost else None,
            notes=notes
        )
        
        # Create history record
        AssetHistory.objects.create(
            asset=asset,
            action='maintenance',
            description=f'Maintenance scheduled: {title}',
            user=request.user
        )
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Maintenance scheduled successfully'})
        else:
            messages.success(request, 'Maintenance scheduled successfully!')
            return redirect('asset_maintenance', asset_id=asset.id)
        
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': str(e)})
        else:
            messages.error(request, f'Error scheduling maintenance: {str(e)}')
            return redirect('asset_maintenance', asset_id=asset.id)


@login_required
@require_POST
def asset_change_status(request, asset_id):
    """Change asset status via AJAX"""
    asset = get_object_or_404(Asset, id=asset_id)
    
    try:
        new_status = request.POST.get('status')
        reason = request.POST.get('reason')
        
        previous_status = asset.status
        asset.status = new_status
        asset.save()
        
        # Create history record
        AssetHistory.objects.create(
            asset=asset,
            action='status_changed',
            description=f'Status changed from {asset.get_status_display()} to {dict(Asset.STATUS_CHOICES)[new_status]}. Reason: {reason}',
            user=request.user,
            previous_values={'status': previous_status},
            new_values={'status': new_status}
        )
        
        return JsonResponse({'success': True, 'message': 'Status updated successfully'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
@require_POST
def maintenance_update_status(request):
    """Update maintenance status via AJAX"""
    try:
        maintenance_id = request.POST.get('maintenance_id')
        new_status = request.POST.get('status')
        
        maintenance = get_object_or_404(MaintenanceRecord, id=maintenance_id)
        maintenance.status = new_status
        
        if new_status == 'completed':
            maintenance.completed_date = timezone.now()
        
        maintenance.save()
        
        # Create history record
        AssetHistory.objects.create(
            asset=maintenance.asset,
            action='maintenance',
            description=f'Maintenance "{maintenance.title}" status changed to {maintenance.get_status_display()}',
            user=request.user
        )
        
        return JsonResponse({'success': True, 'message': 'Maintenance status updated successfully'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@login_required
def maintenance_update(request, maintenance_id):
    """Update maintenance record"""
    maintenance = get_object_or_404(MaintenanceRecord, id=maintenance_id)
    
    if request.method == 'POST':
        try:
            maintenance.maintenance_type = request.POST.get('maintenance_type')
            maintenance.title = request.POST.get('title')
            maintenance.description = request.POST.get('description')
            maintenance.status = request.POST.get('status')
            
            scheduled_date = request.POST.get('scheduled_date')
            maintenance.scheduled_date = datetime.fromisoformat(scheduled_date.replace('T', ' '))
            
            performed_by_id = request.POST.get('performed_by')
            if performed_by_id:
                maintenance.performed_by = get_object_or_404(User, id=performed_by_id)
            else:
                maintenance.performed_by = None
            
            cost = request.POST.get('cost')
            maintenance.cost = cost if cost else None
            
            completed_date = request.POST.get('completed_date')
            if completed_date:
                maintenance.completed_date = datetime.fromisoformat(completed_date.replace('T', ' '))
            else:
                maintenance.completed_date = None
            
            maintenance.notes = request.POST.get('notes', '')
            maintenance.save()
            
            # Create history record
            AssetHistory.objects.create(
                asset=maintenance.asset,
                action='maintenance',
                description=f'Maintenance record "{maintenance.title}" was updated',
                user=request.user
            )
            
            messages.success(request, 'Maintenance record updated successfully!')
            
        except Exception as e:
            messages.error(request, f'Error updating maintenance: {str(e)}')
    
    return redirect('asset_maintenance', asset_id=maintenance.asset.id)


@login_required
def user_assignments(request):
    """Display user assignments view"""
    users_with_assets = User.objects.filter(
        assigned_assets__isnull=False
    ).distinct().prefetch_related('assigned_assets__model__manufacturer')
    
    # Get users without assets
    users_without_assets = User.objects.filter(
        assigned_assets__isnull=True,
        is_active=True
    )
    
    context = {
        'users_with_assets': users_with_assets,
        'users_without_assets': users_without_assets,
    }
    
    return render(request, 'assets/user_assignments.html', context)


@login_required
def location_view(request):
    """Display location view"""
    locations = Location.objects.prefetch_related('asset_set__model__manufacturer').all()
    
    context = {
        'locations': locations,
    }
    
    return render(request, 'assets/location_view.html', context)


@login_required
def department_view(request):
    """Display department view"""
    departments = Department.objects.prefetch_related('asset_set__model__manufacturer').all()
    
    context = {
        'departments': departments,
    }
    
    return render(request, 'assets/department_view.html', context)


@login_required
def dashboard(request):
    """Unified Business Management Dashboard"""
    # Asset statistics
    total_assets = Asset.objects.count()
    active_assets = Asset.objects.filter(status='active').count()
    maintenance_assets = Asset.objects.filter(status='maintenance').count()
    retired_assets = Asset.objects.filter(status='retired').count()
    total_users = User.objects.count()
    
    # CRM statistics
    crm_stats = {}
    try:
        # Import inside try to avoid hard dependency when tables aren't ready
        from crm.models import Customer, Lead, AssetCustomerAssignment
        crm_stats = {
            'total_customers': Customer.objects.count(),
            'total_leads': Lead.objects.filter(status='open').count(),
            'total_assignments': AssetCustomerAssignment.objects.count(),
            'new_customers_this_month': Customer.objects.filter(
                created_at__gte=timezone.now().replace(day=1)
            ).count(),
        }
    except Exception:
        # CRM not installed yet or tables not created; keep UI working with zeros
        crm_stats = {
            'total_customers': 0,
            'total_leads': 0,
            'total_assignments': 0,
            'new_customers_this_month': 0,
        }
    
    # Recent activities
    recent_history = AssetHistory.objects.select_related('asset', 'user')[:10]
    
    # Upcoming maintenance
    upcoming_maintenance = MaintenanceRecord.objects.filter(
        status='scheduled',
        scheduled_date__gte=timezone.now(),
        scheduled_date__lte=timezone.now() + timedelta(days=30)
    ).select_related('asset')[:5]
    
    # Assets by category
    assets_by_category = AssetCategory.objects.annotate(
        asset_count=Count('assetmodel__asset')
    ).order_by('-asset_count')[:5]
    
    context = {
        'stats': {
            'total_assets': total_assets,
            'active_assets': active_assets,
            'maintenance_assets': maintenance_assets,
            'retired_assets': retired_assets,
            'total_users': total_users,
        },
        'crm_stats': crm_stats,
        'recent_history': recent_history,
        'upcoming_maintenance': upcoming_maintenance,
        'assets_by_category': assets_by_category,
    }
    
    return render(request, 'dashboard.html', context)


@login_required
@require_POST
def generate_asset_tag(request):
    """Generate asset tag based on model's category"""
    try:
        model_id = request.POST.get('model_id')
        if not model_id:
            return JsonResponse({'success': False, 'error': 'Model ID is required'})
        
        model = get_object_or_404(AssetModel, id=model_id)
        category_name = model.category.name
        
        # Import here to avoid circular imports
        from .models import generate_asset_tag_for_category
        
        # Generate a unique asset tag
        asset_tag = generate_asset_tag_for_category(category_name)
        
        # Double-check uniqueness
        while Asset.objects.filter(asset_tag=asset_tag).exists():
            asset_tag = generate_asset_tag_for_category(category_name)
        
        return JsonResponse({'success': True, 'asset_tag': asset_tag})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
