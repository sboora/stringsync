from core.BadgeAwarder import BadgeAwarder
from core.ListBuilder import ListBuilder
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
        st.write("")
        dashboard_data = self.portal_repo.fetch_team_dashboard_data(group_id, 'week')

        column_widths = [14.28, 14.28, 14.28, 14.28, 14.28, 14.28, 14.28]
        list_builder = ListBuilder(column_widths)
        list_builder.build_header(
            column_names=["Teammate", "Unique Tracks", "Recordings",
                          "Badges Earned", "Practice Minutes", "Score", "Badges"])

        # Display each team and its member count in a row
        for data in dashboard_data:
            user_id = data['user_id']
            badges = self.user_achievement_repo.get_user_badges(user_id)
            divider = "<hr style='height:1px; margin-top: 0; border-width:0; background: lightblue;'>"
            with st.container():
                col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 1, 1, 1, 1, 1, 1])
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
                    f"<div style='padding-top:5px;color:black;font-size:14px;'>{data['practice_minutes']}</div>",
                    unsafe_allow_html=True)
                col6.write("")
                col6.markdown(
                    f"<div style='padding-top:5px;color:black;font-size:14px;'>{data['score']}</div>",
                    unsafe_allow_html=True)
                with col7:
                    st.write("")
                    cols = st.columns(5)
                    for i, badge in enumerate(badges):
                        with cols[i % 5]:
                            # Display the badge icon from the badge folder
                            st.image(self.badge_awarder.get_badge(badge), width=50)
                st.write("")
                st.markdown(f"{divider}", unsafe_allow_html=True)
