import base64
import json
import time

import streamlit as st

from enums.ActivityType import ActivityType


class NotificationsDashboardBuilder:
    def __init__(self, user_session_repo, portal_repo):
        self.user_session_repo = user_session_repo
        self.portal_repo = portal_repo

    def notify(self, user_id, group_id, last_activity_time):
        # Fetch new notifications since the last activity time
        notifications = self.portal_repo.get_notifications(user_id, group_id, last_activity_time)

        # Display each notification
        messages = []
        for notification in notifications:
            metadata = json.loads(notification.get('metadata', '{}'))
            # If metadata contains a user_id, skip if it doesn't match the current user_id
            if 'user_id' in metadata and metadata['user_id'] != user_id:
                continue

            # Get the user-friendly message and icon for the activity type
            activity_type = ActivityType.from_value(notification['activity_type'])
            activity_message = activity_type.message
            activity_icon = activity_type.icon

            # Construct the display message
            message = f"{activity_icon} {notification['user_name']} {activity_message}"
            messages.append(message)

        return messages



