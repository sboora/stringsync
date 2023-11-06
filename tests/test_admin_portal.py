import time

import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from seleniumbase import BaseCase
from config import ADMIN_USERNAME, ADMIN_PASSWORD, TEACHER_USERNAME, TEACHER_PASSWORD

class AdminPortalTest(BaseCase):
    URL = "http://localhost:8502/"

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
        self.assert_page_title("Guru Shishya Admin Portal")
        self.assert_text_present("Welcome to")
        self.assert_text_present("Administrative Portal")
        self.assert_text_present("Your Comprehensive Dashboard for Educational Management")
        self.assert_text_present("Register a School")
        self.assert_text_present("List Schools")
        self.assert_text_present("Register a Tutor")
        self.assert_text_present("List Tutors")
        self.assert_text_present("Assign a Tutor to School")
        self.assert_text_present("List Tutor Assignments")

    def verify_registration_successful(self, text):
        self.assert_text_present(text)

    def test_flow(self):
        sleep_timer = 0
        # Login
        self.open_login_page()
        time.sleep(sleep_timer)
        self.find_input_and_type("input[aria-label='Username']", ADMIN_USERNAME)
        time.sleep(sleep_timer)
        self.find_input_and_type("input[aria-label='Password']", ADMIN_PASSWORD)
        time.sleep(sleep_timer)
        self.click_button("button:contains('Login')")
        time.sleep(sleep_timer)
        self.verify_login_successful()
        time.sleep(sleep_timer)

        # Register a School
        school_name = "ABC Corp Violin"
        self.find_input_and_type("input[aria-label='School']", school_name)
        time.sleep(sleep_timer)
        self.find_input_and_type("input[aria-label='Description']", school_name)
        time.sleep(sleep_timer)
        self.click_button("button:contains('Register School')")
        time.sleep(sleep_timer)
        self.verify_registration_successful(f"School {school_name} registered successfully")
        time.sleep(sleep_timer)

        # List Schools
        self.click("button[id^='tabs-'][id$='-tab-1']")
        time.sleep(sleep_timer)

        # Register a Tutor
        self.click("button[id^='tabs-'][id$='-tab-2']")
        time.sleep(sleep_timer)
        teacher_email = "abcviolinteacher@gmail.com"
        self.find_input_and_type("input[aria-label='Name']", "ABC Corp Violin Teacher")
        time.sleep(sleep_timer)
        self.find_input_and_type("input[aria-label='Username']", TEACHER_USERNAME)
        time.sleep(sleep_timer)
        self.find_input_and_type("input[aria-label='Email']", teacher_email)
        time.sleep(sleep_timer)
        self.find_input_and_type("input[aria-label='Password']", TEACHER_PASSWORD)
        time.sleep(sleep_timer)
        self.click("button:contains('Register Tutor')")
        time.sleep(sleep_timer)
        self.verify_registration_successful(
            f"User {TEACHER_USERNAME} with email {teacher_email} registered successfully as teacher.")
        time.sleep(sleep_timer)

        # List Tutors
        self.click("button[id^='tabs-'][id$='-tab-3']")
        time.sleep(sleep_timer)

        # Assign Tutor to School
        self.click("button[id^='tabs-'][id$='-tab-4']")
        time.sleep(sleep_timer)
        self.click("div[data-testid='stSelectbox']:contains('School') div[value='0']")
        time.sleep(sleep_timer)
        self.click("//li[div/div/div[text()='ABC Corp Violin']]")
        time.sleep(sleep_timer)

        self.click("div[data-testid='stSelectbox']:contains('Tutor') div[value='0']")
        time.sleep(sleep_timer)
        self.click("//li[div/div/div[text()='abcviolinteacher']]")
        time.sleep(sleep_timer)
        self.click("button:contains('Assign Tutor')")
        time.sleep(sleep_timer)
        self.verify_registration_successful(
            f"Tutor {TEACHER_USERNAME} has been assigned to {school_name}")
        time.sleep(sleep_timer)




