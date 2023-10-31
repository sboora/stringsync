import datetime
from abc import ABC

import pandas as pd
import hashlib
import librosa
import requests
import streamlit as st
import os
import json
from streamlit_lottie import st_lottie
from enums.ActivityType import ActivityType
from enums.Badges import Badges
from enums.Features import Features
from enums.Settings import Settings, Portal
from notations.NotationBuilder import NotationBuilder
from portals.BasePortal import BasePortal
from core.AudioProcessor import AudioProcessor


class StudentPortal(BasePortal, ABC):
    def __init__(self):
        super().__init__()
        self.audio_processor = AudioProcessor()

    def get_portal(self):
        return Portal.STUDENT

    def get_title(self):
        return f"{self.get_app_name()} Student Portal"

    def get_icon(self):
        return "🎶"

    def get_tab_dict(self):
        tabs = [
            ("🎤 Record", self.record),
            ("📥 Submissions", self.submissions),
            ("📊 Progress Dashboard", self.progress_dashboard),
            ("🏆 Badges", self.badges),
            ("⏲️ Practice Log", self.practicelog),
            ("🗂️ Sessions", self.sessions) if self.is_feature_enabled(
                Features.STUDENT_PORTAL_SHOW_USER_SESSIONS) else None,
            ("📊 Activities", self.activities) if self.is_feature_enabled(
                Features.STUDENT_PORTAL_SHOW_USER_ACTIVITY) else None
        ]
        return {tab[0]: tab[1] for tab in tabs if tab}

    def show_introduction(self):
        st.write("""
            ### What Can You Do Here? 🎻

            1. **Listen to Tracks**: Browse through a curated list of tracks that suit your musical taste and skill level.
            2. **Record Performances**: Record your own renditions of these tracks and get instant feedback.
            3. **Progress Dashboard**: Track your practice time, number of tracks completed, and other key metrics.
            4. **Badges**: Earn badges for reaching milestones and accomplishing challenges.
        """)

        if not self.user_logged_in():
            st.write("""
                ### Why Choose GuruShishya? 🌟

                - **Personalized Learning**: Customize your learning journey according to your preferences and skill level.
                - **Instant Feedback**: Get real-time, data-driven feedback on your performances to know where you stand.
                - **Progress Tracking**: Visualize your growth over time with easy-to-understand charts and metrics.
                - **Achievements and Badges**: Get rewarded for your hard work and dedication with exciting badges.
            """)

        st.write(
            "Ready to dive into your musical journey? Scroll down to explore all the exciting features available to "
            "you! "
        )

    def show_animations(self):
        # Center-aligned, bold text with cursive font, improved visibility, and spacing
        st.markdown("""
            <h1 style='text-align: center; letter-spacing: 0.10px; font-family: cursive; font-size: 24px; font-weight: bold;'>
                <span style='color: red;'>C</span>
                <span style='color: orange;'>o</span>
                <span style='color: darkorange;'>n</span>
                <span style='color: green;'>g</span>
                <span style='color: blue;'>r</span>
                <span style='color: indigo;'>a</span>
                <span style='color: violet;'>t</span>
                <span style='color: red;'>u</span>
                <span style='color: orange;'>l</span>
                <span style='color: darkorange;'>a</span>
                <span style='color: green;'>t</span>
                <span style='color: blue;'>i</span>
                <span style='color: indigo;'>o</span>
                <span style='color: violet;'>n</span>
                <span style='color: red;'>s</span>
                🎉🎇
            </h1>
        """, unsafe_allow_html=True)

        st.markdown("""
            <h2 style='text-align: center; letter-spacing: 0.5px; font-family: cursive; font-size: 20spx;'>
                <span style='color: red;'>Y</span>
                <span style='color: orange;'>o</span>
                <span style='color: darkorange;'>u</span>
                <span style='color: green;'>'</span>
                <span style='color: blue;'>v</span>
                <span style='color: indigo;'>e</span>
                <span style='color: violet;'>&nbsp;&nbsp;</span>
                <span style='color: red;'>e</span>
                <span style='color: orange;'>a</span>
                <span style='color: darkorange;'>r</span>
                <span style='color: green;'>n</span>
                <span style='color: blue;'>e</span>
                <span style='color: indigo;'>d</span>
                <span style='color: violet;'>&nbsp;&nbsp;</span>
                <span style='color: red;'>a</span>
                <span style='color: orange;'>&nbsp;&nbsp;</span>
                <span style='color: darkorange;'>n</span>
                <span style='color: green;'>e</span>
                <span style='color: blue;'>w</span>
                <span style='color: indigo;'>&nbsp;&nbsp;</span>
                <span style='color: violet;'>b</span>
                <span style='color: red;'>a</span>
                <span style='color: orange;'>d</span>
                <span style='color: darkorange;'>g</span>
                <span style='color: green;'>e</span>
            </h2>
        """, unsafe_allow_html=True)

        # Load and center the Lottie animation
        byte_data = self.storage_repo.download_blob_by_name(f"animations/giftbox.json")
        lottie_json = json.loads(byte_data.decode('utf-8'))

        col1, col2, col3 = st.columns([1, 6, 1])

        with col2:
            st_lottie(lottie_json, speed=1, width=300, height=150, loop=True, quality='high', key="badge_awarded")

    def record(self):
        track = self.filter_tracks()
        if not track:
            return

        self.create_track_headers()

        # Download and save the audio files to temporary locations
        track_audio_path = self.download_to_temp_file_by_url(track['track_path'])

        col1, col2, col3 = st.columns([5, 5, 5])
        with col1:
            self.display_track_files(track_audio_path)
            track_notes = self.raga_repo.get_notes(track['ragam_id'])
        with col2:
            recording_name, recording_id, is_success = \
                self.handle_file_upload(self.get_user_id(), track['id'])
            if is_success:
                additional_params = {
                    "Track": track['name'],
                    "Recording": recording_name,
                }
                self.user_activity_repo.log_activity(self.get_user_id(),
                                                     ActivityType.UPLOAD_RECORDING,
                                                     additional_params)
                self.user_session_repo.update_last_activity_time(self.get_session_id())
        with col3:
            if is_success:
                score, analysis = self.display_student_performance(
                    track_audio_path, recording_name, track_notes, track['offset'])
                self.recording_repo.update_score_and_analysis(recording_id, score, analysis)
                badge_awarded = self.award_badge()
                if badge_awarded:
                    self.show_animations()

        self.recordings(track['id'])
        if is_success:
            os.remove(recording_name)

    @staticmethod
    def show_notations(track):
        notation_builder = NotationBuilder(track, track['notation_path'])
        track_notes = notation_builder.display_notation()
        return track_notes

    @staticmethod
    def display_recordings_header():
        st.markdown("<h3 style='text-align: center; margin-bottom: 0;'>Recordings</h3>", unsafe_allow_html=True)
        st.markdown("<hr style='height:2px; margin-top: 0; border-width:0; background: lightblue;'>",
                    unsafe_allow_html=True)

    def recordings(self, track_id):
        self.display_recordings_header()
        recordings = self.recording_repo.get_recordings_by_user_id_and_track_id(
            self.get_user_id(), track_id)

        if not recordings:
            st.info("No recordings found.")
            return

        # Create a DataFrame to hold the recording data
        df = pd.DataFrame(recordings)
        column_widths = [20, 20, 20, 20, 20]
        self.build_header(column_names=["Track", "Remarks", "Score", "Analysis", "Time"],
                          column_widths=column_widths)

        # Loop through each recording and create a table row
        for index, recording in df.iterrows():
            col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])
            if recording['blob_url']:
                filename = self.storage_repo.download_blob_by_name(recording['blob_name'])
                col1.write("")
                col1.audio(filename, format='core/m4a')
            else:
                col1.write("No core data available.")

            col2.write("")
            col2.markdown(
                f"<div style='padding-top:5px;color:black;font-size:14px;'>{recording.get('remarks', 'N/A')}</div>",
                unsafe_allow_html=True)
            col3.write("")
            col3.markdown(
                f"<div style='padding-top:5px;color:black;font-size:14px;'>{recording.get('score')}</div>",
                unsafe_allow_html=True)
            col4.write("")
            col4.markdown(
                f"<div style='padding-top:5px;color:black;font-size:14px;'>{recording.get('analysis', 'N/A')}</div>",
                unsafe_allow_html=True)
            formatted_timestamp = recording['timestamp'].strftime('%I:%M %p, ') + self.ordinal(
                int(recording['timestamp'].strftime('%d'))) + recording['timestamp'].strftime(' %b, %Y')
            col5.write("")
            col5.markdown(f"<div style='padding-top:5px;color:black;font-size:14px;'>{formatted_timestamp}</div>",
                          unsafe_allow_html=True)

    def get_audio_data(self, recording):
        if recording['blob_url']:
            filename = self.storage_repo.download_blob_by_name(recording['blob_name'])
            return f"<audio controls><source src='{filename}' type='audio/m4a'></audio>"
        return "No core data available."

    def format_timestamp(self, timestamp):
        formatted_timestamp = timestamp.strftime('%I:%M %p, ') + self.ordinal(
            int(timestamp.strftime('%d'))) + timestamp.strftime(' %b, %Y')
        return formatted_timestamp

    def submissions(self):
        # Fetch submissions from the database
        submissions = self.portal_repo.get_submissions_by_user_id(self.get_user_id())

        if not submissions:
            st.info("No submissions found.")
            return
        column_widths = [16.66, 16.66, 16.66, 16.66, 16.66, 16.66]
        self.build_header(
            column_names=["Tack Name", "Track", "Recording", "Teacher Remarks", "System Remarks", "Score"],
            column_widths=column_widths)

        # Display submissions
        for submission in submissions:
            col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])

            col1.write("")
            col1.markdown(
                f"<div style='padding-top:5px;color:black;font-size:14px;text-align:center;'>{submission['track_name']}</div>",
                unsafe_allow_html=True)

            col2.write("")
            if submission['track_audio_url']:
                track_audio = self.storage_repo.download_blob_by_url(submission['track_audio_url'])
                col2.audio(track_audio, format='core/m4a')
            else:
                col2.warning("No audio available.")

            col3.write("")
            if submission['recording_audio_url']:
                track_audio = self.storage_repo.download_blob_by_url(submission['recording_audio_url'])
                col3.audio(track_audio, format='core/m4a')
            else:
                col3.warning("No audio available.")

            col4.write("")
            col4.markdown(
                f"<div style='padding-top:5px;color:black;font-size:14px;'>{submission.get('teacher_remarks', 'N/A')}</div>",
                unsafe_allow_html=True)

            col5.write("")
            col5.markdown(
                f"<div style='padding-top:5px;color:black;font-size:16px;'>{submission.get('system_remarks', 'N/A')}</div>",
                unsafe_allow_html=True)

            col6.write("")
            col6.markdown(
                f"<div style='padding-top:5px;color:black;font-size:14px;text-align:center;'>{submission.get('score', 'N/A')}</div>",
                unsafe_allow_html=True)

    def assignments(self):
        pass

    def progress_dashboard(self):
        st.write("")
        self.display_tracks()
        st.write("")
        self.show_line_graph()

    def display_tracks(self):
        tracks = self.get_tracks()
        column_widths = [20, 20, 20, 20, 20]
        self.build_header(
            column_names=["Track", "Number of Recordings", "Average Score", "Min Score", "Max Score"],
            column_widths=column_widths)
        for track_detail in tracks:
            row_data = {
                "Track": track_detail['track']['name'],
                "Number of Recordings": track_detail['num_recordings'],
                "Average Score": track_detail['avg_score'],
                "Min Score": track_detail['min_score'],
                "Max Score": track_detail['max_score']
            }
            self.build_row(row_data=row_data, column_widths=column_widths)

    def show_line_graph(self):
        user_id = self.get_user_id()
        time_series_data = self.recording_repo.get_time_series_data(user_id)
        if not time_series_data:
            st.info("No data available.")
            return

        formatted_dates = [point['date'].strftime('%m/%d') for point in time_series_data]
        total_durations = [max(0, int(point['total_duration'])) / 60 for point in time_series_data if
                           point['total_duration'] is not None]
        total_tracks = [int(point['total_tracks']) for point in time_series_data]

        # Create a DataFrame for Total Duration
        df_duration = pd.DataFrame({
            'Date': formatted_dates,
            'Total Duration (minutes)': total_durations
        })

        # Create a DataFrame for Total Tracks
        df_tracks = pd.DataFrame({
            'Date': formatted_dates,
            'Total Tracks': total_tracks
        })

        # Display the charts side by side
        col1, col2 = st.columns(2)
        col1.line_chart(df_duration.set_index('Date'))
        col2.line_chart(df_tracks.set_index('Date'))

    def get_tracks(self):
        # Fetch all tracks and track statistics for this user
        tracks = self.track_repo.get_all_tracks()
        track_statistics = self.recording_repo.get_track_statistics_by_user(self.get_user_id())

        # Create a dictionary for quick lookup of statistics by track_id
        stats_dict = {stat['track_id']: stat for stat in track_statistics}

        # Build track details list using list comprehension
        track_details = [
            {
                'track': track,
                'num_recordings': stats_dict.get(track['id'], {}).get('num_recordings', 0),
                'avg_score': stats_dict.get(track['id'], {}).get('avg_score', 0),
                'min_score': stats_dict.get(track['id'], {}).get('min_score', 0),
                'max_score': stats_dict.get(track['id'], {}).get('max_score', 0)
            }
            for track in tracks
        ]

        return track_details

    def filter_tracks(self):
        ragas = self.raga_repo.get_all_ragas()
        filter_options = self.fetch_filter_options(ragas)

        # Create three columns
        col1, col2, col3 = st.columns(3)

        level = col1.selectbox("Filter by Level", ["All"] + filter_options["Level"])
        raga = col2.selectbox("Filter by Ragam", ["All"] + filter_options["Ragam"])
        tags = col3.multiselect("Filter by Tags", ["All"] + filter_options["Tags"], default=["All"])

        raga_id = None if raga == "All" else ragas[raga]

        tracks = self.track_repo.search_tracks(
            ragam_id=None if raga == "All" else raga_id,
            level=None if level == "All" else level,
            tags=None if tags == ["All"] else tags
        )

        if not tracks:
            return None

        selected_track_name = self.get_selected_track_name(tracks)

        # Update the last selected track in session state
        if st.session_state['last_selected_track'] != selected_track_name and \
                selected_track_name != "Select a Track":
            # Log the track selection change
            self.log_track_selection_change(selected_track_name)

        st.session_state['last_selected_track'] = selected_track_name

        return self.get_selected_track_details(tracks, selected_track_name)

    def log_track_selection_change(self, selected_track_name):
        user_id = self.get_user_id()
        additional_params = {
            "Track": selected_track_name,
        }
        self.user_activity_repo.log_activity(user_id, ActivityType.PLAY_TRACK, additional_params)
        self.user_session_repo.update_last_activity_time(self.get_session_id())

    def fetch_filter_options(self, ragas):
        return {
            "Level": self.track_repo.get_all_levels(),
            "Ragam": [raga['name'] for raga in ragas],
            "Tags": self.track_repo.get_all_tags()
        }

    @staticmethod
    def get_selected_track_name(tracks):
        track_names = [track['name'] for track in tracks]
        return st.selectbox("Select a Track", ["Select a Track"] + track_names, index=0)

    @staticmethod
    def get_selected_track_details(tracks, selected_track_name):
        return next((track for track in tracks if track['name'] == selected_track_name), None)

    @staticmethod
    def create_track_headers():
        col1, col2, col3 = st.columns([5, 5, 5])
        custom_style = "<style>h2 {font-size: 20px;}</style>"
        divider = "<hr style='height:1px; margin-top: 0; border-width:0; background: lightblue;'>"

        with col1:
            st.markdown(f"{custom_style}<h2>Track</h2>{divider}", unsafe_allow_html=True)
        with col2:
            st.markdown(f"{custom_style}<h2>Upload</h2>{divider}", unsafe_allow_html=True)
        with col3:
            st.markdown(f"{custom_style}<h2>Analysis</h2>{divider}", unsafe_allow_html=True)

    @staticmethod
    def display_track_files(track_file):
        st.audio(track_file, format='core/m4a')

    def handle_file_upload(self, user_id, track_id):
        with st.form("recording_uploader_form", clear_on_submit=True):
            uploaded_student_file = st.file_uploader("", type=["m4a", "mp3"])
            original_date = st.date_input("Original File Date", value=None)  # Default value is None
            uploaded = st.form_submit_button("Upload", type="primary")

            if uploaded:
                if uploaded_student_file is None:
                    st.error("File is required.")
                    return None, -1, False

                # If the original date is provided, use it to create a datetime object,
                # otherwise use the current date and time.
                if original_date:
                    original_timestamp = datetime.datetime.combine(original_date, datetime.datetime.min.time())
                else:
                    original_timestamp = datetime.datetime.now()

                recording_name = f"{track_id}-{original_timestamp.strftime('%Y%m%d%H%M%S')}.m4a"
                recording_data = uploaded_student_file.getbuffer()
                file_hash = self.calculate_file_hash(recording_data)

                # Check for duplicates
                if self.recording_repo.is_duplicate_recording(user_id, track_id, file_hash):
                    st.error("You have already uploaded this recording.")
                    return recording_name, -1, False

                # Save the recording
                self.save_recording(recording_data, recording_name)

                # Calculate duration
                duration = self.calculate_audio_duration(recording_name)

                # Upload the recording to storage repo and recording repo
                url, recording_id = self.add_recording(user_id,
                                                       track_id,
                                                       recording_name,
                                                       original_timestamp,
                                                       duration,
                                                       file_hash)
                st.audio(recording_name, format='core/m4a')
                return recording_name, recording_id, True
        return None, -1, False

    @staticmethod
    def calculate_file_hash(recording_data):
        return hashlib.md5(recording_data).hexdigest()

    @staticmethod
    def calculate_audio_duration(student_path):
        y, sr = librosa.load(student_path)
        return librosa.get_duration(y=y, sr=sr)

    @staticmethod
    def save_recording(recording_data, student_path):
        with open(student_path, "wb") as f:
            f.write(recording_data)

    def add_recording(self, user_id, track_id, recording_name, timestamp, duration, file_hash):
        recording_path = f'{self.get_recordings_bucket()}/{recording_name}'
        url = self.storage_repo.upload_file(recording_name, recording_path)
        recording_id = self.recording_repo.add_recording(
            user_id, track_id, recording_path, url, timestamp, duration, file_hash)
        return url, recording_id

    def display_student_performance(self, track_file, student_path, track_notes, offset_distance):
        if not student_path:
            return -1, ""

        distance = self.get_audio_distance(track_file, student_path, offset_distance)
        track_notes = self.get_filtered_track_notes(track_file, track_notes)
        student_notes = self.get_filtered_student_notes(student_path)
        error_notes, missing_notes = self.audio_processor.error_and_missing_notes(track_notes, student_notes)
        score = self.audio_processor.distance_to_score(distance)
        analysis = self.display_score_and_analysis(score, error_notes, missing_notes)
        return score, analysis

    def get_audio_distance(self, track_file, student_path, offset_distance):
        distance = self.audio_processor.compare_audio(track_file, student_path)
        return distance - offset_distance

    def get_filtered_track_notes(self, track_file, track_notes):
        if len(track_notes) == 0:
            track_notes = self.audio_processor.get_notes(track_file)
            track_notes = self.audio_processor.filter_consecutive_notes(track_notes)
        return track_notes

    def get_filtered_student_notes(self, student_path):
        student_notes = self.audio_processor.get_notes(student_path)
        return self.audio_processor.filter_consecutive_notes(student_notes)

    def display_score_and_analysis(self, score, error_notes, missing_notes):
        self.display_similarity_score(score)
        analysis = self.generate_note_analysis(error_notes, missing_notes)
        st.info(analysis)
        encouragement_message = self.generate_message(score)
        st.info(encouragement_message)
        return analysis + encouragement_message

    @staticmethod
    def display_similarity_score(score):
        message = f"Similarity score: {score}\n"
        if score <= 3:
            st.error(message)
        elif score <= 7:
            st.warning(message)
        else:
            st.success(message)

    def generate_note_analysis(self, error_notes, missing_notes):
        error_dict = self.group_notes_by_first_letter(error_notes)
        missing_dict = self.group_notes_by_first_letter(missing_notes)

        message = ""
        if error_dict == missing_dict:
            message += "Your recording had all the notes that the track had.\n"
        else:
            message += self.correlate_notes(error_dict, missing_dict)
        return message

    @staticmethod
    def group_notes_by_first_letter(notes):
        note_dict = {}
        for note in notes:
            first_letter = note[0]
            note_dict.setdefault(first_letter, []).append(note)
        return note_dict

    @staticmethod
    def correlate_notes(error_dict, missing_dict):
        message = ""
        for first_letter, error_note_list in error_dict.items():
            if first_letter in missing_dict:
                for error_note in error_note_list:
                    message += f"Play {missing_dict[first_letter][0]} instead of {error_note}\n"
            else:
                for error_note in error_note_list:
                    message += f"You played the note {error_note}, however that is not present in the track\n"

        for first_letter, missing_note_list in missing_dict.items():
            if first_letter not in error_dict:
                for missing_note in missing_note_list:
                    message += f"You missed playing the note {missing_note}\n"
        return message

    @staticmethod
    def generate_message(score):
        if score <= 3:
            return "Keep trying. You can do better!"
        elif score <= 7:
            return "Good job. You are almost there!"
        elif score <= 9:
            return "Great work. Keep it up!"
        else:
            return "Excellent! You've mastered this track!"

    @staticmethod
    def load_lottie_url(url: str):
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()

    def badges(self):
        badges = self.user_achievement_repo.get_user_badges(self.get_user_id())

        if badges:  # If there are badges
            cols = st.columns(5)

            for i, badge in enumerate(badges):
                with cols[i % 5]:  # Loop through columns
                    # Display the badge icon from the badge folder
                    badge_url = f"{self.get_badges_bucket()}/{badge}.png"
                    filename = self.download_to_temp_file_by_name(badge_url)
                    st.image(filename, width=200)

            st.markdown("</div>", unsafe_allow_html=True)
        else:  # If there are no badges
            st.markdown("### No Badges Yet 🎖️")
            st.markdown("""
                **What Can You Do to Earn Badges?**

                1. **Listen to Tracks**: The more you listen, the more you learn.
                2. **Record Performances**: Every recording earns you points towards your next badge.
                3. **Keep Practicing**: The more points you earn, the more badges you unlock.

                Start by listening to a track and making your first recording today!
            """)

    def award_badge(self):
        # Fetch the total number of tracks and total duration for the user
        min_score = self.settings_repo.get_setting(self.get_org_id(),
                                                   Settings.MIN_SCORE_FOR_EARNING_BADGES)
        total_tracks = self.recording_repo.get_total_recordings(self.get_user_id(), min_score)
        total_duration = self.recording_repo.get_total_duration(self.get_user_id(), min_score)

        # Mapping thresholds to badges
        track_badges = [
            (1, Badges.FIRST_NOTE),
            (20, Badges.RISING_STAR),
            (40, Badges.FAST_LEARNER),
            (75, Badges.SONG_BIRD),
            (100, Badges.MAESTRO),
        ]

        duration_badges = [
            (60, Badges.PRACTICE_MAKES_PERFECT),
            (120, Badges.PERFECT_PITCH),
            (300, Badges.MUSIC_WIZARD),
            (600, Badges.ROCKSTAR),
            (1000, Badges.VIRTUOSO),
        ]

        # Award track badges
        badge_awarded = False
        for threshold, badge in track_badges:
            if total_tracks >= threshold:
                badge_awarded, _ = self.user_achievement_repo.award_badge(self.get_user_id(), badge)

        # Award duration badges
        for threshold, badge in duration_badges:
            if total_duration >= threshold:
                badge_awarded, _ = self.user_achievement_repo.award_badge(self.get_user_id(), badge)

        return badge_awarded

    def practicelog(self):
        with st.form("log_practice_time_form"):
            practice_date = st.date_input("Practice Date")
            practice_minutes = st.selectbox("Minutes Practiced", [i for i in range(15, 61)])
            submit = st.form_submit_button("Log Practice", type="primary")
            if submit:
                user_id = self.get_user_id()
                self.user_practice_log_repo.log_practice(user_id, practice_date, practice_minutes)
                st.success(f"Logged {practice_minutes} minutes of practice on {practice_date}.")

    @staticmethod
    def ordinal(n):
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
        if 11 <= (n % 100) <= 13:
            suffix = 'th'
        return str(n) + suffix
