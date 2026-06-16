from rest_framework import serializers
from .models import (
    Asset, AssetModel, AssetCategory, Manufacturer, 
    Location, Department, AssetHistory, MaintenanceRecord,
    NetworkInterface, SoftwareInstallation
)
from django.contrib.auth.models import User


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = ['id', 'name', 'website', 'support_email', 'support_phone']


class AssetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetCategory
        fields = ['id', 'name', 'description', 'parent']


class AssetModelSerializer(serializers.ModelSerializer):
    manufacturer = ManufacturerSerializer(read_only=True)
    category = AssetCategorySerializer(read_only=True)
    
    class Meta:
        model = AssetModel
        fields = ['id', 'name', 'manufacturer', 'category', 'model_number', 'description']


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'address', 'description']


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'manager']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class AssetSerializer(serializers.ModelSerializer):
    model = AssetModelSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    
    class Meta:
        model = Asset
        fields = [
            'id', 'asset_tag', 'name', 'model', 'serial_number', 'status',
            'assigned_to', 'department', 'location', 'purchase_date', 
            'purchase_cost', 'warranty_expires', 'ip_address', 'mac_address',
            'hostname', 'device_name', 'processor', 'installed_ram',
            'device_id', 'product_id', 'system_type', 'notes',
            'created_at', 'updated_at', 'last_seen'
        ]


class AssetCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = [
            'asset_tag', 'name', 'model', 'serial_number', 'status',
            'assigned_to', 'department', 'location', 'purchase_date', 
            'purchase_cost', 'warranty_expires', 'ip_address', 'mac_address',
            'hostname', 'device_name', 'processor', 'installed_ram',
            'device_id', 'product_id', 'system_type', 'notes'
        ]


class AssetHistorySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = AssetHistory
        fields = [
            'id', 'action', 'description', 'user', 'timestamp',
            'previous_values', 'new_values'
        ]


class MaintenanceRecordSerializer(serializers.ModelSerializer):
    asset = AssetSerializer(read_only=True)
    performed_by = UserSerializer(read_only=True)
    
    class Meta:
        model = MaintenanceRecord
        fields = [
            'id', 'asset', 'maintenance_type', 'status', 'title',
            'description', 'scheduled_date', 'completed_date',
            'performed_by', 'cost', 'notes', 'created_at', 'updated_at'
        ]


class NetworkInterfaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkInterface
        fields = [
            'id', 'interface_name', 'mac_address', 'ip_address',
            'subnet_mask', 'gateway', 'dns_servers', 'is_primary',
            'is_active', 'speed'
        ]


class SoftwareInstallationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoftwareInstallation
        fields = [
            'id', 'name', 'version', 'publisher', 'install_date',
            'license_key', 'is_licensed'
        ]


class AssetDetailSerializer(AssetSerializer):
    """Detailed asset serializer with related data"""
    network_interfaces = NetworkInterfaceSerializer(many=True, read_only=True)
    software_installations = SoftwareInstallationSerializer(many=True, read_only=True)
    maintenance_records = MaintenanceRecordSerializer(many=True, read_only=True)
    history = AssetHistorySerializer(many=True, read_only=True)
    
    class Meta(AssetSerializer.Meta):
        fields = AssetSerializer.Meta.fields + [
            'network_interfaces', 'software_installations', 
            'maintenance_records', 'history'
        ]


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    total_assets = serializers.IntegerField()
    active_assets = serializers.IntegerField()
    inactive_assets = serializers.IntegerField()
    maintenance_assets = serializers.IntegerField()
    retired_assets = serializers.IntegerField()
    total_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    departments_count = serializers.IntegerField()
    locations_count = serializers.IntegerField()
    users_count = serializers.IntegerField()


class AssetDistributionSerializer(serializers.Serializer):
    """Serializer for asset distribution data"""
    status = serializers.CharField()
    count = serializers.IntegerField()
    percentage = serializers.FloatField()


class AssetTrendSerializer(serializers.Serializer):
    """Serializer for asset trend data"""
    labels = serializers.ListField(child=serializers.CharField())
    assets_added = serializers.ListField(child=serializers.IntegerField())
    maintenance_tasks = serializers.ListField(child=serializers.IntegerField())


class RecentActivitySerializer(serializers.Serializer):
    """Serializer for recent activity data"""
    action = serializers.CharField()
    description = serializers.CharField()
    timestamp = serializers.DateTimeField()
    user = serializers.CharField()
    asset_tag = serializers.CharField()