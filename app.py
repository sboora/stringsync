import os
import librosa
import numpy as np
from fastdtw import fastdtw
from scipy.spatial.distance import cosine, euclidean, cityblock, chebyshev, hamming, jaccard, minkowski
import pandas as pd
import streamlit as st


def distance_to_score(distance, min_distance=0, max_distance=1000):
    if distance <= min_distance:
        return 10
    elif distance >= max_distance:
        return 0
    else:
        return 10 - ((distance - min_distance) / (max_distance - min_distance) * 10)


def extract_features(audio_path):
    y, sr = librosa.load(audio_path)
    chroma_stft = librosa.feature.chroma_stft(y=y, sr=sr)
    return chroma_stft


def compare_audio(teacher_path, student_path, distance_function):
    teacher_features = extract_features(teacher_path)
    student_features = extract_features(student_path)

    distance, _ = fastdtw(teacher_features.T, student_features.T, dist=cosine)
    score = distance

    return score


def main():
    st.write("""# String Sync""")
    teacher_path = "teacher.m4a"
    student_paths = [f for f in os.listdir() if f.endswith('.m4a')]

    # Initialize an empty DataFrame
    df = pd.DataFrame(columns=["Student File", "Final Score"])

    print("+----------------+--------------+")
    print("| Student File   | Final Score  |")
    print("+----------------+--------------+")

    for student_path in student_paths:
        score = compare_audio(teacher_path, student_path, cosine)
        new_row = pd.DataFrame({"Student File": [student_path], "Final Score": [score]})
        df = pd.concat([df, new_row], ignore_index=True)

    # Display the DataFrame in the console
    st.write(df)


if __name__ == "__main__":
    main()
