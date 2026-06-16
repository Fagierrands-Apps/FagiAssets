# 🔗 Asset Manager ↔️ CRM Integration

This document describes the seamless integration between your Asset Management system and FagiCRM system, enabling bidirectional synchronization of customer data, employee information, and asset ownership tracking.

## 🌟 Features

### ✅ What's Integrated

- **Customer Synchronization**: CRM customers automatically sync to Asset Manager
- **Employee Data Sync**: Employee information shared between both systems
- **Asset Ownership Tracking**: Link assets to CRM customers with assignment types
- **Bidirectional Updates**: Changes in either system sync to the other
- **Real-time Notifications**: Automatic sync on data changes
- **Web Dashboard**: Manage integration through user-friendly interface
- **REST API**: Programmatic access for custom integrations

### 🔄 Sync Types

1. **Customers → Asset Manager**: CRM customers become available for asset assignment
2. **Assets → CRM**: Asset assignments create notes/records in CRM
3. **Employees**: Employee data synchronized between systems
4. **Assignments**: Track which customers own/lease which assets

## 🚀 Quick Start

### 1. Run Setup Script

```bash
python setup_crm_integration.py
```

This will:
- Configure integration settings
- Test connection between systems
- Perform initial data synchronization
- Show you next steps

### 2. Start Both Systems

**Asset Manager** (Terminal 1):
```bash
cd assetmanagement
python manage.py runserver
```

**CRM System** (Terminal 2):
```bash
cd fagicrm
python manage.py runserver 8001
```

### 3. Access Integration Dashboard

Visit: http://localhost:8000/crm/

## 📊 Integration Dashboard

The web interface provides:

### Dashboard Overview
- **Statistics**: Total customers, assignments, sync status
- **Quick Actions**: Manual sync buttons
- **Recent Activity**: Latest sync logs
- **System Status**: Connection and configuration status

### Customer Management
- **View Synced Customers**: Browse customers from CRM
- **Asset Assignments**: See which assets are assigned to each customer
- **Assignment Types**: Owned, Leased, Service Contract, Temporary

### Sync Monitoring
- **Sync Logs**: Detailed history of all synchronization activities
- **Error Tracking**: Monitor and troubleshoot sync issues
- **Performance Metrics**: Sync duration and success rates

## 🔧 Configuration

### Integration Settings

Access via: http://localhost:8000/crm/settings/

- **CRM URL**: Base URL of your CRM system
- **API Key**: Authentication for CRM access
- **Auto Sync**: Enable/disable automatic synchronization
- **Sync Interval**: How often to sync (minutes)
- **Sync Directions**: Control what syncs where

### Sync Configuration

```python
# Default settings
SYNC_CUSTOMERS_TO_ASSETS = True    # CRM → Asset Manager
SYNC_ASSETS_TO_CRM = True          # Asset Manager → CRM
SYNC_EMPLOYEES = True              # Bidirectional employee sync
AUTO_SYNC_ENABLED = True           # Automatic sync on changes
SYNC_INTERVAL_MINUTES = 30         # Background sync frequency
```

## 🔌 API Endpoints

### Asset Manager API

Base URL: `http://localhost:8000/crm/api/`

- `GET /customers/` - List synced customers
- `GET /customers/{id}/` - Customer details
- `GET /customers/{id}/assets/` - Customer's assets
- `POST /customers/{id}/assign_asset/` - Assign asset to customer
- `GET /assignments/` - List asset assignments
- `POST /assignments/` - Create new assignment
- `GET /sync-logs/` - View sync history
- `POST /integration/sync_customers/` - Manual customer sync
- `POST /integration/full_sync/` - Full synchronization

### CRM API

Base URL: `http://localhost:8001/api/`

- `GET /health/` - Health check
- `GET /customers/` - List customers
- `GET /customers/{id}/` - Customer details
- `GET /employees/` - List employees
- `POST /asset-assignments/` - Receive asset assignments

## 💼 Usage Examples

### 1. Assign Asset to Customer

```python
# Via API
import requests

response = requests.post('http://localhost:8000/crm/api/customers/1/assign_asset/', {
    'asset_id': 5,
    'assignment_type': 'leased',
    'monthly_fee': 150.00,
    'contract_number': 'LEASE-2024-001'
})
```

