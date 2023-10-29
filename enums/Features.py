from enum import Enum


class Features(Enum):
    STUDENT_PORTAL_SHOW_USER_ACTIVITY = "Show Student Activity"
    STUDENT_PORTAL_SHOW_USER_SESSIONS = "Show Student Sessions"
    STUDENT_PORTAL_SHOW_PROGRESS_STATS_CHART = "Show Student Progress Statistics Chart"
    STUDENT_PORTAL_SHOW_RECORDING_STATS_CHART = "Show Student Recording Statistics Chart"
    ADMIN_PORTAL_SHOW_USER_ACTIVITY = "Show Admin Activity"
    ADMIN_PORTAL_SHOW_USER_SESSIONS = "Show Admin Sessions"
    TEACHER_PORTAL_SHOW_USER_ACTIVITY = "Show Teacher Activity"
    TEACHER_PORTAL_SHOW_USER_SESSIONS = "Show Teacher Sessions"
    ADMIN_PORTAL_SETTINGS = "Admin Portal Settings"
    TEACHER_PORTAL_SETTINGS = "Teacher Portal Settings"
    STUDENT_PORTAL_SETTINGS = "Student Portal Settings"
