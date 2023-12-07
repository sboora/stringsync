import datetime
import hashlib

import streamlit as st

from components.AudioProcessor import AudioProcessor
from components.BadgeAwarder import BadgeAwarder
from enums.ActivityType import ActivityType
from enums.Badges import UserBadges
from repositories.RagaRepository import RagaRepository
from repositories.RecordingRepository import RecordingRepository
from repositories.StorageRepository import StorageRepository
from repositories.UserActivityRepository import UserActivityRepository
from repositories.UserSessionRepository import UserSessionRepository


class RecordingUploader:
    def __init__(self, recording_repo: RecordingRepository,
                 raga_repo: RagaRepository,
                 user_activity_repo: UserActivityRepository,
                 user_session_repo: UserSessionRepository,
                 storage_repo: StorageRepository,
                 badge_awarder: BadgeAwarder,
                 audio_processor: AudioProcessor):
        self.recording_repo = recording_repo
        self.raga_repo = raga_repo
        self.user_activity_repo = user_activity_repo
        self.user_session_repo = user_session_repo
        self.storage_repo = storage_repo
        self.badge_awarder = badge_awarder
        self.audio_processor = audio_processor

    def upload(self, session_id, org_id, user_id, track, bucket):
        track_id = track["id"]
        with st.form("recording_uploader_form", clear_on_submit=True):
            uploaded_student_file = st.file_uploader("Choose an audio file", type=["m4a", "mp3"])
            original_date = st.date_input("Original File Date", value=None)  # Default value is None
            uploaded = st.form_submit_button("Recording", type="primary")

            upload_successful = False
            badge_awarded = False
            recording_id = -1
            recording_name = None
            if uploaded:
                if uploaded_student_file is None:
                    st.error("Please upload a recording..")
                    return False, False, -1, None

                # If the original date is provided, use it to create a datetime object,
                # otherwise use the current date and time.
                if original_date:
                    original_timestamp = datetime.datetime.combine(
                        original_date, datetime.datetime.min.time())
                else:
                    original_timestamp = datetime.datetime.now()

                with st.spinner("Please wait.."):
                    recording_data = uploaded_student_file.getbuffer()
                    file_hash = self.calculate_file_hash(recording_data)

                    # Check for duplicates
                    if self.recording_repo.is_duplicate_recording(user_id, track_id, file_hash):
                        st.error("You have already uploaded this recording.")
                        return "", -1, False, original_timestamp

                    # Upload the recording to storage repo and recording repo
                    recording_name, url, recording_id = self.add_recording(
                        user_id, track_id, recording_data, original_timestamp, file_hash, bucket)

                    st.audio(recording_name, format='audio/mp4')
                    # Success
                    additional_params = {
                        "track_name": track['track_name'],
                        "recording_name": recording_name,
                    }
                    self.user_activity_repo.log_activity(
                        user_id, session_id, ActivityType.UPLOAD_RECORDING, additional_params)
                    self.user_session_repo.update_last_activity_time(session_id)
                    badge_awarded = self.badge_awarder.award_user_badge(
                        org_id, user_id, UserBadges.FIRST_NOTE, original_timestamp)
                    upload_successful = True

        return upload_successful, badge_awarded, recording_id, recording_name

    def add_recording(self, user_id, track_id, recording_data, timestamp, file_hash, bucket):
        recording_name = f"{user_id}-{track_id}-{timestamp.strftime('%Y%m%d%H%M%S')}.m4a"
        blob_name = f'{bucket}/{recording_name}'
        blob_url = self.storage_repo.upload_blob(recording_data, blob_name)
        self.storage_repo.download_blob(blob_url, recording_name)
        duration = self.audio_processor.calculate_audio_duration(recording_name)
        recording_id = self.recording_repo.add_recording(
            user_id, track_id, blob_name, blob_url, timestamp, duration, file_hash, bucket)
        return recording_name, blob_url, recording_id

    def analyze_recording(self, track, track_audio_path, recording_name):
            offset = self.get_offset(track)
            distance = self.get_audio_distance(track_audio_path, recording_name)
            offset_corrected_distance = distance - offset
            student_notes = self.get_filtered_student_notes(recording_name)
            track_notes = self.raga_repo.get_notes(track['ragam_id'])
            error_notes, missing_notes = self.audio_processor.error_and_missing_notes(
                track_notes, student_notes)
            score = self.audio_processor.distance_to_score(
                offset_corrected_distance, 0, offset)
            analysis, off_notes = self.audio_processor.generate_note_analysis(
                error_notes, missing_notes)
            return distance, score, analysis

    @staticmethod
    def calculate_file_hash(recording_data):
        return hashlib.md5(recording_data).hexdigest()

    @staticmethod
    def get_offset(track):
        # TODO: control it via settings
        base = 1.1
        multiplier = base ** (track['level']-1)
        return int(round(multiplier * track['offset']))

    def get_audio_distance(self, track_file, student_path):
        return self.audio_processor.compare_audio(track_file, student_path)

    def get_filtered_student_notes(self, student_path):
        student_notes = self.audio_processor.get_notes(student_path)
        return self.audio_processor.filter_consecutive_notes(student_notes)

