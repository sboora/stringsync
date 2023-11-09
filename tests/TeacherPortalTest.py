import time

from PortalTestBase import PortalTestBase
from config import TEACHER_USERNAME, TEACHER_PASSWORD, TRACKS, TEAMS, STUDENT_TEAM_ASSIGNMENTS


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
        self.assert_text_present("Team Assignments")
        self.assert_text_present("Create Track")
        self.assert_text_present("List Tracks")
        self.assert_text_present("Remove Track")
        self.assert_text_present("Recordings")
        self.assert_text_present("Submissions")

    def verify_registration_successful(self, text):
        self.assert_text_present(text)

    def check_tabs(self):
        self.click("button:contains('Create a Team')")
        self.delay()
        self.click("button:contains('List Teams')")
        self.delay()
        self.click("button:contains('Students')")
        self.delay()
        self.click("button:contains('Team Assignments')")
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

    def create_team(self):
        for team in TEAMS:
            self.click("button:contains('Create a Team')")
            self.delay()
            self.find_input_and_type("input[aria-label='Team Name']", team)
            self.delay(2)
            self.click("button:contains('Create Team')")
            self.delay(2)
            self.assert_text_present(f"Team {team} successfully created.")

    def assign_students_to_teams(self):
        self.click("button:contains('Team Assignments')")
        self.delay()
        for assignment in STUDENT_TEAM_ASSIGNMENTS:
            self.click("div[data-testid='stSelectbox']:contains('Select a Team') div[value='0']")
            self.delay()
            self.click(f"//li[div/div/div[text()='{assignment['teamname']}']]")
            self.delay(5)

    def create_tracks(self):
        self.click("button:contains('Create Track')")
        self.delay()

        # Upload all tracks
        for track in TRACKS:
            # Upload the track file
            self.choose_file('section[aria-label="Choose an audio file"] input[type="file"]', track["track_path"])
            self.delay()

            # Upload the reference track file
            self.choose_file('section[aria-label="Choose a reference audio file"] input[type="file"]',
                             track["ref_path"])
            self.delay()

            # Type the track name
            self.type("input[aria-label='Track Name']", track["name"])
            self.delay()

            # Type the description
            self.type("input[aria-label='Description']", track["description"])
            self.delay()

            self.click("div[data-testid='stSelectbox']:contains('Ragam') div[value='0']")
            self.click("//li[div/div/div[text()='Shankarabharanam']]")
            self.delay(2)

            # Submit the track information
            self.click("button:contains('Submit')")
            self.delay(5)

    def get_test_flow_methods(self):
        return [
            self.create_team,
            self.assign_students_to_teams,
            self.create_tracks,
        ]

    def test_flow(self):
        self.flow()




