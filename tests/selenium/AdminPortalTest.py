import re
import time

from PortalTestBase import PortalTestBase
from config import ADMIN_USERNAME, ADMIN_PASSWORD, SCHOOL, TUTOR, SCHOOL_TUTOR_ASSIGNMENT


class AdminPortalTest(PortalTestBase):
    @staticmethod
    def get_url():
        return "http://localhost:8502/"

    def get_username(self):
        return ADMIN_USERNAME

    def get_password(self):
        return ADMIN_PASSWORD

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

    def register_school(self):
        self.find_input_and_type("input[aria-label='School']", SCHOOL['name'])
        self.delay()
        self.find_input_and_type("input[aria-label='Description']", SCHOOL['description'])
        self.delay()
        self.click_button("button:contains('Register School')")
        self.delay(5)
        self.get_join_code(SCHOOL['name'])

    def get_join_code(self, school):
        html_source = self.get_page_source()
        # Define the pattern to search for
        pattern = fr"School {school} registered successfully with join code: (\w+)."
        # Use regular expression to find the pattern
        match = re.search(pattern, html_source)
        if match:
            # If a match is found, return the join code
            join_code = match.group(1)
            self.write_join_code_to_config(join_code)
        else:
            # If no match is found, handle accordingly
            print('Join code not found.')
            return None

    def list_schools(self):
        self.click("button[id^='tabs-'][id$='-tab-1']")
        self.delay()

    def register_tutor(self):
        self.click("button[id^='tabs-'][id$='-tab-2']")
        self.delay()
        self.find_input_and_type("input[aria-label='Name']", TUTOR['name'])
        self.delay()
        self.find_input_and_type("input[aria-label='Username']", TUTOR['username'])
        self.delay()
        self.find_input_and_type("input[aria-label='Email']", TUTOR['email'])
        self.delay()
        self.find_input_and_type("input[aria-label='Password']", TUTOR['password'])
        self.delay()
        self.click("button:contains('Register Tutor')")
        self.delay(5)
        self.verify_registration_successful(
            f"User {TUTOR['username']} with email {TUTOR['email']} registered successfully as teacher.")
        self.delay()

    def list_tutors(self):
        self.click("button[id^='tabs-'][id$='-tab-3']")
        self.delay()

    def assign_tutors_to_schools(self):
        self.click("button[id^='tabs-'][id$='-tab-4']")
        self.delay()
        # Select the school from the dropdown
        self.click("div[data-testid='stSelectbox']:contains('School') div[value='0']")
        self.delay()
        self.click(f"//li[div/div/div[text()='{SCHOOL_TUTOR_ASSIGNMENT['school_name']}']]")
        self.delay()

        # Select the tutor from the dropdown
        tutor_info = TUTOR if TUTOR['username'] == SCHOOL_TUTOR_ASSIGNMENT['tutor_username'] else None
        if tutor_info:
            self.click("div[data-testid='stSelectbox']:contains('Tutor') div[value='0']")
            self.delay()
            self.click(f"//li[div/div/div[text()='{tutor_info['username']}']]")
            self.click("button:contains('Assign Tutor')")
            self.delay()
            self.verify_registration_successful(
                f"Tutor {tutor_info['username']} has been assigned to {SCHOOL_TUTOR_ASSIGNMENT['school_name']}")
            self.delay()
        else:
            print(f"No tutor found with username {SCHOOL_TUTOR_ASSIGNMENT['tutor_username']}")

    def get_test_flow_methods(self):
        return [
            self.register_school,
            self.list_schools,
            self.register_tutor,
            self.list_tutors,
            self.assign_tutors_to_schools
        ]

    def test_flow(self):
        self.flow()



