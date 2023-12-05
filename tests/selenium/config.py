# config.py
ROOT_USERNAME = "root"
ROOT_PASSWORD = "Pass1234!"
TENANT_NAME = "ABCD Corp"
TENANT_DESCRIPTION = "ABCD Corporation of Music & Dance"
TENANT_ADDRESS = "708 Roseum Ct, San Ramon, CA, 94582"
TENANT_EMAIL = "abcdcorp@gmail.com"
ADMIN_USERNAME = "abcdcorp-admin"
ADMIN_PASSWORD = "Admin1234!"
TEACHER_USERNAME = "abcdviolinteacher"
TEACHER_PASSWORD = "Violin1234"

SCHOOL = {
    'name': 'ABCD Corp Violin',
    'description': 'ABCD Corp Violin School',
    'join_code': 'Y6R4BF',
}

TUTOR = {
    'name': 'ABCD Corp Violin Teacher',
    'username': 'abcdviolinteacher',
    'email': 'abcdviolinteacher@gmail.com',
    'password': 'Violin1234'
}

SCHOOL_TUTOR_ASSIGNMENT = {
    'school_name': 'ABCD Corp Violin',
    'tutor_username': 'abcdviolinteacher',
}

# A list of dictionaries for each track with its details
TRACKS_INFO = [
    {
        "track_path": "/Users/csubramanian/Documents/streamlit/stringsync/tracks/worksheet_1_lesson_1.m4a",
        "ref_path": "/Users/csubramanian/Documents/streamlit/stringsync/tracks/worksheet_1_lesson_1_ref.m4a",
        "name": "Lesson 1",
        "description": "Sarali 1",
        "ragam": "Shankarabharanam"
    },
    {
        "track_path": "/Users/csubramanian/Documents/streamlit/stringsync/tracks/worksheet_1_lesson_2.m4a",
        "ref_path": "/Users/csubramanian/Documents/streamlit/stringsync/tracks/worksheet_1_lesson_2_ref.m4a",
        "name": "Lesson 2",
        "description": "Sarali 2",
        "ragam": "Shankarabharanam"
    },
]

STUDENTS = [
    {
        'name': 'abcdcorpstudent-1',
        'email': 'abcdcorpstudent-1@gmail.com',
        'username': 'abcdcorpstudent-1',
        'password': 'Pass1234',
    },
    {
        'name': 'abcdcorpstudent-2',
        'email': 'abcdcorpstudent-2@gmail.com',
        'username': 'abcdcorpstudent-2',
        'password': 'Pass1234',
    },
]

TEAMS = ['Pitch Pioneers', 'Scale Spartans']

STUDENT_TEAM_ASSIGNMENTS = [
    {
        'student_username': 'abcdcorpstudent-1',
        'teamname': 'Pitch Pioneers',
    },
    {
        'student_username': 'abcdcorpstudent-2',
        'teamname': 'Pitch Pioneers',
    },
]

TRACK_NAME = "Lesson 1"
RECORDING_PATH = "/student recordings/R off.m4a"



