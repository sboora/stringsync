import re
import time

from PortalTestBase import PortalTestBase
from config import TEACHER_USERNAME, TEACHER_PASSWORD, TRACKS_INFO


class TeacherPortalTest(PortalTestBase):

    @staticmethod
    def get_url():
        return "http://localhost:8503/"

    def get_username(self):
        return TEACHER_USERNAME

    def get_password(self):
        return TEACHER_PASSWORD

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

    def check_tabs(self):
        self.click("button:contains('Create Team')")
        self.delay()
        self.click("button:contains('List Teams')")
        self.delay()
        self.click("button:contains('Students')")
        self.delay()
        self.click("button:contains('Assign Students to Teams')")
        self.delay()
        self.click("button:contains('Create Track')")
        self.delay()
        self.click("button:contains('List Tracks')")
        self.delay()
        self.click("button:contains('Remove Track')")
        self.delay()
        self.click("button:contains('Recordings')")
        self.delay()
        self.click("button:contains('Submissions')")
        self.delay()
        self.click("button:contains('Settings')")
        self.delay()

    def create_tracks(self):
        self.click("button[id^='tabs-'][id$='-tab-4']")
        self.delay()

        # Upload all tracks
        for track_info in TRACKS_INFO:
            # Upload the track file
            self.choose_file('section[aria-label="Choose an audio file"] input[type="file"]', track_info["track_path"])
            self.delay()

            # Upload the reference track file
            self.choose_file('section[aria-label="Choose a reference audio file"] input[type="file"]',
                             track_info["ref_path"])
            self.delay()

            # Type the track name
            self.type("input[aria-label='Track Name']", track_info["name"])
            self.delay()

            # Type the description
            self.type("input[aria-label='Description']", track_info["description"])
            self.delay()

            self.click("div[data-testid='stSelectbox']:contains('Ragam') div[value='0']")
            self.click("//li[div/div/div[text()='Shankarabharanam']]")
            self.delay()

            # Submit the track information
            self.click("button:contains('Submit')")
            time.sleep(5)

    def get_join_code(self):
        self.click("button[id^='tabs-'][id$='-tab-2']")
        self.delay()

        html_source = self.get_page_source()

        # Define the pattern to search for
        pattern = r"Please ask new members to join the team using join code: (\w+)"

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

    @staticmethod
    def write_join_code_to_config(join_code):
        # Define the path to your config file
        config_path = 'config.py'

        # This is the line format that will be written to tenant_config.py
        join_code_line = f'JOIN_CODE = "{join_code}"\n'

        # Read the current content of the file
        with open(config_path, 'r') as file:
            lines = file.readlines()

        # Check if JOIN_CODE line already exists and update it
        updated = False
        for i, line in enumerate(lines):
            if line.startswith('JOIN_CODE'):
                lines[i] = join_code_line
                updated = True
                break

        # If JOIN_CODE line doesn't exist, append it
        if not updated:
            lines.append(join_code_line)

        # Write the updated content back to the file
        with open(config_path, 'w') as file:
            file.writelines(lines)

    def get_test_flow_methods(self):
        return [
            self.check_tabs,
            self.create_tracks,
            self.get_join_code,
        ]

    def test_flow(self):
        self.flow()




