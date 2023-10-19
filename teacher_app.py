import env
from RecordingRepository import RecordingRepository
from StorageRepository import StorageRepository
from TrackRepository import TrackRepository
import streamlit as st
import pandas as pd

from UserRepository import UserRepository
from UserType import UserType

env.set_env()
user_repository = UserRepository()


def main():
    init_session()
    set_app_layout()
    show_introduction()

    if not st.session_state['user_logged_in']:
        login_user()
    else:
        st.header(f"Welcome, {st.session_state['username']}!")

        create_group_tab, assign_student_to_group_tab, list_recording_tab = \
            st.tabs(["👥 Create Group", "🔀 Assign Students to Groups", "🎵 List Recordings"])

        with create_group_tab:
            create_group()

        with assign_student_to_group_tab:
            assign_students_to_group()

        with list_recording_tab:
            username, user_id, track_id, track_name = list_students_and_tracks()
            display_track_files(track_name)
            if user_id is not None:
                list_recordings(username, user_id, track_id)

    show_copyright()


def set_app_layout():
    st.set_page_config(
        layout='wide'
    )
    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                header {visibility: hidden;}
                footer {visibility: hidden;}   
                </style>

                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    # Create columns for header and logout button
    col1, col2 = st.columns([8.5, 1.5])  # Adjust the ratio as needed

    with col1:
        st.markdown("<h1 style='margin-bottom:0px;'>StringSync</h1>", unsafe_allow_html=True)

    with col2:
        if user_logged_in():
            col2_1, col2_2 = st.columns([1, 3])  # Adjust the ratio as needed
            with col2_2:
                user_options = st.selectbox("", ["", "Settings", "Logout"], index=0,
                                            format_func=lambda
                                                x: f"👤\u2003{get_username()}" if x == "" else x)

                if user_options == "Logout":
                    st.session_state["user_logged_in"] = False
                    st.rerun()
                elif user_options == "Settings":
                    # Navigate to settings page or open settings dialog
                    pass


def show_introduction():
    st.markdown(
        """
        Welcome to the **Teacher Dashboard** of String Sync, an innovative platform designed to revolutionize 
        music education. As a teacher, you can monitor your students' progress, manage class assignments, 
        and provide valuable feedback all in one place.

        ### How Does it Work? 
        1. **Assign Tracks**: Choose from a variety of tracks and assign them to your students.
        2. **Monitor Progress**: View your students' uploaded recordings and scores to track their progress.
        3. **Provide Feedback**: Use the analysis and remarks sections to give personalized feedback.

        ### Why Use String Sync for Teaching?
        - **Objective Feedback**: Enable your students to get unbiased, data-driven feedback on their performances.
        - **Progress Tracking**: Easily monitor the progress of each student over time.
        - **Class Management**: Manage assignments and deadlines effortlessly.
        - **Flexible**: Suitable for teaching any instrument and adaptable to various skill levels.

        "Ready to get started? Use the sidebar to navigate through the various features available on your Teacher Dashboard!"
        """
    )


def show_copyright():
    st.write("")
    st.write("")
    st.write("")
    footer_html = """
        <div style="text-align: center; color: gray;">
            <p style="font-size: 14px;">© 2023 KA Academy of Indian Music and Dance. All rights reserved.</p>
        </div>
        """
    st.markdown(footer_html, unsafe_allow_html=True)


def login_user():
    st.sidebar.header("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login", type='primary'):
        if not username or not password:
            st.sidebar.error("Both username and password are required.")
            return
        success, user_id, org_id = user_repository.authenticate_user(username, password)
        if success:
            set_session_state(user_id, org_id, username)
            st.rerun()
        else:
            st.sidebar.error("Invalid username or password.")


def set_session_state(user_id, org_id, username):
    st.session_state['user_logged_in'] = True
    st.session_state['user_id'] = user_id
    st.session_state['org_id'] = org_id
    st.session_state['username'] = username


def teacher_logout():
    st.session_state['user_logged_in'] = False
    st.session_state['user_id'] = None
    st.session_state['org_id'] = None
    st.session_state['username'] = None
    st.rerun()


