from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from seleniumbase import BaseCase


class PortalTestBase(BaseCase):
    sleep_timer = 1

    def open_login_page(self, url):
        self.open(url)

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

    def login(self, url, username, password):
        self.open_login_page(url)
        self.delay()
        self.find_input_and_type("input[aria-label='Username']", username)
        self.delay()
        self.find_input_and_type("input[aria-label='Password']", password)
        self.sleep(2)
        self.click_button("button:contains('Login')")
        self.delay()
        self.verify_login_successful()
        self.delay()

    def verify_login_successful(self):
        pass

    def flow(self):
        url = self.get_url()
        username = self.get_username()
        password = self.get_password()
        self.login(url, username, password)

        # Execute each test method in the flow
        for method in self.get_test_flow_methods():
            method()

    def get_test_flow_methods(self):
        return []

    @staticmethod
    def get_url():
        return ""

    def get_username(self):
        return ""

    def get_password(self):
        return ""

    def delay(self):
        self.sleep(self.sleep_timer)