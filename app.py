import librosa
import numpy as np
from fastdtw import fastdtw
from scipy.spatial.distance import cosine
import streamlit as st
from audio_recorder_streamlit import audio_recorder
import tempfile
import os


def distance_to_score(distance, min_distance=0, max_distance=500):
    """
    Convert a distance value to a score between 0 and 10.

    Parameters:
        distance (float): The distance value to convert.
        min_distance (float): The distance that corresponds to a score of 10.
        max_distance (float): The distance that corresponds to a score of 0.

    Returns:
        int: The converted score.
    """
    if distance <= min_distance:
        return 10
    elif distance >= max_distance:
        return 0
    else:
        return round(10 - ((distance - min_distance) / (max_distance - min_distance) * 10))


def extract_features(audio_path):
    """
    Extract chroma short-time Fourier transform (STFT) features from an audio file.

    Parameters:
        audio_path (str): The path of the audio file.

    Returns:
        np.ndarray: The chroma STFT features.
    """
    y, sr = librosa.load(audio_path)
    chroma_stft = librosa.feature.chroma_stft(y=y, sr=sr)
    return chroma_stft


def compare_audio(teacher_path, student_path):
    """
    Compare two audio files using Fast Dynamic Time Warping (FastDTW).

    Parameters:
        teacher_path (str): The path of the teacher's audio file.
        student_path (str): The path of the student's audio file.

    Returns:
        float: The distance between the two audio files.
    """
    teacher_features = extract_features(teacher_path)
    student_features = extract_features(student_path)
    distance, _ = fastdtw(teacher_features.T, student_features.T, dist=cosine)
    return distance


def audio_display(filename):
    """
    Display an audio file in the Streamlit app.

    Parameters:
        filename (str): The path of the audio file.
    """
    audio_id = st.empty().audio(filename, format='audio/wav')


def record_audio(text):
    """
    Record audio using the Streamlit audio recorder plugin.

    Parameters:
        text (str): The text to display next to the recorder.

    Returns:
        bytes: The recorded audio data.
    """
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
    st.empty().audio(audio_data, format="audio/wav")
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_audio_file:
        tmp_audio_file.write(audio_data)
    recorded_audio_file = tmp_audio_file.name
    return recorded_audio_file


def error_and_missing_notes(A, B):
    """
    Find notes that are incorrect or missing between two lists.

    Parameters:
        A (list): The list of correct notes.
        B (list): The list of notes to check.

    Returns:
        tuple: Two sets containing notes that are incorrect and missing.
    """
    set_A = set(A)
    set_B = set(B)
    elements_in_B_not_in_A = set_B - set_A
    elements_in_A_not_in_B = set_A - set_B
    return elements_in_B_not_in_A, elements_in_A_not_in_B


def freq_to_note(freq):
    """
    Convert a frequency to a musical note.

    Parameters:
        freq (float): The frequency to convert.

    Returns:
        str: The corresponding musical note.
    """
    G5_freq = 783.99
    all_notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    swaras = ['D2', 'N2', 'N3', 'S', 'R1', 'R2', 'G2', 'G3', 'M1', 'M2', 'P', 'D1']
    num_semitones = int(round(12.0 * np.log2(freq / G5_freq)))
    return swaras[num_semitones % 12]


def get_notes(audio_path):
    """
    Extract notes from an audio file.

    Parameters:
        audio_path (str): The path of the audio file.

    Returns:
        list: The list of extracted notes.
    """
    y, sr = librosa.load(audio_path)
    o_env = librosa.onset.onset_strength(y=y, sr=sr)
    onset_frames = librosa.onset.onset_detect(onset_envelope=o_env, normalize=True, sr=sr)
    onset_samples = librosa.frames_to_samples(onset_frames)
    slices = [y[start:end] for start, end in zip(onset_samples[:-1], onset_samples[1:])]
    notes = []
    for slice in slices:
        fft_result = np.fft.fft(slice)
        frequencies = np.fft.fftfreq(len(fft_result))
        magnitude = np.abs(fft_result)
        peak_frequency = frequencies[np.argmax(magnitude)]
        if peak_frequency > 0:
            note = freq_to_note(peak_frequency)
            notes.append(note)
    return notes


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
    filtered_notes = list(dict.fromkeys(filtered_notes))
    return filtered_notes


