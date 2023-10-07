import librosa
import numpy as np
from fastdtw import fastdtw
from scipy.spatial.distance import cosine
import streamlit as st
from audio_recorder_streamlit import audio_recorder
import tempfile


def distance_to_score(distance, min_distance=0, max_distance=500):
    if distance <= min_distance:
        return 10
    elif distance >= max_distance:
        return 0
    else:
        return round(10 - ((distance - min_distance) / (max_distance - min_distance) * 10))


def extract_features(audio_path):
    y, sr = librosa.load(audio_path)
    chroma_stft = librosa.feature.chroma_stft(y=y, sr=sr)
    return chroma_stft


def compare_audio(teacher_path, student_path):
    teacher_features = extract_features(teacher_path)
    student_features = extract_features(student_path)

    distance, _ = fastdtw(teacher_features.T, student_features.T, dist=cosine)
    return distance


def audio_display(filename):
    # Generate a unique ID for the audio element
    audio_id = st.empty().audio(filename, format='audio/wav')

    # Function to handle the button click event
    def play_audio():
        with open(filename, 'rb') as audio_file:
            audio_bytes = audio_file.read()
        audio_id.audio(audio_bytes, format='audio/wav')


def record_audio(text):
    # Display the audio recorder
    audio_data = audio_recorder(
        key=text,
        text="",
        energy_threshold=0.01,
        pause_threshold=5,
        neutral_color="#303030",
        recording_color="#de1212",
        icon_name="microphone",
        icon_size="2x",
    )

    return audio_data


