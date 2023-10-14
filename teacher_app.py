from RecordingRepository import RecordingRepository
from StorageRepository import StorageRepository
from UserRepository import UserRepository
import streamlit as st
import os
import pandas as pd


def list_students():
    user_repository = UserRepository()
    user_repository.connect()  # Make sure to connect to the database
    st.header("List of Students")
    users = user_repository.get_all_users()
    user_options = {user['username']: user['user_id'] for user in users}
    selected_username = st.selectbox("Select a student to view their recordings:", list(user_options.keys()))
    selected_user_id = user_options[selected_username]
    user_repository.close()  # Close the database connection
    return selected_username, selected_user_id


def list_recordings(username, user_id):
    st.write("**Past Recordings**")
    storage_repository = StorageRepository("stringsync")
    recording_repository = RecordingRepository()
    recordings = recording_repository.get_all_recordings_by_user(user_id)

    if not recordings:
        st.write("No recordings found.")
        return

    # Create a DataFrame to hold the recording data
    df = pd.DataFrame(recordings)

    # Create a table header
    col1, col2, col3 = st.columns(3)
    col1.write("Play")
    col2.markdown("**Score**", unsafe_allow_html=True)
    col3.markdown("**Time**", unsafe_allow_html=True)

    # Loop through each recording and create a table row
    for index, recording in df.iterrows():
        col1, col2, col3 = st.columns(3)
        if recording['blob_url']:
            filename = storage_repository.download_blob(recording['blob_name'])
            col1.audio(filename, format='audio/m4a')
        else:
            col1.write("No audio data available.")

        # Use Markdown to make the text black and larger
        col2.markdown(f"<span style='color:black;font-size:14px;'>{recording['score']}</span>", unsafe_allow_html=True)
        col3.markdown(f"<span style='color:black;font-size:14px;'>{recording['timestamp']}</span>",
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


def main():
    st.set_page_config(layout='wide')
    st.header('**String Sync - Teacher Dashboard**', divider='rainbow')
    st.title("Teacher Dashboard")
    set_env()
    username, user_id = list_students()

    # Create a button called "Get Recordings"
    if st.button('Get Recordings'):
        list_recordings(username, user_id)


if __name__ == "__main__":
    main()
