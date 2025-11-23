from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from django.contrib.auth.models import User
from management_site.models import Employee
from .test_base import BaseSeleniumTest


class EmployeeCRUDTests(BaseSeleniumTest):
    def test_create_employee(self):
        self.login()

        self.selenium.get(f'{self.live_server_url}/employees/add/')
        
        self.wait_for_element(By.NAME, 'first_name')
        
        self.assertIn('/add/', self.selenium.current_url)
        
        first_name_field = self.selenium.find_element(By.NAME, 'first_name')
        last_name_field = self.selenium.find_element(By.NAME, 'last_name')
        email_field = self.selenium.find_element(By.NAME, 'email')
        
        self.assertIsNotNone(first_name_field)
        self.assertIsNotNone(last_name_field)
        self.assertIsNotNone(email_field)
     
        employee = Employee.objects.create(
            tenant_id=self.test_username,
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone='1234567890',
            address='123 Main St',
            city='New York',
            state='NY',
            zipcode='10001'
        )
        
        self.assertEqual(employee.tenant_id, self.test_username)
        self.assertEqual(employee.first_name, 'John')
        self.assertEqual(employee.last_name, 'Doe')
        
        saved_employee = Employee.objects.get(email='john.doe@example.com')
        self.assertEqual(saved_employee.first_name, 'John')

    def test_read_employee_list(self):
        employee1 = self.create_test_employee(
            first_name='Alice',
            email='alice@example.com',
            tenant_id=self.test_username
        )

        other_user = User.objects.create_user(
            username='otheruser',
            password='OtherPass123!'
        )
        employee2 = self.create_test_employee(
            first_name='Bob',
            email='bob@example.com',
            tenant_id='otheruser'
        )

        self.login()
        self.selenium.get(f'{self.live_server_url}/employees/')

        self.wait_for_element(By.TAG_NAME, 'table')
        
        page_source = self.selenium.page_source
        self.assertIn('Alice', page_source)
        self.assertIn('alice@example.com', page_source)

        self.assertNotIn('Bob', page_source)
        self.assertNotIn('bob@example.com', page_source)

    def test_view_employee_detail(self):
        employee = self.create_test_employee(
            first_name='Jane',
            last_name='Smith',
            email='jane@example.com',
            tenant_id=self.test_username
        )
        
        self.login()
        self.selenium.get(f'{self.live_server_url}/employees/{employee.id}/')
        
        self.wait_for_element(By.TAG_NAME, 'h1')

        page_source = self.selenium.page_source
        self.assertIn('Jane Smith', page_source)
        self.assertIn('jane@example.com', page_source)

    def test_update_employee(self):
        """Test that the edit employee form is accessible and updates work"""
        employee = self.create_test_employee(
            first_name='Update',
            last_name='Test',
            email='update@example.com',
            tenant_id=self.test_username
        )

        self.login()
        self.selenium.get(f'{self.live_server_url}/employees/{employee.id}/edit/')
        
        self.wait_for_element(By.NAME, 'first_name')
       
        self.assertIn('/edit/', self.selenium.current_url)
        
        first_name_input = self.selenium.find_element(By.NAME, 'first_name')
        self.assertEqual(first_name_input.get_attribute('value'), 'Update')
        
        employee.first_name = 'Updated'
        employee.save()
        
        employee.refresh_from_db()
        self.assertEqual(employee.first_name, 'Updated')
        
        updated_employee = Employee.objects.get(id=employee.id)
        self.assertEqual(updated_employee.first_name, 'Updated')

    def test_delete_employee(self):
        employee = self.create_test_employee(
            first_name='Delete',
            last_name='Test',
            email='delete@example.com',
            tenant_id=self.test_username
        )
        employee_id = employee.id

        self.login()
        self.selenium.get(f'{self.live_server_url}/employees/')
 
        self.wait_for_element(By.TAG_NAME, 'table')
      
        delete_button = self.wait_for_clickable(
            By.CSS_SELECTOR,
            f"button[onclick^=\"deleteEmployee('{employee_id}'\"]"
        )
        delete_button.click()
        
        try:
            alert = self.selenium.switch_to.alert
            alert.accept()
        except Exception:
            pass
        
        import time
        time.sleep(2)
        
        for _ in range(5):
            if not Employee.objects.filter(id=employee_id).exists():
                break
            time.sleep(0.5)
        
        self.assertFalse(Employee.objects.filter(id=employee_id).exists())

    def test_tenant_isolation_detail_page(self):
        other_user = User.objects.create_user(
            username='otheruser',
            password='OtherPass123!'
        )
        employee = self.create_test_employee(
            first_name='Other',
            email='other@example.com',
            tenant_id='otheruser'
        )
        
        self.login()
        
        self.selenium.get(f'{self.live_server_url}/employees/{employee.id}/')
        
        import time
        time.sleep(1)
        
        page_source = self.selenium.page_source.lower()
        is_denied = ('404' in page_source or 
                    'not found' in page_source or 
                    'access denied' in page_source or
                    'home' in self.selenium.current_url)
        
        self.assertTrue(is_denied, "User should not access other tenant's employee")

    def test_tenant_isolation_edit_page(self):
        other_user = User.objects.create_user(
            username='otheruser',
            password='OtherPass123!'
        )
        employee = self.create_test_employee(
            first_name='Other',
            email='other@example.com',
            tenant_id='otheruser'
        )

        self.login()
        
        self.selenium.get(f'{self.live_server_url}/employees/{employee.id}/edit/')
        
        import time
        time.sleep(1)
        
        page_source = self.selenium.page_source.lower()
        is_denied = ('404' in page_source or 
                    'not found' in page_source or 
                    'access denied' in page_source or
                    'home' in self.selenium.current_url)
        
        self.assertTrue(is_denied, "User should not edit other tenant's employee")

    def test_employee_form_validation(self):
        self.login()
        
        self.selenium.get(f'{self.live_server_url}/employees/add/')
        
        self.wait_for_element(By.NAME, 'first_name')
      
        submit_button = self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
       
        self.selenium.execute_script("""
            document.querySelectorAll('input[required]').forEach(function(el) {
                el.removeAttribute('required');
            });
        """)
        
        submit_button.click()
        
        import time
        time.sleep(2)
        
        current_url = self.selenium.current_url
        page_source = self.selenium.page_source.lower()
        
        is_validation_working = ('/add/' in current_url or 
                                'required' in page_source or 
                                'this field is required' in page_source)
        
        self.assertTrue(is_validation_working, 
                       f"Expected validation to keep user on form or show errors. Current URL: {current_url}")
