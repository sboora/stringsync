from RecordingRepository import RecordingRepository
from StorageRepository import StorageRepository
from UserRepository import UserRepository
import streamlit as st
import os
import pandas as pd


def list_students():
    user_repository = UserRepository()
    user_repository.connect()  # Make sure to connect to the database
    st.header("Students")
    users = user_repository.get_all_users()
    user_options = {user['username']: user['user_id'] for user in users}

    # Add a placeholder to the list of options
    options = ['--Select a student--'] + list(user_options.keys())
    selected_username = st.selectbox("Select a student to view their recordings:", options)

    # Check if a student is actually selected
    if selected_username != '--Select a student--':
        selected_user_id = user_options[selected_username]
    else:
        selected_user_id = None  # No student is selected

    user_repository.close()  # Close the database connection
    return selected_username, selected_user_id


def list_recordings(username, user_id):
    storage_repository = StorageRepository("stringsync")
    recording_repository = RecordingRepository()
    recordings = recording_repository.get_all_recordings_by_user(user_id)

    if not recordings:
        st.write("No recordings found.")
        return

    # Create a DataFrame to hold the recording data
    df = pd.DataFrame(recordings)

    # Create a table header
    col1, col2, col3, col4, col5 = st.columns([3.5, 1, 3, 3, 2])
    col2.markdown("**Score**", unsafe_allow_html=True)
    col3.markdown("**Analysis**", unsafe_allow_html=True)
    col4.markdown("**Remarks**", unsafe_allow_html=True)
    col5.markdown("**Time**", unsafe_allow_html=True)

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
        col2.markdown(f"<div style='padding-top:15px;color:black;font-size:14px;'>{recording['score']}</div>",
                      unsafe_allow_html=True)
        col3.markdown(
            f"<div style='padding-top:15px;color:black;font-size:14px;'>{recording.get('analysis', 'N/A')}</div>",
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
                f"<div style='padding-top:10px;color:black;font-size:14px;'>{recording.get('remarks', 'N/A')}</div>",
                unsafe_allow_html=True)

            # Show an edit icon next to the remarks
            if col4.button("✏️", key=f"edit_{recording['id']}"):
                st.session_state["editable_states"][recording['id']] = True  # Turn on editable state
                st.rerun()

        col5.markdown(f"<div style='padding-top:15px;color:black;font-size:14px;'>{recording['timestamp']}</div>",
                      unsafe_allow_html=True)

    recording_repository.close()  # Close the database connection


def set_env():
    os.environ["GOOGLE_APP_CRED"] = st.secrets["GOOGLE_APPLICATION_CREDENTIALS"]
    os.environ["SQL_SERVER"] = st.secrets["SQL_SERVER"]
    os.environ["SQL_DATABASE"] = st.secrets["SQL_DATABASE"]
    os.environ["SQL_USERNAME"] = st.secrets["SQL_USERNAME"]
    os.environ["SQL_PASSWORD"] = st.secrets["SQL_PASSWORD"]
    os.environ["MYSQL_CONNECTION_STRING"] = st.secrets["MYSQL_CONNECTION_STRING"]
    os.environ["EMAIL_ID"] = st.secrets["EMAIL_ID"]
    os.environ["EMAIL_PASSWORD"] = st.secrets["EMAIL_PASSWORD"]


def setup_streamlit_app():
    """
    Set up the Streamlit app with headers and markdown text for the Teacher Dashboard.
    """
    st.set_page_config(layout='wide')
    st.header('**String Sync - Teacher Dashboard**', divider='rainbow')
    st.markdown(
        """
        Welcome to the Teacher Dashboard of String Sync, an innovative platform designed to revolutionize 
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


def main():
    setup_streamlit_app()
    set_env()
    # Select a user
    username, user_id = list_students()
    # Geet the recordings for the user
    if user_id is not None:
        list_recordings(username, user_id)


if __name__ == "__main__":
    main()
