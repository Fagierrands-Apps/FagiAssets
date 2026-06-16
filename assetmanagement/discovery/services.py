import nmap
import socket
import psutil
import json
from datetime import datetime, timedelta
from django.utils import timezone
from netaddr import IPNetwork, IPAddress
from .models import NetworkRange, DiscoveredDevice, ScanJob, ScanResult, AssetDiscoveryLog
from assets.models import Asset
import logging

logger = logging.getLogger(__name__)


class NetworkDiscoveryService:
    """Service for network discovery and asset scanning"""
    
    def __init__(self):
        self.nm = nmap.PortScanner()
    
    def scan_network_range(self, network_range, scan_type='discovery', scan_options=None):
        """Scan a network range for devices"""
        if scan_options is None:
            scan_options = {}
        
        # Create scan job
        scan_job = ScanJob.objects.create(
            name=f"Network scan of {network_range.network}",
            scan_type=scan_type,
            scan_options=scan_options,
            started_at=timezone.now()
        )
        scan_job.network_ranges.add(network_range)
        
        try:
            # Update scan job status
            scan_job.status = 'running'
            scan_job.save()
            
            # Perform the scan
            devices_found = self._perform_network_scan(network_range, scan_job, scan_options)
            
            # Update scan job with results
            scan_job.status = 'completed'
            scan_job.completed_at = timezone.now()
            scan_job.devices_found = len(devices_found)
            scan_job.save()
            
            # Update network range last scan time
            network_range.last_scan = timezone.now()
            network_range.save()
            
            return scan_job
            
        except Exception as e:
            scan_job.status = 'failed'
            scan_job.errors = [str(e)]
            scan_job.completed_at = timezone.now()
            scan_job.save()
            
            AssetDiscoveryLog.objects.create(
                level='error',
                message=f"Network scan failed: {str(e)}",
                scan_job=scan_job
            )
            
            raise e
    
    def _perform_network_scan(self, network_range, scan_job, scan_options):
        """Perform the actual network scan"""
        devices_found = []
        network = IPNetwork(network_range.network)
        
        # Determine scan arguments based on scan type
        nmap_args = self._get_nmap_args(scan_job.scan_type, scan_options)
        
        try:
            # Scan the network
            self.nm.scan(str(network), arguments=nmap_args)
            
            for host in self.nm.all_hosts():
                if self.nm[host].state() == 'up':
                    device_info = self._extract_device_info(host, scan_job.scan_type)
                    device = self._create_or_update_discovered_device(
                        host, device_info, network_range, scan_job
                    )
                    devices_found.append(device)
                    
        except Exception as e:
            AssetDiscoveryLog.objects.create(
                level='error',
                message=f"Nmap scan error: {str(e)}",
                scan_job=scan_job
            )
            raise e
        
        return devices_found
    
    def _get_nmap_args(self, scan_type, scan_options):
        """Get nmap arguments based on scan type"""
        base_args = "-sn"  # Ping scan by default
        
        if scan_type == 'port_scan':
            base_args = "-sS"  # SYN scan
        elif scan_type == 'service_scan':
            base_args = "-sS -sV"  # Service version detection
        elif scan_type == 'os_detection':
            base_args = "-sS -O"  # OS detection
        elif scan_type == 'full_scan':
            base_args = "-sS -sV -O -A"  # Aggressive scan
        
        # Add custom options
        if scan_options.get('ports'):
            base_args += f" -p {scan_options['ports']}"
        
        if scan_options.get('timing'):
            base_args += f" -T{scan_options['timing']}"
        else:
            base_args += " -T3"  # Normal timing
        
        return base_args
    
    def _extract_device_info(self, host, scan_type):
        """Extract device information from nmap scan results"""
        host_info = self.nm[host]
        
        device_info = {
            'ip_address': host,
            'hostname': '',
            'mac_address': '',
            'ports_open': [],
            'services': {},
            'os_info': {},
            'hardware_info': {},
        }
        
        # Get hostname
        if 'hostnames' in host_info and host_info['hostnames']:
            device_info['hostname'] = host_info['hostnames'][0]['name']
        
        # Get MAC address
        if 'addresses' in host_info and 'mac' in host_info['addresses']:
            device_info['mac_address'] = host_info['addresses']['mac']
        
        # Get open ports and services
        if 'tcp' in host_info:
            for port, port_info in host_info['tcp'].items():
                if port_info['state'] == 'open':
                    device_info['ports_open'].append(port)
                    device_info['services'][str(port)] = {
                        'name': port_info.get('name', ''),
                        'product': port_info.get('product', ''),
                        'version': port_info.get('version', ''),
                        'extrainfo': port_info.get('extrainfo', ''),
                    }
        
        # Get OS information
        if 'osmatch' in host_info:
            for os_match in host_info['osmatch']:
                device_info['os_info'] = {
                    'name': os_match.get('name', ''),
                    'accuracy': os_match.get('accuracy', 0),
                    'line': os_match.get('line', ''),
                }
                break  # Take the first (most accurate) match
        
        return device_info
    
    def _create_or_update_discovered_device(self, ip_address, device_info, network_range, scan_job):
        """Create or update a discovered device"""
        try:
            device, created = DiscoveredDevice.objects.get_or_create(
                ip_address=ip_address,
                network_range=network_range,
                defaults={
                    'hostname': device_info.get('hostname', ''),
                    'mac_address': device_info.get('mac_address', ''),
                    'ports_open': device_info.get('ports_open', []),
                    'services': device_info.get('services', {}),
                    'os_info': device_info.get('os_info', {}),
                    'hardware_info': device_info.get('hardware_info', {}),
                    'raw_data': device_info,
                }
            )
            
            if not created:
                # Update existing device
                device.hostname = device_info.get('hostname', device.hostname)
                device.mac_address = device_info.get('mac_address', device.mac_address)
                device.ports_open = device_info.get('ports_open', [])
                device.services = device_info.get('services', {})
                device.os_info = device_info.get('os_info', {})
                device.hardware_info = device_info.get('hardware_info', {})
                device.raw_data = device_info
                device.last_seen = timezone.now()
                device.scan_count += 1
                device.save()
                
                scan_job.updated_devices += 1
            else:
                scan_job.new_devices += 1
            
            scan_job.save()
            
            # Create scan result
            ScanResult.objects.create(
                scan_job=scan_job,
                discovered_device=device,
                ports_scanned=list(range(1, 1025)) if scan_job.scan_type != 'discovery' else [],
                ports_open=device_info.get('ports_open', []),
                services_detected=device_info.get('services', {}),
                os_fingerprint=device_info.get('os_info', {}),
                is_alive=True,
                scan_successful=True
            )
            
            # Try to match with existing assets
            self._try_match_asset(device)
            
            return device
            
        except Exception as e:
            AssetDiscoveryLog.objects.create(
                level='error',
                message=f"Error creating/updating device {ip_address}: {str(e)}",
                scan_job=scan_job
            )
            raise e
    
    def _try_match_asset(self, discovered_device):
        """Try to match discovered device with existing assets"""
        confidence_score = 0.0
        matched_asset = None
        
        # Try to match by IP address
        if discovered_device.ip_address:
            assets = Asset.objects.filter(ip_address=discovered_device.ip_address)
            if assets.exists():
                matched_asset = assets.first()
                confidence_score = 0.9
        
        # Try to match by MAC address
        if not matched_asset and discovered_device.mac_address:
            assets = Asset.objects.filter(mac_address=discovered_device.mac_address)
            if assets.exists():
                matched_asset = assets.first()
                confidence_score = 0.8
        
        # Try to match by hostname
        if not matched_asset and discovered_device.hostname:
            assets = Asset.objects.filter(hostname=discovered_device.hostname)
            if assets.exists():
                matched_asset = assets.first()
                confidence_score = 0.7
        
        # Update discovered device with match
        if matched_asset:
            discovered_device.matched_asset = matched_asset
            discovered_device.confidence_score = confidence_score
            discovered_device.status = 'matched'
            discovered_device.save()
            
            # Update asset's last seen time
            matched_asset.last_seen = timezone.now()
            matched_asset.save()
            
            AssetDiscoveryLog.objects.create(
                level='info',
                message=f"Matched device {discovered_device.ip_address} to asset {matched_asset.asset_tag}",
                discovered_device=discovered_device,
                details={'confidence_score': confidence_score}
            )
    
    def scan_all_active_ranges(self):
        """Scan all active network ranges"""
        active_ranges = NetworkRange.objects.filter(is_active=True)
        
        for network_range in active_ranges:
            # Check if it's time to scan this range
            if self._should_scan_range(network_range):
                try:
                    self.scan_network_range(network_range)
                except Exception as e:
                    logger.error(f"Failed to scan network range {network_range.network}: {str(e)}")
    
    def _should_scan_range(self, network_range):
        """Check if a network range should be scanned"""
        if not network_range.last_scan:
            return True
        
        time_since_last_scan = timezone.now() - network_range.last_scan
        return time_since_last_scan.total_seconds() >= network_range.scan_frequency


