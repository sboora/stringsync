from ConnectionBuilder import ConnectionBuilder
from RecordingRepository import RecordingRepository
from StorageRepository import StorageRepository
from UserRepository import UserRepository
import streamlit as st
import os


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
    st.header(f"Recordings of {username}")
    storage_repository = StorageRepository("stringsync")
    recording_repository = RecordingRepository()
    recordings = recording_repository.get_all_recordings_by_user(user_id)
    if not recordings:
        st.write("No recordings found for this user.")
        return
    for recording in recordings:
        if recording['blob_url']:
            st.write(f"Track ID: {recording['track_id']}, Timestamp: {recording['timestamp']}")
            filename = storage_repository.download_blob(recording['blob_name'])
            st.audio(filename, format='audio/m4a')
        else:
            st.write(f"Track ID: {recording['track_id']}, Timestamp: {recording['timestamp']}")
            st.write("No audio data available.")
    recording_repository.close()  # Close the database connection


def set_env():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = st.secrets["GOOGLE_APPLICATION_CREDENTIALS"]
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
