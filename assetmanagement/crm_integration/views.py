from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import CRMCustomer, AssetCustomerAssignment, SyncLog, IntegrationSettings
from .services import CRMIntegrationService
from assets.models import Asset
import json


@login_required
def integration_dashboard(request):
    """Main CRM integration dashboard"""
    # Get recent sync logs
    recent_logs = SyncLog.objects.all()[:10]
    
    # Get summary statistics
    total_customers = CRMCustomer.objects.count()
    total_assignments = AssetCustomerAssignment.objects.filter(is_active=True).count()
    pending_syncs = CRMCustomer.objects.filter(sync_status='pending').count()
    error_syncs = CRMCustomer.objects.filter(sync_status='error').count()
    
    # Get settings
    settings = IntegrationSettings.get_settings()
    
    context = {
        'recent_logs': recent_logs,
        'stats': {
            'total_customers': total_customers,
            'total_assignments': total_assignments,
            'pending_syncs': pending_syncs,
            'error_syncs': error_syncs,
        },
        'settings': settings,
    }
    
    return render(request, 'crm_integration/dashboard.html', context)


@login_required
def customer_list(request):
    """List CRM customers"""
    customers = CRMCustomer.objects.all().select_related('assigned_employee')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        customers = customers.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(company_name__icontains=search) |
            Q(email__icontains=search)
        )
    
    # Filter by sync status
    sync_status = request.GET.get('sync_status')
    if sync_status:
        customers = customers.filter(sync_status=sync_status)
    
    # Pagination
    paginator = Paginator(customers, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'sync_status': sync_status,
    }
    
    return render(request, 'crm_integration/customer_list.html', context)


@login_required
def customer_detail(request, customer_id):
    """Customer detail view with asset assignments"""
    customer = get_object_or_404(CRMCustomer, id=customer_id)
    
    # Get customer's asset assignments
    assignments = AssetCustomerAssignment.objects.filter(
        customer=customer
    ).select_related('asset', 'assigned_by').order_by('-assigned_date')
    
    # Get available assets for assignment
    available_assets = Asset.objects.filter(status='active').exclude(
        id__in=assignments.filter(is_active=True).values_list('asset_id', flat=True)
    )
    
    context = {
        'customer': customer,
        'assignments': assignments,
        'available_assets': available_assets,
    }
    
    return render(request, 'crm_integration/customer_detail.html', context)


@login_required
def assignment_list(request):
    """List asset-customer assignments"""
    assignments = AssetCustomerAssignment.objects.all().select_related(
        'asset', 'customer', 'assigned_by'
    )
    
    # Filter by assignment type
    assignment_type = request.GET.get('assignment_type')
    if assignment_type:
        assignments = assignments.filter(assignment_type=assignment_type)
    
    # Filter by active status
    is_active = request.GET.get('is_active')
    if is_active is not None:
        assignments = assignments.filter(is_active=is_active.lower() == 'true')
    
    # Pagination
    paginator = Paginator(assignments, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'assignment_type': assignment_type,
        'is_active': is_active,
    }
    
    return render(request, 'crm_integration/assignment_list.html', context)


@login_required
def sync_logs(request):
    """View sync logs"""
    logs = SyncLog.objects.all().select_related('initiated_by')
    
    # Filter by sync type
    sync_type = request.GET.get('sync_type')
    if sync_type:
        logs = logs.filter(sync_type=sync_type)
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        logs = logs.filter(status=status)
    
    # Pagination
    paginator = Paginator(logs, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'sync_type': sync_type,
        'status': status,
    }
    
    return render(request, 'crm_integration/sync_logs.html', context)