class AssetMatchingService:
    """Service for matching discovered devices with assets"""
    
    def match_discovered_devices(self):
        """Match all unmatched discovered devices with assets"""
        unmatched_devices = DiscoveredDevice.objects.filter(
            status='new',
            matched_asset__isnull=True
        )
        
        for device in unmatched_devices:
            self._match_device(device)
    
    def _match_device(self, discovered_device):
        """Match a single discovered device with assets"""
        discovery_service = NetworkDiscoveryService()
        discovery_service._try_match_asset(discovered_device)


def get_local_network_interfaces():
    """Get local network interfaces for automatic network range detection"""
    interfaces = []
    
    for interface_name, interface_addresses in psutil.net_if_addrs().items():
        for address in interface_addresses:
            if address.family == socket.AF_INET:  # IPv4
                interfaces.append({
                    'name': interface_name,
                    'ip': address.address,
                    'netmask': address.netmask,
                    'broadcast': address.broadcast,
                })
    
    return interfaces


def suggest_network_ranges():
    """Suggest network ranges based on local interfaces"""
    interfaces = get_local_network_interfaces()
    suggested_ranges = []
    
    for interface in interfaces:
        if interface['ip'] != '127.0.0.1':  # Skip loopback
            try:
                # Calculate network address
                ip = IPAddress(interface['ip'])
                netmask = IPAddress(interface['netmask'])
                network = IPNetwork(f"{interface['ip']}/{netmask}")
                network = network.cidr
                
                suggested_ranges.append({
                    'name': f"Network {interface['name']}",
                    'network': str(network),
                    'interface': interface['name'],
                })
            except:
                continue
    
    return suggested_rangesimport nmap
