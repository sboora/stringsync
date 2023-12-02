import base64
import os

from core.AvatarLoader import AvatarLoader
from core.BadgeAwarder import BadgeAwarder
from enums.TimeFrame import TimeFrame
from repositories.PortalRepository import PortalRepository
import streamlit as st


class HallOfFameDashboardBuilder:
    def __init__(self,
                 portal_repo: PortalRepository,
                 badge_awarder: BadgeAwarder,
                 avatar_loader: AvatarLoader):
        self.portal_repo = portal_repo
        self.badge_awarder = badge_awarder
        self.avatar_loader = avatar_loader

    def show_winners(self, group_id, timeframe):
        # Mapping of timeframes to badge types
        timeframe_to_badge_type = {
            TimeFrame.PREVIOUS_WEEK: 'Weekly',
            TimeFrame.CURRENT_WEEK: 'Weekly',
            TimeFrame.PREVIOUS_MONTH: 'Monthly',
            TimeFrame.CURRENT_MONTH: 'Monthly',
            TimeFrame.PREVIOUS_YEAR: 'Yearly',
            TimeFrame.CURRENT_YEAR: 'Yearly'
        }

        # Determine the badge type based on the timeframe
        badge_type = timeframe_to_badge_type.get(timeframe)

        start_date, end_date = timeframe.get_date_range()
        formatted_start_date = self.ordinal(int(start_date.strftime('%d'))) + start_date.strftime(' %b, %Y')
        formatted_end_date = self.ordinal(int(end_date.strftime('%d'))) + end_date.strftime(' %b, %Y')

        # Get the winners from the repository based on the specified timeframe
        winners = self.portal_repo.get_winners(group_id, timeframe)

        # Create a divider line
        divider = "<hr style='height:1px; margin-top: 0; border-width:0; background: lightblue;'>"

        # Check if there are any winners
        if winners:
            st.markdown(
                f"<div style='padding-top:5px;color:#287DAD;font-size:22px;text-align:center'>"
                f"<b>{badge_type} Hall of Fame : {formatted_start_date} to {formatted_end_date}</b>",
                unsafe_allow_html=True)
            st.write("")

            # Create a dictionary to store winners by badge
            winners_by_badge = {}

            # Group winners by badge
            for winner in winners:
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
            col1, col2, col3, col4, col5 = st.columns(5)

            # Keep track of the number of badges processed
            badge_count = 0

            # Iterate through badges and display the winners
            for badge, winners in winners_by_badge.items():
                # Decide in which column to place the badge based on the count
                col = col1
                if badge_count % 5 == 1:
                    col = col2
                elif badge_count % 5 == 2:
                    col = col3
                elif badge_count % 5 == 3:
                    col = col4
                elif badge_count % 5 == 4:
                    col = col5

                # Using the chosen column, display the badge and the winners
                with col:
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
                        f"<div style='padding-top:0px;padding-left:20px;color:black;font-size:18px;'> {''.join(winners_with_avatars)}</div>",
                        unsafe_allow_html=True
                    )
                # Increment the badge count
                badge_count += 1

            st.write("")

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

    @staticmethod
    def ordinal(n):
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
        if 11 <= (n % 100) <= 13:
            suffix = 'th'
        return str(n) + suffix