from rest_framework import serializers
from django.contrib.auth.models import User
from .models import CRMCustomer, AssetCustomerAssignment, SyncLog, IntegrationSettings
from assets.models import Asset


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'full_name']


class CRMCustomerSerializer(serializers.ModelSerializer):
    """Serializer for CRM Customer"""
    assigned_employee = UserSerializer(read_only=True)
    assigned_employee_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    full_name = serializers.CharField(read_only=True)
    full_address = serializers.CharField(read_only=True)
    
    class Meta:
        model = CRMCustomer
        fields = [
            'id', 'crm_customer_id', 'first_name', 'last_name', 'company_name',
            'email', 'phone', 'address_line1', 'address_line2', 'city', 'state',
            'postal_code', 'country', 'status', 'customer_type', 'assigned_employee',
            'assigned_employee_id', 'full_name', 'full_address', 'last_synced',
            'sync_status', 'sync_error', 'created_at', 'updated_at'
        ]
        read_only_fields = ['crm_customer_id', 'last_synced', 'created_at', 'updated_at']


class AssetSerializer(serializers.ModelSerializer):
    """Simple Asset serializer for assignments"""
    model_name = serializers.CharField(source='model.name', read_only=True)
    manufacturer = serializers.CharField(source='model.manufacturer.name', read_only=True)
    
    class Meta:
        model = Asset
        fields = ['id', 'asset_tag', 'name', 'model_name', 'manufacturer', 'serial_number', 'status']


class AssetCustomerAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for Asset-Customer assignments"""
    asset = AssetSerializer(read_only=True)
    asset_id = serializers.IntegerField(write_only=True)
    customer = CRMCustomerSerializer(read_only=True)
    customer_id = serializers.IntegerField(write_only=True)
    assigned_by = UserSerializer(read_only=True)
    
    class Meta:
        model = AssetCustomerAssignment
        fields = [
            'id', 'asset', 'asset_id', 'customer', 'customer_id', 'assignment_type',
            'is_active', 'assigned_date', 'assigned_by', 'contract_number',
            'start_date', 'end_date', 'monthly_fee', 'total_value', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['assigned_date', 'created_at', 'updated_at']
    
    def validate_asset_id(self, value):
        """Validate that the asset exists"""
        try:
            Asset.objects.get(id=value)
            return value
        except Asset.DoesNotExist:
            raise serializers.ValidationError("Asset not found")
    
    def validate_customer_id(self, value):
        """Validate that the customer exists"""
        try:
            CRMCustomer.objects.get(id=value)
            return value
        except CRMCustomer.DoesNotExist:
            raise serializers.ValidationError("Customer not found")
    
    def validate(self, data):
        """Validate assignment data"""
        asset_id = data.get('asset_id')
        customer_id = data.get('customer_id')
        
        if asset_id and customer_id:
            # Check if there's already an active assignment
            existing = AssetCustomerAssignment.objects.filter(
                asset_id=asset_id,
                customer_id=customer_id,
                is_active=True
            )
            
            # Exclude current instance if updating
            if self.instance:
                existing = existing.exclude(id=self.instance.id)
            
            if existing.exists():
                raise serializers.ValidationError(
                    "An active assignment already exists between this asset and customer"
                )
        
        return data


class SyncLogSerializer(serializers.ModelSerializer):
    """Serializer for Sync logs"""
    initiated_by = UserSerializer(read_only=True)
    duration_display = serializers.SerializerMethodField()
    
    class Meta:
        model = SyncLog
        fields = [
            'id', 'sync_type', 'sync_action', 'status', 'records_processed',
            'records_success', 'records_error', 'error_message', 'error_details',
            'initiated_by', 'sync_id', 'started_at', 'completed_at',
            'duration_seconds', 'duration_display'
        ]
    
    def get_duration_display(self, obj):
        """Get human-readable duration"""
        if obj.duration_seconds is None:
            return None
        
        seconds = int(obj.duration_seconds)
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds}s"
        else:
            hours = seconds // 3600
            remaining_minutes = (seconds % 3600) // 60
            return f"{hours}h {remaining_minutes}m"


class IntegrationSettingsSerializer(serializers.ModelSerializer):
    """Serializer for Integration settings"""
    
    class Meta:
        model = IntegrationSettings
        fields = [
            'id', 'crm_base_url', 'crm_api_key', 'auto_sync_enabled',
            'sync_interval_minutes', 'sync_customers_to_assets', 'sync_assets_to_crm',
            'sync_employees', 'customer_assignment_field_mapping', 'notify_on_sync_error',
            'notification_email', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'crm_api_key': {'write_only': True}  # Don't expose API key in responses
        }