import socket
import psutil
import json
from datetime import datetime, timedelta
from django.utils import timezone
from netaddr import IPNetwork, IPAddress
from .models import NetworkRange, DiscoveredDevice, ScanJob, ScanResult, AssetDiscoveryLog
from assets.models import Asset
import logging

logger = logging.getLogger(__name__)


class NetworkDiscoveryService:
    """Service for network discovery and asset scanning"""
    
    def __init__(self):
        self.nm = nmap.PortScanner()
    
    def scan_network_range(self, network_range, scan_type='discovery', scan_options=None):
        """Scan a network range for devices"""
        if scan_options is None:
            scan_options = {}
        
        # Create scan job
        scan_job = ScanJob.objects.create(
            name=f"Network scan of {network_range.network}",
            scan_type=scan_type,
            scan_options=scan_options,
            started_at=timezone.now()
        )
        scan_job.network_ranges.add(network_range)
        
        try:
            # Update scan job status
            scan_job.status = 'running'
            scan_job.save()
            
            # Perform the scan
            devices_found = self._perform_network_scan(network_range, scan_job, scan_options)
            
            # Update scan job with results
            scan_job.status = 'completed'
            scan_job.completed_at = timezone.now()
            scan_job.devices_found = len(devices_found)
            scan_job.save()
            
            # Update network range last scan time
            network_range.last_scan = timezone.now()
            network_range.save()
            
            return scan_job
            
        except Exception as e:
            scan_job.status = 'failed'
            scan_job.errors = [str(e)]
            scan_job.completed_at = timezone.now()
            scan_job.save()
            
            AssetDiscoveryLog.objects.create(
                level='error',
                message=f"Network scan failed: {str(e)}",
                scan_job=scan_job
            )
            
            raise e
    
    def _perform_network_scan(self, network_range, scan_job, scan_options):
        """Perform the actual network scan"""
        devices_found = []
        network = IPNetwork(network_range.network)
        
        # Determine scan arguments based on scan type
        nmap_args = self._get_nmap_args(scan_job.scan_type, scan_options)
        
        try:
            # Scan the network
            self.nm.scan(str(network), arguments=nmap_args)
            
            for host in self.nm.all_hosts():
                if self.nm[host].state() == 'up':
                    device_info = self._extract_device_info(host, scan_job.scan_type)
                    device = self._create_or_update_discovered_device(
                        host, device_info, network_range, scan_job
                    )
                    devices_found.append(device)
                    
        except Exception as e:
            AssetDiscoveryLog.objects.create(
                level='error',
                message=f"Nmap scan error: {str(e)}",
                scan_job=scan_job
            )
            raise e
        
        return devices_found
    
    def _get_nmap_args(self, scan_type, scan_options):
        """Get nmap arguments based on scan type"""
        base_args = "-sn"  # Ping scan by default
        
        if scan_type == 'port_scan':
            base_args = "-sS"  # SYN scan
        elif scan_type == 'service_scan':
            base_args = "-sS -sV"  # Service version detection
        elif scan_type == 'os_detection':
            base_args = "-sS -O"  # OS detection
        elif scan_type == 'full_scan':
            base_args = "-sS -sV -O -A"  # Aggressive scan
        
        # Add custom options
        if scan_options.get('ports'):
            base_args += f" -p {scan_options['ports']}"
        
        if scan_options.get('timing'):
            base_args += f" -T{scan_options['timing']}"
        else:
            base_args += " -T3"  # Normal timing
        
        return base_args
    
    def _extract_device_info(self, host, scan_type):
        """Extract device information from nmap scan results"""
        host_info = self.nm[host]
        
        device_info = {
            'ip_address': host,
            'hostname': '',
            'mac_address': '',
            'ports_open': [],
            'services': {},
            'os_info': {},
            'hardware_info': {},
        }
        
        # Get hostname
        if 'hostnames' in host_info and host_info['hostnames']:
            device_info['hostname'] = host_info['hostnames'][0]['name']
        
        # Get MAC address
        if 'addresses' in host_info and 'mac' in host_info['addresses']:
            device_info['mac_address'] = host_info['addresses']['mac']
        
        # Get open ports and services
        if 'tcp' in host_info:
            for port, port_info in host_info['tcp'].items():
                if port_info['state'] == 'open':
                    device_info['ports_open'].append(port)
                    device_info['services'][str(port)] = {
                        'name': port_info.get('name', ''),
                        'product': port_info.get('product', ''),
                        'version': port_info.get('version', ''),
                        'extrainfo': port_info.get('extrainfo', ''),
                    }
        
        # Get OS information
        if 'osmatch' in host_info:
            for os_match in host_info['osmatch']:
                device_info['os_info'] = {
                    'name': os_match.get('name', ''),
                    'accuracy': os_match.get('accuracy', 0),
                    'line': os_match.get('line', ''),
                }
                break  # Take the first (most accurate) match
        
        return device_info
    
    def _create_or_update_discovered_device(self, ip_address, device_info, network_range, scan_job):
        """Create or update a discovered device"""
        try:
            device, created = DiscoveredDevice.objects.get_or_create(
                ip_address=ip_address,
                network_range=network_range,
                defaults={
                    'hostname': device_info.get('hostname', ''),
                    'mac_address': device_info.get('mac_address', ''),
                    'ports_open': device_info.get('ports_open', []),
                    'services': device_info.get('services', {}),
                    'os_info': device_info.get('os_info', {}),
                    'hardware_info': device_info.get('hardware_info', {}),
                    'raw_data': device_info,
                }
            )
            
            if not created:
                # Update existing device
                device.hostname = device_info.get('hostname', device.hostname)
                device.mac_address = device_info.get('mac_address', device.mac_address)
                device.ports_open = device_info.get('ports_open', [])
                device.services = device_info.get('services', {})
                device.os_info = device_info.get('os_info', {})
                device.hardware_info = device_info.get('hardware_info', {})
                device.raw_data = device_info
                device.last_seen = timezone.now()
                device.scan_count += 1
                device.save()
                
                scan_job.updated_devices += 1
            else:
                scan_job.new_devices += 1
            
            scan_job.save()
            
            # Create scan result
            ScanResult.objects.create(
                scan_job=scan_job,
                discovered_device=device,
                ports_scanned=list(range(1, 1025)) if scan_job.scan_type != 'discovery' else [],
                ports_open=device_info.get('ports_open', []),
                services_detected=device_info.get('services', {}),
                os_fingerprint=device_info.get('os_info', {}),
                is_alive=True,
                scan_successful=True
            )
            
            # Try to match with existing assets
            self._try_match_asset(device)
            
            return device
            
        except Exception as e:
            AssetDiscoveryLog.objects.create(
                level='error',
                message=f"Error creating/updating device {ip_address}: {str(e)}",
                scan_job=scan_job
            )
            raise e
    
    def _try_match_asset(self, discovered_device):
        """Try to match discovered device with existing assets"""
        confidence_score = 0.0
        matched_asset = None
        
        # Try to match by IP address
        if discovered_device.ip_address:
            assets = Asset.objects.filter(ip_address=discovered_device.ip_address)
            if assets.exists():
                matched_asset = assets.first()
                confidence_score = 0.9
        
        # Try to match by MAC address
        if not matched_asset and discovered_device.mac_address:
            assets = Asset.objects.filter(mac_address=discovered_device.mac_address)
            if assets.exists():
                matched_asset = assets.first()
                confidence_score = 0.8
        
        # Try to match by hostname
        if not matched_asset and discovered_device.hostname:
            assets = Asset.objects.filter(hostname=discovered_device.hostname)
            if assets.exists():
                matched_asset = assets.first()
                confidence_score = 0.7
        
        # Update discovered device with match
        if matched_asset:
            discovered_device.matched_asset = matched_asset
            discovered_device.confidence_score = confidence_score
            discovered_device.status = 'matched'
            discovered_device.save()
            
            # Update asset's last seen time
            matched_asset.last_seen = timezone.now()
            matched_asset.save()
            
            AssetDiscoveryLog.objects.create(
                level='info',
                message=f"Matched device {discovered_device.ip_address} to asset {matched_asset.asset_tag}",
                discovered_device=discovered_device,
                details={'confidence_score': confidence_score}
            )
    
    def scan_all_active_ranges(self):
        """Scan all active network ranges"""
        active_ranges = NetworkRange.objects.filter(is_active=True)
        
        for network_range in active_ranges:
            # Check if it's time to scan this range
            if self._should_scan_range(network_range):
                try:
                    self.scan_network_range(network_range)
                except Exception as e:
                    logger.error(f"Failed to scan network range {network_range.network}: {str(e)}")
    
    def _should_scan_range(self, network_range):
        """Check if a network range should be scanned"""
        if not network_range.last_scan:
            return True
        
        time_since_last_scan = timezone.now() - network_range.last_scan
        return time_since_last_scan.total_seconds() >= network_range.scan_frequency


