import time

import streamlit as st

from enums.ActivityType import ActivityType


class NotificationsDashboardBuilder:
    def __init__(self, user_session_repo, portal_repo):
        self.user_session_repo = user_session_repo
        self.portal_repo = portal_repo

    def notify(self, user_id, group_id, session_id):
        # Assume get_last_activity_time is a method that retrieves the last activity timestamp
        last_activity_time = self.user_session_repo.get_last_activity_time(session_id)

        # Fetch new notifications since the last activity time
        notifications = self.portal_repo.get_notifications(user_id, group_id, last_activity_time)

        # Display each notification
        for notification in notifications:
            # Get the user-friendly message and icon for the activity type
            activity_type = ActivityType.from_value(notification['activity_type'])
            activity_message = activity_type.message
            activity_icon = activity_type.icon

            # Construct the display message
            message = f"{activity_icon} {notification['user_name']} {activity_message}"

            # Display the message with an icon
            st.toast(message)


