import os
import librosa
import numpy as np
from fastdtw import fastdtw
from scipy.spatial.distance import cosine, euclidean, cityblock, chebyshev, hamming, jaccard, minkowski
import pandas as pd
import streamlit as st


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


def main():
    st.set_page_config(layout='wide')
    st.write("""# String Sync""")
    st.markdown(
        """
        ## Welcome to String Sync! 🎶

        ### What is String Sync?
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
    col1, col2, col3, col4 = st.columns([3, 4, 1, 2])
    with col1:
        st.write("Lesson")
    with col2:
        st.write("Student Recording")
    with col3:
        st.write("Score")
    with col4:
        st.write("Remarks")

    # Compare it with the reference as build an offset

    for lesson in lessons:
        lesson_file = f"{lesson}.m4a"
        lesson_ref_file = f"{lesson}_ref.m4a"
        offset_distance = compare_audio(lesson_file, lesson_ref_file)
        # Create columns for Teacher File, Upload Button, and Distance
        col1, col2, col3, col4 = st.columns([3, 4, 1, 2])

        # Display teacher file in the first column
        with col1:
            st.write("")
            st.write("")
            st.audio(lesson_file, format='audio/m4a')

        # Display file uploader in the second column
        with col2:
            uploaded_student_file = st.file_uploader(f"", type=["m4a", "wav", "mp3"])

        # Process the uploaded student file and display the distance in the third column
        with col3:
            if uploaded_student_file is not None:
                student_path = "student.m4a"

                with open(student_path, "wb") as f:
                    f.write(uploaded_student_file.getbuffer())

                distance = compare_audio(lesson_file, student_path)
                relative_distance = distance - offset_distance
                st.write("")
                st.write("")
                st.write("")
                st.write(f"{distance_to_score(relative_distance)}")

                # Optionally, you can delete the uploaded student file after processing
                os.remove(student_path)

        with col4:
            st.write("")
            st.write("")
            st.write("")


def process_student_files(teacher_path):
    student_paths = [f for f in os.listdir() if f.endswith('.m4a')]
    # Initialize an empty DataFrame
    df = pd.DataFrame(columns=["Student File", "Final Score"])
    print("+----------------+--------------+")
    print("| Student File   | Final Score  |")
    print("+----------------+--------------+")
    audio_display("lessons/w1_l1.m4a")
    for student_path in student_paths:
        score = compare_audio(teacher_path, student_path)
        new_row = pd.DataFrame({"Student File": [student_path], "Final Score": [score]})
        df = pd.concat([df, new_row], ignore_index=True)
    # Display the DataFrame in the console
    st.write(df)


if __name__ == "__main__":
    main()
