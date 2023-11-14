import hashlib
import os
from abc import ABC

from core.AudioProcessor import AudioProcessor
from core.BadgeAwarder import BadgeAwarder
from core.ListBuilder import ListBuilder
from core.MessageDashboardBuilder import MessageDashboardBuilder
from core.PracticeDashboardBuilder import PracticeDashboardBuilder
from core.ProgressDashboardBuilder import ProgressDashboardBuilder
from core.TeamDashboardBuilder import TeamDashboardBuilder
from enums.Badges import TrackBadges
from enums.Features import Features
from enums.Settings import Portal
from portals.BasePortal import BasePortal
import streamlit as st
import pandas as pd

from enums.UserType import UserType


class TeacherPortal(BasePortal, ABC):
    def __init__(self):
        super().__init__()
        self.audio_processor = AudioProcessor()
        self.badge_awarder = BadgeAwarder(
            self.settings_repo, self.recording_repo,
            self.user_achievement_repo, self.user_practice_log_repo,
            self.portal_repo, self.storage_repo)
        self.practice_dashboard_builder = PracticeDashboardBuilder(
            self.user_practice_log_repo)
        self.progress_dashboard_builder = ProgressDashboardBuilder(
            self.settings_repo, self.recording_repo, self.user_achievement_repo,
            self.user_practice_log_repo, self.track_repo)
        self.team_dashboard_builder = TeamDashboardBuilder(
            self.portal_repo, self.user_achievement_repo, self.badge_awarder, self.avatar_loader)
        self.message_dashboard_builder = MessageDashboardBuilder(
            self.message_repo, self.avatar_loader)

    def get_portal(self):
        return Portal.TEACHER

    def get_title(self):
        return f"{self.get_app_name()} Teacher Portal"

    def get_icon(self):
        return "🎶"

    def get_tab_dict(self):
        tabs = [
            ("👥 Create a Team", self.create_team),
            ("👥 List Teams", self.teams),
            ("👩‍🎓 Students", self.list_students),
            ("🔀 Team Assignments", self.team_assignments),
            ("📚 Resources", self.resource_management),
            ("🎵 Create Track", self.create_track),
            ("🎵 List Tracks", self.list_tracks),
            ("🎵 Remove Track", self.remove_track),
            ("📝 Assignments", self.assignment_management),
            ("🎵 Recordings", self.list_recordings) if self.is_feature_enabled(
                Features.TEACHER_PORTAL_RECORDINGS) else None,
            ("📥 Submissions", self.submissions),
            ("📊 Progress Dashboard", self.progress_dashboard),
            ("👥 Team Dashboard", self.team_dashboard),
            ("🔗 Team Connect", self.team_connect),
            ("⚙️ Settings", self.settings) if self.is_feature_enabled(
                Features.TEACHER_PORTAL_SETTINGS) else None,
            ("🗂️ Sessions", self.sessions) if self.is_feature_enabled(
                Features.TEACHER_PORTAL_SHOW_USER_SESSIONS) else None,
            ("📊 Activities", self.activities) if self.is_feature_enabled(
                Features.TEACHER_PORTAL_SHOW_USER_ACTIVITY) else None
        ]
        return {tab[0]: tab[1] for tab in tabs if tab}

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

    def create_team(self):
        with st.form(key='create_team_form', clear_on_submit=True):
            group_name = st.text_input("Team Name")
            if st.form_submit_button("Create Team", type='primary'):
                if group_name:
                    success, message = self.user_repo.create_user_group(group_name, self.get_org_id())
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.warning("Team name cannot be empty.")

    def teams(self):
        # Fetch all groups
        groups = self.user_repo.get_all_groups(self.get_org_id())

        # No groups?
        if not groups:
            st.info("No teams found. Create a new team to get started.")
            return

        # Define the column widths for three columns
        column_widths = [33, 33, 33]
        list_builder = ListBuilder(column_widths)
        list_builder.build_header(column_names=["Team ID", "Team Name", "Member Count"])

        # Display each team and its member count in a row
        for group in groups:
            row_data = {
                "Team ID": group['group_id'],
                "Team Name": group['group_name'],
                "Member Count": group['member_count']
            }
            list_builder.build_row(row_data=row_data)

    def list_students(self):
        students = self.user_repo.get_users_by_org_id_and_type(self.get_org_id(), UserType.STUDENT.value)

        if not students:
            st.info(f"Please ask new members to join the team using join code: {st.session_state['join_code']}")
            return

        column_widths = [20, 20, 20, 20, 20]
        list_builder = ListBuilder(column_widths)
        list_builder.build_header(column_names=["Name", "Username", "Email", "Team", "Join Code"])

        for student_detail in students:
            row_data = {
                "Name": student_detail['name'],
                "Username": student_detail['username'],
                "Email": student_detail['email'],
                "Team": student_detail['group_name'] if 'group_name' in student_detail else 'N/A',
                "Join Code": st.session_state['join_code']
            }
            list_builder.build_row(row_data=row_data)

    def team_assignments(self):
        groups = self.user_repo.get_all_groups(self.get_org_id())
        if not groups:
            st.info("Please create a team to get started.")
            return

        group_options = ["--Select a Team--"] + [group['group_name'] for group in groups]
        group_ids = [None] + [group['group_id'] for group in groups]
        group_name_to_id = {group['group_name']: group['group_id'] for group in groups}

        students = self.user_repo.get_users_by_org_id_and_type(
            self.get_org_id(), UserType.STUDENT.value)

        if not students:
            st.info(f"Please ask new members to join the team using join code: {st.session_state['join_code']}")
            return

        # Column headers
        list_builder = ListBuilder(column_widths=[33.33, 33.33, 33.33])
        list_builder.build_header(column_names=["Name", "Email", "Team"])

        for student in students:
            st.markdown("<div style='border-top:1px solid #AFCAD6; height: 1px;'>", unsafe_allow_html=True)
            with st.container():
                current_group_id = self.user_repo.get_group_by_user_id(student['id'])['group_id']
                if current_group_id is None:
                    current_group_index = 0
                else:
                    current_group_index = group_ids.index(current_group_id)

                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    st.write("")
                    st.markdown(
                        f"<div style='padding-top:14px;color:black;font-size:14px;'>{student['name']}</div>",
                        unsafe_allow_html=True)
                with col2:
                    st.write("")
                    st.markdown(
                        f"<div style='padding-top:14px;color:black;font-size:14px;'>{student['email']}</div>",
                        unsafe_allow_html=True)
                with col3:
                    selected_group = col3.selectbox(
                        "Select a Team", group_options, index=current_group_index, key=student['id'],
                    )

                    if selected_group != "--Select a Team--":
                        selected_group_id = group_name_to_id[selected_group]
                        if selected_group_id != current_group_id:
                            self.user_repo.assign_user_to_group(student['id'], selected_group_id)
                            st.rerun()

    def resource_management(self):
        st.header("Resources Management")

        # Part for uploading new resources
        with st.form("resource_upload"):
            resource_title = st.text_input("Title", key='resource_title')
            resource_description = st.text_area("Description", key='resource_description')
            resource_file = st.file_uploader("Upload Resource", type=['pdf', 'mp3', 'mp4'], key='resource_file')
            resource_type = st.selectbox("Type", ["PDF", "Audio", "Video", "Link"], key='resource_type')
            resource_link = st.text_input("Resource Link (if applicable)", key='resource_link')
            submit_button = st.form_submit_button("Upload Resource")

            if submit_button:
                self.handle_resource_upload(
                    title=resource_title,
                    description=resource_description,
                    file=resource_file,
                    rtype=resource_type,
                    link=resource_link
                )

        # Part for listing existing resources
        self.list_resources()

    def assignment_management(self):
        st.header("Assignment Management")

        with st.form("assignment_creation"):
            assignment_title = st.text_input("Assignment Title", key='assignment_title')
            assignment_description = st.text_area("Assignment Description", key='assignment_description')
            due_date = st.date_input("Due Date", key='due_date')

            all_tracks = self.track_repo.get_all_tracks()
            all_resources = self.resource_repo.get_all_resources()

            track_options = {track['name']: track['id'] for track in all_tracks}
            resource_options = {resource['title']: resource['id'] for resource in all_resources}

            selected_track_ids = [track_options[track_name] for track_name in
                                  st.multiselect("Select Tracks", list(track_options.keys()),
                                                 key='selected_tracks')]
            selected_resource_ids = [resource_options[resource_title] for resource_title in
                                     st.multiselect("Select Resources", list(resource_options.keys()),
                                                    key='selected_resources')]
            # Fetch all teams
            all_teams = self.user_repo.get_all_groups(self.get_org_id())
            team_options = {team['group_name']: team['group_id'] for team in all_teams}
            selected_team_ids = [team_options[team_name] for team_name in
                                 st.multiselect("Select Teams", list(team_options.keys()),
                                 key='selected_teams')]

            # Fetch all individual users
            all_users = self.user_repo.get_users_by_org_id_and_type(
                self.get_org_id(), UserType.STUDENT.value)
            user_options = {user['username']: user['id'] for user in all_users}
            selected_user_ids = [user_options[username] for username in
                                 st.multiselect("Select Individual Users", list(user_options.keys()),
                                 key='selected_users')]

            submit_button = st.form_submit_button("Create Assignment")

            if submit_button:
                assignment_id = self.assignment_repo.add_assignment(
                    assignment_title, assignment_description, due_date
                )

                for track_id in selected_track_ids:
                    self.assignment_repo.add_assignment_detail(assignment_id,
                                                               track_id=track_id)
                for resource_id in selected_resource_ids:
                    self.assignment_repo.add_assignment_detail(assignment_id,
                                                               resource_id=resource_id)

                # Combine users from selected teams with individually selected users
                users_to_assign = set(selected_user_ids)
                for team_id in selected_team_ids:
                    team_members = self.user_repo.get_users_by_org_id_group_and_type(
                        self.get_org_id(), team_id, UserType.STUDENT.value)
                    users_to_assign.update(member['id'] for member in team_members)

                # Deduplicate and assign the assignment to each user
                self.assignment_repo.assign_to_users(assignment_id, list(users_to_assign))

                st.success("Assignment created and assigned successfully!")

    def handle_resource_upload(self, title, description, file, rtype, link):
        if rtype != "Link" and not file:
            st.error("Please upload a file.")
            return

        if rtype == "Link" and not link:
            st.error("Please provide a resource link.")
            return

        if title:
            if rtype == "Link":
                # Save the link to the database
                self.resource_repo.add_resource(self.get_user_id(), title, description, rtype, None, link)
                st.success("Resource link added successfully!")
            else:
                # Save the file to storage and get the URL
                file_url = self.upload_resource_to_storage(file, file.getvalue())
                # Save the file information to the database
                self.resource_repo.add_resource(self.get_user_id(), title, description, rtype, file_url, None)
                st.success("File uploaded successfully!")
        else:
            st.error("Title is required.")

    def list_resources(self):
        # Fetch resources from the DB
        resources = self.resource_repo.get_all_resources()
        if resources:
            for resource in resources:
                with st.expander(f"{resource['title']}"):
                    st.write(resource['description'])
                    if resource['type'] == "Link":
                        st.markdown(f"[Resource Link]({resource['link']})")
                    else:
                        data = self.storage_repo.download_blob_by_url(resource['file_url'])
                        st.download_button(
                            label="Download",
                            data=data,
                            file_name=resource['title'],
                            mime='application/octet-stream'
                        )
                    if st.button(f"Delete {resource['title']}", key=f"delete_{resource['id']}"):
                        self.delete_resource(resource['id'])
        else:
            st.info("No resources found. Upload a resource to get started.")

    def delete_resource(self, resource_id):
        # Delete resource from the database and storage
        resource = self.resource_repo.get_resource_by_id(resource_id)
        if resource:
            if resource['file_url']:
                # Delete the file from storage
                self.storage_repo.delete_blob(resource['file_url'])
            # Delete the resource from the database
            self.resource_repo.delete_resource(resource_id)
            st.success("Resource deleted successfully!")
            # Refresh the page to show the updated list
            st.experimental_rerun()
        else:
            st.error("Resource not found.")

    def create_track(self):
        with st.form(key='create_track_form', clear_on_submit=True):
            track_name = st.text_input("Track Name")
            track_file = st.file_uploader("Choose an audio file", type=["m4a", "mp3"])
            ref_track_file = st.file_uploader("Choose a reference audio file", type=["m4a", "mp3"])

            description = st.text_input("Description")

            ragas = self.raga_repo.get_all_ragas()
            ragam_options = {raga['name']: raga['id'] for raga in ragas}
            selected_ragam = st.selectbox("Select Ragam",
                                          ['--Select a Ragam--'] + list(ragam_options.keys()))

            # Existing tags
            tags = self.track_repo.get_all_tags()
            selected_tags = st.multiselect("Select tags:", tags)
            new_tags = st.text_input("Add new tags (comma-separated):")
            if new_tags:
                new_tags = [tag.strip() for tag in new_tags.split(",")]
                selected_tags.extend(new_tags)
            level = st.selectbox("Select Level", [1, 2, 3, 4, 5])

            if st.form_submit_button("Submit", type="primary"):
                if self.validate_inputs(track_name, track_file, ref_track_file):
                    ragam_id = ragam_options[selected_ragam]
                    track_data = track_file.getbuffer()
                    track_hash = self.calculate_file_hash(track_data)
                    if self.track_repo.is_duplicate(track_hash):
                        st.error("You have already uploaded this track.")
                        return
                    track_url = self.upload_track_to_storage(track_file, track_data)
                    ref_track_data = ref_track_file.getbuffer()
                    ref_track_url = self.upload_track_to_storage(ref_track_file, ref_track_data)
                    self.storage_repo.download_blob(track_url, track_file.name)
                    self.storage_repo.download_blob(ref_track_url, ref_track_file.name)
                    offset = self.audio_processor.compare_audio(track_file.name, ref_track_file.name)
                    os.remove(track_file.name)
                    os.remove(ref_track_file.name)
                    self.track_repo.add_track(
                        name=track_name,
                        track_path=track_url,
                        track_ref_path=ref_track_url,
                        level=level,
                        ragam_id=ragam_id,
                        tags=selected_tags,
                        description=description,
                        offset=offset,
                        track_hash=track_hash
                    )
                    st.success("Track added successfully!")

    def list_tracks(self):
        # Fetching all track details using the method from PortalRepository
        tracks = self.portal_repo.list_tracks()
        if not tracks:
            st.info("No tracks found. Create a track to get started.")
            return

        list_builder = ListBuilder(column_widths=[20, 20, 20, 20, 20])
        list_builder.build_header(
            column_names=["Track Name", "Audio", "Ragam", "Level", "Description"])

        for track_detail in tracks:
            col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
            row_data = {
                "Track Name": track_detail['track_name'],
                "Ragam": track_detail['ragam'],
                "Level": track_detail['level'],
                "Description": track_detail['description']
            }
            col1.write("")
            col1.markdown(
                f"<div style='padding-top:12px;color:black;font-size:14px;text-align:left'>{row_data['Track Name']}</div>",
                unsafe_allow_html=True)

            col2.write("")
            blob_url = track_detail['track_path']
            audio_file_path = self.storage_repo.download_blob_by_url(blob_url)
            col2.audio(audio_file_path, format='core/m4a')

            col3.write("")
            col3.markdown(
                f"<div style='padding-top:12px;color:black;font-size:14px;text-align:left'>{row_data['Ragam']}</div>",
                unsafe_allow_html=True)
            col4.write("")
            col4.markdown(
                f"<div style='padding-top:12px;color:black;font-size:14px;text-align:left'>{row_data['Level']}</div>",
                unsafe_allow_html=True)
            col5.write("")
            col5.markdown(
                f"<div style='padding-top:12px;color:black;font-size:14px;text-align:left'>{row_data['Description']}</div>",
                unsafe_allow_html=True)

    def validate_inputs(self, track_name, track_file, ref_track_file):
        if not track_name:
            st.warning("Please provide a name for the track.")
            return False
        if not track_file:
            st.error("Please upload an audio file.")
            return False
        if not ref_track_file:
            st.error("Please upload a reference audio file.")
            return False
        if self.track_repo.get_track_by_name(track_name):
            st.error(f"A track with the name '{track_name}' already exists.")
            return False
        return True

    def upload_track_to_storage(self, file, data):
        blob_path = f'{self.get_tracks_bucket()}/{file.name}'
        return self.storage_repo.upload_blob(data, blob_path)

    def upload_resource_to_storage(self, file, data):
        blob_path = f'{self.get_resources_bucket()}/{file.name}'
        return self.storage_repo.upload_blob(data, blob_path)

    def remove_track(self):
        # Fetch all tracks
        all_tracks = self.track_repo.get_all_tracks()

        if not all_tracks:
            st.info("No tracks found.")
            return

        track_options = {track['name']: track['id'] for track in all_tracks}

        # Dropdown to select a track to remove
        selected_track_name = st.selectbox("Select a track to remove:",
                                           ["--Select a track--"] + list(track_options.keys()))

        # Button to initiate the removal process
        if st.button("Remove", type="primary"):
            if selected_track_name and selected_track_name != "--Select a track--":
                selected_track_id = track_options[selected_track_name]

                # Check if recordings for the track exist
                if self.recording_repo.recordings_exist_for_track(selected_track_id):
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
                    st.rerun()
                else:
                    st.error("Error removing track from database.")

    @staticmethod
    def save_audio(audio, path):
        with open(path, "wb") as f:
            f.write(audio)

    def list_students_and_tracks(self, source):
        # Show groups in a dropdown
        groups = self.user_repo.get_all_groups(self.get_org_id())
        group_options = {group['group_name']: group['group_id'] for group in groups}
        selected_group_name = st.selectbox(key=f"{source}-group", label="Select a team:",
                                           options=['--Select a team--'] + list(group_options.keys()))

        # Filter users by the selected group
        selected_group_id = None
        if selected_group_name != '--Select a team--':
            selected_group_id = group_options[selected_group_name]
            users = self.user_repo.get_users_by_org_id_group_and_type(
                self.get_org_id(), selected_group_id, UserType.STUDENT.value)
        else:
            users = self.user_repo.get_users_by_org_id_and_type(
                self.get_org_id(), UserType.STUDENT.value)

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
                tracks = self.track_repo.get_tracks_by_ids(track_ids)
                # Create a mapping for the dropdown
                track_options = {tracks[id]['name']: id for id in track_ids if id in tracks}
                selected_track_name = st.selectbox(key=f"{source}-track", label="Select a track:",
                                                   options=['--Select a track--'] + list(track_options.keys()))
                if selected_track_name != '--Select a track--':
                    selected_track_id = track_options[selected_track_name]
                    track = tracks[selected_track_id]
                    track_path = track['track_path']

        return selected_group_id, selected_username, selected_user_id, selected_track_id, track_path

    def display_track_files(self, url):
        if url is None:
            return

        st.write("")
        st.write("")
        audio_data = self.storage_repo.download_blob_by_url(url)
        st.audio(audio_data, format='core/m4a')

    def list_recordings(self):
        group_id, username, user_id, track_id, track_name = self.list_students_and_tracks("R")
        if user_id is None or track_id is None:
            return

        self.display_track_files(track_name)
        recordings = self.recording_repo.get_recordings_by_user_id_and_track_id(user_id, track_id)
        if not recordings:
            st.info("No recordings found.")
            return

        # Create a DataFrame to hold the recording data
        df = pd.DataFrame(recordings)

        # Create a table header
        list_builder = ListBuilder(column_widths=[20, 20, 20, 20, 20])
        header_html = list_builder.build_header(
            column_names=["Recording", "Score", "System Analysis", "Remarks", "Timestamp"])
        st.markdown(header_html, unsafe_allow_html=True)

        # Loop through each recording and create a table row
        for index, recording in df.iterrows():
            col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])

            if recording['blob_url']:
                filename = self.storage_repo.download_blob_by_url(recording['blob_url'])
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

    def submissions(self):
        # Filter criteria
        group_id, username, user_id, track_id, track_name = self.list_students_and_tracks("S")
        if group_id is None and user_id is None:
            return

        # Fetch and sort recordings
        recordings = self.portal_repo.get_unremarked_recordings(group_id, user_id, track_id)
        if not recordings:
            st.info("No submissions found.")
            return

        df = pd.DataFrame(recordings)
        list_builder = ListBuilder(column_widths=[16.66, 16.66, 16.66, 16.66, 16.66, 16.66])
        list_builder.build_header(
            column_names=["Track", "Recording", "Score", "System Analysis", "Remarks", "Badges"])
        # Display each recording
        for index, recording in df.iterrows():
            self.display_submission_row(recording)

    def display_submission_row(self, submission):
        col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])

        col1.write("")
        if submission['track_path']:
            filename = self.storage_repo.download_blob_by_url(submission['track_path'])
            col1.audio(filename, format='core/m4a')
        else:
            col1.write("No core data available.")

        col2.write("")
        if submission['blob_url']:
            filename = self.storage_repo.download_blob_by_name(submission['blob_name'])
            col2.audio(filename, format='core/m4a')
        else:
            col2.write("No core data available.")

        score = col3.text_input("", key=f"score_{submission['id']}", value=submission['score'])
        if score:
            self.recording_repo.update_score(submission["id"], score)

        col4.write("", style={"fontSize": "5px"})
        col4.markdown(
            f"<div style='padding-top:14px;color:black;font-size:14px;'>{submission.get('analysis', 'N/A')}</div>",
            unsafe_allow_html=True)

        remarks = col5.text_input("", key=f"remarks_{submission['id']}")

        badge_options = [badge.value for badge in TrackBadges]
        selected_badge = col6.selectbox("", ['--Select a badge--', 'N/A'] + badge_options,
                                        key=f"badge_{submission['id']}")

        if remarks and selected_badge != '--Select a badge--':
            self.recording_repo.update_remarks(submission["id"], remarks)
            if selected_badge != 'N/A':
                self.user_achievement_repo.award_track_badge(submission['user_id'],
                                                             submission['id'],
                                                             TrackBadges(selected_badge),
                                                             submission['timestamp'])
            st.rerun()

    def progress_dashboard(self):
        users = self.user_repo.get_users_by_org_id_and_type(
            self.get_org_id(), UserType.STUDENT.value)

        user_options = {user['username']: user['id'] for user in users}
        options = ['--Select a student--'] + list(user_options.keys())
        selected_username = st.selectbox(key=f"user_select_progress_dashboard",
                                         label="Select a student to view their progress report:",
                                         options=options)

        divider = "<hr style='height:5px; margin-top: 10px; border-width:3px; background: lightblue;'>"
        st.markdown(f"{divider}", unsafe_allow_html=True)

        selected_user_id = None
        if selected_username != '--Select a student--':
            selected_user_id = user_options[selected_username]
        else:
            return

        self.progress_dashboard_builder.progress_dashboard(selected_user_id)
        st.markdown("<h1 style='font-size: 20px;'>Practice Logs</h1>", unsafe_allow_html=True)
        self.practice_dashboard_builder.practice_dashboard(selected_user_id)

    def team_dashboard(self):
        groups = self.user_repo.get_all_groups(self.get_org_id())

        if not groups:
            st.info("Please create a team to get started.")
            return

        group_options = ["--Select a Team--"] + [group['group_name'] for group in groups]
        group_name_to_id = {group['group_name']: group['group_id'] for group in groups}

        col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])

        with col1:
            selected_group = st.selectbox(
                "Select a Team", group_options, key="team_dashboard_group_selector")

        with col3:
            st.write("")
            st.write("")
            if selected_group != "--Select a Team--":
                selected_group_id = group_name_to_id[selected_group]
                if st.button("Award Weekly Badges", type='primary'):
                    self.badge_awarder.auto_award_weekly_badges(selected_group_id)

        with col4:
            st.write("")
            st.write("")
            if selected_group != "--Select a Team--":
                selected_group_id = group_name_to_id[selected_group]
                if st.button("Award Monthly Badges", type='primary'):
                    self.badge_awarder.auto_award_monthly_badges(selected_group_id)

        with col5:
            st.write("")
            st.write("")
            if selected_group != "--Select a Team--":
                selected_group_id = group_name_to_id[selected_group]
                if st.button("Award Yearly Badges", type='primary'):
                    self.badge_awarder.auto_award_yearly_badges(selected_group_id)

        if selected_group != "--Select a Team--":
            # Show dashboard
            self.team_dashboard_builder.team_dashboard(selected_group_id)

    def team_connect(self):
        st.markdown(f"<h2 style='text-align: center; font-weight: bold; color: {self.tab_heading_font_color}; "
                    "font-size: 24px;'> 💼 Team Engagement & Insights 💼</h2>", unsafe_allow_html=True)
        st.write("This is a space for team members to share messages and updates.")
        self.divider()

        # Fetch all groups
        all_groups = self.user_repo.get_all_groups(self.get_org_id())
        group_options = ["Select a Team"] + [group['group_name'] for group in all_groups]
        group_ids = [None] + [group['group_id'] for group in all_groups]
        group_name_to_id = {group['group_name']: group['group_id'] for group in all_groups}

        # Dropdown to select a group
        selected_group = st.selectbox("Choose a Team to Interact With:", group_options)

        # Only show the message dashboard if a group is selected
        if selected_group != "Select a Team":
            selected_group_id = group_name_to_id[selected_group]
            self.message_dashboard_builder.message_dashboard(self.get_user_id(), selected_group_id)

    def award_weekly_badges(self, group_id):
        self.badge_awarder.auto_award_weekly_badges(group_id)

    @staticmethod
    def calculate_file_hash(audio_data):
        return hashlib.md5(audio_data).hexdigest()

    @staticmethod
    def ordinal(n):
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
        if 11 <= (n % 100) <= 13:
            suffix = 'th'
        return str(n) + suffix