class AssetMatchingService:
    """Service for matching discovered devices with assets"""
    
    def match_discovered_devices(self):
        """Match all unmatched discovered devices with assets"""
        unmatched_devices = DiscoveredDevice.objects.filter(
            status='new',
            matched_asset__isnull=True
        )
        
        for device in unmatched_devices:
            self._match_device(device)
    
    def _match_device(self, discovered_device):
        """Match a single discovered device with assets"""
        discovery_service = NetworkDiscoveryService()
        discovery_service._try_match_asset(discovered_device)


def get_local_network_interfaces():
    """Get local network interfaces for automatic network range detection"""
    interfaces = []
    
    for interface_name, interface_addresses in psutil.net_if_addrs().items():
        for address in interface_addresses:
            if address.family == socket.AF_INET:  # IPv4
                interfaces.append({
                    'name': interface_name,
                    'ip': address.address,
                    'netmask': address.netmask,
                    'broadcast': address.broadcast,
                })
    
    return interfaces


def suggest_network_ranges():
    """Suggest network ranges based on local interfaces"""
    interfaces = get_local_network_interfaces()
    suggested_ranges = []
    
    for interface in interfaces:
        if interface['ip'] != '127.0.0.1':  # Skip loopback
            try:
                # Calculate network address
                ip = IPAddress(interface['ip'])
                netmask = IPAddress(interface['netmask'])
                network = IPNetwork(f"{interface['ip']}/{netmask}")
                network = network.cidr
                
                suggested_ranges.append({
                    'name': f"Network {interface['name']}",
                    'network': str(network),
                    'interface': interface['name'],
                })
            except:
                continue
    
    return suggested_rangesimport nmap
