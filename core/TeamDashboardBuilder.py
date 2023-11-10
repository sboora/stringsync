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
                 badge_awarder: BadgeAwarder):
        self.portal_repo = portal_repo
        self.user_achievement_repo = user_achievement_repo
        self.badge_awarder = badge_awarder

    def team_dashboard(self, group_id):
        self.show_last_week_winners(group_id)
        st.write("")
        options = [time_frame for time_frame in TimeFrame]

        # Find the index for 'CURRENT_WEEK' to set as default
        default_index = next((i for i, time_frame in enumerate(TimeFrame) if time_frame == TimeFrame.CURRENT_WEEK), 0)

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

        column_widths = [12.5, 12.5, 12.5, 12.5, 12.5, 12.5, 12.5, 12.5]
        list_builder = ListBuilder(column_widths)
        list_builder.build_header(
            column_names=["Teammate", "Unique Tracks", "Recordings",
                          "Badges Earned", "Recording Minutes", "Practice Minutes",
                          "Score", "Badges"])

        # Display each team and its member count in a row
        for data in dashboard_data:
            user_id = data['user_id']
            badges = self.user_achievement_repo.get_user_badges(
                user_id, time_frame_selected)
            divider = "<hr style='height:1px; margin-top: 0; border-width:0; background: lightblue;'>"
            with st.container():
                col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1, 1, 1, 1, 1, 1, 1, 1])
                col1.write("")
                col1.markdown(
                    f"<div style='padding-top:5px;color:black;font-size:14px;'>{data['teammate']}</div>",
                    unsafe_allow_html=True)
                col2.write("")
                col2.markdown(
                    f"<div style='padding-top:8px;color:black;font-size:14px;'>{data['unique_tracks']}</div>",
                    unsafe_allow_html=True)
                col3.write("")
                col3.markdown(
                    f"<div style='padding-top:5px;color:black;font-size:14px;'>{data['unique_tracks']}</div>",
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
        print(winners)

        # Create a divider line
        divider = "<hr style='height:1px; margin-top: 0; border-width:0; background: lightblue;'>"

        # Check if there are any winners
        if winners:
            st.markdown(
                f"<div style='padding-top:5px;color:#5CB5D2;font-size:20px;'><b>Congratulations</b> "
                f"to all the <b>Weekly Badge Winners!!!</b>",
                unsafe_allow_html=True)
            st.write("")

            # Create a dictionary to store winners by badge
            winners_by_badge = {}

            # Group winners by badge
            for winner in winners:
                student_name = winner['student_name']
                badge = winner['weekly_badge']

                if badge not in winners_by_badge:
                    winners_by_badge[badge] = []

                winners_by_badge[badge].append(student_name)

            # Iterate through badges and display the winners
            for badge, student_names in winners_by_badge.items():
                with st.container():
                    col1, col2 = st.columns([1, 2])
                    col1.image(self.badge_awarder.get_badge(badge), width=100)
                    col2.write("")
                    col2.markdown(
                        f"<div style='padding-top:5px;color:black;font-size:18px;'><b>Winners:</b> {', '.join(student_names)}</div>",
                        unsafe_allow_html=True)

            st.write("")
            st.markdown(f"{divider}", unsafe_allow_html=True)
