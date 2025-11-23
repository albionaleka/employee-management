"""
Authentication tests: login, logout, register, theme toggle
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth.models import User
from .test_base import BaseSeleniumTest


class AuthenticationTests(BaseSeleniumTest):
    def test_user_registration(self):
        self.selenium.get(f'{self.live_server_url}/register/')
        
        self.selenium.find_element(By.NAME, 'username').send_keys('newuser')
        self.selenium.find_element(By.NAME, 'email').send_keys('newuser@example.com')
        self.selenium.find_element(By.NAME, 'first_name').send_keys('New')
        self.selenium.find_element(By.NAME, 'last_name').send_keys('User')
        self.selenium.find_element(By.NAME, 'password1').send_keys('TestPass123!')
        self.selenium.find_element(By.NAME, 'password2').send_keys('TestPass123!')

        self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        WebDriverWait(self.selenium, 10).until(
            EC.url_contains('/home/')
        )

        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_user_login_success(self):
        self.selenium.get(f'{self.live_server_url}/login/')
        
        self.selenium.find_element(By.ID, 'username').send_keys(self.test_username)
        self.selenium.find_element(By.ID, 'password').send_keys(self.test_password)
        self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        WebDriverWait(self.selenium, 10).until(
            EC.url_contains('/home/')
        )
       
        self.assertIn('home', self.selenium.current_url)

    def test_user_login_failure(self):
        self.selenium.get(f'{self.live_server_url}/login/')

        self.selenium.find_element(By.ID, 'username').send_keys(self.test_username)
        self.selenium.find_element(By.ID, 'password').send_keys('WrongPassword')
        self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        WebDriverWait(self.selenium, 5).until(
            EC.url_contains('/login/')
        )

        self.assertIn('login', self.selenium.current_url)

    def test_user_logout(self):
        self.login()

        logout_button = self.wait_for_clickable(
            By.CSS_SELECTOR, 
            'form[action*="logout"] button[type="submit"]'
        )
        logout_button.click()
        
        WebDriverWait(self.selenium, 10).until(
            EC.url_contains('/login/')
        )
        
        self.assertIn('login', self.selenium.current_url)

    def test_theme_toggle_on_login_page(self):
        self.selenium.get(f'{self.live_server_url}/login/')

        html_element = self.selenium.find_element(By.TAG_NAME, 'html')
        initial_has_dark = 'dark' in html_element.get_attribute('class')

        theme_toggle = self.wait_for_clickable(By.ID, 'theme-toggle')
        theme_toggle.click()

        import time
        time.sleep(0.5)

        html_element = self.selenium.find_element(By.TAG_NAME, 'html')
        final_has_dark = 'dark' in html_element.get_attribute('class')

        self.assertNotEqual(initial_has_dark, final_has_dark)

    def test_protected_page_redirect(self):
        self.selenium.get(f'{self.live_server_url}/home/')

        WebDriverWait(self.selenium, 10).until(
            EC.url_contains('/login/')
        )
        
        self.assertIn('login', self.selenium.current_url)

    def test_registration_link_from_login(self):
        self.selenium.get(f'{self.live_server_url}/login/')

        register_link = self.selenium.find_element(By.LINK_TEXT, 'Register')
        register_link.click()

        WebDriverWait(self.selenium, 10).until(
            EC.url_contains('/register/')
        )
        
        self.assertIn('register', self.selenium.current_url)

    def test_login_link_from_register(self):
        self.selenium.get(f'{self.live_server_url}/register/')
   
        login_link = self.selenium.find_element(By.LINK_TEXT, 'Login')
        login_link.click()
  
        WebDriverWait(self.selenium, 10).until(
            EC.url_contains('/login/')
        )
        
        self.assertIn('login', self.selenium.current_url)