@login_required
def sync_action(request):
    """Handle sync actions via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    action = request.POST.get('action')
    service = CRMIntegrationService()
    
    try:
        if action == 'test_connection':
            success, message = service.test_connection()
            return JsonResponse({
                'success': success,
                'message': message
            })
        
        elif action == 'sync_customers':
            sync_log = service.sync_customers_from_crm(request.user)
            return JsonResponse({
                'success': sync_log.status in ['success', 'partial'],
                'message': f"Synced {sync_log.records_success}/{sync_log.records_processed} customers",
                'sync_id': str(sync_log.sync_id)
            })
        
        elif action == 'sync_assignments':
            sync_log = service.sync_asset_assignments_to_crm(request.user)
            return JsonResponse({
                'success': sync_log.status in ['success', 'partial'],
                'message': f"Synced {sync_log.records_success}/{sync_log.records_processed} assignments",
                'sync_id': str(sync_log.sync_id)
            })
        
        elif action == 'sync_employees':
            sync_log = service.sync_employee_data(request.user)
            return JsonResponse({
                'success': sync_log.status in ['success', 'partial'],
                'message': f"Synced {sync_log.records_success}/{sync_log.records_processed} employees",
                'sync_id': str(sync_log.sync_id)
            })
        
        elif action == 'full_sync':
            results = service.full_sync(request.user)
            total_success = sum(log.records_success for log in results.values())
            total_processed = sum(log.records_processed for log in results.values())
            
            return JsonResponse({
                'success': True,
                'message': f"Full sync completed: {total_success}/{total_processed} records",
                'results': {k: str(v.sync_id) for k, v in results.items()}
            })
        
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def create_assignment(request):
    """Create a new asset-customer assignment"""
    if request.method == 'POST':
        try:
            asset_id = request.POST.get('asset_id')
            customer_id = request.POST.get('customer_id')
            assignment_type = request.POST.get('assignment_type', 'owned')
            
            asset = get_object_or_404(Asset, id=asset_id)
            customer = get_object_or_404(CRMCustomer, id=customer_id)
            
            # Check for existing active assignment
            existing = AssetCustomerAssignment.objects.filter(
                asset=asset,
                customer=customer,
                is_active=True
            ).exists()
            
            if existing:
                messages.error(request, 'An active assignment already exists between this asset and customer.')
            else:
                service = CRMIntegrationService()
                assignment = service.create_customer_assignment(
                    asset=asset,
                    customer=customer,
                    assignment_type=assignment_type,
                    user=request.user,
                    contract_number=request.POST.get('contract_number', ''),
                    monthly_fee=request.POST.get('monthly_fee') or None,
                    total_value=request.POST.get('total_value') or None,
                    notes=request.POST.get('notes', ''),
                )
                
                messages.success(request, f'Successfully assigned {asset.asset_tag} to {customer.full_name}')
                return redirect('crm_integration:customer_detail', customer_id=customer.id)
        
        except Exception as e:
            messages.error(request, f'Error creating assignment: {str(e)}')
    
    return redirect('crm_integration:customer_list')


@login_required
def settings_view(request):
    """Integration settings view"""
    settings = IntegrationSettings.get_settings()
    
    if request.method == 'POST':
        try:
            # Update settings
            settings.crm_base_url = request.POST.get('crm_base_url', settings.crm_base_url)
            settings.auto_sync_enabled = request.POST.get('auto_sync_enabled') == 'on'
            settings.sync_interval_minutes = int(request.POST.get('sync_interval_minutes', 30))
            settings.sync_customers_to_assets = request.POST.get('sync_customers_to_assets') == 'on'
            settings.sync_assets_to_crm = request.POST.get('sync_assets_to_crm') == 'on'
            settings.sync_employees = request.POST.get('sync_employees') == 'on'
            settings.notify_on_sync_error = request.POST.get('notify_on_sync_error') == 'on'
            settings.notification_email = request.POST.get('notification_email', '')
            
            # Update API key if provided
            api_key = request.POST.get('crm_api_key')
            if api_key:
                settings.crm_api_key = api_key
            
            settings.save()
            messages.success(request, 'Settings updated successfully')
            
        except Exception as e:
            messages.error(request, f'Error updating settings: {str(e)}')
    
    context = {
        'settings': settings,
    }
    
    return render(request, 'crm_integration/settings.html', context)