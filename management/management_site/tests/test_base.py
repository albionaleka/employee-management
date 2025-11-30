from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from management_site.models import Employee
import unittest
import os

try:
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from webdriver_manager.chrome import ChromeDriverManager
except Exception:
    ChromeService = ChromeOptions = ChromeDriverManager = None


class BaseSeleniumTest(StaticLiveServerTestCase):
    serialized_rollback = True

    @classmethod
    def setUpClass(cls):
        from django.conf import settings
        settings.ALLOWED_HOSTS.append('localhost')
        settings.ALLOWED_HOSTS.append('127.0.0.1')
        settings.ALLOWED_HOSTS.append('[::1]')
        super().setUpClass()

        driver = None
        headless = (os.environ.get('HEADLESS', '1') != '0')

        if ChromeOptions and ChromeDriverManager:
            try:
                chrome_options = ChromeOptions()
                if headless:
                    chrome_options.add_argument('--headless=new')
                else:
                    chrome_options.add_argument('--auto-open-devtools-for-tabs')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--window-size=1400,1000')
                service = ChromeService(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                cls.browser_used = 'chrome'
            except WebDriverException:
                driver = None

        if driver is None:
            raise unittest.SkipTest('No local browser (Chrome/Firefox) available; skipping Selenium tests.')

        cls.selenium = driver
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, 'selenium', None):
            try:
                cls.selenium.quit()
            except Exception:
                pass
        super().tearDownClass()

    def setUp(self):
        self.test_username = 'testuser'
        self.test_password = 'TestPass123!'
        self.test_email = 'test@example.com'
        
        self.user = User.objects.create_user(
            username=self.test_username,
            password=self.test_password,
            email=self.test_email,
            first_name='Test',
            last_name='User'
        )

    def tearDown(self):
        User.objects.all().delete()
        Employee.objects.all().delete()

    def login(self, username=None, password=None):
        username = username or self.test_username
        password = password or self.test_password

        try:
            alert = self.selenium.switch_to.alert
            alert.accept()
        except Exception:
            pass
        
        self.selenium.get(f'{self.live_server_url}/login/')

        username_input = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.ID, 'username'))
        )
        password_input = self.selenium.find_element(By.ID, 'password')
        submit_button = self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        
        username_input.send_keys(username)
        password_input.send_keys(password)
        submit_button.click()

        WebDriverWait(self.selenium, 15).until(
            EC.url_contains('/home/')
        )

    def logout(self):
        logout_button = self.selenium.find_element(By.CSS_SELECTOR, 'form[action*="logout"] button[type="submit"]')
        logout_button.click()
        
        WebDriverWait(self.selenium, 10).until(
            EC.url_contains('/login/')
        )

    def wait_for_element(self, by, value, timeout=10):
        try:
            element = WebDriverWait(self.selenium, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            self.fail(f"Element {value} not found within {timeout} seconds")

    def wait_for_clickable(self, by, value, timeout=10):
        try:
            element = WebDriverWait(self.selenium, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            return element
        except TimeoutException:
            self.fail(f"Element {value} not clickable within {timeout} seconds")

    def create_test_employee(self, tenant_id=None, **overrides):
        defaults = {
            'tenant_id': tenant_id or self.test_username,
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '1234567890',
            'address': '123 Test St',
            'city': 'Test City',
            'state': 'Test State',
            'zipcode': '12345',
        }
        defaults.update(overrides)
        return Employee.objects.create(**defaults)

    def fill_employee_form(self, data):
        allowed = {'first_name','last_name','email','phone','address','city','state','zipcode'}
        for field_name in allowed:
            if field_name in data:
                el = self.selenium.find_element(By.NAME, field_name)
                el.clear()
                el.send_keys(str(data[field_name]))
