from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from .test_base import BaseSeleniumTest


class NavigationTests(BaseSeleniumTest):
    def test_navbar_home_link(self):
        self.login()
        self.selenium.get(f'{self.live_server_url}/employees/')
        
        home_link = self.wait_for_clickable(By.LINK_TEXT, 'menaxheri')
        home_link.click()
        
        WebDriverWait(self.selenium, 10).until(
            EC.url_contains('/home/')
        )
        
        self.assertIn('home', self.selenium.current_url)

    def test_navbar_employees_link(self):
        self.login()
        
        # Ensure desktop view (md breakpoint is 768px)
        self.selenium.set_window_size(1024, 768)
        
        # Find the desktop menu link (inside .hidden.md:flex container)
        employees_link = self.wait_for_clickable(
            By.CSS_SELECTOR, 
            'div.hidden.md\\:flex a[href*="employees"]',
            timeout=15
        )
        employees_link.click()
        
        WebDriverWait(self.selenium, 15).until(
            EC.url_contains('/employees/')
        )
        
        self.assertIn('employees', self.selenium.current_url)

    def test_navbar_add_employee_link(self):
        self.login()
        
        # Ensure desktop view (md breakpoint is 768px)
        self.selenium.set_window_size(1024, 768)
        
        # Find the desktop menu link (inside .hidden.md:flex container)
        add_link = self.wait_for_clickable(
            By.CSS_SELECTOR,
            'div.hidden.md\\:flex a[href*="add"]',
            timeout=15
        )
        add_link.click()
        
        WebDriverWait(self.selenium, 15).until(
            EC.url_contains('/add/')
        )
        
        self.assertIn('/add/', self.selenium.current_url)

    def test_navbar_logout_button(self):
        self.login()
        
        # Ensure desktop view (md breakpoint is 768px)
        self.selenium.set_window_size(1024, 768)
        
        # Find the desktop logout button (inside .hidden.md:block form)
        logout_button = self.wait_for_clickable(
            By.CSS_SELECTOR,
            'form.hidden.md\\:block[action*="logout"] button[type="submit"]',
            timeout=15
        )
        logout_button.click()
        
        WebDriverWait(self.selenium, 10).until(
            EC.url_contains('/login/')
        )
        
        self.assertIn('login', self.selenium.current_url)

    def test_mobile_burger_menu_toggle(self):
        self.login()
        
        self.selenium.set_window_size(375, 667)
        
        menu_button = self.wait_for_clickable(By.ID, 'mobile-menu-btn')
        
        menu_button.click()
        
        import time
        time.sleep(0.5)
        
        mobile_menu = self.selenium.find_element(By.ID, 'mobile-menu')
        menu_classes = mobile_menu.get_attribute('class')

        is_hidden = ' hidden ' in f' {menu_classes} ' or menu_classes.startswith('hidden ') or menu_classes.endswith(' hidden') or menu_classes == 'hidden'
        self.assertFalse(is_hidden, "Mobile menu should be visible after clicking button")

        menu_button.click()
        time.sleep(0.5)

        self.assertTrue('hidden' in mobile_menu.get_attribute('class'))

    def test_mobile_menu_navigation_links(self):
        self.login()
        
        self.selenium.set_window_size(375, 667)
        
        menu_button = self.wait_for_clickable(By.ID, 'mobile-menu-btn')
        menu_button.click()
        
        import time
        time.sleep(0.5)
        
        mobile_menu = self.selenium.find_element(By.ID, 'mobile-menu')
        menu_html = mobile_menu.get_attribute('innerHTML')
        
        self.assertIn('View Employees', menu_html)
        self.assertIn('Add Employee', menu_html)
        self.assertIn('Logout', menu_html)

    def test_theme_toggle_button_exists(self):
        self.login()
        
        theme_toggle = self.wait_for_element(By.ID, 'theme-toggle')
        self.assertIsNotNone(theme_toggle)

    def test_theme_toggle_switches_mode(self):
        self.login()
        
        html_element = self.selenium.find_element(By.TAG_NAME, 'html')
        initial_has_dark = 'dark' in html_element.get_attribute('class')
        
        theme_toggle = self.wait_for_clickable(By.ID, 'theme-toggle')
        theme_toggle.click()
        
        import time
        time.sleep(0.5)
        
        html_element = self.selenium.find_element(By.TAG_NAME, 'html')
        final_has_dark = 'dark' in html_element.get_attribute('class')
        
        self.assertNotEqual(initial_has_dark, final_has_dark)

    def test_theme_persists_across_pages(self):
        self.login()
        
        theme_toggle = self.wait_for_clickable(By.ID, 'theme-toggle')
        
        html_element = self.selenium.find_element(By.TAG_NAME, 'html')
        if 'dark' not in html_element.get_attribute('class'):
            theme_toggle.click()
            import time
            time.sleep(0.5)
        
        self.selenium.get(f'{self.live_server_url}/employees/')
        
        self.wait_for_element(By.TAG_NAME, 'html')
        
        html_element = self.selenium.find_element(By.TAG_NAME, 'html')
        self.assertIn('dark', html_element.get_attribute('class'))

    def test_navbar_visible_on_all_pages(self):
        self.login()
        
        pages = [
            '/home/',
            '/employees/',
            '/employees/add/'
        ]
        
        for page in pages:
            self.selenium.get(f'{self.live_server_url}{page}')
            
            navbar = self.wait_for_element(By.TAG_NAME, 'nav')
            
            self.assertTrue(navbar.is_displayed(), f"Navbar should be visible on {page}")

    def test_navbar_not_visible_on_login_page(self):
        self.selenium.get(f'{self.live_server_url}/login/')
        
        navbars = self.selenium.find_elements(By.TAG_NAME, 'nav')
        
        if navbars:
            navbar_html = navbars[0].get_attribute('innerHTML')
            self.assertNotIn('Logout', navbar_html)

    def test_mobile_menu_icon_changes(self):
        self.login()
        
        self.selenium.set_window_size(375, 667)
       
        menu_button = self.wait_for_clickable(By.ID, 'mobile-menu-btn')
        
        initial_icon_html = menu_button.get_attribute('innerHTML')
        
        menu_button.click()
        import time
        time.sleep(0.5)
        
        opened_icon_html = menu_button.get_attribute('innerHTML')
        self.assertNotEqual(initial_icon_html, opened_icon_html)

    def test_desktop_menu_hidden_on_mobile(self):
        self.login()
        
        self.selenium.set_window_size(375, 667)
        
        desktop_links = self.selenium.find_elements(
            By.CSS_SELECTOR,
            'nav a.hover\\:text-blue-400'
        )
       
        visible_desktop_links = [link for link in desktop_links if link.is_displayed()]
        self.assertEqual(len(visible_desktop_links), 0, 
                        "Desktop menu links should be hidden on mobile")

    def test_breadcrumb_navigation(self):
        self.login()
        
        # Ensure desktop view
        self.selenium.set_window_size(1024, 768)
        
        self.assertIn('home', self.selenium.current_url)
        
        employees_link = self.wait_for_clickable(
            By.CSS_SELECTOR,
            'div.hidden.md\\:flex a[href*="employees"]'
        )
        employees_link.click()
        WebDriverWait(self.selenium, 10).until(
            EC.url_contains('/employees/')
        )
        
        add_link = self.wait_for_clickable(
            By.CSS_SELECTOR,
            'div.hidden.md\\:flex a[href*="add"]'
        )
        add_link.click()
        WebDriverWait(self.selenium, 10).until(
            EC.url_contains('/add/')
        )
        
        home_link = self.wait_for_clickable(By.LINK_TEXT, 'menaxheri')
        home_link.click()
        WebDriverWait(self.selenium, 10).until(
            EC.url_contains('/home/')
        )
       
        self.assertIn('home', self.selenium.current_url)