def assign_students_to_group():
    # Feature to assign a user to a group
    groups = user_repository.get_all_groups()
    group_options = {group['group_name']: group['group_id'] for group in groups}
    users = user_repository.get_users_by_org_id_and_type(get_org_id(), UserType.STUDENT.value)
    user_options = {user['username']: user['id'] for user in users}

    selected_username = st.selectbox("Select a student:", ['--Select a student--'] + list(user_options.keys()))
    if selected_username != '--Select a student--':
        selected_user_id = user_options[selected_username]

        # Get the current group of the user
        current_group = user_repository.get_group_by_user_id(selected_user_id)
        current_group_name = current_group['group_name'] if current_group else '--Select a group--'

        # Dropdown to assign a new group, with the current group pre-selected
        assign_to_group = st.selectbox("Assign to group:", ['--Select a group--'] + list(group_options.keys()),
                                       index=list(group_options.keys()).index(
                                           current_group_name) + 1 if current_group else 0)

        if assign_to_group != '--Select a group--' and assign_to_group != current_group_name:
            user_repository.assign_user_to_group(selected_user_id, group_options[assign_to_group])
            st.success(f"User '{selected_username}' assigned to group '{assign_to_group}'.")


def init_session():
    if 'user_logged_in' not in st.session_state:
        st.session_state['user_logged_in'] = False
    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = None
    if 'org_id' not in st.session_state:
        st.session_state['org_id'] = None
    if 'username' not in st.session_state:
        st.session_state['username'] = None


def user_logged_in():
    return st.session_state['user_logged_in']


def get_username():
    return st.session_state['username']


def get_org_id():
    return st.session_state['org_id']


def create_group():
    # Feature to create a new group
    group_name = st.text_input("Create a new group:")
    if st.button("Create Group", type='primary'):
        if group_name:
            success, message = user_repository.create_user_group(group_name, get_org_id())
            if success:
                st.success(message)
            else:
                st.error(message)
        else:
            st.warning("Group name cannot be empty.")


def list_students_and_tracks():
    st.header("Students")

    # Show groups in a dropdown
    groups = user_repository.get_all_groups()
    group_options = {group['group_name']: group['group_id'] for group in groups}
    selected_group_name = st.selectbox("Select a group:", ['--Select a group--'] + list(group_options.keys()))

    # Filter users by the selected group
    if selected_group_name != '--Select a group--':
        selected_group_id = group_options[selected_group_name]
        users = user_repository.get_users_by_group(selected_group_id)
    else:
        users = user_repository.get_all_users()

    user_options = {user['username']: user['user_id'] for user in users}
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
            track_repository = TrackRepository()
            track_names = track_repository.get_track_names_by_ids(track_ids)

            # Create a mapping for the dropdown
            track_options = {track_names[id]: id for id in track_ids}

            selected_track_name = st.selectbox("Select a track:", ['--Select a track--'] + list(track_options.keys()))
            if selected_track_name != '--Select a track--':
                selected_track_id = track_options[selected_track_name]
                track = track_repository.get_track_by_name(selected_track_name)
                track_path = track[2]

    return selected_username, selected_user_id, selected_track_id, track_path


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
    st.audio(track_file, format='audio/m4a')


def list_recordings(username, user_id, track_id):
    storage_repository = StorageRepository("stringsync")
    recording_repository = RecordingRepository()

    if user_id is None or track_id is None:
        return

    recordings = recording_repository.get_recordings_by_user_id_and_track_id(user_id, track_id)
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
            filename = storage_repository.download_blob(recording['blob_name'])
            col1.audio(filename, format='audio/m4a')
        else:
            col1.write("No audio data available.")

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
                recording_repository.update_remarks(recording['id'], new_remarks)
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

        formatted_timestamp = recording['timestamp'].strftime('%I:%M %p, ') + ordinal(
            int(recording['timestamp'].strftime('%d'))) + recording['timestamp'].strftime(' %b, %Y')
        col5.markdown(f"<div style='padding-top:5px;color:black;font-size:14px;'>{formatted_timestamp}</div>",
                      unsafe_allow_html=True)


def ordinal(n):
    suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    return str(n) + suffix


if __name__ == "__main__":
    main()