def main():
    st.set_page_config(layout='wide')
    st.header('**String Sync**', divider='rainbow')
    st.markdown(
        """
        String Sync is an innovative platform designed to help music teachers and students enhance their learning experience. By leveraging advanced audio analysis, this app allows you to compare your musical performance with a reference recording, providing you with a quantifiable score based on the similarity.

        ### How Does it Work?
        1. **Listen to the Lesson**: Each lesson comes with a reference audio file. Listen to it carefully to understand what you need to achieve.
        2. **Upload Your Recording**: Record your own performance and upload it here.
        3. **Get Your Score**: Our advanced algorithm will compare your performance with the reference audio and give you a score based on how closely they match.

        ### Why Use String Sync?
        - **Objective Feedback**: Get unbiased, data-driven feedback on your performance.
        - **Progress Tracking**: Keep track of your scores to monitor your improvement over time.
        - **Flexible**: Suitable for any instrument and skill level.

        Ready to get started? Scroll down to find your lesson and upload your performance!
        """
    )
    # Sidebar for Student Login
    st.sidebar.header("Student Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username and password:  # Add your authentication logic here
            st.sidebar.success(f"Welcome, {username}!")
        else:
            st.sidebar.error("Invalid credentials")
    # Assuming teacher_files is a list of all teacher audio files
    lessons = ["lessons/w1_l1"]

    # Create a header
    col1, col2, col3, col4, col5 = st.columns([2, 1, 2, 2, 3])
    with col1:
        st.subheader('Lesson', divider='rainbow')
    with col2:
        st.subheader('Record', divider='rainbow')
    with col3:
        st.subheader('Play', divider='rainbow')
    with col4:
        st.subheader('Remarks', divider='rainbow')
    with col5:
        st.subheader('Notation', divider='rainbow')

    # Compare it with the reference as build an offset
    lesson_notes = []
    student_notes = []
    for lesson in lessons:
        lesson_file = f"{lesson}.m4a"
        lesson_ref_file = f"{lesson}_ref.m4a"
        offset_distance = compare_audio(lesson_file, lesson_ref_file)
        # Create columns for Teacher File, Upload Button, and Distance
        col1, col2, col3, col4, col5 = st.columns([2, 1, 2, 2, 3])

        # Display teacher file in the first column
        with col1:
            st.write("")
            st.write("")
            st.write("")
            st.audio(lesson_file, format='audio/m4a')

        # Display file uploader in the second column
        with col2:
            st.write("")
            st.write("")
            st.write("")
            audio_data = record_audio("Record")

        # Process the uploaded student file and display the distance in the third column
        with col3:
            student_path = ""
            if audio_data:
                print("found recorded data")
                st.write("")
                st.empty().audio(audio_data, format="audio/wav")
                # Save the recorded audio to a temporary file
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_audio_file:
                    tmp_audio_file.write(audio_data)
                student_path = tmp_audio_file.name
            else:
                uploaded_student_file = st.file_uploader("", type=["m4a", "wav", "mp3"])
                if uploaded_student_file is not None:
                    student_path = "student_temp.m4a"

                    with open(student_path, "wb") as f:
                        f.write(uploaded_student_file.getbuffer())

            if student_path:
                distance = compare_audio(lesson_file, student_path)
                relative_distance = distance - offset_distance
                lesson_notes = filter_consecutive_notes(get_notes(lesson_file))
                student_notes = filter_consecutive_notes(get_notes(student_path))
        with col4:
            st.write("")
            st.write("")
            if student_path:
                error_notes, missing_notes = error_and_missing_notes(lesson_notes, student_notes)
                score = distance_to_score(relative_distance)
                if score <= 3:
                    message = f"Your score: {score}.\n"
                    if error_notes:
                        message += f"Error notes: {error_notes}.\n"
                    if missing_notes:
                        message += f"Missing notes: {missing_notes}.\n"
                    message += "Keep trying. You can do better!"
                    st.error(message)

                elif score <= 7:
                    message = f"Your score: {score}.\n"
                    if error_notes:
                        message += f"Error notes: {error_notes}.\n"
                    if missing_notes:
                        message += f"Missing notes: {missing_notes}.\n"
                    message += "Good job. You are almost there!"
                    st.warning(message)

                elif score <= 9:
                    message = f"Your score: {score}.\n"
                    if error_notes:
                        message += f"Error notes: {error_notes}.\n"
                    if missing_notes:
                        message += f"Missing notes: {missing_notes}.\n"
                    message += "Great work. Keep it up!"
                    st.info(message)

                else:
                    message = f"Your score: {score}.\n"
                    if error_notes:
                        message += f"Error notes: {error_notes}.\n"
                    if missing_notes:
                        message += f"Missing notes: {missing_notes}.\n"
                    message += "Excellent! You've mastered this lesson!"
                    st.info(message)
        with col5:
            st.write("")
            st.write("")
            message = f"**Lesson notes:** {str(lesson_notes)}"
            if student_path:
                message += f"\n**Student notes:** {str(student_notes)}"
            st.write(message)


def error_and_missing_notes(A, B):
    # Convert lists to sets for easier manipulation
    set_A = set(A)
    set_B = set(B)

    # Find elements in B that are not in A
    elements_in_B_not_in_A = set_B - set_A

    # Find elements in A that are not in B
    elements_in_A_not_in_B = set_A - set_B

    # Convert the sets back to lists, if needed
    list_elements_in_B_not_in_A = list(elements_in_B_not_in_A)
    list_elements_in_A_not_in_B = list(elements_in_A_not_in_B)
    return elements_in_B_not_in_A, elements_in_A_not_in_B


# Function to convert frequency to note
def freq_to_note(freq):
    A4_freq = 440.0
    all_notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    swaras = ['N3', 'S', 'R1', 'R2', 'G2', 'G3', 'M1', 'M2', 'P', 'D1', 'D2', 'N2']
    num_semitones = int(round(12.0 * np.log2(freq / A4_freq)))
    return swaras[num_semitones % 12]


# Function to get frequencies and map them to notes
def get_notes(audio_path):
    y, sr = librosa.load(audio_path)
    o_env = librosa.onset.onset_strength(y=y, sr=sr)
    onset_frames = librosa.onset.onset_detect(onset_envelope=o_env, normalize=True, sr=sr)
    onset_samples = librosa.frames_to_samples(onset_frames)

    # Assuming `slices` is a list of audio slices
    slices = [y[start:end] for start, end in zip(onset_samples[:-1], onset_samples[1:])]
    # Initialize notes list
    notes = []

    for slice in slices:
        # Perform Fourier Transform
        fft_result = np.fft.fft(slice)
        frequencies = np.fft.fftfreq(len(fft_result))

        # Find the peak frequency
        magnitude = np.abs(fft_result)
        peak_frequency = frequencies[np.argmax(magnitude)]

        # Convert frequency to note
        if peak_frequency > 0:
            note = freq_to_note(peak_frequency)
            notes.append(note)

    return notes


from collections import Counter


def filter_consecutive_notes(notes, min_consecutive=2):
    """
    Filters out notes that don't appear consecutively at least `min_consecutive` times.

    Parameters:
        notes (list): List of detected notes.
        min_consecutive (int): Minimum number of consecutive occurrences for a note to be considered.

    Returns:
        list: List of filtered notes.
    """
    filtered_notes = []
    prev_note = None
    count = 0

    for note in notes:
        if note == prev_note:
            count += 1
        else:
            count = 1

        if count == min_consecutive:
            filtered_notes.append(note)

        prev_note = note

    # Remove duplicates while preserving order
    filtered_notes = list(dict.fromkeys(filtered_notes))

    return filtered_notes


if __name__ == "__main__":
    main()
