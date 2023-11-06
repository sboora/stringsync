import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from seleniumbase import BaseCase
from config import ROOT_USERNAME, ROOT_PASSWORD


class TenantPortalTest(BaseCase):
    URL = "http://localhost:8501/"

    def open_login_page(self):
        self.open(self.URL)

    def wait_for_element(self, selector, selector_type=By.CSS_SELECTOR, timeout=25):
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((selector_type, selector))
        )

    def type_text(self, selector, text):
        self.type(selector, text)

    def click_button(self, selector):
        self.click(selector)

    def assert_page_title(self, title):
        self.assert_title(title)

    def assert_text_present(self, text, selector="html"):
        self.assert_text(text, selector=selector)

    def find_input_and_type(self, selector, text):
        element = self.find_element(selector)
        element.send_keys(text)

    def field_check(self, text, selector):
        self.assert_text(text, selector=selector)

    def verify_login_successful(self):
        self.assert_page_title("Guru Shishya Tenant Portal")
        self.assert_text_present("Welcome to")
        self.assert_text_present("Tenant Management Portal")
        self.assert_text_present("Your Centralized Platform for Multi-Organization Educational Oversight")
        self.assert_text_present("Register a Tenant")
        self.assert_text_present("List Tenants")
        self.assert_text_present("Feature Toggles")

    def verify_registration_successful(self):
        self.assert_text_present("Tenant ABC Corp registered successfully")

    def test_login(self):
        # Login
        self.open_login_page()
        self.find_input_and_type("input[aria-label='Username']", ROOT_USERNAME)
        self.find_input_and_type("input[aria-label='Password']", ROOT_PASSWORD)
        self.click_button("button:contains('Login')")
        self.verify_login_successful()
        # Tenant Registration
        self.find_input_and_type("input[aria-label='Name']", "ABC Corp")
        self.find_input_and_type("input[aria-label='Description']", "ABC Corp")
        self.find_input_and_type("input[aria-label='Address']", "ABC Corp")
        self.find_input_and_type("input[aria-label='Email']", "abc@gmail.com")
        self.click_button('[data-testid="baseButton-primaryFormSubmit"]')
        self.verify_registration_successful()
