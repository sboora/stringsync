# config.py
ROOT_USERNAME = "root"
ROOT_PASSWORD = "Pass1234!"
TENANT_NAME = "ABC Corp"
TENANT_DESCRIPTION = "ABC Corporation of Music & Dance"
TENANT_ADDRESS = "708 Roseum Ct, San Ramon, CA, 94582"
TENANT_EMAIL = "abccorp@gmail.com"
ADMIN_USERNAME = "abccorp-admin"
ADMIN_PASSWORD = "Admin1234!"
TEACHER_USERNAME = "abcviolinteacher"
TEACHER_PASSWORD = "Violin1234"

SCHOOLS = [
    {
        'name': 'ABC Corp Violin',
        'description': 'ABC Corp Violin School'
    },
]

TUTORS = [
    {
        'name': 'ABC Corp Violin Teacher',
        'username': 'abcviolinteacher',
        'email': 'abcviolinteacher@gmail.com',
        'password': 'Violin1234'
    },
]

SCHOOL_TUTOR_ASSIGNMENTS = [
    {
        'school_name': 'ABC Corp Violin',
        'tutor_username': 'abcviolinteacher',
    },
]

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

JOIN_CODE = "EJR08E"