### 2. Manual Sync

```python
# Via management command
python manage.py sync_crm --type customers
python manage.py sync_crm --type full
```

### 3. Monitor Sync Status

```python
from crm_integration.models import SyncLog

# Get recent sync logs
recent_syncs = SyncLog.objects.all()[:10]
for log in recent_syncs:
    print(f"{log.sync_type}: {log.status} - {log.records_success}/{log.records_processed}")
```

## 🏗️ Architecture

### Data Flow

```
┌─────────────────┐    API Calls    ┌─────────────────┐
│   Asset Manager │ ←──────────────→ │    FagiCRM      │
│                 │                 │                 │
│ • Assets        │                 │ • Customers     │
│ • Users         │                 │ • Employees     │
│ • Assignments   │                 │ • Notes         │
└─────────────────┘                 └─────────────────┘
         │                                   │
         └─────────── Integration Layer ─────┘
                           │
                    ┌─────────────┐
                    │ Sync Engine │
                    │ • Signals   │
                    │ • Scheduler │
                    │ • API Client│
                    └─────────────┘
```

### Models

**CRMCustomer**: Mirror of CRM customer data in Asset Manager
**AssetCustomerAssignment**: Links assets to customers
**SyncLog**: Tracks all synchronization activities
**IntegrationSettings**: Configuration for the integration

## 🔍 Troubleshooting

### Common Issues

1. **Connection Failed**
   - Check if CRM server is running on correct port
   - Verify CRM URL in settings
   - Check firewall/network settings

2. **Sync Errors**
   - Check sync logs for detailed error messages
   - Verify API key configuration
   - Ensure both systems have compatible data

3. **Missing Data**
   - Run manual sync: `python manage.py sync_crm --type full`
   - Check sync status in dashboard
   - Verify data exists in source system

### Debug Mode

Enable detailed logging:

```python
# In settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'crm_integration': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## 🔒 Security

### API Authentication

- Development: Simple API key
- Production: Use proper authentication (JWT, OAuth2)
- HTTPS: Always use HTTPS in production
- Rate Limiting: Implement rate limiting for API endpoints

### Data Privacy

- Customer data is synchronized securely
- No sensitive data stored in logs
- Configurable field mapping
- Audit trail for all changes

## 🚀 Advanced Usage

### Custom Field Mapping

```python
# Configure custom field mappings
settings = IntegrationSettings.get_settings()
settings.customer_assignment_field_mapping = {
    'custom_field_1': 'asset_tag',
    'custom_field_2': 'assignment_type'
}
settings.save()
```

### Webhook Integration

Set up webhooks for real-time sync:

```python
# In your CRM system
@webhook_handler
def asset_assignment_webhook(request):
    # Trigger sync when assignments change
    service = CRMIntegrationService()
    service.sync_asset_assignments_to_crm()
```

### Scheduled Sync

```python
# Using Django-Crontab or Celery
from django_crontab import crontab

@crontab(minute='*/30')  # Every 30 minutes
def scheduled_sync():
    service = CRMIntegrationService()
    service.full_sync()
```

## 📈 Monitoring & Analytics

### Sync Metrics

- Success/failure rates
- Sync duration trends
- Data volume statistics
- Error frequency analysis

### Performance Optimization

- Batch processing for large datasets
- Incremental sync (only changed records)
- Connection pooling
- Caching frequently accessed data

## 🤝 Support

### Getting Help

1. Check the integration dashboard for status
2. Review sync logs for error details
3. Test connection using health check endpoint
4. Run manual sync to isolate issues

### Maintenance

- Regular backup of integration settings
- Monitor sync log size and cleanup old entries
- Update API keys periodically
- Test integration after system updates

---

## 🎯 Next Steps

1. **Test the Integration**: Create test customers and assets
2. **Configure Notifications**: Set up email alerts for sync errors
3. **Customize Field Mapping**: Map additional fields as needed
4. **Set Up Monitoring**: Implement health checks and alerts
5. **Scale for Production**: Add proper authentication and rate limiting

The integration is now ready to seamlessly connect your Asset Management and CRM systems! 🚀