import socket
import psutil
import json
from datetime import datetime, timedelta
from django.utils import timezone
from netaddr import IPNetwork, IPAddress
from .models import NetworkRange, DiscoveredDevice, ScanJob, ScanResult, AssetDiscoveryLog
from assets.models import Asset
import logging

logger = logging.getLogger(__name__)


class NetworkDiscoveryService:
    """Service for network discovery and asset scanning"""
    
    def __init__(self):
        self.nm = nmap.PortScanner()
    
    def scan_network_range(self, network_range, scan_type='discovery', scan_options=None):
        """Scan a network range for devices"""
        if scan_options is None:
            scan_options = {}
        
        # Create scan job
        scan_job = ScanJob.objects.create(
            name=f"Network scan of {network_range.network}",
            scan_type=scan_type,
            scan_options=scan_options,
            started_at=timezone.now()
        )
        scan_job.network_ranges.add(network_range)
        
        try:
            # Update scan job status
            scan_job.status = 'running'
            scan_job.save()
            
            # Perform the scan
            devices_found = self._perform_network_scan(network_range, scan_job, scan_options)
            
            # Update scan job with results
            scan_job.status = 'completed'
            scan_job.completed_at = timezone.now()
            scan_job.devices_found = len(devices_found)
            scan_job.save()
            
            # Update network range last scan time
            network_range.last_scan = timezone.now()
            network_range.save()
            
            return scan_job
            
        except Exception as e:
            scan_job.status = 'failed'
            scan_job.errors = [str(e)]
            scan_job.completed_at = timezone.now()
            scan_job.save()
            
            AssetDiscoveryLog.objects.create(
                level='error',
                message=f"Network scan failed: {str(e)}",
                scan_job=scan_job
            )
            
            raise e
    
    def _perform_network_scan(self, network_range, scan_job, scan_options):
        """Perform the actual network scan"""
        devices_found = []
        network = IPNetwork(network_range.network)
        
        # Determine scan arguments based on scan type
        nmap_args = self._get_nmap_args(scan_job.scan_type, scan_options)
        
        try:
            # Scan the network
            self.nm.scan(str(network), arguments=nmap_args)
            
            for host in self.nm.all_hosts():
                if self.nm[host].state() == 'up':
                    device_info = self._extract_device_info(host, scan_job.scan_type)
                    device = self._create_or_update_discovered_device(
                        host, device_info, network_range, scan_job
                    )
                    devices_found.append(device)
                    
        except Exception as e:
            AssetDiscoveryLog.objects.create(
                level='error',
                message=f"Nmap scan error: {str(e)}",
                scan_job=scan_job
            )
            raise e
        
        return devices_found
    
    def _get_nmap_args(self, scan_type, scan_options):
        """Get nmap arguments based on scan type"""
        base_args = "-sn"  # Ping scan by default
        
        if scan_type == 'port_scan':
            base_args = "-sS"  # SYN scan
        elif scan_type == 'service_scan':
            base_args = "-sS -sV"  # Service version detection
        elif scan_type == 'os_detection':
            base_args = "-sS -O"  # OS detection
        elif scan_type == 'full_scan':
            base_args = "-sS -sV -O -A"  # Aggressive scan
        
        # Add custom options
        if scan_options.get('ports'):
            base_args += f" -p {scan_options['ports']}"
        
        if scan_options.get('timing'):
            base_args += f" -T{scan_options['timing']}"
        else:
            base_args += " -T3"  # Normal timing
        
        return base_args
    
    def _extract_device_info(self, host, scan_type):
        """Extract device information from nmap scan results"""
        host_info = self.nm[host]
        
        device_info = {
            'ip_address': host,
            'hostname': '',
            'mac_address': '',
            'ports_open': [],
            'services': {},
            'os_info': {},
            'hardware_info': {},
        }
        
        # Get hostname
        if 'hostnames' in host_info and host_info['hostnames']:
            device_info['hostname'] = host_info['hostnames'][0]['name']
        
        # Get MAC address
        if 'addresses' in host_info and 'mac' in host_info['addresses']:
            device_info['mac_address'] = host_info['addresses']['mac']
        
        # Get open ports and services
        if 'tcp' in host_info:
            for port, port_info in host_info['tcp'].items():
                if port_info['state'] == 'open':
                    device_info['ports_open'].append(port)
                    device_info['services'][str(port)] = {
                        'name': port_info.get('name', ''),
                        'product': port_info.get('product', ''),
                        'version': port_info.get('version', ''),
                        'extrainfo': port_info.get('extrainfo', ''),
                    }
        
        # Get OS information
        if 'osmatch' in host_info:
            for os_match in host_info['osmatch']:
                device_info['os_info'] = {
                    'name': os_match.get('name', ''),
                    'accuracy': os_match.get('accuracy', 0),
                    'line': os_match.get('line', ''),
                }
                break  # Take the first (most accurate) match
        
        return device_info
    
    def _create_or_update_discovered_device(self, ip_address, device_info, network_range, scan_job):
        """Create or update a discovered device"""
        try:
            device, created = DiscoveredDevice.objects.get_or_create(
                ip_address=ip_address,
                network_range=network_range,
                defaults={
                    'hostname': device_info.get('hostname', ''),
                    'mac_address': device_info.get('mac_address', ''),
                    'ports_open': device_info.get('ports_open', []),
                    'services': device_info.get('services', {}),
                    'os_info': device_info.get('os_info', {}),
                    'hardware_info': device_info.get('hardware_info', {}),
                    'raw_data': device_info,
                }
            )
            
            if not created:
                # Update existing device
                device.hostname = device_info.get('hostname', device.hostname)
                device.mac_address = device_info.get('mac_address', device.mac_address)
                device.ports_open = device_info.get('ports_open', [])
                device.services = device_info.get('services', {})
                device.os_info = device_info.get('os_info', {})
                device.hardware_info = device_info.get('hardware_info', {})
                device.raw_data = device_info
                device.last_seen = timezone.now()
                device.scan_count += 1
                device.save()
                
                scan_job.updated_devices += 1
            else:
                scan_job.new_devices += 1
            
            scan_job.save()
            
            # Create scan result
            ScanResult.objects.create(
                scan_job=scan_job,
                discovered_device=device,
                ports_scanned=list(range(1, 1025)) if scan_job.scan_type != 'discovery' else [],
                ports_open=device_info.get('ports_open', []),
                services_detected=device_info.get('services', {}),
                os_fingerprint=device_info.get('os_info', {}),
                is_alive=True,
                scan_successful=True
            )
            
            # Try to match with existing assets
            self._try_match_asset(device)
            
            return device
            
        except Exception as e:
            AssetDiscoveryLog.objects.create(
                level='error',
                message=f"Error creating/updating device {ip_address}: {str(e)}",
                scan_job=scan_job
            )
            raise e
    
    def _try_match_asset(self, discovered_device):
        """Try to match discovered device with existing assets"""
        confidence_score = 0.0
        matched_asset = None
        
        # Try to match by IP address
        if discovered_device.ip_address:
            assets = Asset.objects.filter(ip_address=discovered_device.ip_address)
            if assets.exists():
                matched_asset = assets.first()
                confidence_score = 0.9
        
        # Try to match by MAC address
        if not matched_asset and discovered_device.mac_address:
            assets = Asset.objects.filter(mac_address=discovered_device.mac_address)
            if assets.exists():
                matched_asset = assets.first()
                confidence_score = 0.8
        
        # Try to match by hostname
        if not matched_asset and discovered_device.hostname:
            assets = Asset.objects.filter(hostname=discovered_device.hostname)
            if assets.exists():
                matched_asset = assets.first()
                confidence_score = 0.7
        
        # Update discovered device with match
        if matched_asset:
            discovered_device.matched_asset = matched_asset
            discovered_device.confidence_score = confidence_score
            discovered_device.status = 'matched'
            discovered_device.save()
            
            # Update asset's last seen time
            matched_asset.last_seen = timezone.now()
            matched_asset.save()
            
            AssetDiscoveryLog.objects.create(
                level='info',
                message=f"Matched device {discovered_device.ip_address} to asset {matched_asset.asset_tag}",
                discovered_device=discovered_device,
                details={'confidence_score': confidence_score}
            )
    
    def scan_all_active_ranges(self):
        """Scan all active network ranges"""
        active_ranges = NetworkRange.objects.filter(is_active=True)
        
        for network_range in active_ranges:
            # Check if it's time to scan this range
            if self._should_scan_range(network_range):
                try:
                    self.scan_network_range(network_range)
                except Exception as e:
                    logger.error(f"Failed to scan network range {network_range.network}: {str(e)}")
    
    def _should_scan_range(self, network_range):
        """Check if a network range should be scanned"""
        if not network_range.last_scan:
            return True
        
        time_since_last_scan = timezone.now() - network_range.last_scan
        return time_since_last_scan.total_seconds() >= network_range.scan_frequency


