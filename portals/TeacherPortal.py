import hashlib
from abc import ABC

from core.AudioProcessor import AudioProcessor
from enums.Features import Features
from portals.BasePortal import BasePortal
import streamlit as st
import pandas as pd

from enums.UserType import UserType


class TeacherPortal(BasePortal, ABC):
    def __init__(self):
        super().__init__()
        self.audio_processor = AudioProcessor()

    def get_title(self):
        return f"{self.get_app_name()} Teacher Portal"

    def get_icon(self):
        return "🎶"

    def get_tab_dict(self):
        tab_dict = {
            "👥 Create Group": self.create_group,
            "👩‍🎓 Students": self.display_students,
            "🔀 Assign Students to Groups": self.assign_students_to_group,
            "🎵 Create Track": self.create_track,
            "🎵 Remove Track": self.remove_track,
            "🎵 Recordings": self.list_recordings,
            "📥 Submissions": self.list_submissions
        }

        if self.is_feature_enabled(Features.TEACHER_PORTAL_SHOW_USER_SESSIONS):
            tab_dict['Sessions'] = self.show_sessions_tab

        if self.is_feature_enabled(Features.TEACHER_PORTAL_SHOW_USER_ACTIVITY):
            tab_dict['Activities'] = self.show_user_activities_tab

        return tab_dict

    def show_introduction(self):
        st.write("""
            ### **Teacher Portal**

            **Empowering Music Educators with Comprehensive Tools**

            Dive into a platform tailored for the needs of progressive music educators. With the StringSync Teacher Portal, manage your classroom with precision and efficiency. Here's what you can do directly from the dashboard:
            - 👥 **Group Management**: Craft student groups for efficient class structures with the "Create Group" feature.
            - 👩‍🎓 **Student Overview**: Browse through your students' profiles and details under the "Students" tab.
            - 🔀 **Student Assignments**: Directly assign students to specific groups using the "Assign Students to Groups" functionality.
            - 🎵 **Track Creation**: Introduce new tracks for practice or teaching via the "Create Track" feature.
            - 🎵 **Recording Review**: Listen, evaluate, and manage student recordings under the "Recordings" tab.
            - 📥 **Submission Insights**: Monitor and manage student submissions through the "Submissions" section.

            Tap into the tabs, explore the features, and elevate your teaching methods. Together, let's redefine music education!
        """)

    def assign_students_to_group(self):
        # Feature to assign a user to a group
        groups = self.user_repo.get_all_groups()
        group_options = {group['group_name']: group['group_id'] for group in groups}
        users = self.user_repo.get_users_by_org_id_and_type(self.get_org_id(), UserType.STUDENT.value)
        user_options = {user['username']: user['id'] for user in users}

        selected_usernames = st.multiselect("Select students:", ['--Select a student--'] + list(user_options.keys()))

        # Check if the list is not empty and doesn't contain the placeholder
        if selected_usernames and '--Select a student--' not in selected_usernames:

            # Dropdown to assign a new group
            assign_to_group = st.selectbox("Assign to group:", ['--Select a group--'] + list(group_options.keys()))

            if assign_to_group != '--Select a group--':
                for selected_username in selected_usernames:
                    selected_user_id = user_options[selected_username]

                    # Get the current group of the user
                    current_group = self.user_repo.get_group_by_user_id(selected_user_id)
                    current_group_name = current_group['group_name'] if current_group else '--Select a group--'

                    if assign_to_group != current_group_name:
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

    def display_students(self):
        st.markdown("<h2 style='text-align: center; font-size: 20px;'>Student Details</h2>", unsafe_allow_html=True)

        # Assuming you have a method to get students assigned to you
        students = self.user_repo.get_users_by_org_id_and_type(self.get_org_id(), UserType.STUDENT.value)

        self.build_header(column_names=["Name", "Username", "Email", "Group"])

        for student_detail in students:
            row_data = {
                "Name": student_detail['name'],
                "Username": student_detail['username'],
                "Email": student_detail['email'],
                "Group": student_detail['group_name'],
            }
            self.build_row(row_data)

    def create_track(self):
        with st.form(key='create_track_form'):
            track_name = st.text_input("Track Name")
            track_file = st.file_uploader("Choose an audio file", type=["m4a", "mp3"])
            ref_track_file = st.file_uploader("Choose a reference audio file", type=["m4a", "mp3"])

            description = st.text_input("Description")

            ragas = self.raga_repo.get_all_ragas()
            ragam_options = {raga['name']: raga['id'] for raga in ragas}
            selected_ragam = st.selectbox("Select Ragam",
                                          ['--Select a Ragam--'] + list(ragam_options.keys()))

            tags = st.text_input("Tags (comma-separated)")
            level = st.selectbox("Select Level", [1, 2, 3, 4, 5])

            if st.form_submit_button("Submit", type="primary"):
                if self.validate_inputs(track_name, track_file, ref_track_file):
                    ragam_id = ragam_options[selected_ragam]
                    track_url = self.upload_to_storage(track_file)
                    ref_track_url = self.upload_to_storage(ref_track_file)
                    tags_list = [tag.strip() for tag in tags.split(",")]
                    track_data = track_file.getbuffer()
                    track_hash = self.calculate_file_hash(track_data)
                    if self.track_repo.is_duplicate(track_hash):
                        st.error("You have already uploaded this track.")
                        return
                    # self.save_track(track_data, track_file.name)
                    # self.save_track(ref_track_data, ref_track_file.name)
                    offset = self.audio_processor.compare_audio(track_file.name, ref_track_file.name)
                    self.track_repo.add_track(
                        name=track_name,
                        track_path=track_url,
                        track_ref_path=ref_track_url,
                        level=level,
                        ragam_id=ragam_id,
                        tags=tags_list,
                        description=description,
                        offset=offset,
                        track_hash=track_hash
                    )
                    st.success("Track added successfully!")

    def validate_inputs(self, track_name, track_file, ref_track_file):
        if not track_name:
            st.warning("Please provide a name for the track.")
            return False
        if not track_file:
            st.warning("Please upload an audio file.")
            return False
        if not ref_track_file:
            st.warning("Please upload a reference audio file.")
            return False
        if self.track_repo.get_track_by_name(track_name):
            st.error(f"A track with the name '{track_name}' already exists.")
            return False
        return True

    def upload_to_storage(self, file):
        file_path = f'{self.get_tracks_bucket()}/{file.name}'
        return self.storage_repo.upload_file(file.name, file_path)

    def remove_track(self):
        # Fetch all tracks
        all_tracks = self.track_repo.get_all_tracks()
        track_options = {track['name']: track['id'] for track in all_tracks}

        # Dropdown to select a track to remove
        selected_track_name = st.selectbox("Select a track to remove:",
                                           ["--Select a track--"] + list(track_options.keys()))

        # Button to initiate the removal process
        if st.button("Remove", type="primary"):
            if selected_track_name and selected_track_name != "--Select a track--":
                selected_track_id = track_options[selected_track_name]

                # Check if recordings for the track exist
                recordings = self.recording_repo.get_recordings_by_user_id_and_track_id(
                    self.get_user_id(), selected_track_id)
                if recordings:
                    st.error(
                        f"Cannot remove track '{selected_track_name}' as there are recordings associated with it.")
                    return

                # Get the track details
                track_details = self.track_repo.get_track_by_id(selected_track_id)
                files_to_remove = [track_details['track_path'], track_details.get('track_ref_path'),
                                   track_details.get('notation_path')]

                # Remove the track and associated files from storage
                for file_path in files_to_remove:
                    if file_path and not self.storage_repo.delete_file(file_path):
                        st.warning(f"Failed to remove file '{file_path}' from storage.")
                        return

                # Remove the track from database
                if self.track_repo.remove_track_by_id(selected_track_id):
                    st.success(f"Track '{selected_track_name}' removed successfully!")
                else:
                    st.error("Error removing track from database.")
            else:
                st.warning("Please select a valid track to remove.")

    @staticmethod
    def save_audio(audio, path):
        with open(path, "wb") as f:
            f.write(audio)

    def list_students_and_tracks(self, source):
        # Show groups in a dropdown
        groups = self.user_repo.get_all_groups()
        group_options = {group['group_name']: group['group_id'] for group in groups}
        selected_group_name = st.selectbox(key=f"{source}-group", label="Select a group:",
                                           options=['--Select a group--'] + list(group_options.keys()))

        # Filter users by the selected group
        selected_group_id = None
        if selected_group_name != '--Select a group--':
            selected_group_id = group_options[selected_group_name]
            users = self.user_repo.get_users_by_group(selected_group_id)
        else:
            users = self.user_repo.get_users_by_org_id_and_type(self.get_org_id(), UserType.STUDENT.value)

        user_options = {user['username']: user['id'] for user in users}
        options = ['--Select a student--'] + list(user_options.keys())
        selected_username = st.selectbox(key=f"{source}-user", label="Select a student to view their recordings:",
                                         options=options)

        selected_user_id = None
        if selected_username != '--Select a student--':
            selected_user_id = user_options[selected_username]

        selected_track_id = None
        track_path = None
        if selected_user_id is not None:
            track_ids = self.recording_repo.get_unique_tracks_by_user(selected_user_id)

            if track_ids:
                # Fetch track names by their IDs
                track_names = self.track_repo.get_track_names_by_ids(track_ids)

                # Create a mapping for the dropdown
                track_options = {track_names[id]: id for id in track_ids}

                selected_track_name = st.selectbox(key=f"{source}-track", label="Select a track:",
                                                   options=['--Select a track--'] + list(track_options.keys()))
                if selected_track_name != '--Select a track--':
                    selected_track_id = track_options[selected_track_name]
                    track = self.track_repo.get_track_by_name(selected_track_name)
                    track_path = track['track_path']

        return selected_group_id, selected_username, selected_user_id, selected_track_id, track_path

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
        group_id, username, user_id, track_id, track_name = self.list_students_and_tracks("R")
        if user_id is None:
            return

        if user_id is None or track_id is None:
            return

        self.display_track_files(track_name)
        recordings = self.recording_repo.get_recordings_by_user_id_and_track_id(user_id, track_id)
        if not recordings:
            st.write("No recordings found.")
            return

        # Create a DataFrame to hold the recording data
        df = pd.DataFrame(recordings)

        # Create a table header
        header_html = self.generate_table_header()
        st.markdown(header_html, unsafe_allow_html=True)

        # Loop through each recording and create a table row
        for index, recording in df.iterrows():
            col1, col2, col3, col4, col5 = st.columns([3.5, 1, 3, 3, 2])

            if recording['blob_url']:
                filename = self.storage_repo.download_blob_by_name(recording['blob_name'])
                col1.audio(filename, format='core/m4a')
            else:
                col1.write("No core data available.")

            # Use Markdown to make the text black and larger
            col2.markdown(f"<div style='padding-top:10px;color:black;font-size:14px;'>{recording['score']}</div>",
                          unsafe_allow_html=True)
            col3.markdown(
                f"<div style='padding-top:5px;color:black;font-size:14px;'>{recording.get('analysis', 'N/A')}</div>",
                unsafe_allow_html=True)

            # Show the remarks as markdown
            col4.markdown(
                f"<div style='padding-top:5px;color:black;font-size:14px;'>{recording.get('remarks', 'N/A')}</div>",
                unsafe_allow_html=True)

            formatted_timestamp = recording['timestamp'].strftime('%I:%M %p, ') + self.ordinal(
                int(recording['timestamp'].strftime('%d'))) + recording['timestamp'].strftime(' %b, %Y')
            col5.markdown(f"<div style='padding-top:5px;color:black;font-size:14px;'>{formatted_timestamp}</div>",
                          unsafe_allow_html=True)

    def list_submissions(self):
        # Filter criteria
        group_id, username, user_id, track_id, track_name = self.list_students_and_tracks("S")

        # Fetch and sort recordings
        recordings = self.recording_repo.get_unremarked_recordings(group_id, user_id, track_id)
        if not recordings:
            st.write("No submissions found.")
            return

        df = pd.DataFrame(recordings)

        header_html = self.generate_table_header()
        st.markdown(header_html, unsafe_allow_html=True)

        # Display each recording
        for index, recording in df.iterrows():
            self.display_submission_row(recording)

    @staticmethod
    def generate_table_header():
        # Create a table header
        header_html = """
            <div style='background-color:lightgrey;padding:5px;border-radius:3px;border:1px solid black;'>
                <div style='display:inline-block;width:28%;text-align:center;'>
                    <p style='color:black;margin:0;font-size:15px;font-weight:bold;'>Track</p>
                </div>
                <div style='display:inline-block;width:8%;text-align:left;'>
                    <p style='color:black;margin:0;font-size:15px;font-weight:bold;'>Score</p>
                </div>
                <div style='display:inline-block;width:20%;text-align:left;'>
                    <p style='color:black;margin:0;font-size:15px;font-weight:bold;'>Analysis</p>
                </div>
                <div style='display:inline-block;width:20%;text-align:left;'>
                    <p style='color:black;margin:0;font-size:15px;font-weight:bold;'>Remarks</p>
                </div>
                <div style='display:inline-block;width:10%;text-align:left;'>
                    <p style='color:black;margin:0;font-size:15px;font-weight:bold;'>Time</p>
                </div>
            </div>
            """
        return header_html

    def display_submission_row(self, recording):
        col1, col2, col3, col4, col5 = st.columns([3.5, 1, 3, 3, 2])

        col1.write("")
        if recording['blob_url']:
            filename = self.storage_repo.download_blob_by_name(recording['blob_name'])
            col1.audio(filename, format='core/m4a')
        else:
            col1.write("No core data available.")

        score = col2.text_input("", key=f"score_{recording['id']}", value=recording['score'])
        if score:
            self.recording_repo.update_score(recording["id"], score)

        col3.write("", style={"fontSize": "5px"})
        col3.markdown(
            f"<div style='padding-top:5px;color:black;font-size:14px;'>{recording.get('analysis', 'N/A')}</div>",
            unsafe_allow_html=True)

        remarks = col4.text_input("", key=f"remarks_{recording['id']}")
        if remarks:
            self.recording_repo.update_remarks(recording["id"], remarks)

        col5.write("")
        formatted_timestamp = recording['timestamp'].strftime('%I:%M %p, ') + self.ordinal(
            int(recording['timestamp'].strftime('%d'))) + recording['timestamp'].strftime(' %b, %Y')
        col5.markdown(f"<div style='padding-top:5px;color:black;font-size:14px;'>{formatted_timestamp}</div>",
                      unsafe_allow_html=True)

    @staticmethod
    def calculate_file_hash(recording_data):
        return hashlib.md5(recording_data).hexdigest()

    @staticmethod
    def save_track(track_data, track_path):
        with open(track_path, "wb") as f:
            f.write(track_data)

    @staticmethod
    def ordinal(n):
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
        if 11 <= (n % 100) <= 13:
            suffix = 'th'
        return str(n) + suffix
