import tempfile

import streamlit as st

from core.ListBuilder import ListBuilder
from core.ResourceDashboardBuilder import ResourceDashboardBuilder
from repositories.AssignmentRepository import AssignmentRepository
from repositories.ResourceRepository import ResourceRepository
from repositories.StorageRepository import StorageRepository
from repositories.TrackRepository import TrackRepository


class AssignmentDashboardBuilder:
    def __init__(self,
                 resource_repo: ResourceRepository,
                 track_repo: TrackRepository,
                 assignment_repo: AssignmentRepository,
                 storage_repo: StorageRepository,
                 resource_dashboard_builder: ResourceDashboardBuilder):
        self.resource_repo = resource_repo
        self.track_repo = track_repo
        self.assignment_repo = assignment_repo
        self.resource_dashboard_builder = resource_dashboard_builder
        self.storage_repo = storage_repo

    def assignments_dashboard(self, user_id):
        # Retrieve assignments for the specific user
        user_assignments = self.assignment_repo.get_assignments(user_id)
        if not user_assignments:
            st.info("No assignments available.")
            return

        # Loop through assignments and display them
        for assignment in user_assignments:
            st.markdown(f"""
                <h3 style='font-weight: bold; font-size: 20px; text-align: left; margin-bottom: 0;'>
                    {assignment['title']} - Due: {assignment['due_date'].strftime('%Y-%m-%d')}
                </h3>
                <hr style="height:2px;border-width:0;color:gray;background-color:gray;margin-top: 0;">
                """, unsafe_allow_html=True)
            st.write(assignment['description'])

            # Display assigned tracks with their own expanders and status updates
            assigned_tracks = self.assignment_repo.get_assigned_tracks(
                assignment['id'], user_id)
            for track in assigned_tracks:
                with st.expander(f"**Track**: {track['name']}"):
                    st.write(f"**Instructions**: {track['description']}")
                    # Add a button to load the audio track
                    if st.button(f"Load Track", key=f"load_{track['assignment_detail_id']}"):
                        # Assume self.storage_repo has a method to get the audio URL directly
                        audio_url = self.storage_repo.download_blob_by_url(track['track_path'])
                        st.audio(audio_url, format='audio/m4a')

                    self._display_status_update(track['assignment_detail_id'], user_id)

            # Display assigned resources with their own expanders and status updates
            assigned_resources = self.assignment_repo.get_assigned_resources(
                assignment['id'], user_id)
            for resource in assigned_resources:
                with st.expander(f"Resource: {resource['title']} - Details"):
                    st.write(f"Description: {resource['description']}")
                    if resource.get('link'):
                        st.markdown(f"[Watch the video]({resource['link']})")
                    self._display_status_update(resource['assignment_detail_id'], user_id)
            st.write("")

    def _display_status_update(self, assignment_detail_id, user_id):
        # Fetch current status from the database
        current_status = self.assignment_repo.get_detail_status(assignment_detail_id, user_id)

        # If there is no status yet for this detail, default to 'Not Started'
        current_status = current_status or 'Not Started'

        status_options = ["Not Started", "In Progress", "Completed"]
        new_status = st.selectbox(
            "Status",
            options=status_options,
            index=status_options.index(current_status),
            key=f"status_{assignment_detail_id}"
        )

        if st.button("Update Status", key=f"update_{assignment_detail_id}", type='primary'):
            self.assignment_repo.update_assignment_status_by_detail(user_id, assignment_detail_id, new_status)
            st.success(f"Status updated to {new_status}")