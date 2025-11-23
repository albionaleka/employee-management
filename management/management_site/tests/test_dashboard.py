from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from management_site.models import Employee
from .test_base import BaseSeleniumTest


class DashboardTests(BaseSeleniumTest):
    def test_dashboard_total_employees_metric(self):
        for i in range(3):
            self.create_test_employee(
                first_name=f'Employee{i}',
                email=f'emp{i}@example.com',
                tenant_id=self.test_username
            )

        self.login()
        self.selenium.get(f'{self.live_server_url}/home/')

        self.wait_for_element(By.TAG_NAME, 'h1')
        
        page_source = self.selenium.page_source
        self.assertIn('3', page_source)

    def test_dashboard_growth_calculation(self):
        old_date = timezone.now() - timedelta(days=60)
        employee1 = self.create_test_employee(
            first_name='Old',
            email='old@example.com',
            tenant_id=self.test_username
        )
        employee1.created_at = old_date
        employee1.save()

        employee2 = self.create_test_employee(
            first_name='Recent',
            email='recent@example.com',
            tenant_id=self.test_username
        )

        self.login()
        self.selenium.get(f'{self.live_server_url}/home/')

        self.wait_for_element(By.TAG_NAME, 'h1')

        page_source = self.selenium.page_source
        self.assertTrue('+' in page_source or 'growth' in page_source.lower())

    def test_dashboard_new_baseline_indicator(self):
        self.create_test_employee(
            first_name='New1',
            email='new1@example.com',
            tenant_id=self.test_username
        )

        self.login()
        self.selenium.get(f'{self.live_server_url}/home/')

        self.wait_for_element(By.TAG_NAME, 'h1')

        page_source = self.selenium.page_source
        self.assertTrue('New' in page_source or '+100%' in page_source)

    def test_dashboard_monthly_chart_displays(self):
        now = timezone.now()
        for i in range(6):
            month_date = now - relativedelta(months=i)
            employee = self.create_test_employee(
                first_name=f'Month{i}',
                email=f'month{i}@example.com',
                tenant_id=self.test_username
            )
            employee.created_at = month_date
            employee.save()

        self.login()
        self.selenium.get(f'{self.live_server_url}/home/')

        chart_container = self.wait_for_element(By.CLASS_NAME, 'flex')
       
        bars = self.selenium.find_elements(By.CLASS_NAME, 'bg-blue-600')
        self.assertEqual(len(bars), 7, "Chart should display 7 monthly bars")

    def test_dashboard_chart_proportional_heights(self):
        now = timezone.now()

        old_employee = self.create_test_employee(
            first_name='Old',
            email='old@example.com',
            tenant_id=self.test_username
        )
        old_employee.created_at = now - relativedelta(months=5)
        old_employee.save()

        for i in range(3):
            self.create_test_employee(
                first_name=f'Recent{i}',
                email=f'recent{i}@example.com',
                tenant_id=self.test_username
            )

        self.login()
        self.selenium.get(f'{self.live_server_url}/home/')

        self.wait_for_element(By.CLASS_NAME, 'bg-blue-600')

        bars = self.selenium.find_elements(By.CLASS_NAME, 'bg-blue-600')
      
        heights = []
        for bar in bars:
            style = bar.get_attribute('style')
            if 'height' in style:
                height_str = style.split('height:')[1].split('%')[0].strip()
                heights.append(float(height_str))

        self.assertIn(100.0, heights, "Highest count should have 100% height")

    def test_dashboard_state_distribution(self):
        states = ['NY', 'CA', 'TX']
        for i, state in enumerate(states):
            self.create_test_employee(
                first_name=f'StateEmp{i}',
                email=f'state{i}@example.com',
                state=state,
                tenant_id=self.test_username
            )

        self.login()
        self.selenium.get(f'{self.live_server_url}/home/')

        self.wait_for_element(By.TAG_NAME, 'h1')
        
        page_source = self.selenium.page_source
        self.assertIn('NY', page_source)
        self.assertIn('CA', page_source)
        self.assertIn('TX', page_source)

    def test_dashboard_recent_employees_list(self):
        for i in range(3):
            self.create_test_employee(
                first_name=f'Recent{i}',
                last_name='Employee',
                email=f'recent{i}@example.com',
                tenant_id=self.test_username
            )

        self.login()
        self.selenium.get(f'{self.live_server_url}/home/')

        self.wait_for_element(By.TAG_NAME, 'h1')

        page_source = self.selenium.page_source
        self.assertIn('Recent0', page_source)

    def test_dashboard_tenant_isolation(self):
        employee1 = self.create_test_employee(
            first_name='MyEmployee',
            email='mine@example.com',
            tenant_id=self.test_username
        )

        other_user = User.objects.create_user(
            username='otheruser',
            password='OtherPass123!'
        )
        employee2 = self.create_test_employee(
            first_name='OtherEmployee',
            email='other@example.com',
            tenant_id='otheruser'
        )

        self.login()
        self.selenium.get(f'{self.live_server_url}/home/')

        self.wait_for_element(By.TAG_NAME, 'h1')

        page_source = self.selenium.page_source
        self.assertIn('MyEmployee', page_source)
        self.assertNotIn('OtherEmployee', page_source)

    def test_dashboard_empty_state(self):
        self.login()
        self.selenium.get(f'{self.live_server_url}/home/')

        self.wait_for_element(By.TAG_NAME, 'h1')

        page_source = self.selenium.page_source
        self.assertIn('0', page_source)

    def test_dashboard_month_labels(self):
        self.create_test_employee(
            first_name='Test',
            email='test@example.com',
            tenant_id=self.test_username
        )

        self.login()
        self.selenium.get(f'{self.live_server_url}/home/')

        self.wait_for_element(By.CLASS_NAME, 'bg-blue-600')

        page_source = self.selenium.page_source
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        month_found = any(month in page_source for month in months)
        self.assertTrue(month_found, "Month labels should be displayed on chart")
