import requests
import logging
from typing import Dict, List, Optional, Tuple
from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from datetime import datetime
from .models import CRMCustomer, AssetCustomerAssignment, SyncLog, IntegrationSettings
from assets.models import Asset

logger = logging.getLogger(__name__)


class CRMIntegrationService:
    """Service class for handling CRM integration operations"""
    
    def __init__(self):
        self.settings = IntegrationSettings.get_settings()
        self.session = requests.Session()
        if self.settings.crm_api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.settings.crm_api_key}',
                'Content-Type': 'application/json'
            })
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test connection to CRM system"""
        try:
            response = self.session.get(f"{self.settings.crm_base_url}/api/health/")
            if response.status_code == 200:
                return True, "Connection successful"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"
    
    def sync_customers_from_crm(self, user: Optional[User] = None) -> SyncLog:
        """Sync customers from CRM to Asset Manager"""
        sync_log = SyncLog.objects.create(
            sync_type='customer_to_asset',
            sync_action='sync',
            status='pending',
            initiated_by=user
        )
        
        try:
            # Fetch customers from CRM
            response = self.session.get(f"{self.settings.crm_base_url}/api/customers/")
            response.raise_for_status()
            
            crm_customers = response.json()
            if isinstance(crm_customers, dict) and 'results' in crm_customers:
                crm_customers = crm_customers['results']
            
            sync_log.records_processed = len(crm_customers)
            success_count = 0
            error_count = 0
            errors = []
            
            with transaction.atomic():
                for crm_customer_data in crm_customers:
                    try:
                        self._sync_single_customer(crm_customer_data)
                        success_count += 1
                    except Exception as e:
                        error_count += 1
                        errors.append(f"Customer ID {crm_customer_data.get('id', 'unknown')}: {str(e)}")
                        logger.error(f"Error syncing customer {crm_customer_data.get('id')}: {e}")
            
            sync_log.records_success = success_count
            sync_log.records_error = error_count
            sync_log.status = 'success' if error_count == 0 else ('partial' if success_count > 0 else 'error')
            
            if errors:
                sync_log.error_message = "; ".join(errors[:5])  # Store first 5 errors
                sync_log.error_details = {'errors': errors}
            
        except Exception as e:
            sync_log.status = 'error'
            sync_log.error_message = str(e)
            logger.error(f"Failed to sync customers from CRM: {e}")
        
        finally:
            sync_log.completed_at = timezone.now()
            if sync_log.started_at:
                duration = (sync_log.completed_at - sync_log.started_at).total_seconds()
                sync_log.duration_seconds = duration
            sync_log.save()
        
        return sync_log
    
    def _sync_single_customer(self, crm_customer_data: Dict) -> CRMCustomer:
        """Sync a single customer from CRM data"""
        crm_customer_id = crm_customer_data['id']
        
        # Map assigned employee
        assigned_employee = None
        if crm_customer_data.get('assigned_employee'):
            try:
                # Try to find employee by employee ID or username
                employee_data = crm_customer_data['assigned_employee']
                if isinstance(employee_data, dict):
                    employee_id = employee_data.get('employee_id') or employee_data.get('user', {}).get('username')
                    if employee_id:
                        assigned_employee = User.objects.filter(
                            models.Q(profile__employee_id=employee_id) | 
                            models.Q(username=employee_id)
                        ).first()
            except Exception as e:
                logger.warning(f"Could not map assigned employee for customer {crm_customer_id}: {e}")
        
        # Create or update customer
        customer, created = CRMCustomer.objects.update_or_create(
            crm_customer_id=crm_customer_id,
            defaults={
                'first_name': crm_customer_data.get('first_name', ''),
                'last_name': crm_customer_data.get('last_name', ''),
                'company_name': crm_customer_data.get('company_name', ''),
                'email': crm_customer_data.get('email', ''),
                'phone': crm_customer_data.get('phone', ''),
                'address_line1': crm_customer_data.get('address_line1', ''),
                'address_line2': crm_customer_data.get('address_line2', ''),
                'city': crm_customer_data.get('city', ''),
                'state': crm_customer_data.get('state', ''),
                'postal_code': crm_customer_data.get('postal_code', ''),
                'country': crm_customer_data.get('country', 'USA'),
                'status': crm_customer_data.get('status', 'active'),
                'customer_type': crm_customer_data.get('customer_type', 'individual'),
                'assigned_employee': assigned_employee,
                'sync_status': 'synced',
                'sync_error': None,
            }
        )
        
        return customer
    
    def sync_asset_assignments_to_crm(self, user: Optional[User] = None) -> SyncLog:
        """Sync asset assignments to CRM system"""
        sync_log = SyncLog.objects.create(
            sync_type='asset_to_crm',
            sync_action='sync',
            status='pending',
            initiated_by=user
        )
        
        try:
            # Get all active asset assignments
            assignments = AssetCustomerAssignment.objects.filter(is_active=True).select_related(
                'asset', 'customer', 'assigned_by'
            )
            
            sync_log.records_processed = assignments.count()
            success_count = 0
            error_count = 0
            errors = []
            
            for assignment in assignments:
                try:
                    self._sync_assignment_to_crm(assignment)
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    errors.append(f"Assignment {assignment.id}: {str(e)}")
                    logger.error(f"Error syncing assignment {assignment.id}: {e}")
            
            sync_log.records_success = success_count
            sync_log.records_error = error_count
            sync_log.status = 'success' if error_count == 0 else ('partial' if success_count > 0 else 'error')
            
            if errors:
                sync_log.error_message = "; ".join(errors[:5])
                sync_log.error_details = {'errors': errors}
        
        except Exception as e:
            sync_log.status = 'error'
            sync_log.error_message = str(e)
            logger.error(f"Failed to sync asset assignments to CRM: {e}")
        
        finally:
            sync_log.completed_at = timezone.now()
            if sync_log.started_at:
                duration = (sync_log.completed_at - sync_log.started_at).total_seconds()
                sync_log.duration_seconds = duration
            sync_log.save()
        
        return sync_log
    
    def _sync_assignment_to_crm(self, assignment: AssetCustomerAssignment):
        """Sync a single asset assignment to CRM"""
        # Prepare assignment data for CRM
        assignment_data = {
            'customer_id': assignment.customer.crm_customer_id,
            'asset_tag': assignment.asset.asset_tag,
            'asset_name': assignment.asset.name,
            'asset_serial': assignment.asset.serial_number,
            'assignment_type': assignment.assignment_type,
            'assigned_date': assignment.assigned_date.isoformat(),
            'contract_number': assignment.contract_number,
            'monthly_fee': float(assignment.monthly_fee) if assignment.monthly_fee else None,
            'total_value': float(assignment.total_value) if assignment.total_value else None,
            'notes': assignment.notes,
        }
        
        # Send to CRM system
        response = self.session.post(
            f"{self.settings.crm_base_url}/api/asset-assignments/",
            json=assignment_data
        )
        response.raise_for_status()
    
    def create_customer_assignment(self, asset: Asset, customer: CRMCustomer, 
                                 assignment_type: str = 'owned', user: Optional[User] = None,
                                 **kwargs) -> AssetCustomerAssignment:
        """Create a new asset-customer assignment"""
        assignment = AssetCustomerAssignment.objects.create(
            asset=asset,
            customer=customer,
            assignment_type=assignment_type,
            assigned_by=user,
            **kwargs
        )
        
        # Log the assignment creation
        SyncLog.objects.create(
            sync_type='assignment_sync',
            sync_action='create',
            status='success',
            records_processed=1,
            records_success=1,
            initiated_by=user,
            content_object=assignment
        )
        
        return assignment
    
    def get_customer_assets(self, customer: CRMCustomer) -> List[Asset]:
        """Get all assets assigned to a customer"""
        assignments = AssetCustomerAssignment.objects.filter(
            customer=customer,
            is_active=True
        ).select_related('asset')
        
        return [assignment.asset for assignment in assignments]
    
    def get_asset_customers(self, asset: Asset) -> List[CRMCustomer]:
        """Get all customers associated with an asset"""
        assignments = AssetCustomerAssignment.objects.filter(
            asset=asset,
            is_active=True
        ).select_related('customer')
        
        return [assignment.customer for assignment in assignments]
    
    def sync_employee_data(self, user: Optional[User] = None) -> SyncLog:
        """Sync employee data between systems"""
        sync_log = SyncLog.objects.create(
            sync_type='employee_sync',
            sync_action='sync',
            status='pending',
            initiated_by=user
        )
        
        try:
            # Fetch employees from CRM
            response = self.session.get(f"{self.settings.crm_base_url}/api/employees/")
            response.raise_for_status()
            
            crm_employees = response.json()
            if isinstance(crm_employees, dict) and 'results' in crm_employees:
                crm_employees = crm_employees['results']
            
            sync_log.records_processed = len(crm_employees)
            success_count = 0
            error_count = 0
            errors = []
            
            for crm_employee_data in crm_employees:
                try:
                    self._sync_single_employee(crm_employee_data)
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    errors.append(f"Employee ID {crm_employee_data.get('employee_id', 'unknown')}: {str(e)}")
                    logger.error(f"Error syncing employee {crm_employee_data.get('employee_id')}: {e}")
            
            sync_log.records_success = success_count
            sync_log.records_error = error_count
            sync_log.status = 'success' if error_count == 0 else ('partial' if success_count > 0 else 'error')
            
            if errors:
                sync_log.error_message = "; ".join(errors[:5])
                sync_log.error_details = {'errors': errors}
        
        except Exception as e:
            sync_log.status = 'error'
            sync_log.error_message = str(e)
            logger.error(f"Failed to sync employees: {e}")
        
        finally:
            sync_log.completed_at = timezone.now()
            if sync_log.started_at:
                duration = (sync_log.completed_at - sync_log.started_at).total_seconds()
                sync_log.duration_seconds = duration
            sync_log.save()
        
        return sync_log
    
    def _sync_single_employee(self, crm_employee_data: Dict):
        """Sync a single employee from CRM data"""
        from users.models import UserProfile
        from assets.models import Department
        
        employee_id = crm_employee_data.get('employee_id')
        user_data = crm_employee_data.get('user', {})
        
        if not employee_id or not user_data:
            raise ValueError("Missing employee_id or user data")
        
        # Find or create user
        username = user_data.get('username') or user_data.get('email', '').split('@')[0]
        user, user_created = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': user_data.get('first_name', ''),
                'last_name': user_data.get('last_name', ''),
                'email': user_data.get('email', ''),
                'is_active': crm_employee_data.get('employment_status') == 'active',
            }
        )
        
        # Update user profile
        profile, profile_created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'employee_id': employee_id}
        )
        
        # Update profile fields
        profile.employee_id = employee_id
        profile.phone = crm_employee_data.get('phone', '')
        profile.job_title = crm_employee_data.get('position', '')
        
        # Map department if exists
        department_data = crm_employee_data.get('department')
        if department_data and isinstance(department_data, dict):
            department_name = department_data.get('name')
            if department_name:
                department, _ = Department.objects.get_or_create(
                    name=department_name,
                    defaults={'description': f'Synced from CRM: {department_name}'}
                )
                profile.department = department
        
        profile.save()
        
        return user
    
    def full_sync(self, user: Optional[User] = None) -> Dict[str, SyncLog]:
        """Perform a full bidirectional sync"""
        results = {}
        
        if self.settings.sync_employees:
            results['employees'] = self.sync_employee_data(user)
        
        if self.settings.sync_customers_to_assets:
            results['customers'] = self.sync_customers_from_crm(user)
        
        if self.settings.sync_assets_to_crm:
            results['assignments'] = self.sync_asset_assignments_to_crm(user)
        
        return results