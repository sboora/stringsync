import base64
import os
import re
from datetime import datetime
import streamlit as st

from components.AvatarLoader import AvatarLoader
from enums.ActivityType import ActivityType
from repositories.MessageRepository import MessageRepository
from repositories.UserActivityRepository import UserActivityRepository


class MessageDashboard:
    def __init__(self, message_repo: MessageRepository,
                 user_activity_repo: UserActivityRepository,
                 avatar_loader: AvatarLoader):
        self.message_repo = message_repo
        self.user_activity_repo = user_activity_repo
        self.avatar_loader = avatar_loader

    def message_dashboard(self, user_id, group_id, session_id):
        # Message posting area
        with st.form("post_message", clear_on_submit=True):
            message_content = st.text_area("Share an update with your team:", height=150)
            submit_message = st.form_submit_button("Post Message 🚀")

            if submit_message and message_content:
                self.message_repo.post_message(user_id, group_id, message_content)
                additional_params = {
                    "group_id": group_id,
                }
                self.user_activity_repo.log_activity(
                    user_id, session_id, ActivityType.POST_MESSAGE, additional_params)
                st.success("Your message has been posted 🌟")
                st.rerun()

        # Display messages
        with st.spinner("Please wait.."):
            messages = self.message_repo.get_messages_by_group(group_id)
            for message in messages:
                timestamp = message['timestamp'].strftime('%-I:%M %p | %b %d') \
                    if isinstance(message['timestamp'], datetime) else message['timestamp']
                # Make URLs in the message content clickable
                content_with_links = re.sub(
                    r'(https?://\S+)', r'<a href="\1" target="_blank">\1</a>', message['content']
                )

                content_with_links = content_with_links.replace("\n", "<br>")
                sender_name = message['sender_name']
                avatar_name = message.get('avatar_name', 'avatar 10')
                avatar_file_path = self.avatar_loader.get_avatar(avatar_name) \
                    if avatar_name else 'path_to_default_avatar'

                # Check if the avatar file exists, else use a default image
                if avatar_file_path and os.path.isfile(avatar_file_path):
                    with open(avatar_file_path, "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read()).decode()
                else:
                    # Use a default base64 encoded string for a placeholder image
                    encoded_string = 'base64_string_of_a_default_placeholder_avatar'

                # Embed the base64 string into the HTML image tag
                avatar_image_html = f'<img src="data:image/png;base64,{encoded_string}" alt="avatar" style="width: 60px; ' \
                                    f'height: 60px; border-radius: 50%; margin-right: 10px;"> '

                st.markdown(f"""
                    <div style='display: flex; align-items: center; background-color: #E8F4FA; border-radius: 10px; padding: 10px; margin-bottom: 5px;'>
                        {avatar_image_html}
                        <div>
                            <p style='color: #4F8BF9; font-weight: bold; margin: 0;'>{sender_name}</p>
                            <p style='margin: 0;'>{content_with_links}</p>
                            <p style='color: #6C757D; font-size: 0.8em; margin-top: 5px;'>{timestamp}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

