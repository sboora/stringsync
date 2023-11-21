import librosa
import numpy as np
from fastdtw import fastdtw
from scipy.spatial.distance import cosine, euclidean
from scipy.stats import zscore


class AudioProcessor:

    @staticmethod
    def load_and_normalize_audio(audio_path):
        y, sr = librosa.load(audio_path)
        y = librosa.util.normalize(y)
        return y, sr

    @staticmethod
    def compute_mfcc(audio, sr):
        return librosa.feature.mfcc(y=audio, sr=sr)

    @staticmethod
    def compute_chromagram(audio, sr):
        return librosa.feature.chroma_stft(y=audio, sr=sr)

    @staticmethod
    def euclidean_distance(feature1, feature2):
        return euclidean(feature1.flatten(), feature2.flatten())

    @staticmethod
    def cosine_distance(feature1, feature2):
        return cosine(feature1.flatten(), feature2.flatten())

    @staticmethod
    def dtw_euclidean_distance(feature1, feature2):
        distance, _ = fastdtw(feature1.T, feature2.T, dist=euclidean)
        return distance

    @staticmethod
    def dtw_cosine_distance(feature1, feature2):
        distance, _ = fastdtw(feature1.T, feature2.T, dist=cosine)
        return distance

    @staticmethod
    def distance_to_score(distance, min_distance=0, max_distance=1000):
        if distance <= min_distance:
            return 10
        elif distance >= max_distance:
            return 0
        else:
            return round(10 - ((distance - min_distance) / (max_distance - min_distance) * 10))

    @classmethod
    def extract_features(cls, audio_path):
        y, sr = cls.load_and_normalize_audio(audio_path)
        chroma = cls.compute_chromagram(y, sr)
        mfcc = cls.compute_mfcc(y, sr)
        return chroma, zscore(mfcc)

    @classmethod
    def compare_audio(cls, teacher_path, student_path):
        t_chroma, t_mfcc = cls.extract_features(teacher_path)
        s_chroma, s_mfcc = cls.extract_features(student_path)
        return np.mean([cls.dtw_euclidean_distance(t_chroma, s_chroma)])

    @staticmethod
    def error_and_missing_notes(set_a, set_b):
        set_a = set(set_a)
        set_b = set(set_b)
        return set_b - set_a, set_a - set_b

    @staticmethod
    def freq_to_note(freq):
        a4_freq = 440.0
        swaras = ['N3', 'S', 'R1', 'R2', 'G2', 'G3', 'M1', 'M2', 'P', 'D1', 'D2', 'N2']
        num_semitones = int(round(12.0 * np.log2(freq / a4_freq)))
        return swaras[num_semitones % 12]

    @classmethod
    def get_notes(cls, audio_path):
        y, sr = cls.load_and_normalize_audio(audio_path)
        o_env = librosa.onset.onset_strength(y=y, sr=sr)
        onset_frames = librosa.onset.onset_detect(onset_envelope=o_env, normalize=True, sr=sr)
        onset_samples = librosa.frames_to_samples(onset_frames)
        slices = [y[start:end] for start, end in zip(onset_samples[:-1], onset_samples[1:])]
        notes = []
        for audio_slice in slices:
            fft_result = np.fft.fft(audio_slice)
            frequencies = np.fft.fftfreq(len(fft_result))
            magnitude = np.abs(fft_result)
            peak_frequency = frequencies[np.argmax(magnitude)]
            if peak_frequency > 0:
                note= cls.freq_to_note(peak_frequency)
                notes.append(note)
        return notes

    @staticmethod
    def filter_consecutive_notes(notes, min_consecutive=1):
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
        return list(dict.fromkeys(filtered_notes))

    def generate_note_analysis(self, error_notes, missing_notes):
        error_dict = self.group_notes_by_first_letter(error_notes)
        missing_dict = self.group_notes_by_first_letter(missing_notes)

        message = ""
        error_count = 0
        if error_dict == missing_dict:
            message += "Your recording had all the notes that the track had.\n"
        else:
            msg, error_count = self.correlate_notes(error_dict, missing_dict)
            message += msg
        return message, error_count

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
        error_count = 0
        for first_letter, error_note_list in error_dict.items():
            if first_letter in missing_dict:
                for error_note in error_note_list:
                    message += f"Play {missing_dict[first_letter][0]} instead of {error_note}\n"
                    error_count += 1
            else:
                for error_note in error_note_list:
                    message += f"You played the note {error_note}, however that is not present in the track\n"
                    error_count += 1

        for first_letter, missing_note_list in missing_dict.items():
            if first_letter not in error_dict:
                for missing_note in missing_note_list:
                    message += f"You missed playing the note {missing_note}\n"
                    error_count += 1
        return message, error_count

    @staticmethod
    def calculate_audio_duration(path):
        y, sr = librosa.load(path)
        return librosa.get_duration(y=y, sr=sr)
