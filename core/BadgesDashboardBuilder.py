import os

import streamlit as st

from enums.Settings import Settings
from repositories.SettingsRepository import SettingsRepository
from repositories.StorageRepository import StorageRepository
from repositories.UserAchievementRepository import UserAchievementRepository


class BadgesDashboardBuilder:
    def __init__(self,
                 settings_repo: SettingsRepository,
                 user_achievement_repo: UserAchievementRepository,
                 storage_repo: StorageRepository):
        self.settings_repo = settings_repo
        self.user_achievement_repo = user_achievement_repo
        self.storage_repo = storage_repo

    def badges_dashboard(self, org_id, user_id):
        with st.spinner("Please wait.."):
            badges = self.user_achievement_repo.get_user_badges(user_id)
            if badges:  # If there are badges
                cols = st.columns(5)
                for i, badge in enumerate(badges):
                    with cols[i % 5]:
                        # Display the badge icon from the badge folder
                        st.image(self.get_badge(badge), width=200)
            else:  # If there are no badges
                st.markdown("### No Badges Yet 🎖️")
                st.markdown("""
                    **What Can You Do to Earn Badges?**
        
                    1. **Listen to Tracks**: The more you listen, the more you learn.
                    2. **Record Performances**: Every recording earns you points towards your next badge.
                    3. **Keep Practicing**: The more points you earn, the more badges you unlock.
        
                    Start by listening to a track and making your first recording today!
                """)

            st.write("")
            self.divider()
            st.markdown(f"""
                <h2 style='text-align: center; color: {self.tab_heading_font_color(org_id)}; font-size: 24px;'>
                    🌟 Discover the Treasure Trove of Badges! 🌟
                </h2>
                <p style='text-align: center; color: {self.tab_heading_font_color(org_id)}; font-size: 18px;'>
                    🚀 Embark on an epic adventure and collect them all! 🚀
                </p>
                """, unsafe_allow_html=True)

            # Display all badges in columns
            badges_info = {
                "First Note": "Celebrate your start by uploading your first recording.",
                "2 Day Streak": "Keep the rhythm! Practice for 2 consecutive days.",
                "3 Day Streak": "Harmonize your week with a 3-day practice streak.",
                "5 Day Streak": "Show your dedication with a streak of practicing for 5 days.",
                "7 Day Streak": "Demonstrate your commitment with a full week of practice.",
                "10 Day Streak": "Set the bar high with a 10-day practice streak.",
                "Practice Champ": "Top the charts with the most practice minutes in a week, starting at a minimum of 75 "
                                  "minutes.",
                "Sound Sorcerer": "Cast a spell by recording the most minutes in a week, with a starting spell of 10 "
                                  "minutes.",
                "Recording Kingpin": "Rule the studio by making the most recordings in a week, starting at a minimum of 5 "
                                     "recordings.",
                "Melody Master": "Hit the high score by earning the most points in a week, starting at 40 points.",
                "Track Titan": "Be prolific! Record on the most number of different tracks in a week, starting at 3.",
                "Badge Baron": "Be the ultimate achiever by earning the highest variety of badges."
            }

            # Create columns for badges
            cols = st.columns(3)
            for index, (badge_name, badge_criteria) in enumerate(badges_info.items()):
                with cols[index % 3]:
                    st.markdown(f"### {badge_name}")
                    st.markdown(f"_{badge_criteria}_")
                    st.image(self.get_badge(badge_name), width=200)

    def get_badge(self, badge_name):
        # Directory where badges are stored locally
        local_badges_directory = 'badges'

        # Construct the local file path for the badge
        local_file_path = os.path.join(local_badges_directory, f"{badge_name}.png")

        # Check if the badge exists locally
        if os.path.exists(local_file_path):
            return local_file_path

        # If badge not found locally, attempt to download from remote
        remote_path = f"{self.get_badges_bucket()}/{badge_name}.png"
        success = self.storage_repo.download_blob_and_save(remote_path, local_file_path)

        if success:
            return local_file_path
        else:
            print(f"Failed to download badge named '{badge_name}' from remote location.")
            return None

    @staticmethod
    def get_badges_bucket():
        return 'badges'

    @staticmethod
    def divider(height=2):
        divider = f"<hr style='height:{height}px; margin-top: 0; border-width:0; background: lightblue;'>"
        st.markdown(f"{divider}", unsafe_allow_html=True)

    def tab_heading_font_color(self, org_id):
        self.settings_repo.get_setting(
            org_id, Settings.TAB_HEADING_FONT_COLOR)
