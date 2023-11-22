import base64
import os

from core.AvatarLoader import AvatarLoader
from core.BadgeAwarder import BadgeAwarder
from core.ListBuilder import ListBuilder
from enums.TimeFrame import TimeFrame
from repositories.PortalRepository import PortalRepository
from repositories.UserAchievementRepository import UserAchievementRepository
import streamlit as st


class TeamDashboardBuilder:
    def __init__(self,
                 portal_repo: PortalRepository,
                 user_achievement_repo: UserAchievementRepository,
                 badge_awarder: BadgeAwarder,
                 avatar_loader: AvatarLoader):
        self.portal_repo = portal_repo
        self.user_achievement_repo = user_achievement_repo
        self.badge_awarder = badge_awarder
        self.avatar_loader = avatar_loader

    def team_dashboard(self, group_id):
        with st.spinner("Please wait.."):
            self.show_last_week_winners(group_id)
            st.write("")
            options = [time_frame for time_frame in TimeFrame]

            # Find the index for 'CURRENT_WEEK' to set as default
            default_index = next((i for i, time_frame in enumerate(TimeFrame)
                                  if time_frame == TimeFrame.CURRENT_WEEK), 0)

            # Create the select box with the default set to 'Current Week'
            time_frame_selected = st.selectbox(
                'Select a time frame:',
                options,
                index=default_index,
                format_func=lambda x: x.value
            )

            # Fetch the dashboard data for the selected time frame
            dashboard_data = self.portal_repo.fetch_team_dashboard_data(
                group_id, time_frame_selected)

            column_widths = [1.5, 11, 12.5, 12.5, 12.5, 12.5, 13, 14, 10.5]
            list_builder = ListBuilder(column_widths)
            list_builder.build_header(
                column_names=["", "Teammate", "Unique Tracks", "Recordings",
                              "Badges Earned", "Recording Minutes", "Practice Minutes",
                              "Score", "Badges"])

            # Display each team and its member count in a row
            for data in dashboard_data:
                user_id = data['user_id']
                badges = self.user_achievement_repo.get_user_badges(user_id, time_frame_selected)
                avatar = data.get('avatar')
                avatar_file_path = self.avatar_loader.get_avatar(avatar) if avatar else None

                # If an avatar file path is provided and the file exists
                avatar_image_html = ""
                if avatar_file_path and os.path.isfile(avatar_file_path):
                    with open(avatar_file_path, "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read()).decode()
                    avatar_image_html = f'<img src="data:image/png;base64,{encoded_string}" alt="avatar" style="width: ' \
                                        f'60px; height: 60px; border-radius: 50%; margin-right: 10px;"> '

                divider = "<hr style='height:1px; margin-top: 0; border-width:0; background: lightblue;'>"
                with st.container():
                    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1, 1, 1, 1, 1, 1, 1, 1])
                    col1.markdown(f"<div style='display: flex; align-items: center;'>{avatar_image_html}<span "
                                  f"style='padding-top:5px;color:black;font-size:14px;'>{data['teammate']}</span></div>",
                                  unsafe_allow_html=True)
                    col2.write("")
                    col2.markdown(
                        f"<div style='padding-top:8px;color:black;font-size:14px;'>{data['unique_tracks']}</div>",
                        unsafe_allow_html=True)
                    col3.write("")
                    col3.markdown(
                        f"<div style='padding-top:5px;color:black;font-size:14px;'>{data['recordings']}</div>",
                        unsafe_allow_html=True)
                    col4.write("")
                    col4.markdown(
                        f"<div style='padding-top:5px;color:black;font-size:14px;'>{data['badges_earned']}</div>",
                        unsafe_allow_html=True)
                    col5.write("")
                    col5.markdown(
                        f"<div style='padding-top:5px;color:black;font-size:14px;'>{data['recording_minutes']}</div>",
                        unsafe_allow_html=True)
                    col6.write("")
                    col6.markdown(
                        f"<div style='padding-top:5px;color:black;font-size:14px;'>{data['practice_minutes']}</div>",
                        unsafe_allow_html=True)
                    col7.write("")
                    col7.markdown(
                        f"<div style='padding-top:5px;color:black;font-size:14px;'>{data['score']}</div>",
                        unsafe_allow_html=True)
                    with col8:
                        st.write("")
                        cols = st.columns(3)
                        for i, badge in enumerate(badges):
                            with cols[i % 3]:
                                # Display the badge icon from the badge folder
                                st.image(self.badge_awarder.get_badge(badge), width=50)
                    st.write("")
                    st.markdown(f"{divider}", unsafe_allow_html=True)

    def show_last_week_winners(self, group_id):
        # Get the winners from the repository
        winners = self.portal_repo.get_weekly_winners(group_id)

        # Create a divider line
        divider = "<hr style='height:1px; margin-top: 0; border-width:0; background: lightblue;'>"

        # Check if there are any winners
        if winners:
            st.markdown(
                f"<div style='padding-top:5px;color:#287DAD;font-size:20px;text-align:left'><b>Congratulations</b> "
                f"to all the <b>Weekly Badge Winners!!!</b>",
                unsafe_allow_html=True)
            st.write("")

            # Create a dictionary to store winners by badge
            winners_by_badge = {}

            # Group winners by badge
            for winner in winners:
                student_name = winner['student_name']
                badge = winner['weekly_badge']
                avatar = winner['avatar']

                # Get the avatar image file path
                avatar_file_path = self.avatar_loader.get_avatar(
                    avatar) if avatar else 'path_to_default_avatar'

                # Convert the image to a base64 string for embedding
                encoded_string = self.get_avatar_base64_string(avatar_file_path)

                # Embed the base64 string into the HTML image tag
                avatar_image_html = f'<img src="data:image/png;base64,{encoded_string}" alt="avatar" style="width: ' \
                                    f'60px; height: 60px; border-radius: 50%; margin-right: 10px;"> '
                winner['avatar_image_html'] = avatar_image_html

                if badge not in winners_by_badge:
                    winners_by_badge[badge] = []

                winners_by_badge[badge].append(winner)

            # Create 3 columns with equal width
            col1, col2, col3 = st.columns(3)

            # Keep track of the number of badges processed
            badge_count = 0

            # Iterate through badges and display the winners
            for badge, winners in winners_by_badge.items():
                # Decide in which column to place the badge based on the count
                if badge_count % 6 < 3:
                    if badge_count % 3 == 0:
                        col = col1
                    elif badge_count % 3 == 1:
                        col = col2
                    else:
                        col = col3
                else:
                    if badge_count % 3 == 0:
                        col = col1
                    elif badge_count % 3 == 1:
                        col = col2
                    else:
                        col = col3

                # Using the chosen column, display the badge and the winners
                with col:
                    if badge_count % 6 >= 3:
                        col.write("")

                    col.image(self.badge_awarder.get_badge(badge), width=175)

                    # Add congratulatory emojis next to each winner's name
                    winners_with_avatars = []
                    for winner in winners:
                        # Get the winner's avatar and name
                        avatar_image_html = winner['avatar_image_html']
                        student_name = winner['student_name']
                        # Create a HTML snippet for each winner
                        winner_html = f"<span style='display: flex; align-items: center;'>{avatar_image_html}" \
                                      f"<span style='margin-left: 0px; font-size:14px'>{student_name} 🎉</span></span> "
                        winners_with_avatars.append(winner_html)

                    # Join the winners' HTML snippets with commas and display them
                    col.markdown(
                        f"<div style='padding-top:0px;color:black;font-size:18px;'> {''.join(winners_with_avatars)}</div>",
                        unsafe_allow_html=True
                    )
                # Increment the badge count
                badge_count += 1

            st.write("")
            st.markdown(f"{divider}", unsafe_allow_html=True)

    @staticmethod
    def get_avatar_base64_string(avatar_file_path):
        # Check if the avatar file exists, else use a default image
        if avatar_file_path and os.path.isfile(avatar_file_path):
            with open(avatar_file_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
        else:
            # Use a default base64 encoded string for a placeholder image
            encoded_string = 'base64_string_of_a_default_placeholder_avatar'
        return encoded_string
