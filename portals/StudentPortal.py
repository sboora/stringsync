import datetime
from abc import ABC

import pandas as pd
import hashlib
import librosa
import streamlit as st
import os
import re

from portals.BasePortal import BasePortal
from repositories.RecordingRepository import RecordingRepository
from repositories.StorageRepository import StorageRepository
from repositories.TrackRepository import TrackRepository
from core.AudioProcessor import AudioProcessor


class StudentPortal(BasePortal, ABC):
    def __init__(self):
        super().__init__()
        self.track_repo = TrackRepository()
        self.recording_repo = RecordingRepository()
        self.storage_repo = StorageRepository("stringsync")
        self.audio_processor = AudioProcessor()

    def get_tab_dict(self):
        return {
            "🎵 Tracks": self.display_tracks,
            "🎤 Record": self.record,
            " Performances": self.performances,
            "📝 Assignments": self.assignments,
        }

    def assignments(self):
        pass

    def show_introduction(self):
        st.write("""
            Welcome to the **Student Portal** of String Sync, your personal space for musical growth and exploration. 
            This platform is designed to offer you a comprehensive and interactive music learning experience.

            ### How Does it Work?
            1. **Listen to Tracks**: Explore a wide range of tracks to find the ones that resonate with you.
            2. **Record Performances**: Once you've practiced, record your performances for these tracks.
            3. **Work on Assignments**: Complete assignments given by your teacher and submit them for review.

            ### Why Use String Sync for Learning?
            - **Personalized Learning**: Tailor your learning experience by choosing tracks that suit your taste and skill level.
            - **Instant Feedback**: Receive immediate, data-driven feedback on your performances.
            - **Track Your Progress**: Keep an eye on your improvement over time with easy-to-understand metrics.
            - **Interactive Assignments**: Engage with assignments that challenge you and help you grow as a musician.

            Ready to dive in? Use the sidebar to explore all the exciting features available on your Student Portal!
        """)

    @staticmethod
    def create_track_headers():
        """
        Create headers for the track section.
        """
        col1, col2, col3 = st.columns([3, 3, 5])
        custom_style = "<style>h2 {font-size: 20px;}</style>"
        divider = "<hr style='height:1px; margin-top: 0; border-width:0; background: grey;'>"

        with col1:
            st.markdown(f"{custom_style}<h2>Track</h2>{divider}", unsafe_allow_html=True)
        with col2:
            st.markdown(f"{custom_style}<h2>Upload</h2>{divider}", unsafe_allow_html=True)
        with col3:
            st.markdown(f"{custom_style}<h2>Analysis</h2>{divider}", unsafe_allow_html=True)

    @staticmethod
    def display_track_files(track_file):
        """
        Display the teacher's track files.

        Parameters:
            track_file (str): The path to the track file.
        """
        st.write("")
        st.write("")
        st.audio(track_file, format='core/m4a')

    @staticmethod
    def display_notation_pdf_link():
        """
        Display a link to the musical notation PDF for the track and an option to download it.
        """
        notation_pdf_path = "notations/Practice Worksheet 1.pdf"

        # Provide a download button for the PDF
        with open(notation_pdf_path, "rb") as f:
            pdf_bytes = f.read()
        st.download_button(
            label="Download Notations",
            data=pdf_bytes,
            file_name="Practice Worksheet 1.pdf",
            mime="application/pdf",
            type="primary"
        )

    @staticmethod
    def download_track(track):
        # Provide a download button for the original core file
        st.write("")
        with open(track, "rb") as f:
            audio_bytes = f.read()
        st.download_button(
            label="Download track",
            data=audio_bytes,
            file_name=track,
            mime="core/mp3",
            type="primary"
        )

    def handle_file_upload(self, user_id, track_id):
        student_path = ""
        recording_id = -1
        uploaded_student_file = st.file_uploader("", type=["m4a", "wav", "mp3"])
        if uploaded_student_file is not None:
            timestamp = datetime.datetime.now()
            student_path = f"{user_id}-{track_id}-{timestamp}.m4a"

            # Read the uploaded file into a bytes buffer
            recording_data = uploaded_student_file.getbuffer()

            # Calculate the hash of the file
            file_hash = hashlib.md5(recording_data).hexdigest()

            # Check if a recording with the same hash already exists
            if self.recording_repo.is_duplicate_recording(user_id, track_id, file_hash):
                st.error("You have already uploaded this recording.")
                return student_path, recording_id, False

            # Calculate duration
            with open(student_path, "wb") as f:
                f.write(recording_data)

            y, sr = librosa.load(student_path)
            duration = librosa.get_duration(y=y, sr=sr)

            # Store in database
            storage_repository = StorageRepository("stringsync")
            url = storage_repository.upload_file(student_path, student_path)
            recording_id = self.recording_repo.add_recording(
                self.get_user_id(), track_id, student_path, url, timestamp, duration, file_hash)
            st.audio(student_path, format='core/m4a')

        return student_path, recording_id, True

    def display_student_performance(self, track_file, student_path, track_notes, offset_distance):
        """
        Display the student's performance score and remarks.

        Parameters:
            track_file (str): The path to the track file.
            student_path (str): The path to the student's recorded or uploaded file.
            offset_distance: The distance between the track file and its reference.
            track_notes: The unique notes in the track
        """
        st.write("")
        st.write("")
        score = -1
        analysis = ""
        if student_path:
            distance = self.audio_processor.compare_audio(track_file, student_path)
            print("Distance: ", distance)
            relative_distance = distance - offset_distance
            if len(track_notes) == 0:
                track_notes = self.audio_processor.get_notes(track_file)
                track_notes = self.audio_processor.filter_consecutive_notes(track_notes)
            print("track notes:", track_notes)
            student_notes = self.audio_processor.get_notes(student_path)
            print(student_notes)
            student_notes = self.audio_processor.filter_consecutive_notes(student_notes)
            print("Student notes:", student_notes)
            error_notes, missing_notes = self.audio_processor.error_and_missing_notes(
                track_notes, student_notes)
            score = self.audio_processor.distance_to_score(relative_distance)
            analysis = self.display_score_and_analysis(score, error_notes, missing_notes)
            os.remove(student_path)

        return score, analysis

    @staticmethod
    def display_score_and_analysis(score, error_notes, missing_notes):
        """
        Display the student's score and any error or missing notes.

        Parameters:
            score (int): The student's performance score.
            error_notes (list): The list of error notes.
            missing_notes (list): The list of missing notes.
        """
        message = f"Similarity score: {score}\n"
        if score <= 3:
            st.error(message)
        elif score <= 7:
            st.warning(message)
        elif score <= 9:
            st.success(message)
        else:
            st.success(message)

        # Create dictionaries to hold the first alphabet of each note and the corresponding notes
        error_dict = {}
        missing_dict = {}

        for note in error_notes:
            first_letter = note[0]
            if first_letter not in error_dict:
                error_dict[first_letter] = []
            error_dict[first_letter].append(note)

        for note in missing_notes:
            first_letter = note[0]
            if first_letter not in missing_dict:
                missing_dict[first_letter] = []
            missing_dict[first_letter].append(note)

        # Correlate error notes with missing notes
        analysis = ""
        message = "Note analysis:\n"
        if error_dict == missing_dict:
            message += f"Your recording had all the notes that the track had.\n"
        else:
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
        st.info(message)
        analysis += message
        message = ""
        if score <= 3:
            message += "Keep trying. You can do better!"
            st.error(message)
        elif score <= 7:
            message += "Good job. You are almost there!"
            st.warning(message)
        elif score <= 9:
            message += "Great work. Keep it up!"
            st.success(message)
        else:
            message += "Excellent! You've mastered this track!"
            st.success(message)
        analysis += message
        return analysis

    def display_notation(self, track, notation_path):
        unique_notes = []
        if os.path.exists(notation_path):
            with open(notation_path, "r") as f:
                notation_content = f.read()
            st.markdown(f"**Notation:**")
            self.display_notes_with_subscript(notation_content)

            # Extract and filter notes
            notes = re.split(r'[,\s_]+', notation_content.replace('b', '').strip())
            valid_notes = {'S', 'R1', 'R2', 'R3', 'G1', 'G2', 'G3', 'M1', 'M2', 'P', 'D1', 'D2', 'D3', 'N1', 'N2', 'N3'}
            unique_notes = list(set(notes).intersection(valid_notes))
        else:
            st.warning(f"No notation file found for track: {track}")
        return unique_notes

    @staticmethod
    def display_notes_with_subscript(notation_content):
        formatted_notes = ""
        buffer = ""
        bold_flag = False
        section_flag = False

        for char in notation_content:
            if char.isalpha() and char != 'b':
                buffer += char
            elif char == ':':
                buffer += char
            elif char.isdigit():
                buffer += char
            elif char == 'b':
                bold_flag = True
            else:
                if section_flag:
                    formatted_notes += f"<b>{buffer}</b>"
                    section_flag = False
                else:
                    if len(buffer) > 1:
                        note = f"{buffer[0]}<sub>{buffer[1:]}</sub>"
                    else:
                        note = buffer

                    if bold_flag:
                        formatted_notes += f"<b>{note}</b>"
                    else:
                        formatted_notes += note

                if char in ['_', ',', '\n', ' ']:
                    formatted_notes += char if char != '\n' else "<br>"

                buffer = ""
                bold_flag = False

            if buffer == "Section:":
                section_flag = True
                buffer = ""

        if buffer:
            if len(buffer) > 1:
                note = f"{buffer[0]}<sub>{buffer[1:]}</sub>"
            else:
                note = buffer

            if bold_flag:
                formatted_notes += f"<b>{note}</b>"
            else:
                formatted_notes += note

        st.markdown(f"<div style='font-size: 16px; font-weight: normal;'>{formatted_notes}</div>",
                    unsafe_allow_html=True)

    def display_tracks(self):
        tracks = self.get_tracks()
        # Create an empty DataFrame with the desired columns
        df = pd.DataFrame(columns=["Track Name", "Number of Recordings", "Average Score", "Min Score", "Max Score"])

        # Populate the DataFrame
        for track_detail in tracks:
            track_name = track_detail['track'][1]
            num_recordings = track_detail['num_recordings']
            avg_score = track_detail['avg_score']
            min_score = track_detail['min_score']
            max_score = track_detail['max_score']

            # Create a DataFrame for this row
            row_df = pd.DataFrame({
                "Track Name": [track_name],
                "Number of Recordings": [num_recordings],
                "Average Score": [avg_score],
                "Min Score": [min_score],
                "Max Score": [max_score]
            })

            # Append this track's details to the DataFrame
            df = pd.concat([df, row_df], ignore_index=True)

        # Display the table using Streamlit
        st.table(df)

    def get_tracks(self):
        # Fetch all tracks
        tracks = self.track_repo.get_all_tracks()  # Replace with your actual method to get all tracks

        # Fetch track statistics for this user
        track_statistics = self.recording_repo.get_track_statistics_by_user(self.get_user_id())

        # Initialize an empty list to hold track details
        track_details = []

        for track in tracks:
            track_id = track[0]  # Assuming the track object has an 'id' field

            # Find statistics for this track if available
            stats = next((item for item in track_statistics if item["track_id"] == track_id), None)

            # Append track details to the list
            if stats:
                track_details.append({
                    'track': track,
                    'num_recordings': stats['num_recordings'],
                    'avg_score': stats['avg_score'],
                    'min_score': stats['min_score'],
                    'max_score': stats['max_score']
                })
            else:
                track_details.append({
                    'track': track,
                    'num_recordings': 0,
                    'avg_score': 0,
                    'min_score': 0,
                    'max_score': 0
                })

        return track_details

    def record(self):
        # Fetch all levels, ragams, and tags
        all_levels = self.track_repo.get_all_levels()
        all_ragams = self.track_repo.get_all_ragams()
        all_tags = self.track_repo.get_all_tags()
        all_track_types = self.track_repo.get_all_track_types()

        # Create four columns
        col1, col2, col3, col4 = st.columns(4)

        # Place a dropdown in each column
        selected_track_type = col1.selectbox("Filter by Track Type", ["All"] + all_track_types)
        selected_level = col2.selectbox("Filter by Level", ["All"] + all_levels)
        selected_ragam = col3.selectbox("Filter by Ragam", ["All"] + all_ragams)
        selected_tags = col4.multiselect("Filter by Tags", ["All"] + all_tags, default=["All"])

        # Fetch tracks based on selected filters
        tracks = self.track_repo.search_tracks(
            ragam=None if selected_ragam == "All" else selected_ragam,
            level=None if selected_level == "All" else selected_level,
            tags=None if selected_tags == ["All"] else selected_tags,
            track_type=None if selected_track_type == "All" else selected_track_type,
        )
        if len(tracks) == 0:
            return

        # Convert tracks to a list of track names for the selectbox
        track_names = [track[1] for track in tracks]
        selected_track = st.selectbox("Select a Track", ["Select a Track"] + track_names, index=0)

        # Find the details of the selected track
        selected_track_details = next((track for track in tracks if track[1] == selected_track), None)
        if selected_track_details is None:
            return

        self.create_track_headers()
        # Use the selected track
        track_id = selected_track_details[0]
        track_name = selected_track_details[1]
        track_file = selected_track_details[2]
        track_ref_file = selected_track_details[3]
        notation_file = selected_track_details[4]
        offset_distance = self.audio_processor.compare_audio(track_file, track_ref_file)
        print("Offset:", offset_distance)

        student_recording = None
        col1, col2, col3 = st.columns([3, 3, 5])
        with col1:
            self.display_track_files(track_file)
            unique_notes = self.display_notation(selected_track, notation_file)
        with col2:
            student_recording, recording_id, is_success = self.handle_file_upload(self.get_user_id(), track_id)
        with col3:
            if is_success:
                score, analysis = self.display_student_performance(track_file, student_recording, unique_notes,
                                                                   offset_distance)
                self.update_score_and_analysis(recording_id, score, analysis)

        # List all recordings for the track
        st.write("")
        st.write("")
        st.write("")

    def performances(self):
        # Fetch all levels, ragams, and tags
        all_levels = self.track_repo.get_all_levels()
        all_ragams = self.track_repo.get_all_ragams()
        all_tags = self.track_repo.get_all_tags()
        all_track_types = self.track_repo.get_all_track_types()

        # Create four columns
        col1, col2, col3, col4 = st.columns(4)

        # Place a dropdown in each column
        selected_track_type = col1.selectbox(key="p_col1", label="Filter by Track Type", options=["All"] + all_track_types)
        selected_level = col2.selectbox(key="p_col2", label="Filter by Level", options=["All"] + all_levels)
        selected_ragam = col3.selectbox(key="p_col3", label="Filter by Ragam", options=["All"] + all_ragams)
        selected_tags = col4.multiselect(key="p_col4", label="Filter by Tags", options=["All"] + all_tags, default=["All"])

        # Fetch tracks based on selected filters
        tracks = self.track_repo.search_tracks(
            ragam=None if selected_ragam == "All" else selected_ragam,
            level=None if selected_level == "All" else selected_level,
            tags=None if selected_tags == ["All"] else selected_tags,
            track_type=None if selected_track_type == "All" else selected_track_type,
        )
        if len(tracks) == 0:
            return

        # Convert tracks to a list of track names for the selectbox
        track_names = [track[1] for track in tracks]
        selected_track = st.selectbox(key="p_st", label="Select a Track", options=["Select a Track"] + track_names, index=0)

        # Find the details of the selected track
        selected_track_details = next((track for track in tracks if track[1] == selected_track), None)
        if selected_track_details is None:
            return

        # Use the selected track
        track_id = selected_track_details[0]
        self.list_recordings(self.get_user_id(), track_id)

    def update_score_and_analysis(self, recording_id, score, analysis):
        self.recording_repo.update_score_and_analysis(recording_id, score, analysis)

    def list_recordings(self, user_id, track_id):
        # Center-align the subheader with reduced margin-bottom
        st.markdown("<h3 style='text-align: center; margin-bottom: 0;'>Performances</h3>", unsafe_allow_html=True)

        # Add a divider with reduced margin-top
        st.markdown(
            "<hr style='height:2px; margin-top: 0; border-width:0; background: lightblue;'>",
            unsafe_allow_html=True
        )

        recordings = self.recording_repo.get_recordings_by_user_id_and_track_id(user_id, track_id)

        if not recordings:
            st.write("No recordings found.")
            return

        # Create a DataFrame to hold the recording data
        df = pd.DataFrame(recordings)

        col1, col2, col3, col4, col5 = st.columns([3.5, 1, 3, 3, 2])

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
            col4.markdown(
                f"<div style='padding-top:5px;color:black;font-size:14px;'>{recording.get('remarks', 'N/A')}</div>",
                unsafe_allow_html=True)
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
