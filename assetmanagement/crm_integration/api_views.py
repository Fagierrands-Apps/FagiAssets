from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import CRMCustomer, AssetCustomerAssignment, SyncLog, IntegrationSettings
from .serializers import (
    CRMCustomerSerializer, AssetCustomerAssignmentSerializer, 
    SyncLogSerializer, IntegrationSettingsSerializer
)
from .services import CRMIntegrationService
from assets.models import Asset
import logging

logger = logging.getLogger(__name__)


class CRMCustomerViewSet(viewsets.ModelViewSet):
    """ViewSet for CRM customers"""
    queryset = CRMCustomer.objects.all()
    serializer_class = CRMCustomerSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by search query
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(company_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        # Filter by assigned employee
        assigned_employee = self.request.query_params.get('assigned_employee')
        if assigned_employee:
            queryset = queryset.filter(assigned_employee_id=assigned_employee)
        
        # Filter by sync status
        sync_status = self.request.query_params.get('sync_status')
        if sync_status:
            queryset = queryset.filter(sync_status=sync_status)
        
        return queryset.select_related('assigned_employee')
    
    @action(detail=True, methods=['get'])
    def assets(self, request, pk=None):
        """Get all assets assigned to this customer"""
        customer = self.get_object()
        service = CRMIntegrationService()
        assets = service.get_customer_assets(customer)
        
        # Simple asset data
        asset_data = [{
            'id': asset.id,
            'asset_tag': asset.asset_tag,
            'name': asset.name,
            'model': str(asset.model),
            'status': asset.status,
            'serial_number': asset.serial_number,
        } for asset in assets]
        
        return Response(asset_data)
    
    @action(detail=True, methods=['post'])
    def assign_asset(self, request, pk=None):
        """Assign an asset to this customer"""
        customer = self.get_object()
        asset_id = request.data.get('asset_id')
        assignment_type = request.data.get('assignment_type', 'owned')
        
        if not asset_id:
            return Response(
                {'error': 'asset_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            asset = Asset.objects.get(id=asset_id)
            service = CRMIntegrationService()
            
            assignment = service.create_customer_assignment(
                asset=asset,
                customer=customer,
                assignment_type=assignment_type,
                user=request.user,
                **{k: v for k, v in request.data.items() 
                   if k not in ['asset_id', 'assignment_type']}
            )
            
            serializer = AssetCustomerAssignmentSerializer(assignment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Asset.DoesNotExist:
            return Response(
                {'error': 'Asset not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error assigning asset to customer: {e}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AssetCustomerAssignmentViewSet(viewsets.ModelViewSet):
    """ViewSet for asset-customer assignments"""
    queryset = AssetCustomerAssignment.objects.all()
    serializer_class = AssetCustomerAssignmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by asset
        asset_id = self.request.query_params.get('asset')
        if asset_id:
            queryset = queryset.filter(asset_id=asset_id)
        
        # Filter by customer
        customer_id = self.request.query_params.get('customer')
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        
        # Filter by assignment type
        assignment_type = self.request.query_params.get('assignment_type')
        if assignment_type:
            queryset = queryset.filter(assignment_type=assignment_type)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.select_related('asset', 'customer', 'assigned_by')
    
    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)


class SyncLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for sync logs (read-only)"""
    queryset = SyncLog.objects.all()
    serializer_class = SyncLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by sync type
        sync_type = self.request.query_params.get('sync_type')
        if sync_type:
            queryset = queryset.filter(sync_type=sync_type)
        
        # Filter by status
        sync_status = self.request.query_params.get('status')
        if sync_status:
            queryset = queryset.filter(status=sync_status)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(started_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(started_at__lte=end_date)
        
        return queryset.select_related('initiated_by')


class IntegrationViewSet(viewsets.ViewSet):
    """ViewSet for integration operations"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def settings(self, request):
        """Get integration settings"""
        settings = IntegrationSettings.get_settings()
        serializer = IntegrationSettingsSerializer(settings)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def update_settings(self, request):
        """Update integration settings"""
        settings = IntegrationSettings.get_settings()
        serializer = IntegrationSettingsSerializer(settings, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def test_connection(self, request):
        """Test connection to CRM system"""
        service = CRMIntegrationService()
        success, message = service.test_connection()
        
        return Response({
            'success': success,
            'message': message
        })
    
    @action(detail=False, methods=['post'])
    def sync_customers(self, request):
        """Sync customers from CRM"""
        service = CRMIntegrationService()
        sync_log = service.sync_customers_from_crm(request.user)
        
        serializer = SyncLogSerializer(sync_log)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def sync_assignments(self, request):
        """Sync asset assignments to CRM"""
        service = CRMIntegrationService()
        sync_log = service.sync_asset_assignments_to_crm(request.user)
        
        serializer = SyncLogSerializer(sync_log)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def sync_employees(self, request):
        """Sync employee data"""
        service = CRMIntegrationService()
        sync_log = service.sync_employee_data(request.user)
        
        serializer = SyncLogSerializer(sync_log)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def full_sync(self, request):
        """Perform full bidirectional sync"""
        service = CRMIntegrationService()
        results = service.full_sync(request.user)
        
        # Serialize all sync logs
        serialized_results = {}
        for key, sync_log in results.items():
            serialized_results[key] = SyncLogSerializer(sync_log).data
        
        return Response(serialized_results)
    
    @action(detail=False, methods=['get'])
    def sync_status(self, request):
        """Get recent sync status"""
        recent_logs = SyncLog.objects.all()[:10]
        serializer = SyncLogSerializer(recent_logs, many=True)
        
        # Summary statistics
        total_logs = SyncLog.objects.count()
        success_logs = SyncLog.objects.filter(status='success').count()
        error_logs = SyncLog.objects.filter(status='error').count()
        
        return Response({
            'recent_logs': serializer.data,
            'summary': {
                'total_syncs': total_logs,
                'successful_syncs': success_logs,
                'failed_syncs': error_logs,
                'success_rate': (success_logs / total_logs * 100) if total_logs > 0 else 0
            }
        })