# Main function where the Streamlit app runs
def setup_streamlit_app():
    """
    Set up the Streamlit app with headers and markdown text.
    """
    st.set_page_config(layout='wide')
    st.header('**String Sync**', divider='rainbow')
    st.markdown(
        """
        String Sync is an innovative platform designed to help music teachers and students enhance 
        their learning experience. By leveraging advanced audio analysis, this app allows you to 
        compare your musical performance with a reference recording, providing you with a 
        quantifiable score based on the similarity.
        
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


def handle_student_login():
    """
    Handle student login through the sidebar.
    """
    st.sidebar.header("Student Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if username and password:  # Add your authentication logic here
            st.sidebar.success(f"Welcome, {username}!")
        else:
            st.sidebar.error("Invalid credentials")


def create_lesson_headers():
    """
    Create headers for the lesson section.
    """
    col1, col2, col3 = st.columns([3, 3, 4])
    with col1:
        st.subheader('Lesson', divider='rainbow')
    with col2:
        st.subheader('Play', divider='rainbow')
    with col3:
        st.subheader('Analysis', divider='rainbow')


def display_lesson_files(lesson_file):
    """
    Display the teacher's lesson files.

    Parameters:
        lesson_file (str): The path to the lesson file.
    """
    st.write("")
    st.write("")
    st.write("")
    st.audio(lesson_file, format='audio/m4a')


def handle_audio_recording():
    """
    Handle audio recording and uploading.

    Returns:
        str: The path to the recorded or uploaded audio file.
    """
    st.write("")
    st.write("")
    st.write("")
    audio_data = record_audio("Record")

    return audio_data


def handle_file_upload(lesson):
    student_path = ""
    uploaded_student_file = st.file_uploader("", type=["m4a", "wav", "mp3"])
    if uploaded_student_file is not None:
        student_path = f"{lesson}-student-recording.m4a"
        with open(student_path, "wb") as f:
            f.write(uploaded_student_file.getbuffer())
    st.audio(uploaded_student_file, format='audio/m4a')
    return student_path


def display_student_performance(lesson_file, student_path, offset_distance):
    """
    Display the student's performance score and remarks.

    Parameters:
        lesson_file (str): The path to the lesson file.
        student_path (str): The path to the student's recorded or uploaded file.
        offset_distance:
    """
    st.write("")
    st.write("")
    if student_path:
        distance = compare_audio(lesson_file, student_path)
        relative_distance = distance - offset_distance
        lesson_notes = get_notes(lesson_file)
        lesson_notes = filter_consecutive_notes(lesson_notes)
        print("Lesson notes:", lesson_notes)
        student_notes = get_notes(student_path)
        student_notes = filter_consecutive_notes(student_notes)
        print("Student notes:", student_notes)
        error_notes, missing_notes = error_and_missing_notes(lesson_notes, student_notes)
        score = distance_to_score(relative_distance)
        display_score_and_remarks(score, error_notes, missing_notes)


def display_score_and_remarks(score, error_notes, missing_notes):
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

    message = ""
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
    message = "Note analysis:\n"
    if error_dict == missing_dict:
        message += f"Your recording had all the notes that the lesson had.\n"
        st.success(message)
    else:
        for first_letter, error_note_list in error_dict.items():
            if first_letter in missing_dict:
                for error_note in error_note_list:
                    message += f"Play {missing_dict[first_letter][0]} instead of {error_note}\n"
            else:
                for error_note in error_note_list:
                    message += f"You played the note {error_note}, however that is not present in the lesson\n"

        for first_letter, missing_note_list in missing_dict.items():
            if first_letter not in error_dict:
                for missing_note in missing_note_list:
                    message += f"You missed playing the note {missing_note}\n"
    st.info(message)
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
        message += "Excellent! You've mastered this lesson!"
        st.success(message)


def display_notation(lesson_notes, student_notes, student_path):
    """
    Display the musical notation for the lesson and student performance.

    Parameters:
        lesson_notes (list): The list of notes in the lesson.
        student_notes (list): The list of notes recorded by the student.
        student_path
    """
    st.write("")
    st.write("")
    message = f"**Lesson notes:** {str(lesson_notes)}"
    if student_path:
        message += f"\n**Student notes:** {str(student_notes)}"
    st.write(message)


def main():
    setup_streamlit_app()
    handle_student_login()
    create_lesson_headers()

    # List all files in the 'lessons' folder
    # List all files in the 'lessons' folder, remove extensions, and filter out files that end with '_ref'
    lesson_files = [os.path.splitext(f)[0] for f in os.listdir('lessons') if not f.endswith('_ref.m4a')]
    selected_lesson = st.sidebar.selectbox("Select a Lesson", lesson_files)

    # Use the selected lesson
    lesson_file = f"lessons/{selected_lesson}.m4a"
    lesson_ref_file = f"lessons/{selected_lesson}_ref.m4a"

    offset_distance = compare_audio(lesson_file, lesson_ref_file)

    col1, col2, col3 = st.columns([3, 3, 4])
    with col1:
        display_lesson_files(lesson_file)
    with col2:
        student_path = handle_file_upload(selected_lesson)
    with col3:
        display_student_performance(lesson_file, student_path, offset_distance)


if __name__ == "__main__":
    main()