class AssetMatchingService:
    """Service for matching discovered devices with assets"""
    
    def match_discovered_devices(self):
        """Match all unmatched discovered devices with assets"""
        unmatched_devices = DiscoveredDevice.objects.filter(
            status='new',
            matched_asset__isnull=True
        )
        
        for device in unmatched_devices:
            self._match_device(device)
    
    def _match_device(self, discovered_device):
        """Match a single discovered device with assets"""
        discovery_service = NetworkDiscoveryService()
        discovery_service._try_match_asset(discovered_device)


def get_local_network_interfaces():
    """Get local network interfaces for automatic network range detection"""
    interfaces = []
    
    for interface_name, interface_addresses in psutil.net_if_addrs().items():
        for address in interface_addresses:
            if address.family == socket.AF_INET:  # IPv4
                interfaces.append({
                    'name': interface_name,
                    'ip': address.address,
                    'netmask': address.netmask,
                    'broadcast': address.broadcast,
                })
    
    return interfaces


def suggest_network_ranges():
    """Suggest network ranges based on local interfaces"""
    interfaces = get_local_network_interfaces()
    suggested_ranges = []
    
    for interface in interfaces:
        if interface['ip'] != '127.0.0.1':  # Skip loopback
            try:
                # Calculate network address
                ip = IPAddress(interface['ip'])
                netmask = IPAddress(interface['netmask'])
                network = IPNetwork(f"{interface['ip']}/{netmask}")
                network = network.cidr
                
                suggested_ranges.append({
                    'name': f"Network {interface['name']}",
                    'network': str(network),
                    'interface': interface['name'],
                })
            except:
                continue
    
    return suggested_ranges