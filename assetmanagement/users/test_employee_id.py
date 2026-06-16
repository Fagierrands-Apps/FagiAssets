from django.test import TestCase
from django.contrib.auth.models import User
from users.models import UserProfile
from datetime import datetime


class EmployeeIdGenerationTest(TestCase):
    
    def test_employee_id_format(self):
        """Test that employee ID has the correct format"""
        user = User.objects.create_user(username='testformat', email='test@example.com')
        emp_id = user.profile.employee_id
        
        # Should have format FGEXXX (FGE + 3 digits)
        self.assertTrue(emp_id.startswith("FGE"))
        self.assertEqual(len(emp_id), 6)  # FGE + 3 digits
        
        # Last 3 characters should be digits
        self.assertTrue(emp_id[3:].isdigit())
    
    def test_automatic_employee_id_generation(self):
        """Test that employee ID is automatically generated when creating a user"""
        user = User.objects.create_user(
            username='testuser',
            first_name='Test',
            last_name='User',
            email='test@example.com'
        )
        
        # User profile should be created automatically with employee ID
        profile = user.profile
        self.assertIsNotNone(profile.employee_id)
        self.assertTrue(profile.employee_id.startswith('FGE'))
    
    def test_unique_employee_ids(self):
        """Test that employee IDs are unique"""
        # Create multiple users
        user1 = User.objects.create_user(username='user1', email='user1@example.com')
        user2 = User.objects.create_user(username='user2', email='user2@example.com')
        user3 = User.objects.create_user(username='user3', email='user3@example.com')
        
        # All should have different employee IDs
        emp_ids = [user1.profile.employee_id, user2.profile.employee_id, user3.profile.employee_id]
        self.assertEqual(len(emp_ids), len(set(emp_ids)))  # All unique
    
    def test_sequential_employee_ids(self):
        """Test that employee IDs are sequential"""
        # Create users one by one
        user1 = User.objects.create_user(username='seq1', email='seq1@example.com')
        user2 = User.objects.create_user(username='seq2', email='seq2@example.com')
        
        # Extract the numeric parts (remove FGE prefix)
        id1_num = int(user1.profile.employee_id[3:])
        id2_num = int(user2.profile.employee_id[3:])
        
        # Should be sequential
        self.assertEqual(id2_num, id1_num + 1)
    
    def test_employee_id_not_overwritten(self):
        """Test that existing employee IDs are not overwritten"""
        user = User.objects.create_user(username='testuser2', email='test2@example.com')
        original_id = user.profile.employee_id
        
        # Save again - should not change the employee ID
        user.profile.save()
        self.assertEqual(user.profile.employee_id, original_id)
    
    def test_manual_employee_id_preservation(self):
        """Test that manually set employee IDs are preserved"""
        user = User.objects.create_user(username='manual', email='manual@example.com')
        
        # Set a custom employee ID
        user.profile.employee_id = 'CUSTOM-001'
        user.profile.save()
        
        # Should keep the custom ID
        self.assertEqual(user.profile.employee_id, 'CUSTOM-001')
        
        # Creating a new user should not interfere
        user2 = User.objects.create_user(username='auto', email='auto@example.com')
        self.assertNotEqual(user2.profile.employee_id, 'CUSTOM-001')
        self.assertTrue(user2.profile.employee_id.startswith('FGE'))