from abc import ABC

from portals.BasePortal import BasePortal
from repositories.RecordingRepository import RecordingRepository
from repositories.StorageRepository import StorageRepository
from repositories.TrackRepository import TrackRepository
import streamlit as st
import pandas as pd

from enums.UserType import UserType


class TeacherPortal(BasePortal, ABC):
    def __init__(self):
        super().__init__()
        self.recording_repo = RecordingRepository()
        self.storage_repo = StorageRepository("stringsync")
        self.track_repo = TrackRepository()

    def get_tab_dict(self):
        return {
            "👥 Create Group": self.create_group,
            "🔀 Assign Students to Groups": self.assign_students_to_group,
            "🎵 List Recordings": self.list_recordings
        }

    def show_introduction(self):
        st.write("""
            ### Welcome to the **Teacher Dashboard**!!

            **Your Comprehensive Dashboard for Music Education Management**

            This portal is designed to provide a centralized platform for seamless administration of your music classes. Here are the core functionalities you can leverage:
            - 👥 **Create Group**: Create groups to manage your students more efficiently.
            - 🔀 **Assign Students to Groups**: Assign students to specific groups for better management.
            - 🎵 **List Recordings**: View and manage recordings submitted by your students.

            Navigate through the tabs to perform these operations and more. Your effective management is just a few clicks away.
        """)

    def assign_students_to_group(self):
        # Feature to assign a user to a group
        groups = self.user_repo.get_all_groups()
        group_options = {group['group_name']: group['group_id'] for group in groups}
        users = self.user_repo.get_users_by_org_id_and_type(self.get_org_id(), UserType.STUDENT.value)
        user_options = {user['username']: user['id'] for user in users}

        selected_username = st.selectbox("Select a student:", ['--Select a student--'] + list(user_options.keys()))
        if selected_username != '--Select a student--':
            selected_user_id = user_options[selected_username]

            # Get the current group of the user
            current_group = self.user_repo.get_group_by_user_id(selected_user_id)
            current_group_name = current_group['group_name'] if current_group else '--Select a group--'

            # Dropdown to assign a new group, with the current group pre-selected
            assign_to_group = st.selectbox("Assign to group:", ['--Select a group--'] + list(group_options.keys()),
                                           index=list(group_options.keys()).index(
                                               current_group_name) + 1 if current_group else 0)

            if assign_to_group != '--Select a group--' and assign_to_group != current_group_name:
                self.user_repo.assign_user_to_group(selected_user_id, group_options[assign_to_group])
                st.success(f"User '{selected_username}' assigned to group '{assign_to_group}'.")

    def create_group(self):
        # Feature to create a new group
        group_name = st.text_input("Create a new group:")
        if st.button("Create Group", type='primary'):
            if group_name:
                success, message = self.user_repo.create_user_group(group_name, self.get_org_id())
                if success:
                    st.success(message)
                else:
                    st.error(message)
            else:
                st.warning("Group name cannot be empty.")

    def list_students_and_tracks(self):
        st.header("Students")

        # Show groups in a dropdown
        groups = self.user_repo.get_all_groups()
        group_options = {group['group_name']: group['group_id'] for group in groups}
        selected_group_name = st.selectbox("Select a group:", ['--Select a group--'] + list(group_options.keys()))

        # Filter users by the selected group
        if selected_group_name != '--Select a group--':
            selected_group_id = group_options[selected_group_name]
            users = self.user_repo.get_users_by_group(selected_group_id)
        else:
            users = self.user_repo.get_users_by_org_id_and_type(self.get_org_id(), UserType.STUDENT.value)

        user_options = {user['username']: user['id'] for user in users}
        options = ['--Select a student--'] + list(user_options.keys())
        selected_username = st.selectbox("Select a student to view their recordings:", options)

        selected_user_id = None
        if selected_username != '--Select a student--':
            selected_user_id = user_options[selected_username]

        selected_track_id = None
        track_path = None
        if selected_user_id is not None:
            recording_repository = RecordingRepository()
            track_ids = recording_repository.get_unique_tracks_by_user(selected_user_id)

            if track_ids:
                # Fetch track names by their IDs
                track_names = self.track_repo.get_track_names_by_ids(track_ids)

                # Create a mapping for the dropdown
                track_options = {track_names[id]: id for id in track_ids}

                selected_track_name = st.selectbox("Select a track:",
                                                   ['--Select a track--'] + list(track_options.keys()))
                if selected_track_name != '--Select a track--':
                    selected_track_id = track_options[selected_track_name]
                    track = self.track_repo.get_track_by_name(selected_track_name)
                    track_path = track[2]

        return selected_username, selected_user_id, selected_track_id, track_path

    @staticmethod
    def display_track_files(track_file):
        """
        Display the teacher's track files.

        Parameters:
            track_file (str): The path to the track file.
        """
        if track_file is None:
            return

        st.write("")
        st.write("")
        st.audio(track_file, format='core/m4a')

    def list_recordings(self):
        username, user_id, track_id, track_name = self.list_students_and_tracks()
        self.display_track_files(track_name)
        if user_id is None:
            return

        if user_id is None or track_id is None:
            return

        recordings = self.recording_repo.get_recordings_by_user_id_and_track_id(user_id, track_id)
        if not recordings:
            st.write("No recordings found.")
            return

        # Create a DataFrame to hold the recording data
        df = pd.DataFrame(recordings)

        # Create a table header
        header_html = """
            <div style='background-color:lightgrey;padding:5px;border-radius:3px;border:1px solid black;'>
                <div style='display:inline-block;width:28%;text-align:center;'>
                    <p style='color:black;margin:0;font-size:15px;font-weight:bold;'>Track</p>
                </div>
                <div style='display:inline-block;width:8%;text-align:left;'>
                    <p style='color:black;margin:0;font-size:15px;font-weight:bold;'>Score</p>
                </div>
                <div style='display:inline-block;width:24%;text-align:left;'>
                    <p style='color:black;margin:0;font-size:15px;font-weight:bold;'>Analysis</p>
                </div>
                <div style='display:inline-block;width:24%;text-align:left;'>
                    <p style='color:black;margin:0;font-size:15px;font-weight:bold;'>Remarks</p>
                </div>
                <div style='display:inline-block;width:10%;text-align:left;'>
                    <p style='color:black;margin:0;font-size:15px;font-weight:bold;'>Time</p>
                </div>
            </div>
            """
        st.markdown(header_html, unsafe_allow_html=True)

        # Initialize session_state if it doesn't exist
        if 'editable_states' not in st.session_state:
            st.session_state["editable_states"] = {}

        # Loop through each recording and create a table row
        for index, recording in df.iterrows():
            col1, col2, col3, col4, col5 = st.columns([3.5, 1, 3, 3, 2])

            if recording['blob_url']:
                filename = self.storage_repo.download_blob(recording['blob_name'])
                col1.audio(filename, format='core/m4a')
            else:
                col1.write("No core data available.")

            # Use Markdown to make the text black and larger
            col2.markdown(f"<div style='padding-top:10px;color:black;font-size:14px;'>{recording['score']}</div>",
                          unsafe_allow_html=True)
            col3.markdown(
                f"<div style='padding-top:5px;color:black;font-size:14px;'>{recording.get('analysis', 'N/A')}</div>",
                unsafe_allow_html=True)

            # Check if the remarks are editable
            is_editable = st.session_state["editable_states"].get(recording['id'], False)

            if is_editable:
                # Show an editable text box without a label
                new_remarks = col4.text_input("", recording.get('remarks', 'N/A'))

                if col4.button("Save", type="primary"):
                    self.recording_repo.update_remarks(recording['id'], new_remarks)
                    st.session_state["editable_states"][recording['id']] = False  # Turn off editable state
                    st.rerun()
            else:
                # Show the remarks as markdown
                col4.markdown(
                    f"<div style='padding-top:5px;color:black;font-size:14px;'>{recording.get('remarks', 'N/A')}</div>",
                    unsafe_allow_html=True)

                # Show an edit icon next to the remarks
                if col4.button("✏️", key=f"edit_{recording['id']}"):
                    st.session_state["editable_states"][recording['id']] = True  # Turn on editable state
                    st.rerun()

            formatted_timestamp = recording['timestamp'].strftime('%I:%M %p, ') + self.ordinal(
                int(recording['timestamp'].strftime('%d'))) + recording['timestamp'].strftime(' %b, %Y')
            col5.markdown(f"<div style='padding-top:5px;color:black;font-size:14px;'>{formatted_timestamp}</div>",
                          unsafe_allow_html=True)

    @staticmethod
    def ordinal(n):
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
        if 11 <= (n % 100) <= 13:
            suffix = 'th'
        return str(n) + suffix
