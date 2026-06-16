# QR Code Network Configuration Fix

## Problem
QR codes were being generated with `127.0.0.1:8000` (localhost) URLs, making them inaccessible from mobile devices and other network clients.

## Solution
Modified the QR code generation to use a configurable network IP address instead of the request's host.

## Changes Made

### 1. Django Settings (assetmanager/settings.py)
Added a new setting for the network base URL:

```python
# Network QR Code Settings
# Base URL for QR codes (should be accessible from mobile devices)
QR_CODE_BASE_URL = 'https://fagiassets.vercel.app'
```

### 2. QR Code Utility Function (assets/utils.py)
Updated `generate_asset_label_data()` to use the network URL:

```python
def generate_asset_label_data(asset, request):
    """
    Generate all data needed for asset labels
    """
    from django.conf import settings
    
    # Build network URL for the asset (accessible from mobile devices)
    if hasattr(settings, 'QR_CODE_BASE_URL') and settings.QR_CODE_BASE_URL:
        asset_url = f"{settings.QR_CODE_BASE_URL}/assets/{asset.id}/"
    else:
        # Fallback to request-based URL
        asset_url = request.build_absolute_uri(f'/assets/{asset.id}/')
    
    # Generate QR code image
    qr_image = generate_qr_code_image(asset_url)
    # ...
```

### 3. QR Code Image Views (assets/views.py)
Updated both `asset_qr_code_image()` and `download_asset_qr_code()` functions:

```python
# Build network URL for the asset (accessible from mobile devices)
from django.conf import settings
if hasattr(settings, 'QR_CODE_BASE_URL') and settings.QR_CODE_BASE_URL:
    asset_url = f"{settings.QR_CODE_BASE_URL}/assets/{asset.id}/"
else:
    # Fallback to request-based URL
    asset_url = request.build_absolute_uri(f'/assets/{asset.id}/')
```

## Configuration

### Change Network IP
To use a different network IP address, update the `QR_CODE_BASE_URL` setting in `assetmanager/settings.py`:

```python
# For a different network IP
QR_CODE_BASE_URL = 'http://192.168.1.100:8000'

# For domain name
QR_CODE_BASE_URL = 'http://asset-server.company.com:8000'
```

### Server Startup
Make sure to start the Django server with the network IP:

```bash
# Start server on network interface
python manage.py runserver 10.246.23.10:8000

# Or start on all interfaces
python manage.py runserver 0.0.0.0:8000
```

## Testing

### Run Configuration Test
```bash
python test_qr_config.py
```

### Run Full System Test
```bash
python test_network_qr.py
```

## How It Works

1. **Label Generation**: When generating asset labels, the system now uses the configured network URL instead of the request's host.

2. **QR Code Content**: QR codes now contain URLs like `http://10.246.23.10:8000/assets/123/` instead of `http://127.0.0.1:8000/assets/123/`.

3. **Mobile Access**: Mobile devices can now scan QR codes and access the asset information directly from the network.

4. **Fallback**: If the network URL is not configured, the system falls back to the original request-based URL generation.

## Benefits

- ✅ QR codes work from mobile devices
- ✅ Network-accessible asset information
- ✅ Professional label printing with scannable QR codes
- ✅ Maintains backward compatibility with fallback
- ✅ Configurable for different network setups

## Verification

After making these changes, QR codes generated for assets will:

1. **Print with network URLs**: Asset labels will have QR codes pointing to the network server
2. **Scan from mobile**: Mobile devices can scan and access asset information
3. **Work across network**: Any device on the network can access the QR code destination

Example QR code URL before: `http://127.0.0.1:8000/assets/123/`
Example QR code URL after: `https://fagiassets.vercel.app/assets/123/`

## Troubleshooting

### QR Codes Still Show Localhost
1. Check that `QR_CODE_BASE_URL` is set in settings.py
2. Restart the Django server
3. Clear browser cache
4. Run `python test_qr_config.py` to verify configuration

### Network Access Issues
1. Ensure Django server is running on the network IP: `python manage.py runserver 10.246.23.10:8000`
2. Check firewall settings allow access to port 8000
3. Verify the IP address is correct for your network
4. Test access from mobile device: `http://10.246.23.10:8000/assets/`

### Mobile Device Can't Access
1. Ensure mobile device is on the same network
2. Try accessing the URL directly in mobile browser first
3. Check that the IP address is reachable from mobile device
4. Verify there are no network restrictions blocking access