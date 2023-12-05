import time

from PortalTestBase import PortalTestBase
from config import STUDENTS, SCHOOL, RECORDINGS


class StudentPortalTest(PortalTestBase):
    user = ""
    email = ""
    username = ""
    password = ""

    @staticmethod
    def get_url():
        return "http://localhost:8504/"

    def get_username(self):
        return self.username

    def get_password(self):
        return self.password

    def verify_registration_successful(self, text):
        self.assert_text_present(text)

    def record(self):
        value = 0
        for recording in RECORDINGS:
            self.click(f"div[data-testid='stSelectbox']:contains('Select a Track') div[value='{value}']")
            self.click(f"//li[div/div/div[text()='{recording['track_name']}']]")
            self.delay(5)
            self.choose_file('section[aria-label="Choose an audio file"] input[type="file"]', recording['recording_path'])
            self.delay(3)
            # Submit the recording
            self.click("button:contains('Upload')")
            self.delay(7)
            if recording['track_name'] == 'Lesson 1':
                value = 1
            elif recording['track_name'] == 'Lesson 2':
                value = 2

    def submissions(self):
        self.click("button[id^='tabs-'][id$='-tab-1']")
        self.delay()
        self.click_button("button:contains('Load Submissions')")
        self.sleep(5)

    def register_student(self):
        self.open_login_page(self.get_url())
        self.delay(3)
        self.click_button("button:contains('Register')")
        self.delay(3)
        self.find_input_and_type("input[aria-label='Name']", self.user)
        self.delay()
        self.find_input_and_type("input[aria-label='Email']", self.email)
        self.delay()
        self.find_input_and_type("input[aria-label='User']", self.username)
        self.delay()
        self.find_input_and_type("input[aria-label='Password']", self.password)
        self.delay()
        self.find_input_and_type("input[aria-label='Confirm Password']", self.password)
        self.delay()
        self.find_input_and_type("input[aria-label='Join Code']", SCHOOL['join_code'])
        self.delay(3)
        self.click_button("button:contains('Submit')")
        self.delay(1)
        self.verify_registration_successful(f"User {self.username} with email {self.email} registered successfully as "
                                            f"student.")

    def get_test_flow_methods(self):
        return [
            self.record,
            self.submissions
        ]

    def test_flow(self):
        for student in STUDENTS:
            self.user = student['name']
            self.email = student['email']
            self.username = student['username']
            self.password = student['password']
            self.register_student()
            self.flow()



