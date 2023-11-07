import time

from PortalTestBase import PortalTestBase
from config import ADMIN_USERNAME, ADMIN_PASSWORD, SCHOOLS, TUTORS, \
     SCHOOL_TUTOR_ASSIGNMENTS


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

    def register_schools(self):
        for school in SCHOOLS:
            self.find_input_and_type("input[aria-label='School']", school['name'])
            self.delay()
            self.find_input_and_type("input[aria-label='Description']", school['description'])
            self.delay()
            self.click_button("button:contains('Register School')")
            time.sleep(3)
            self.verify_registration_successful(f"School {school['name']} registered successfully")

    def list_schools(self):
        self.click("button[id^='tabs-'][id$='-tab-1']")
        self.delay()

    def register_tutors(self):
        for tutor in TUTORS:
            self.click("button[id^='tabs-'][id$='-tab-2']")
            self.delay()
            self.find_input_and_type("input[aria-label='Name']", tutor['name'])
            self.delay()
            self.find_input_and_type("input[aria-label='Username']", tutor['username'])
            self.delay()
            self.find_input_and_type("input[aria-label='Email']", tutor['email'])
            self.delay()
            self.find_input_and_type("input[aria-label='Password']", tutor['password'])
            self.delay()
            self.click("button:contains('Register Tutor')")
            self.delay()
            self.verify_registration_successful(
                f"User {tutor['username']} with email {tutor['email']} registered successfully as teacher.")
            self.delay()

    def list_tutors(self):
        self.click("button[id^='tabs-'][id$='-tab-3']")
        self.delay()

    def assign_tutors_to_schools(self):
        for assignment in SCHOOL_TUTOR_ASSIGNMENTS:
            self.click("button[id^='tabs-'][id$='-tab-4']")
            self.delay()
            # Select the school from the dropdown
            self.click("div[data-testid='stSelectbox']:contains('School') div[value='0']")
            self.delay()
            self.click(f"//li[div/div/div[text()='{assignment['school_name']}']]")
            self.delay()

            # Select the tutor from the dropdown
            tutor_info = next((tutor for tutor in TUTORS if tutor['username'] == assignment['tutor_username']), None)
            if tutor_info:
                self.click("div[data-testid='stSelectbox']:contains('Tutor') div[value='0']")
                self.delay()
                self.click(f"//li[div/div/div[text()='{tutor_info['username']}']]")
                self.click("button:contains('Assign Tutor')")
                self.delay()
                self.verify_registration_successful(
                    f"Tutor {tutor_info['username']} has been assigned to {assignment['school_name']}")
                self.delay()
            else:
                print(f"No tutor found with username {assignment['tutor_username']}")

    def get_test_flow_methods(self):
        return [
            self.register_schools,
            self.list_schools,
            self.register_tutors,
            self.list_tutors,
            self.assign_tutors_to_schools
        ]

    def test_flow(self):
        self.flow()



