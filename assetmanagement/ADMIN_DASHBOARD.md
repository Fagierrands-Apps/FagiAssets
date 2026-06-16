# Custom Admin Dashboard

This custom admin dashboard provides a comprehensive interface for managing the Asset Management System without needing to use Django's default admin panel.

## Features

### User Management
- **User List**: View all users with search and filtering
- **User Creation**: Create new users with profiles
- **User Details**: View detailed user information and assigned assets
- **User Editing**: Edit user information and permissions
- **User Status**: Activate/deactivate users

### Asset Management
- **Asset List**: View all assets with advanced filtering
- **Asset Creation**: Add new assets with complete information
- **Asset Details**: View detailed asset information and history
- **Asset Editing**: Update asset information
- **Asset History**: Track all changes to assets

### Organization Management
- **Categories**: Manage asset categories and hierarchies
- **Manufacturers**: Manage asset manufacturers and support info
- **Asset Models**: Manage specific asset models
- **Locations**: Manage office locations and sites
- **Departments**: Manage organizational departments

### Discovery Management
- **Network Ranges**: Configure network discovery ranges
- **Discovery Dashboard**: Monitor discovery activities
- **Device Management**: Manage discovered devices

### System Administration
- **System Settings**: Configure system-wide settings
- **System Logs**: View user activities and system logs
- **Backup Management**: Create and manage system backups

## Access

### URL
The admin dashboard is accessible at: `/admin-dashboard/`

### Permissions
- Users must be logged in
- Users must have `is_staff` or `is_superuser` permissions
- Different sections may have additional permission requirements

### Navigation
- **Main Navigation**: Access from the user dropdown menu
- **Sidebar Navigation**: Organized by functional areas
- **Breadcrumbs**: Easy navigation within sections

## Key Components

### Templates
- `admin_dashboard/base.html`: Base template with navigation
- `admin_dashboard/dashboard.html`: Main dashboard with statistics
- Individual templates for each management section

### Views
- Class-based and function-based views
- Proper permission checking
- Search and filtering capabilities
- Pagination support

### Forms
- Django forms with Bootstrap styling
- Validation and error handling
- Select2 integration for dropdowns

### Features
- **Search**: Full-text search across relevant fields
- **Filtering**: Advanced filtering options
- **Pagination**: Efficient handling of large datasets
- **Export**: CSV export capabilities
- **Responsive**: Mobile-friendly design
- **Real-time**: Auto-refresh for logs and statistics

## Usage Examples

### Creating a New User
1. Navigate to Admin Dashboard → Users
2. Click "Add New User"
3. Fill in user information and profile details
4. Set appropriate permissions
5. Save the user

### Adding an Asset
1. Navigate to Admin Dashboard → Assets
2. Click "Add New Asset"
3. Select or create manufacturer and model
4. Fill in asset details
5. Assign to user/department if needed
6. Save the asset

### Managing Categories
1. Navigate to Admin Dashboard → Categories
2. Create parent categories first
3. Add subcategories as needed
4. Use categories when creating asset models

## Security Features

- **Permission Checks**: All views check user permissions
- **Activity Logging**: All actions are logged
- **Session Management**: Secure session handling
- **CSRF Protection**: All forms include CSRF tokens
- **Input Validation**: Comprehensive form validation

## Customization

The admin dashboard can be customized by:
- Modifying templates in `templates/admin_dashboard/`
- Adding new views in `admin_dashboard/views.py`
- Creating new forms in `admin_dashboard/forms.py`
- Extending the URL patterns in `admin_dashboard/urls.py`

## Troubleshooting

### Common Issues
1. **Permission Denied**: Ensure user has staff privileges
2. **Template Not Found**: Check template paths and names
3. **Form Errors**: Verify form validation and field requirements
4. **Search Issues**: Check database indexes and query performance

### Debug Mode
Enable Django debug mode for detailed error information during development.

## Future Enhancements

Planned features:
- Bulk operations for assets and users
- Advanced reporting and analytics
- Email notifications for important events
- API integration for external systems
- Mobile app support
- Advanced workflow management