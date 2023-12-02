from enum import Enum

from enum import Enum


class UserBadges(Enum):
    FIRST_NOTE = ("First Note", 1, "Celebrate your start by uploading your first recording.")
    RISING_STAR = ("Rising Star", 3, "Shine bright with your emerging talent.")
    ROCKSTAR = ("Rockstar", 5, "Take center stage with your impressive skills.")
    TWO_DAY_STREAK = ("2 Day Streak", 2, "Keep the rhythm! Practice for 2 consecutive days.")
    THREE_DAY_STREAK = ("3 Day Streak", 3, "Harmonize your week with a 3-day practice streak.")
    FIVE_DAY_STREAK = ("5 Day Streak", 5, "Show your dedication with a streak of practicing for 5 days.")
    SEVEN_DAY_STREAK = ("7 Day Streak", 7, "Demonstrate your commitment with a full week of practice.")
    TEN_DAY_STREAK = ("10 Day Streak", 10, "Set the bar high with a 10-day practice streak.")
    WEEKLY_MAX_PRACTICE_MINUTES = ("Practice Champ", 60, "Top the charts with the most practice minutes in a week.")
    WEEKLY_MAX_RECORDING_MINUTES = ("Sound Sorcerer", 10, "Cast a spell by recording the most minutes in a week.")
    WEEKLY_MAX_DAILY_PRACTICE_MINUTES = ("Practice Prodigy", 45, "Showcase your daily diligence in practice.")
    WEEKLY_MAX_RECORDINGS = ("Recording Kingpin", 5, "Rule the studio by making the most recordings in a week.")
    WEEKLY_MAX_SCORER = ("Melody Master", 40, "Hit the high score by earning the most points in a week.")
    WEEKLY_MAX_TRACK_RECORDER = ("Track Titan", 3, "Be prolific! Record on the most number of different tracks.")
    WEEKLY_MAX_BADGE_EARNER = ("Badge Baron", 3, "Be the ultimate achiever by earning a variety of badges.")
    MONTHLY_MAX_PRACTICE_MINUTES = ("Monthly Star", 250, "Be the monthly highlight with your practice minutes.")
    MONTHLY_MAX_RECORDING_MINUTES = ("Mic Champ", 30, "Be the champion of the mic with your monthly recordings.")

    def __init__(self, description, threshold, criteria):
        self._value_ = description
        self.description = description
        self.threshold = threshold
        self.criteria = criteria

    @property
    def value(self):
        return self._value_


class TrackBadges(Enum):
    FAST_LEARNER = "Fast Learner"
    SONG_BIRD = "Song Bird"
    MAESTRO = "Maestro"
    PERFECT_PITCH = "Perfect Pitch"
    MUSIC_WIZARD = "Music Wizard"
    VIRTUOSO = "Virtuoso"
    PRACTICE_MAKES_PERFECT = "Practice Makes Perfect"
