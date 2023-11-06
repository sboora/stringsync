import time

import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from seleniumbase import BaseCase
from config import USERNAME, PASSWORD, TRACKS_INFO


class TeacherPortalTest(BaseCase):
    URL = "http://localhost:8503/"

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
        self.assert_page_title("Guru Shishya Teacher Portal")
        self.assert_text_present("Welcome to")
        self.assert_text_present("Teacher Portal")
        self.assert_text_present("Empowering Music Educators with Comprehensive Tools")
        self.assert_text_present("Create Team")
        self.assert_text_present("List Teams")
        self.assert_text_present("Students")
        self.assert_text_present("Assign Students to Teams")
        self.assert_text_present("Create Track")
        self.assert_text_present("List Tracks")
        self.assert_text_present("Remove Track")
        self.assert_text_present("Recordings")
        self.assert_text_present("Submissions")
        self.assert_text_present("Settings")

    def verify_registration_successful(self, text):
        self.assert_text_present(text)

    def login(self, sleep_timer):
        # Login
        self.open_login_page()
        time.sleep(sleep_timer)
        self.find_input_and_type("input[aria-label='Username']", USERNAME)
        time.sleep(sleep_timer)
        self.find_input_and_type("input[aria-label='Password']", PASSWORD)
        time.sleep(sleep_timer)
        self.click_button("button:contains('Login')")
        time.sleep(sleep_timer)
        self.verify_login_successful()
        time.sleep(sleep_timer)

    def check_tabs(self, sleep_timer):
        self.click("button:contains('Create Team')")
        time.sleep(sleep_timer)
        self.click("button:contains('List Teams')")
        time.sleep(sleep_timer)
        self.click("button:contains('Students')")
        time.sleep(sleep_timer)
        self.click("button:contains('Assign Students to Teams')")
        time.sleep(sleep_timer)
        self.click("button:contains('Create Track')")
        time.sleep(sleep_timer)
        self.click("button:contains('List Tracks')")
        time.sleep(sleep_timer)
        self.click("button:contains('Remove Track')")
        time.sleep(sleep_timer)
        self.click("button:contains('Recordings')")
        time.sleep(sleep_timer)
        self.click("button:contains('Submissions')")
        time.sleep(sleep_timer)
        self.click("button:contains('Settings')")
        time.sleep(sleep_timer)

    def upload_track(self, track_info, sleep_timer):
        # Upload the track file
        self.choose_file('section[aria-label="Choose an audio file"] input[type="file"]', track_info["track_path"])
        time.sleep(sleep_timer)

        # Upload the reference track file
        self.choose_file('section[aria-label="Choose a reference audio file"] input[type="file"]',
                         track_info["ref_path"])
        time.sleep(sleep_timer)

        # Type the track name
        self.type("input[aria-label='Track Name']", track_info["name"])
        time.sleep(sleep_timer)

        # Type the description
        self.type("input[aria-label='Description']", track_info["description"])
        time.sleep(sleep_timer)

        self.click("div[data-testid='stSelectbox']:contains('Ragam') div[value='0']")
        self.click("//li[div/div/div[text()='Shankarabharanam']]")
        time.sleep(sleep_timer)

        # Submit the track information
        self.click("button:contains('Submit')")
        time.sleep(5)

    def test_flow(self):
        sleep_timer = 0.5
        self.login(sleep_timer)
        self.check_tabs(sleep_timer)

        # Create track
        self.click("button[id^='tabs-'][id$='-tab-4']")
        time.sleep(sleep_timer)

        # Upload all tracks
        for track_info in TRACKS_INFO:
            self.upload_track(track_info, sleep_timer)


